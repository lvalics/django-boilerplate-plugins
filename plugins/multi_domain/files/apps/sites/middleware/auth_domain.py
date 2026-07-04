"""
Cross-domain authentication middleware.

Handles authentication redirect flow for sites configured with shared auth.
Uses JWT tokens for secure cross-domain user verification.

Security features:
- JWT tokens with unique ID (jti) to prevent replay attacks
- One-time use tokens stored in cache blacklist
- Short expiry (default 5 minutes)
- Target domain validation
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.core.cache import cache
from django.http import HttpResponseRedirect

logger = logging.getLogger(__name__)

# JWT settings
AUTH_TOKEN_SECRET = getattr(settings, "AUTH_TOKEN_SECRET", settings.SECRET_KEY)
AUTH_TOKEN_EXPIRY_MINUTES = getattr(settings, "AUTH_TOKEN_EXPIRY_MINUTES", 5)
AUTH_TOKEN_ALGORITHM = "HS256"

# Cache key prefix for used tokens
USED_TOKEN_CACHE_PREFIX = "auth_token_used:"

# Cache key for cross-site session invalidation
SESSION_INVALIDATION_KEY = "user_session_invalid:{user_id}"
SESSION_INVALIDATION_TIMEOUT = 86400  # 24 hours


def create_auth_token(user, target_domain: str) -> str:
    """
    Create a JWT token for cross-domain authentication.

    Args:
        user: The authenticated user
        target_domain: The domain the user is being redirected to

    Returns:
        JWT token string
    """
    payload = {
        "jti": str(uuid.uuid4()),  # Unique token ID to prevent replay attacks
        "user_id": user.id,
        "email": user.email,
        "target_domain": target_domain,
        "exp": datetime.now(UTC) + timedelta(minutes=AUTH_TOKEN_EXPIRY_MINUTES),
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, AUTH_TOKEN_SECRET, algorithm=AUTH_TOKEN_ALGORITHM)


def verify_auth_token(token: str) -> dict | None:
    """
    Verify and decode a JWT auth token.

    Args:
        token: The JWT token string

    Returns:
        Decoded payload dict or None if invalid
    """
    try:
        payload = jwt.decode(token, AUTH_TOKEN_SECRET, algorithms=[AUTH_TOKEN_ALGORITHM])
    except jwt.ExpiredSignatureError:
        logger.warning("Auth token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid auth token: {e}")
        return None

    # Check for jti claim (required for replay protection)
    jti = payload.get("jti")
    if not jti:
        logger.warning("Auth token missing jti claim")
        return None

    # Atomically consume the token: mark-then-verify closes the TOCTOU window between a
    # separate "is it used?" check and marking it used, so concurrent replays cannot both
    # pass. _mark_token_used returns False if the jti was already consumed OR the cache is
    # unavailable (fail closed).
    if not _mark_token_used(jti):
        return None

    return payload


def _mark_token_used(jti: str) -> bool:
    """
    Atomically mark a token's jti as used.

    Returns True if this call is the first to mark the jti (token may be used). Returns
    False if the jti was already marked (replay) OR the cache backend is unavailable
    (fail closed — never accept a token whose single-use guarantee cannot be enforced).
    """
    cache_key = f"{USED_TOKEN_CACHE_PREFIX}{jti}"
    # Store for slightly longer than token expiry to handle clock skew
    timeout = (AUTH_TOKEN_EXPIRY_MINUTES + 1) * 60
    try:
        added = cache.add(cache_key, True, timeout=timeout)
    except Exception as e:
        logger.warning(f"Auth token replay-protection cache unavailable, rejecting token (jti={jti}): {e}")
        return False

    if not added:
        logger.warning(f"Auth token replay attempt detected: jti={jti}")
    return added


def invalidate_user_sessions(user_id: int) -> None:
    """
    Invalidate all sessions for a user across all sites.

    Call this when:
    - User logs out (to propagate logout to other sites)
    - User changes password
    - User account is deactivated
    - Admin forces logout

    Args:
        user_id: The user ID to invalidate sessions for
    """
    cache_key = SESSION_INVALIDATION_KEY.format(user_id=user_id)
    # Store current timestamp - sessions created before this are invalid
    import time

    cache.set(cache_key, time.time(), timeout=SESSION_INVALIDATION_TIMEOUT)
    logger.info(f"Invalidated sessions for user {user_id} across all sites")


def is_session_valid(user_id: int, session_created: float = None) -> bool:
    """
    Check if user session is still valid (not invalidated).

    Args:
        user_id: The user ID to check
        session_created: When the session was created (timestamp)

    Returns:
        True if session is valid, False if invalidated
    """
    cache_key = SESSION_INVALIDATION_KEY.format(user_id=user_id)
    invalidation_time = cache.get(cache_key)

    if invalidation_time is None:
        # No invalidation record - session is valid
        return True

    if session_created is None:
        # Can't verify session age - assume invalid for safety
        return False

    # Session is valid only if created after invalidation
    return session_created > invalidation_time


def clear_session_invalidation(user_id: int) -> None:
    """
    Clear session invalidation for a user.

    Call this after user logs in fresh to allow new session.

    Args:
        user_id: The user ID to clear invalidation for
    """
    cache_key = SESSION_INVALIDATION_KEY.format(user_id=user_id)
    cache.delete(cache_key)


class AuthDomainMiddleware:
    """
    Handles authentication redirection for shared auth mode.

    For sites configured with auth_mode='shared':
    - If user is not authenticated, redirect to auth_domain for login
    - Auth domain redirects back with JWT token after successful login
    - This middleware captures the return and logs user in

    Must come AFTER MultiDomainMiddleware and AuthenticationMiddleware.
    """

    # Paths that don't require authentication redirect
    EXEMPT_PATHS = [
        "/health/",
        "/api/",
        "/static/",
        "/media/",
        "/__debug__/",
        "/favicon.ico",
    ]

    # Paths that handle auth explicitly
    AUTH_PATHS = [
        "/accounts/",
        "/auth/",
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        site_config = getattr(request, "site_config", None)

        # No site config or isolated auth mode - skip
        if not site_config or site_config.get("auth_mode") != "shared":
            return self.get_response(request)

        # Check if path is exempt
        if self._is_exempt_path(request.path):
            return self.get_response(request)

        # User is authenticated - proceed normally
        if request.user.is_authenticated:
            return self.get_response(request)

        # User not authenticated on shared auth site - redirect to auth domain
        auth_domain_url = site_config.get("auth_domain_url")
        if not auth_domain_url:
            logger.error(f"Site {site_config['domain']} has shared auth but no auth_domain configured")
            return self.get_response(request)

        # Build redirect URL to auth domain
        return_url = request.build_absolute_uri()
        auth_url = self._build_auth_redirect_url(auth_domain_url, return_url)

        logger.debug(f"Redirecting unauthenticated user to auth domain: {auth_url}")
        return HttpResponseRedirect(auth_url)

    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from auth redirect."""
        # Normalize path to prevent traversal attacks (e.g., /static/../admin/)
        from posixpath import normpath

        normalized = normpath(path)
        # Ensure path still starts with / after normalization
        if not normalized.startswith("/"):
            normalized = "/" + normalized

        return any(normalized.startswith(exempt) for exempt in self.EXEMPT_PATHS + self.AUTH_PATHS)

    def _build_auth_redirect_url(self, auth_domain: str, return_url: str) -> str:
        """
        Build the URL to redirect to auth domain.

        The flow is:
        1. Redirect to auth domain's login page
        2. After login, allauth redirects to /auth/callback/ with original URL
        3. auth_callback generates JWT and redirects back to original URL
        """
        scheme = "https" if not settings.DEBUG else "http"
        # First, build the callback URL that allauth should redirect to after login
        callback_params = urlencode({"next": return_url})
        callback_url = f"/auth/callback/?{callback_params}"
        # Then, build the login URL with callback as the next parameter
        login_params = urlencode({"next": callback_url})
        return f"{scheme}://{auth_domain}/accounts/login/?{login_params}"


