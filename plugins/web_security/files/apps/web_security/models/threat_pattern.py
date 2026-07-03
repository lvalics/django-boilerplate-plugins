import logging
import re
import signal
from contextlib import contextmanager
from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel

logger = logging.getLogger(__name__)

# Default timeout for regex matching (in seconds)
REGEX_MATCH_TIMEOUT = getattr(settings, "WEB_SECURITY_REGEX_TIMEOUT", 0.1)

# Maximum pattern length to prevent extremely long patterns
MAX_PATTERN_LENGTH = getattr(settings, "WEB_SECURITY_MAX_PATTERN_LENGTH", 500)

# Maximum body size to inspect (in bytes) - prevents memory exhaustion on large uploads
# Default 64KB - most malicious payloads are in the first few KB
MAX_BODY_INSPECTION_SIZE = getattr(settings, "WEB_SECURITY_MAX_BODY_SIZE", 65536)


class RegexTimeoutError(Exception):
    """Raised when regex matching exceeds timeout."""

    pass


@contextmanager
def regex_timeout(seconds):
    """
    Context manager to timeout regex operations.

    Uses SIGALRM on Unix systems. Falls back to no timeout on Windows.
    """

    def timeout_handler(signum, frame):
        raise RegexTimeoutError(f"Regex matching timed out after {seconds} seconds")

    # Check if we can use signals (Unix only, main thread only)
    try:
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, old_handler)
    except (ValueError, AttributeError):
        # Windows or not main thread - no timeout available
        yield


def detect_dangerous_pattern(pattern):
    """
    Detect regex patterns that may cause catastrophic backtracking (ReDoS).

    Checks for common dangerous constructs:
    - Nested quantifiers: (a+)+ or (a*)*
    - Overlapping alternations with quantifiers
    - Excessive backtracking potential

    Args:
        pattern: Regex pattern string to check

    Returns:
        tuple: (is_dangerous, reason) - bool and explanation string
    """
    if not pattern:
        return False, ""

    # Check pattern length
    if len(pattern) > MAX_PATTERN_LENGTH:
        return True, f"Pattern exceeds maximum length of {MAX_PATTERN_LENGTH} characters"

    # Dangerous nested quantifier patterns
    # Matches patterns like (a+)+, (a*)+, (a+)* - only + and * after groups are dangerous
    # Note: ? after a group is safe (0 or 1 can't cause catastrophic backtracking)
    nested_quantifiers = re.compile(r"\([^)]*[+*][^)]*\)[+*]|\([^)]*[+*][^)]*\)\{")
    if nested_quantifiers.search(pattern):
        return True, "Nested quantifiers detected - potential catastrophic backtracking"

    # Overlapping character classes with quantifiers
    # E.g., (.+)+ or (.*)*
    greedy_nested = re.compile(r"\(\.[+*]\)[+*]")
    if greedy_nested.search(pattern):
        return True, "Greedy dot with nested quantifier - potential ReDoS"

    # Multiple adjacent quantified groups that could overlap
    # E.g., (\w+)+(\w+)+ - both can match same characters
    adjacent_quantified = re.compile(r"\([^)]+[+*]\)\s*\([^)]+[+*]\)")
    if adjacent_quantified.search(pattern):
        # This is a heuristic - not always dangerous but worth flagging
        logger.warning("Adjacent quantified groups in pattern: %s", pattern[:100])

    # Extreme repetition bounds
    extreme_bounds = re.compile(r"\{(\d+),?\}|\{\d*,(\d+)\}")
    for match in extreme_bounds.finditer(pattern):
        for group in match.groups():
            if group and int(group) > 100:
                return True, f"Excessive repetition bound ({group}) - potential DoS"

    return False, ""


def safe_regex_match(compiled_pattern, target, timeout=None):
    """
    Perform regex match with timeout protection.

    Args:
        compiled_pattern: Pre-compiled regex pattern
        target: String to match against
        timeout: Timeout in seconds (defaults to REGEX_MATCH_TIMEOUT)

    Returns:
        Match object or None if no match or timeout
    """
    if timeout is None:
        timeout = REGEX_MATCH_TIMEOUT

    try:
        with regex_timeout(timeout):
            return compiled_pattern.search(target)
    except RegexTimeoutError:
        logger.warning(
            "Regex match timed out after %.2fs for pattern: %s",
            timeout,
            str(compiled_pattern.pattern)[:50],
        )
        return None
    except Exception as e:
        logger.error("Regex match error: %s", e)
        return None


@lru_cache(maxsize=128)
def compile_pattern_cached(pattern, flags):
    """
    Compile regex pattern with caching.

    Args:
        pattern: Regex pattern string
        flags: Regex flags

    Returns:
        Compiled pattern or None if invalid
    """
    try:
        return re.compile(pattern, flags)
    except re.error:
        return None


