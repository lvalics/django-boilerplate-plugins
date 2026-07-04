"""
Simple rate limiting using Django's cache.

Provides rate limiting for views and API endpoints to prevent brute-force attacks.
"""

import functools
import hashlib
import logging
from collections.abc import Callable

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, JsonResponse

logger = logging.getLogger(__name__)

# Default rate limit settings
DEFAULT_RATE_LIMIT = getattr(settings, "SITES_RATE_LIMIT", "10/m")  # 10 per minute
DEFAULT_RATE_LIMIT_BLOCK_TIME = getattr(settings, "SITES_RATE_LIMIT_BLOCK_TIME", 60)  # 60 seconds

# Cache key prefix
RATE_LIMIT_KEY = "ratelimit:{key}"


def parse_rate(rate: str) -> tuple[int, int]:
    """
    Parse rate string like "10/m" or "100/h".

    Args:
        rate: Rate string (e.g., "10/m", "100/h", "5/s")

    Returns:
        Tuple of (limit, period_in_seconds)
    """
    parts = rate.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid rate format: {rate}")

    limit = int(parts[0])
    period_char = parts[1].lower()

    periods = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
    }

    if period_char not in periods:
        raise ValueError(f"Invalid period: {period_char}")

    return limit, periods[period_char]


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client IP address from the request.

    X-Forwarded-For is client-controlled and must not be trusted blindly. The number
    of trusted reverse proxies in front of the app is configured via the
    ``SITES_TRUSTED_PROXY_COUNT`` setting (default 0):

    - 0 (default): ignore XFF entirely and use REMOTE_ADDR.
    - N > 0: take the Nth-from-the-right XFF entry (the address the outermost trusted
      proxy observed), since attackers can only prepend spoofed values on the left.

    Falls back to REMOTE_ADDR when the header is missing or malformed.
    """
    remote_addr = request.META.get("REMOTE_ADDR", "unknown")

    trusted_proxies = getattr(settings, "SITES_TRUSTED_PROXY_COUNT", 0)
    if trusted_proxies and trusted_proxies > 0:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            parts = [p.strip() for p in x_forwarded_for.split(",") if p.strip()]
            if len(parts) >= trusted_proxies:
                return parts[-trusted_proxies]

    return remote_addr


def is_rate_limited(key: str, limit: int, period: int, fail_closed: bool = False) -> tuple[bool, int]:
    """
    Check if key is rate limited using an atomic fixed-window counter.

    The counter is stored in the cache and incremented atomically via ``cache.add``
    (seed the window) + ``cache.incr`` so concurrent requests cannot bypass the limit
    through a read-modify-write race (the previous list-based implementation could).

    Note: this is a fixed-window counter (resets every ``period`` seconds), not a
    sliding window, so up to ``limit`` requests are allowed per discrete window.

    Args:
        key: Unique key for rate limiting (e.g., IP + endpoint)
        limit: Maximum requests allowed
        period: Time period in seconds
        fail_closed: On cache outage, deny (True) or allow (False). Auth-sensitive
            callers should fail closed.

    Returns:
        Tuple of (is_limited, remaining_requests)
    """
    cache_key = RATE_LIMIT_KEY.format(key=key)

    try:
        # Seed the window counter only if absent, then increment atomically.
        cache.add(cache_key, 0, timeout=period)
        current = cache.incr(cache_key)
    except Exception as e:
        # Cache outage: fail closed for auth-sensitive callers, open otherwise.
        logger.warning(f"Rate-limit cache unavailable for {key}: {e} (fail_closed={fail_closed})")
        if fail_closed:
            return True, 0
        return False, limit

    if current > limit:
        return True, 0

    return False, max(0, limit - current)


def ratelimit(
    rate: str = None,
    key: str = "ip",
    block_time: int = None,
    message: str = "Too many requests. Please try again later.",
    fail_closed: bool = False,
):
    """
    Rate limiting decorator for views.

    Args:
        rate: Rate limit string (e.g., "10/m", "100/h")
        key: What to rate limit by ("ip", "user", or callable)
        block_time: How long to block after limit exceeded (seconds)
        message: Error message to return
        fail_closed: On cache outage, deny the request (True) instead of allowing it.
            Set True for auth-sensitive endpoints.

    Usage:
        @ratelimit(rate="5/m", key="ip")
        def my_view(request):
            ...
    """
    rate = rate or DEFAULT_RATE_LIMIT
    block_time = block_time or DEFAULT_RATE_LIMIT_BLOCK_TIME
    limit, period = parse_rate(rate)

    def decorator(view_func: Callable) -> Callable:
        @functools.wraps(view_func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            # Build rate limit key
            if callable(key):
                rate_key = key(request)
            elif key == "ip":
                rate_key = f"{get_client_ip(request)}:{request.path}"
            elif key == "user":
                if request.user.is_authenticated:
                    rate_key = f"user:{request.user.id}:{request.path}"
                else:
                    rate_key = f"{get_client_ip(request)}:{request.path}"
            else:
                rate_key = f"{key}:{request.path}"

            # Hash the key for consistent length
            rate_key = hashlib.md5(rate_key.encode()).hexdigest()

            # Check rate limit
            is_limited, remaining = is_rate_limited(rate_key, limit, period, fail_closed=fail_closed)

            if is_limited:
                logger.warning(f"Rate limit exceeded for {rate_key} on {request.path}")
                return JsonResponse(
                    {
                        "error": message,
                        "retry_after": block_time,
                    },
                    status=429,
                )

            # Add rate limit headers to response
            response = view_func(request, *args, **kwargs)

            if hasattr(response, "__setitem__"):
                response["X-RateLimit-Limit"] = str(limit)
                response["X-RateLimit-Remaining"] = str(remaining)
                response["X-RateLimit-Reset"] = str(period)

            return response

        return wrapper

    return decorator


def ratelimit_method(
    rate: str = None, key: str = "ip", block_time: int = None, message: str = None, fail_closed: bool = False
):
    """
    Rate limiting decorator for class-based view methods.

    Usage:
        class MyView(APIView):
            @ratelimit_method(rate="5/m")
            def post(self, request):
                ...
    """
    return ratelimit(
        rate=rate, key=key, block_time=block_time, message=message or "Too many requests.", fail_closed=fail_closed
    )
