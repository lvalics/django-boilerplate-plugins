"""
Multi-domain middleware for site configuration resolution.

Resolves current site from domain or path prefix and attaches
configuration to request.site_config.
"""

import logging

from asgiref.local import Local
from django.conf import settings
from django.contrib.sites.models import Site
from django.http import Http404

from apps.sites.cache import get_site_config_by_domain

logger = logging.getLogger(__name__)

# Async-safe task/thread-local storage for the current site config (asgiref ships with
# Django; Local works correctly under both WSGI threads and ASGI coroutines).
_thread_locals = Local()


def get_current_site_config():
    """
    Get current site config from thread-local storage.
    Use this in places where request is not available.
    """
    return getattr(_thread_locals, "site_config", None)


def get_current_site():
    """
    Get current Django Site from thread-local storage.
    """
    return getattr(_thread_locals, "site", None)


def get_current_request():
    """
    Get the current request from thread-local storage.

    Set by ThreadLocalMiddleware. Returns None outside the request/response cycle
    (e.g. management commands, Celery tasks). Used for audit attribution in signals.
    """
    return getattr(_thread_locals, "request", None)


class ThreadLocalMiddleware:
    """
    Stores site configuration in thread-local storage.
    Must come AFTER MultiDomainMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store in thread-local
        _thread_locals.site_config = getattr(request, "site_config", None)
        _thread_locals.site = getattr(request, "site", None)
        _thread_locals.request = request

        try:
            return self.get_response(request)
        finally:
            # Clean up
            _thread_locals.site_config = None
            _thread_locals.site = None
            _thread_locals.request = None


class MultiDomainMiddleware:
    """
    Resolves site configuration from domain or path prefix.

    In production: Uses request domain
    In development: Supports path prefix routing (e.g., /site1/page)

    Attaches to request:
    - request.site_config: Full configuration dict
    - request.site: Django Site object
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config = None

        # In DEBUG mode, try path-prefix resolution FIRST
        # This allows /sitename/ to work on any host (localhost, ngrok, etc.)
        if settings.DEBUG:
            config = self._resolve_by_path_prefix(request)

        # Then try domain-based resolution
        if config is None:
            config = self._resolve_by_domain(request)

        if config is None:
            # Fall back to default site
            config = self._get_default_site_config()

        if config is None:
            logger.error("No site configuration found and no default site")
            raise Http404("Site not found")

        # Attach to request
        request.site_config = config
        request.site = self._get_site_object(config["site_id"])

        return self.get_response(request)

    def _resolve_by_domain(self, request) -> dict | None:
        """
        Resolve site by request domain.
        """
        host = request.get_host().split(":")[0]  # Remove port
        return get_site_config_by_domain(host)

    def _resolve_by_path_prefix(self, request) -> dict | None:
        """
        Resolve site by path prefix (development mode only).

        Looks for paths like /mysite/... where 'mysite' is a SiteProfile.path_prefix.
        """
        from apps.sites.models import SiteProfile

        path = request.path_info

        # Extract potential prefix (first path segment)
        parts = path.strip("/").split("/")
        if not parts or not parts[0]:
            return None

        potential_prefix = parts[0]

        try:
            profile = SiteProfile.objects.select_related("site", "auth_domain__site").get(
                path_prefix=potential_prefix, is_active=True
            )

            # Modify path to remove prefix for downstream processing
            new_path = "/" + "/".join(parts[1:])
            if not new_path.endswith("/") and request.path_info.endswith("/"):
                new_path += "/"
            request.path_info = new_path
            request.path = new_path

            logger.debug(f"Resolved site by path prefix: {potential_prefix}")
            return profile.to_config_dict()

        except SiteProfile.DoesNotExist:
            return None

    def _get_default_site_config(self) -> dict | None:
        """
        Get the default (primary) site configuration.
        """
        from apps.sites.models import SiteProfile

        try:
            profile = SiteProfile.objects.select_related("site", "auth_domain__site").get(
                is_primary=True, is_active=True
            )
            return profile.to_config_dict()
        except SiteProfile.DoesNotExist:
            # Try SITE_ID from settings as fallback
            site_id = getattr(settings, "SITE_ID", 1)
            try:
                profile = SiteProfile.objects.select_related("site", "auth_domain__site").get(
                    site_id=site_id, is_active=True
                )
                return profile.to_config_dict()
            except SiteProfile.DoesNotExist:
                return None

    def _get_site_object(self, site_id: int) -> Site:
        """
        Get Django Site object by ID.
        """
        try:
            return Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            return None
