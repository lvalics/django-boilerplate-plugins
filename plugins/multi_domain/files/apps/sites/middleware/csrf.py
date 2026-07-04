"""
Dynamic CSRF middleware for per-site trusted origins.

This middleware extends Django's CsrfViewMiddleware to support per-site
CSRF trusted origins stored in SiteProfile.extra_settings.

Security measures:
1. Only HTTPS origins allowed in production
2. No wildcards permitted
3. Fallback to Django's default if no valid config
4. All custom origin usage is logged for audit
5. Normalizes origins for consistent comparison

Usage:
    In SiteProfile.extra_settings:
    {
        "csrf_trusted_origins": ["https://app.example.com", "https://admin.example.com"]
    }
"""

import logging
from urllib.parse import urlparse

from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware

from apps.sites.middleware.cors import normalize_origin

logger = logging.getLogger(__name__)


class DynamicCsrfMiddleware(CsrfViewMiddleware):
    """
    Per-site CSRF trusted origins with security validation.

    Must be placed AFTER MultiDomainMiddleware in the middleware stack
    to have access to request.site_config.

    Security features:
    - Validates origin format (scheme, no wildcards, no paths)
    - Requires HTTPS in production (DEBUG=False)
    - Logs all custom origin verifications for audit trail
    - Falls back to Django's global CSRF_TRUSTED_ORIGINS if no site config
    """

    def _is_valid_origin(self, origin: str) -> bool:
        """
        Validate origin format for security.

        Args:
            origin: The origin URL to validate

        Returns:
            True if origin is valid and safe to trust
        """
        if not origin or not isinstance(origin, str):
            return False

        # No wildcards allowed
        if "*" in origin:
            logger.warning("CSRF origin rejected - contains wildcard: %s", origin)
            return False

        try:
            parsed = urlparse(origin)

            # Must have scheme and netloc (domain)
            if not parsed.scheme or not parsed.netloc:
                logger.warning("CSRF origin rejected - missing scheme or domain: %s", origin)
                return False

            # In production, require HTTPS
            if not settings.DEBUG and parsed.scheme != "https":
                logger.warning("CSRF origin rejected - must use HTTPS in production: %s", origin)
                return False

            # No paths allowed (origin only, not full URLs)
            if parsed.path and parsed.path != "/":
                logger.warning("CSRF origin rejected - paths not allowed: %s", origin)
                return False

            return True

        except Exception as e:
            logger.warning("CSRF origin rejected - parse error: %s (%s)", origin, e)
            return False

    def _origin_verified(self, request) -> bool:
        """
        Check if the request origin is trusted for this site.

        Origins are normalized before comparison to handle:
        - Case differences (HTTPS://Example.COM vs https://example.com)
        - Default port differences (https://example.com:443 vs https://example.com)
        - Trailing slashes

        First checks site-specific trusted origins from extra_settings,
        then falls back to Django's global CSRF_TRUSTED_ORIGINS.

        Args:
            request: The HTTP request object

        Returns:
            True if origin is verified/trusted
        """
        origin = request.META.get("HTTP_ORIGIN")
        if not origin:
            # No origin header - return False to let Django use other checks (Referer, etc.)
            return False

        # Normalize the request origin for comparison
        normalized_origin = normalize_origin(origin)

        # Get site-specific trusted origins
        site_config = getattr(request, "site_config", None)
        if site_config:
            extra = site_config.get("extra_settings") or {}
            trusted_origins = extra.get("csrf_trusted_origins") or []

            # Validate and check each configured origin (normalized comparison)
            for trusted in trusted_origins:
                if self._is_valid_origin(trusted) and normalized_origin == normalize_origin(trusted):
                    # Log for audit trail
                    logger.info(
                        "CSRF origin verified via site config: origin=%s, site=%s, domain=%s",
                        origin,
                        site_config.get("site_name"),
                        site_config.get("domain"),
                    )
                    return True

        # Fall back to Django's global CSRF_TRUSTED_ORIGINS
        return super()._origin_verified(request)
