import logging

from django.http import HttpResponseForbidden

from apps.web_security.models import IPThreatSummary, SecuritySettings
from apps.web_security.utils import get_client_ip, get_exempt_ips, is_private_ip

logger = logging.getLogger(__name__)


class IPBlockMiddleware:
    """
    Middleware to block requests from blocked IP addresses.

    Should be placed early in the middleware chain for efficiency.
    Checks against cached blocked IP list for < 1ms performance.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get security settings
        settings = SecuritySettings.get_settings()

        # Check if security and IP blocking are enabled
        if not settings.security_enabled or not settings.ip_blocking_enabled:
            return self.get_response(request)

        # Check exempt paths first (webhooks, callbacks - before IP check for efficiency)
        if settings.is_path_whitelisted(request.path):
            return self.get_response(request)

        # Get client IP
        ip_address = get_client_ip(request)

        # Skip private/internal IPs (Docker, localhost, etc.)
        if is_private_ip(ip_address):
            return self.get_response(request)

        # Check whitelist first (from settings and env)
        if settings.is_ip_whitelisted(ip_address):
            return self.get_response(request)

        if ip_address in get_exempt_ips():
            return self.get_response(request)

        # Check if IP is blocked
        if IPThreatSummary.is_ip_blocked(ip_address):
            logger.warning(f"Blocked request from {ip_address} to {request.path}")
            return HttpResponseForbidden(b"Access denied. Your IP address has been blocked due to suspicious activity.")

        return self.get_response(request)
