import logging

from django.http import HttpResponse

from apps.web_security.models import IPThreatSummary, RateLimitRule
from apps.web_security.utils import get_cached_client_ip, get_cached_settings, get_exempt_ips, is_private_ip

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Middleware to enforce rate limits on endpoints.

    Checks requests against configured rate limit rules and
    takes appropriate action when limits are exceeded.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get security settings
        settings = get_cached_settings(request)

        # Check if security and rate limiting are enabled
        if not settings.security_enabled or not settings.rate_limiting_enabled:
            return self.get_response(request)

        # Get client IP
        ip_address = get_cached_client_ip(request)

        # Skip private/internal IPs (Docker, localhost, etc.)
        if is_private_ip(ip_address):
            # Log once per minute to help debug IP resolution issues
            if not hasattr(self, "_last_private_log") or (__import__("time").time() - self._last_private_log > 60):
                self._last_private_log = __import__("time").time()
                logger.warning(
                    "RateLimit: skipping private IP %s (REMOTE_ADDR=%s, XFF=%s, CF=%s)",
                    ip_address,
                    request.META.get("REMOTE_ADDR", ""),
                    request.META.get("HTTP_X_FORWARDED_FOR", ""),
                    request.META.get("HTTP_CF_CONNECTING_IP", ""),
                )
            return self.get_response(request)

        # Check whitelist
        if settings.is_ip_whitelisted(ip_address):
            return self.get_response(request)

        if ip_address in get_exempt_ips():
            return self.get_response(request)

        # Check rate limit
        is_limited, rule, count = RateLimitRule.check_rate_limit(ip_address, request.path, request.method)

        if is_limited and rule:
            action = rule["action"]
            logger.warning(
                f"Rate limit exceeded for {ip_address} on {request.path} "
                f"({count}/{rule['max_requests']} in {rule['time_window_seconds']}s)"
            )

            if action == RateLimitRule.Action.THROTTLE:
                # Return 429 Too Many Requests
                response = HttpResponse(
                    b"Too many requests. Please slow down.",
                    status=429,
                )
                response["Retry-After"] = str(rule["time_window_seconds"])
                return response

            elif action == RateLimitRule.Action.BLOCK:
                # Block IP temporarily
                IPThreatSummary.block_ip(
                    ip_address,
                    reason=f"Rate limit exceeded: {rule['name']}",
                    duration_minutes=rule["block_duration_minutes"],
                )
                return HttpResponse(
                    b"Access denied. Too many requests.",
                    status=403,
                )

            # LOG action - just continue with request

        return self.get_response(request)
