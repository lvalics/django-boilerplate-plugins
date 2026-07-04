"""
Dynamic ALLOWED_HOSTS middleware.

Replaces Django's host validation with database-driven allowed hosts.
Must be placed BEFORE SecurityMiddleware.
"""

import logging

from django.conf import settings
from django.http import HttpResponseBadRequest

from apps.sites.cache import get_all_site_domains

logger = logging.getLogger(__name__)


class DynamicAllowedHostsMiddleware:
    """
    Validates request host against database-configured site domains.

    In DEBUG mode, allows all hosts (like Django's default behavior).
    In production, validates against cached list of site domains.

    Must be placed at the very beginning of MIDDLEWARE list.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # In DEBUG mode, allow all hosts
        if settings.DEBUG:
            return self.get_response(request)

        host = request.get_host().split(":")[0]  # Remove port

        # Check against static ALLOWED_HOSTS first
        static_hosts = getattr(settings, "ALLOWED_HOSTS", [])
        if "*" in static_hosts or host in static_hosts:
            return self.get_response(request)

        # Check against dynamic site domains
        dynamic_hosts = get_all_site_domains()

        if host in dynamic_hosts:
            return self.get_response(request)

        # Note: localhost/127.0.0.1/[::1] are intentionally NOT auto-allowed here. This code
        # path only runs when DEBUG=False (DEBUG short-circuits above and allows all hosts),
        # and silently trusting localhost in production would let a misrouted request bypass
        # host validation. Add such hosts to ALLOWED_HOSTS or a Site domain if truly needed.

        logger.warning(f"Invalid host header: {host}")
        return HttpResponseBadRequest(f"Invalid HTTP_HOST header: '{host}'")