class AuthCallbackMiddleware:
    """
    Handles the callback from auth domain with JWT token.

    When auth domain completes login, it redirects back with:
    ?auth_token=<jwt>&next=<original_url>

    This middleware:
    1. Validates the JWT token
    2. Gets or creates the local user
    3. Logs them in
    4. Redirects to original URL

    Must come AFTER MultiDomainMiddleware and SessionMiddleware.
    """

    AUTH_TOKEN_PARAM = "auth_token"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check for auth token in query params
        auth_token = request.GET.get(self.AUTH_TOKEN_PARAM)
        if not auth_token:
            return self.get_response(request)

        # Verify token
        payload = verify_auth_token(auth_token)
        if not payload:
            logger.warning("Invalid auth token in callback")
            return self.get_response(request)

        # Verify target domain matches current site
        site_config = getattr(request, "site_config", None)
        if site_config and payload.get("target_domain") != site_config.get("domain"):
            logger.warning(
                f"Auth token target domain mismatch: {payload.get('target_domain')} != {site_config.get('domain')}"
            )
            return self.get_response(request)

        # Get user from shared database
        User = get_user_model()
        try:
            user = User.objects.get(id=payload["user_id"])
        except User.DoesNotExist:
            # User not found - could be deleted or invalid token
            # In single-database setup, user should always exist
            logger.error(
                f"User {payload['user_id']} ({payload.get('email')}) not found for auth callback. "
                "User may have been deleted or token is invalid."
            )
            return self.get_response(request)

        # The token's jti was already atomically consumed inside verify_auth_token()
        # (mark-then-verify), so no separate mark step is needed here.
        jti = payload.get("jti")

        # Log user in
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")

        # Mark session login time for cross-site session validation
        import time

        request.session["_auth_login_time"] = time.time()

        logger.info(f"User {user.email} logged in via auth domain callback (jti={jti})")

        # Redirect to current URL without the auth_token parameter
        clean_url = self._strip_auth_token_from_url(request)
        return HttpResponseRedirect(clean_url)

    def _strip_auth_token_from_url(self, request) -> str:
        """Remove auth_token parameter from current URL."""
        from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

        parsed = urlparse(request.get_full_path())
        query_params = parse_qs(parsed.query, keep_blank_values=True)

        # Remove auth_token
        query_params.pop(self.AUTH_TOKEN_PARAM, None)

        # Rebuild URL
        # parse_qs returns lists, so flatten single values
        clean_params = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        new_query = urlencode(clean_params, doseq=True)

        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment)) or "/"


class SessionValidationMiddleware:
    """
    Validates user sessions against cross-site invalidation cache.

    If a user's session has been invalidated (e.g., logout on another site,
    password change), this middleware will log them out.

    Must come AFTER AuthenticationMiddleware.
    """

    # Session key to store login timestamp
    SESSION_LOGIN_TIME_KEY = "_auth_login_time"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only check authenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Get session login time
        session_login_time = request.session.get(self.SESSION_LOGIN_TIME_KEY)

        # Check if session is still valid
        if not is_session_valid(request.user.id, session_login_time):
            logger.info(f"Session invalidated for user {request.user.id}, logging out")
            from django.contrib.auth import logout

            logout(request)
            # Continue with request as anonymous user
            return self.get_response(request)

        return self.get_response(request)

    @classmethod
    def mark_session_login_time(cls, request):
        """
        Mark the current time as session login time.

        Call this after successful login to enable session validation.
        """
        import time

        request.session[cls.SESSION_LOGIN_TIME_KEY] = time.time()
