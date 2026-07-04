"""
Rate limiting for landing page form submissions.

Provides IP-based and email-based rate limiting to prevent abuse.
"""

import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """
    Get the client IP address from the request.

    X-Forwarded-For is client-controlled and must not be trusted blindly. The
    number of trusted reverse proxies in front of the app is configured via the
    ``SITES_TRUSTED_PROXY_COUNT`` setting (default 0, same setting the
    multi_domain plugin uses):

    - 0 (default): ignore XFF entirely and use REMOTE_ADDR.
    - N > 0: take the Nth-from-the-right XFF entry (the address the outermost
      trusted proxy observed), since attackers can only prepend spoofed values
      on the left.

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


def _mask_email(email: str) -> str:
    """Mask email for GDPR-compliant logging (e.g., 'j***@g***.com')."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.rsplit("@", 1)
    domain_parts = domain.rsplit(".", 1)
    masked_local = local[0] + "***" if local else "***"
    masked_domain = domain_parts[0][0] + "***" if domain_parts[0] else "***"
    tld = "." + domain_parts[1] if len(domain_parts) > 1 else ""
    return f"{masked_local}@{masked_domain}{tld}"


def _mask_ip(ip: str) -> str:
    """Mask IP for GDPR-compliant logging (e.g., '192.168.xxx.xxx')."""
    if not ip:
        return "***"
    parts = ip.split(".")
    if len(parts) == 4:  # IPv4
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    # IPv6 - show first segment only
    if ":" in ip:
        return ip.split(":")[0] + ":***"
    return "***"


class RateLimiter:
    """
    Rate limiter for form submissions.

    Configuration via settings:
    - CMS_RATE_LIMIT_IP_REQUESTS: Max requests per IP (default: 2)
    - CMS_RATE_LIMIT_IP_WINDOW: IP window in seconds (default: 3600)
    - CMS_RATE_LIMIT_EMAIL_REQUESTS: Max requests per email (default: 3)
    - CMS_RATE_LIMIT_EMAIL_WINDOW: Email window in seconds (default: 86400)
    - CMS_EXEMPT_IPS: List of IPs exempt from rate limiting
    """

    def __init__(self):
        self.ip_requests = getattr(settings, "CMS_RATE_LIMIT_IP_REQUESTS", 2)
        self.ip_window = getattr(settings, "CMS_RATE_LIMIT_IP_WINDOW", 3600)
        self.email_requests = getattr(settings, "CMS_RATE_LIMIT_EMAIL_REQUESTS", 3)
        self.email_window = getattr(settings, "CMS_RATE_LIMIT_EMAIL_WINDOW", 86400)
        self.exempt_ips = getattr(settings, "CMS_EXEMPT_IPS", [])

    def _get_cache_key(self, key_type: str, identifier: str) -> str:
        """Generate a cache key for rate limiting."""
        return f"cms:rate_limit:{key_type}:{identifier}"

    def _check_and_increment(self, cache_key: str, limit: int, window: int) -> bool:
        """
        Atomically count a request against a fixed window; True when limited.

        Uses ``cache.add`` (seed) + ``cache.incr`` so concurrent requests cannot
        bypass the limit through a read-modify-write race.
        """
        if cache.add(cache_key, 1, timeout=window):
            return 1 > limit
        try:
            count = cache.incr(cache_key)
        except ValueError:
            # Window expired between add and incr; start a fresh one.
            cache.add(cache_key, 1, timeout=window)
            count = 1
        return count > limit

    def check_limit(self, ip_address: str) -> tuple[bool, str]:
        """
        Check if an IP address is rate limited.

        Returns:
            Tuple of (is_limited, message)
        """
        # Check if IP is exempt
        if ip_address in self.exempt_ips:
            return False, ""

        cache_key = self._get_cache_key("ip", ip_address)
        if self._check_and_increment(cache_key, self.ip_requests, self.ip_window):
            logger.warning("Rate limit exceeded for IP %s", _mask_ip(ip_address))
            return True, f"Too many requests. Please try again in {self.ip_window // 60} minutes."

        return False, ""

    def check_email_limit(self, email: str) -> tuple[bool, str]:
        """
        Check if an email is rate limited.

        Returns:
            Tuple of (is_limited, message)
        """
        email_lower = email.lower().strip()
        cache_key = self._get_cache_key("email", email_lower)
        if self._check_and_increment(cache_key, self.email_requests, self.email_window):
            logger.warning("Rate limit exceeded for email %s", _mask_email(email_lower))
            hours = self.email_window // 3600
            return True, f"This email has reached the maximum number of submissions. Please try again in {hours} hours."

        return False, ""

    def reset_ip_limit(self, ip_address: str):
        """Reset rate limit for an IP address."""
        cache.delete(self._get_cache_key("ip", ip_address))
        logger.info("Reset rate limit for IP %s", _mask_ip(ip_address))

    def reset_email_limit(self, email: str):
        """Reset rate limit for an email."""
        email_lower = email.lower().strip()
        cache.delete(self._get_cache_key("email", email_lower))
        logger.info("Reset rate limit for email %s", _mask_email(email_lower))
