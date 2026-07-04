"""
Dynamic CORS middleware for per-site allowed origins.

This middleware provides per-site CORS configuration by reading allowed
origins from SiteProfile.extra_settings and setting appropriate headers.

It works alongside django-cors-headers:
- django-cors-headers handles global CORS settings (fallback)
- This middleware overrides/enhances for site-specific origins

Security measures:
1. Only HTTPS origins allowed in production
2. No wildcards permitted
3. Validates origin format before trusting
4. Logs all CORS grants for audit
5. Normalizes origins for consistent comparison

Usage:
    In SiteProfile.extra_settings:
    {
        "cors_allowed_origins": ["https://app.example.com", "https://admin.example.com"],
        "frontend_address": "https://app.example.com"
    }
"""

import logging
from urllib.parse import urlparse

from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_origin(origin: str) -> str:
    """
    Normalize an origin for consistent comparison.

    Normalizations applied:
    1. Lowercase scheme and host (domains are case-insensitive)
    2. Strip default ports (:80 for http, :443 for https)
    3. Remove trailing slashes

    Args:
        origin: Origin URL (e.g., "HTTPS://Example.COM:443/")

    Returns:
        Normalized origin (e.g., "https://example.com")
    """
    if not origin or not isinstance(origin, str):
        return ""

    # Strip whitespace and trailing slashes
    origin = origin.strip().rstrip("/")

    try:
        parsed = urlparse(origin)

        if not parsed.scheme or not parsed.netloc:
            return origin.lower()

        # Lowercase scheme
        scheme = parsed.scheme.lower()

        # Parse host and port
        host = parsed.hostname or ""
        port = parsed.port

        # Lowercase the host (domains are case-insensitive)
        host = host.lower()

        # Strip default ports
        if port:
            if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
                port = None

        # Reconstruct the origin
        if port:
            return f"{scheme}://{host}:{port}"
        return f"{scheme}://{host}"

    except Exception:
        # If parsing fails, just lowercase the whole thing
        return origin.lower()


class DynamicCorsMiddleware:
    """
    Per-site CORS allowed origins with security validation.

    Must be placed AFTER MultiDomainMiddleware in the middleware stack
    to have access to request.site_config.

    This middleware:
    1. Checks if the request origin is in the site's cors_allowed_origins
    2. If yes, sets the appropriate CORS headers
    3. If no, lets django-cors-headers handle it (global fallback)

    Security features:
    - Validates origin format (scheme, no wildcards, no paths)
    - Requires HTTPS in production (DEBUG=False)
    - Logs all CORS grants for audit trail
    """

    # Standard CORS headers to allow
    ALLOWED_HEADERS = [
        "accept",
        "accept-encoding",
        "authorization",
        "content-type",
        "dnt",
        "origin",
        "user-agent",
        "x-csrftoken",
        "x-requested-with",
        "x-password-reset-key",
        "x-email-verification-key",
    ]

    ALLOWED_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle preflight OPTIONS requests
        if request.method == "OPTIONS":
            response = self._handle_preflight(request)
            if response:
                return response

        # Process normal request
        response = self.get_response(request)

        # Add CORS headers if origin is allowed
        return self._add_cors_headers(request, response)

    def _is_valid_origin(self, origin: str) -> bool:
        """
        Validate origin format for security.

        Args:
            origin: The origin URL to validate

        Returns:
            True if origin is valid and safe to allow
        """
        if not origin or not isinstance(origin, str):
            return False

        # No wildcards allowed
        if "*" in origin:
            logger.warning("CORS origin rejected - contains wildcard: %s", origin)
            return False

        try:
            parsed = urlparse(origin)

            # Must have scheme and netloc (domain)
            if not parsed.scheme or not parsed.netloc:
                logger.warning("CORS origin rejected - missing scheme or domain: %s", origin)
                return False

            # In production, require HTTPS
            if not settings.DEBUG and parsed.scheme != "https":
                logger.warning("CORS origin rejected - must use HTTPS in production: %s", origin)
                return False

            # No paths allowed (origin only)
            if parsed.path and parsed.path != "/":
                logger.warning("CORS origin rejected - paths not allowed: %s", origin)
                return False

            return True

        except Exception as e:
            logger.warning("CORS origin rejected - parse error: %s (%s)", origin, e)
            return False

    def _is_origin_allowed(self, request, origin: str) -> bool:
        """
        Check if the origin is allowed for this site.

        Origins are normalized before comparison to handle:
        - Case differences (HTTPS://Example.COM vs https://example.com)
        - Default port differences (https://example.com:443 vs https://example.com)
        - Trailing slashes

        Args:
            request: The HTTP request object
            origin: The origin to check

        Returns:
            True if origin is in the site's cors_allowed_origins
        """
        if not origin:
            return False

        site_config = getattr(request, "site_config", None)
        if not site_config:
            return False

        extra = site_config.get("extra_settings") or {}
        allowed_origins = extra.get("cors_allowed_origins") or []

        # Also include frontend_address if set
        frontend_address = extra.get("frontend_address")
        if frontend_address and frontend_address not in allowed_origins:
            allowed_origins = list(allowed_origins) + [frontend_address]

        # Normalize the request origin for comparison
        normalized_origin = normalize_origin(origin)

        # Compare normalized origins
        return any(
            self._is_valid_origin(allowed) and normalized_origin == normalize_origin(allowed)
            for allowed in allowed_origins
        )

    def _handle_preflight(self, request):
        """
        Handle CORS preflight (OPTIONS) requests.

        Returns a response with CORS headers if origin is allowed,
        or None to let other middleware handle it.
        """
        origin = request.META.get("HTTP_ORIGIN", "")

        if not self._is_origin_allowed(request, origin):
            # Let django-cors-headers or other middleware handle it
            return None

        # Origin is allowed for this site - return preflight response
        from django.http import HttpResponse

        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Methods"] = ", ".join(self.ALLOWED_METHODS)
        response["Access-Control-Allow-Headers"] = ", ".join(self.ALLOWED_HEADERS)
        response["Access-Control-Max-Age"] = "86400"  # 24 hours

        site_config = getattr(request, "site_config", None)
        logger.info(
            "CORS preflight allowed: origin=%s, site=%s",
            origin,
            site_config.get("site_name") if site_config else "unknown",
        )

        return response

    def _add_cors_headers(self, request, response):
        """
        Add CORS headers to response if origin is allowed.

        Args:
            request: The HTTP request object
            response: The response object to modify

        Returns:
            The response with CORS headers added (if applicable)
        """
        origin = request.META.get("HTTP_ORIGIN", "")

        if not origin:
            return response

        # Check if already handled by django-cors-headers
        if response.get("Access-Control-Allow-Origin"):
            return response

        if not self._is_origin_allowed(request, origin):
            return response

        # Origin is allowed for this site - add CORS headers
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Credentials"] = "true"

        # Add expose headers for client access
        response["Access-Control-Expose-Headers"] = "Content-Type, X-CSRFToken"

        site_config = getattr(request, "site_config", None)
        logger.debug(
            "CORS headers added: origin=%s, site=%s",
            origin,
            site_config.get("site_name") if site_config else "unknown",
        )

        return response
