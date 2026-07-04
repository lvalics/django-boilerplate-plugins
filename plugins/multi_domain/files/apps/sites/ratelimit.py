"""
Simple rate limiting using Django's cache.

Provides rate limiting for views and API endpoints to prevent brute-force attacks.
"""

import functools
import hashlib
import logging
import time
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
    """Get client IP address from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def is_rate_limited(key: str, limit: int, period: int) -> tuple[bool, int]:
    """
    Check if key is rate limited.

    Args:
        key: Unique key for rate limiting (e.g., IP + endpoint)
        limit: Maximum requests allowed
        period: Time period in seconds

    Returns:
        Tuple of (is_limited, remaining_requests)
    """
    cache_key = RATE_LIMIT_KEY.format(key=key)
    current_time = time.time()

    # Get existing request times
    request_times = cache.get(cache_key, [])

    # Filter to only requests within the period
    cutoff_time = current_time - period
    request_times = [t for t in request_times if t > cutoff_time]

    # Check if over limit
    if len(request_times) >= limit:
        return True, 0

    # Add current request
    request_times.append(current_time)
    cache.set(cache_key, request_times, timeout=period)

    return False, limit - len(request_times)


def ratelimit(
    rate: str = None,
    key: str = "ip",
    block_time: int = None,
    message: str = "Too many requests. Please try again later.",
):
    """
    Rate limiting decorator for views.

    Args:
        rate: Rate limit string (e.g., "10/m", "100/h")
        key: What to rate limit by ("ip", "user", or callable)
        block_time: How long to block after limit exceeded (seconds)
        message: Error message to return

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
            is_limited, remaining = is_rate_limited(rate_key, limit, period)

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


def ratelimit_method(rate: str = None, key: str = "ip", block_time: int = None, message: str = None):
    """
    Rate limiting decorator for class-based view methods.

    Usage:
        class MyView(APIView):
            @ratelimit_method(rate="5/m")
            def post(self, request):
                ...
    """
    return ratelimit(rate=rate, key=key, block_time=block_time, message=message or "Too many requests.")
