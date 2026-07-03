import time

from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class RateLimitRule(BaseModel):
    """
    Rate limiting rules for endpoints.

    Configurable per-endpoint rate limits with different actions
    when limits are exceeded.
    """

    class HttpMethod(models.TextChoices):
        ALL = "all", _("All Methods")
        GET = "GET", _("GET")
        POST = "POST", _("POST")
        PUT = "PUT", _("PUT")
        PATCH = "PATCH", _("PATCH")
        DELETE = "DELETE", _("DELETE")

    class Action(models.TextChoices):
        THROTTLE = "throttle", _("Throttle (429 response)")
        BLOCK = "block", _("Block IP temporarily")
        LOG = "log", _("Log only")

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Descriptive name for this rule"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_("Description of what this rule protects"),
    )
    path_pattern = models.CharField(
        max_length=255,
        verbose_name=_("Path Pattern"),
        help_text=_("URL path pattern to match (supports * wildcards)"),
    )
    http_method = models.CharField(
        max_length=10,
        choices=HttpMethod.choices,
        default=HttpMethod.ALL,
        verbose_name=_("HTTP Method"),
        help_text=_("HTTP method to apply rule to"),
    )
    max_requests = models.PositiveIntegerField(
        default=60,
        verbose_name=_("Max Requests"),
        help_text=_("Maximum number of requests allowed in time window"),
    )
    time_window_seconds = models.PositiveIntegerField(
        default=60,
        verbose_name=_("Time Window (seconds)"),
        help_text=_("Time window for rate limiting"),
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        default=Action.THROTTLE,
        verbose_name=_("Action"),
        help_text=_("Action to take when limit is exceeded"),
    )
    block_duration_minutes = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Block Duration (minutes)"),
        help_text=_("How long to block IP when using block action"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this rule is actively enforced"),
    )
    priority = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Priority"),
        help_text=_("Lower number = higher priority (checked first)"),
    )

    CACHE_KEY = "web_security:rate_limit_rules"
    CACHE_TIMEOUT = 300

    class Meta:
        verbose_name = _("Rate Limit Rule")
        verbose_name_plural = _("Rate Limit Rules")
        ordering = ["priority", "name"]

    def __str__(self):
        return f"{self.name} ({self.max_requests}/{self.time_window_seconds}s)"

    def save(self, *args, **kwargs):
        """Clear cache on save."""
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    def delete(self, *args, **kwargs):
        """Clear cache on delete."""
        super().delete(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    @classmethod
    def get_active_rules(cls):
        """
        Get all active rules, cached for performance.

        Returns:
            list: List of active rules ordered by priority
        """
        rules = cache.get(cls.CACHE_KEY)
        if rules is None:
            rules = list(
                cls.objects.filter(is_active=True)
                .order_by("priority")
                .values(
                    "id",
                    "name",
                    "path_pattern",
                    "http_method",
                    "max_requests",
                    "time_window_seconds",
                    "action",
                    "block_duration_minutes",
                )
            )
            cache.set(cls.CACHE_KEY, rules, cls.CACHE_TIMEOUT)
        return rules

    @classmethod
    def find_matching_rule(cls, path, method):
        """
        Find the first matching rule for a path and method.

        Args:
            path: URL path
            method: HTTP method

        Returns:
            dict or None: Matching rule or None
        """
        rules = cls.get_active_rules()

        for rule in rules:
            # Check method
            if rule["http_method"] != cls.HttpMethod.ALL and rule["http_method"] != method:
                continue

            # Check path pattern (simple wildcard matching)
            pattern = rule["path_pattern"]
            if cls._match_path(pattern, path):
                return rule

        return None

    @staticmethod
    def _match_path(pattern, path):
        """
        Match a path against a pattern with wildcard support.

        Args:
            pattern: Pattern with optional * wildcards
            path: URL path to match

        Returns:
            bool: True if path matches pattern
        """
        import fnmatch

        return fnmatch.fnmatch(path, pattern)

    @classmethod
    def check_rate_limit(cls, ip_address, path, method):
        """
        Check if a request exceeds rate limits.

        Args:
            ip_address: Client IP address
            path: URL path
            method: HTTP method

        Returns:
            tuple: (is_limited, rule, current_count)
        """
        rule = cls.find_matching_rule(path, method)
        if rule is None:
            return False, None, 0

        # Generate cache key for this IP + rule combination
        rule_id = rule["id"]
        window = rule["time_window_seconds"]
        max_requests = rule["max_requests"]
        cache_key = cls._get_rate_limit_key(ip_address, rule_id, window)

        # Atomic rate limiting using Redis SETNX + INCR pattern
        # cache.add() is atomic set-if-not-exists (Redis SETNX)
        cache.add(cache_key, 0, window)

        # cache.incr() is atomic increment (Redis INCR)
        try:
            current_count = cache.incr(cache_key)
        except ValueError:
            # Fallback if cache doesn't support incr (e.g., DummyCache in dev)
            current_count = cache.get(cache_key, 0) + 1
            cache.set(cache_key, current_count, window)

        # Check if over limit
        if current_count > max_requests:
            return True, rule, current_count

        return False, rule, current_count

    @staticmethod
    def _get_rate_limit_key(ip_address, rule_id, window):
        """
        Generate a cache key for rate limiting.

        Uses time window bucketing to ensure accurate counting.
        Key format: web_security:rl:{ip}:{rule_id}:{bucket}
        """
        bucket = int(time.time() / window)
        return f"web_security:rl:{ip_address}:{rule_id}:{bucket}"