class ThreatPattern(BaseModel):
    """
    Dynamic threat detection patterns.

    Stores regex patterns for detecting malicious requests.
    Patterns can match against path, user agent, headers, or request body.
    """

    class MatchType(models.TextChoices):
        PATH = "path", _("URL Path")
        USER_AGENT = "user_agent", _("User Agent")
        HEADER = "header", _("Request Header")
        BODY = "body", _("Request Body")

    class Category(models.TextChoices):
        WORDPRESS = "wordpress", _("WordPress")
        PHP = "php", _("PHP Files")
        SENSITIVE = "sensitive", _("Sensitive Files")
        ADMIN = "admin", _("Admin Panels")
        SCANNER = "scanner", _("Vulnerability Scanners")
        INJECTION = "injection", _("SQL/Code Injection")
        TRAVERSAL = "traversal", _("Directory Traversal")
        SHELL = "shell", _("Shell/Webshell Access")
        API = "api", _("API Endpoints")
        CUSTOM = "custom", _("Custom")

    class ThreatLevel(models.TextChoices):
        LOW = "low", _("Low")
        MEDIUM = "medium", _("Medium")
        HIGH = "high", _("High")
        CRITICAL = "critical", _("Critical")

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Descriptive name for this pattern"),
    )
    description = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Description"),
        help_text=_("Description of what this pattern detects"),
    )
    pattern = models.TextField(
        verbose_name=_("Pattern"),
        help_text=_("Regex pattern to match against requests"),
    )
    match_type = models.CharField(
        max_length=20,
        choices=MatchType.choices,
        default=MatchType.PATH,
        verbose_name=_("Match Type"),
        help_text=_("What part of the request to match against"),
    )
    header_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Header Name"),
        help_text=_("Header name to match (only for Header match type)"),
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.CUSTOM,
        verbose_name=_("Category"),
        help_text=_("Category of threat this pattern detects"),
    )
    threat_level = models.CharField(
        max_length=20,
        choices=ThreatLevel.choices,
        default=ThreatLevel.MEDIUM,
        verbose_name=_("Threat Level"),
        help_text=_("Severity level of matched threats"),
    )
    threat_score = models.PositiveIntegerField(
        default=20,
        verbose_name=_("Threat Score"),
        help_text=_("Score added to IP threat total when matched (0-100)"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this pattern is actively checking requests"),
    )
    case_sensitive = models.BooleanField(
        default=False,
        verbose_name=_("Case Sensitive"),
        help_text=_("Whether pattern matching is case sensitive"),
    )

    CACHE_KEY = "web_security:threat_patterns"
    CACHE_TIMEOUT = 300

    class Meta:
        verbose_name = _("Threat Pattern")
        verbose_name_plural = _("Threat Patterns")
        ordering = ["-threat_level", "category", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()} - {self.get_threat_level_display()})"

    def save(self, *args, **kwargs):
        """Validate pattern and clear cache on save."""
        # Check for dangerous ReDoS patterns first
        is_dangerous, reason = detect_dangerous_pattern(self.pattern)
        if is_dangerous:
            raise ValueError(f"Dangerous regex pattern rejected: {reason}")

        # Validate regex pattern syntax
        try:
            re.compile(self.pattern)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}") from e

        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)
        # Clear the pattern compilation cache too
        compile_pattern_cached.cache_clear()

    def delete(self, *args, **kwargs):
        """Clear cache on delete."""
        super().delete(*args, **kwargs)
        cache.delete(self.CACHE_KEY)

    @classmethod
    def get_active_patterns(cls):
        """
        Get all active patterns, cached for performance.

        Returns:
            list: List of pattern dictionaries
        """
        patterns = cache.get(cls.CACHE_KEY)
        if patterns is None:
            patterns = list(
                cls.objects.filter(is_active=True).values(
                    "id",
                    "name",
                    "pattern",
                    "match_type",
                    "header_name",
                    "category",
                    "threat_level",
                    "threat_score",
                    "case_sensitive",
                )
            )
            # Pre-compile patterns
            for p in patterns:
                flags = 0 if p["case_sensitive"] else re.IGNORECASE
                try:
                    p["compiled"] = re.compile(p["pattern"], flags)
                except re.error:
                    p["compiled"] = None
            cache.set(cls.CACHE_KEY, patterns, cls.CACHE_TIMEOUT)
        return patterns

    @classmethod
    def check_request(cls, path, user_agent="", headers=None, body="", categories=None):
        """
        Check a request against all active patterns.

        Args:
            path: URL path
            user_agent: User-Agent header value
            headers: Dict of request headers
            body: Request body content
            categories: Optional list of categories to check (None = all)

        Returns:
            list: List of matched pattern info dicts
        """
        headers = headers or {}
        matches = []
        patterns = cls.get_active_patterns()

        def should_check_pattern(pattern):
            """Check if pattern should be checked based on categories filter."""
            if categories is None:
                return True
            return pattern["category"] in categories

        for pattern in patterns:
            if pattern["compiled"] is None:
                continue

            if not should_check_pattern(pattern):
                continue

            match_type = pattern["match_type"]
            target = None

            if match_type == cls.MatchType.PATH:
                target = path
            elif match_type == cls.MatchType.USER_AGENT:
                target = user_agent
            elif match_type == cls.MatchType.HEADER:
                header_name = pattern["header_name"]
                target = headers.get(header_name, "")
            elif match_type == cls.MatchType.BODY:
                # Limit body inspection to prevent memory exhaustion on large uploads
                target = body[:MAX_BODY_INSPECTION_SIZE] if body else ""

            if target:
                # Use safe matching with timeout to prevent ReDoS
                match = safe_regex_match(pattern["compiled"], target)
                if match:
                    matches.append(
                        {
                            "pattern_id": pattern["id"],
                            "pattern_name": pattern["name"],
                            "category": pattern["category"],
                            "threat_level": pattern["threat_level"],
                            "threat_score": pattern["threat_score"],
                            "match_type": match_type,
                            "matched_value": target[:200],  # Truncate for storage
                        }
                    )

        return matches
