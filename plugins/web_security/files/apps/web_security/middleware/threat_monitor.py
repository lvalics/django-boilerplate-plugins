import logging

from apps.web_security.models import ThreatPattern
from apps.web_security.models.threat_pattern import MAX_BODY_INSPECTION_SIZE
from apps.web_security.utils import get_cached_client_ip, get_cached_settings, get_exempt_ips, is_private_ip

logger = logging.getLogger(__name__)


class ThreatMonitorMiddleware:
    """
    Middleware to detect and log threats based on patterns.

    Checks incoming requests against configured threat patterns
    and logs suspicious activity for analysis.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get security settings (resolved once per request, shared across middleware)
        settings = get_cached_settings(request)

        # Check if security and threat detection are enabled
        if not settings.security_enabled or not settings.threat_detection_enabled:
            return self.get_response(request)

        # Check exempt paths first (webhooks, callbacks - skip threat detection)
        if settings.is_path_whitelisted(request.path):
            return self.get_response(request)

        # Get client IP (resolved once per request, shared across middleware)
        ip_address = get_cached_client_ip(request)

        # Skip private/internal IPs (Docker, localhost, etc.)
        if is_private_ip(ip_address):
            return self.get_response(request)

        # Check whitelist
        if settings.is_ip_whitelisted(ip_address):
            return self.get_response(request)

        if ip_address in get_exempt_ips():
            return self.get_response(request)

        # Get enabled categories
        enabled_categories = settings.get_enabled_categories()

        # Prepare request data for pattern matching
        path = request.path
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Get headers
        headers = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value

        # Get body for POST/PUT/PATCH
        body = ""
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.META.get("CONTENT_LENGTH")
            try:
                content_length = int(content_length)
            except (TypeError, ValueError):
                content_length = None

            if content_length is not None and content_length > MAX_BODY_INSPECTION_SIZE:
                logger.debug(
                    f"Skipping body inspection for {request.method} {request.path}: "
                    f"Content-Length {content_length} exceeds {MAX_BODY_INSPECTION_SIZE}"
                )
            else:
                import contextlib

                with contextlib.suppress(Exception):
                    body = request.body[:MAX_BODY_INSPECTION_SIZE].decode("utf-8", errors="replace")

        # Check against patterns
        matches = ThreatPattern.check_request(
            path=path,
            user_agent=user_agent,
            headers=headers,
            body=body,
            categories=enabled_categories,
        )

        if matches:
            for match in matches:
                logger.warning(
                    f"Threat detected from {ip_address}: "
                    f"{match['pattern_name']} ({match['category']}) "
                    f"on {request.method} {path}"
                )

            # Persist off the request path (DB writes + row locks run in a Celery task, not
            # inline in the response). Args are plain/serializable — no request object.
            request_data = {
                "path": path,
                "method": request.method,
                "user_agent": user_agent,
                "headers": headers,
                "body_preview": body[:1000],
            }
            try:
                from apps.web_security.tasks import record_threat_matches

                record_threat_matches.delay(ip_address, matches, request_data, settings.ip_reputation_enabled)
            except Exception as e:
                logger.error(f"Failed to enqueue threat recording for {ip_address}: {e}")

        response = self.get_response(request)

        return response
