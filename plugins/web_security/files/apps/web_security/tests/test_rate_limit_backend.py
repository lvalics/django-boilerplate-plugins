"""Tests for RateLimitRule.check_rate_limit's cache-backend handling.

Covers:
- The non-atomic `cache.get`/`cache.set` fallback (taken when `cache.incr` raises
  ValueError, e.g. under Django's DummyCache) now logs loudly instead of silently
  no-opping rate limiting.
- The warning is only emitted once per process ("warn once"), not on every request.
- The normal atomic path (LocMemCache, supports `incr`) still works as expected.
"""

from unittest import mock

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings

from apps.web_security.models import rate_limit as rate_limit_module
from apps.web_security.models.rate_limit import RateLimitRule

LOGGER_NAME = "apps.web_security.models.rate_limit"

FAKE_RULE = {
    "id": 1,
    "name": "test-rule",
    "path_pattern": "/api/*",
    "http_method": RateLimitRule.HttpMethod.ALL,
    "max_requests": 2,
    "time_window_seconds": 60,
    "action": RateLimitRule.Action.THROTTLE,
    "block_duration_minutes": 5,
}


class RateLimitDummyCacheTests(SimpleTestCase):
    """DummyCache makes cache.incr raise ValueError, forcing the fallback path."""

    def setUp(self):
        # Reset the module-level warn-once flag so each test observes it fresh.
        rate_limit_module._warned_non_atomic_cache = False

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_dummy_cache_logs_disabled_warning(self):
        """Under DummyCache, the fallback must log that rate limiting is effectively disabled."""
        with (
            mock.patch.object(RateLimitRule, "find_matching_rule", return_value=FAKE_RULE),
            self.assertLogs(LOGGER_NAME, level="WARNING") as captured,
        ):
            is_limited, rule, count = RateLimitRule.check_rate_limit("1.2.3.4", "/api/foo", "GET")

        self.assertTrue(any("DISABLED" in message for message in captured.output))
        # The DummyCache fallback also means it never actually blocks anything.
        self.assertFalse(is_limited)
        self.assertEqual(rule, FAKE_RULE)
        self.assertEqual(count, 1)

    @override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
    def test_warning_is_only_logged_once(self):
        """The warn-once flag must prevent log spam across repeated calls."""
        with mock.patch.object(RateLimitRule, "find_matching_rule", return_value=FAKE_RULE):
            with self.assertLogs(LOGGER_NAME, level="WARNING") as captured:
                RateLimitRule.check_rate_limit("1.2.3.4", "/api/foo", "GET")
            self.assertEqual(len(captured.output), 1)

            # A second call must not log again (warn-once), so assertLogs would
            # raise AssertionError if no log records were emitted - which is what
            # we want to confirm here.
            with self.assertRaises(AssertionError):
                with self.assertLogs(LOGGER_NAME, level="WARNING"):
                    RateLimitRule.check_rate_limit("1.2.3.4", "/api/foo", "GET")


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class RateLimitLocMemCacheTests(SimpleTestCase):
    """Sanity check: the normal atomic path (cache.incr supported) still works."""

    def setUp(self):
        rate_limit_module._warned_non_atomic_cache = False
        cache.clear()

    def test_locmem_allows_then_blocks_over_limit(self):
        with mock.patch.object(RateLimitRule, "find_matching_rule", return_value=FAKE_RULE):
            # max_requests is 2 - first two requests are allowed.
            is_limited, rule, count = RateLimitRule.check_rate_limit("5.6.7.8", "/api/foo", "GET")
            self.assertFalse(is_limited)
            self.assertEqual(count, 1)

            is_limited, rule, count = RateLimitRule.check_rate_limit("5.6.7.8", "/api/foo", "GET")
            self.assertFalse(is_limited)
            self.assertEqual(count, 2)

            # Third request exceeds max_requests=2.
            is_limited, rule, count = RateLimitRule.check_rate_limit("5.6.7.8", "/api/foo", "GET")
            self.assertTrue(is_limited)
            self.assertEqual(rule, FAKE_RULE)
            self.assertEqual(count, 3)
