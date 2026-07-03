import logging

from apps.web_security.models import (
    IPReputationCache,
    IPThreatSummary,
    SecuritySettings,
    SuspiciousRequest,
    ThreatPattern,
)
from apps.web_security.models.threat_pattern import MAX_BODY_INSPECTION_SIZE
from apps.web_security.utils import get_client_ip, get_exempt_ips, is_private_ip

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
        # Get security settings
        settings = SecuritySettings.get_settings()

        # Check if security and threat detection are enabled
        if not settings.security_enabled or not settings.threat_detection_enabled:
            return self.get_response(request)

        # Check exempt paths first (webhooks, callbacks - skip threat detection)
        if settings.is_path_whitelisted(request.path):
            return self.get_response(request)

        # Get client IP
        ip_address = get_client_ip(request)

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
            # Log each match
            for match in matches:
                logger.warning(
                    f"Threat detected from {ip_address}: "
                    f"{match['pattern_name']} ({match['category']}) "
                    f"on {request.method} {path}"
                )

                # Log suspicious request
                SuspiciousRequest.log_suspicious_request(
                    request=request,
                    ip_address=ip_address,
                    match_info=match,
                    action_taken="logged",
                )

                # Update IP threat summary
                IPThreatSummary.add_threat(
                    ip_address=ip_address,
                    threat_score=match["threat_score"],
                    category=match["category"],
                )

            # Queue IP for reputation check if enabled
            if settings.ip_reputation_enabled:
                IPReputationCache.get_or_queue(ip_address)

        response = self.get_response(request)

        return response
