"""
Behavior tests for the security-hardening fixes (F3-F10).

Run with:
    make test ARGS='apps.sites.tests.test_security_fixes'

These tests exercise the trusted-proxy IP parsing, atomic JWT replay protection,
integration-secret handling, template_dir traversal defenses, atomic/fail-closed rate
limiting, request-local audit attribution, production ALLOWED_HOSTS behavior, and the
cache lock/health-check fixes.
"""

import os
import types
from unittest import mock

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.template import Engine
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from apps.sites import cache as cache_mod
from apps.sites.context_processors import site_config as site_config_cp
from apps.sites.middleware.allowed_hosts import DynamicAllowedHostsMiddleware
from apps.sites.middleware.auth_domain import create_auth_token, verify_auth_token
from apps.sites.middleware.multi_domain import ThreadLocalMiddleware, get_current_request
from apps.sites.models import SiteProfile, resolve_integration
from apps.sites.ratelimit import get_client_ip, is_rate_limited

LOCMEM = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "security-fixes-tests",
    }
}


# --- F3: trusted-proxy-aware client IP -------------------------------------------------


class ClientIPTrustedProxyTest(SimpleTestCase):
    def _req(self, remote="10.0.0.1", xff=None):
        req = RequestFactory().get("/")
        req.META["REMOTE_ADDR"] = remote
        if xff is not None:
            req.META["HTTP_X_FORWARDED_FOR"] = xff
        return req

    @override_settings(SITES_TRUSTED_PROXY_COUNT=0)
    def test_default_ignores_forwarded_for(self):
        req = self._req(remote="10.0.0.1", xff="9.9.9.9, 8.8.8.8")
        self.assertEqual(get_client_ip(req), "10.0.0.1")

    @override_settings(SITES_TRUSTED_PROXY_COUNT=1)
    def test_one_trusted_proxy_takes_rightmost(self):
        req = self._req(remote="10.0.0.1", xff="9.9.9.9, 8.8.8.8")
        self.assertEqual(get_client_ip(req), "8.8.8.8")

    @override_settings(SITES_TRUSTED_PROXY_COUNT=2)
    def test_two_trusted_proxies_take_second_from_right(self):
        req = self._req(remote="10.0.0.1", xff="1.1.1.1, 9.9.9.9, 8.8.8.8")
        self.assertEqual(get_client_ip(req), "9.9.9.9")

    @override_settings(SITES_TRUSTED_PROXY_COUNT=2)
    def test_malformed_header_falls_back_to_remote_addr(self):
        # Only one XFF entry but two proxies expected -> cannot trust; fall back.
        req = self._req(remote="10.0.0.1", xff="8.8.8.8")
        self.assertEqual(get_client_ip(req), "10.0.0.1")

    @override_settings(SITES_TRUSTED_PROXY_COUNT=1)
    def test_missing_header_falls_back_to_remote_addr(self):
        req = self._req(remote="10.0.0.1")
        self.assertEqual(get_client_ip(req), "10.0.0.1")


# --- F4: atomic single-use JWT replay protection ---------------------------------------


@override_settings(CACHES=LOCMEM)
class AuthTokenReplayTest(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.user = types.SimpleNamespace(id=1, email="user@example.com")

    def test_token_is_single_use(self):
        token = create_auth_token(self.user, "example.com")
        self.assertIsNotNone(verify_auth_token(token))
        # Second verification of the same token is a replay and must be rejected.
        self.assertIsNone(verify_auth_token(token))

    def test_fails_closed_on_cache_outage(self):
        token = create_auth_token(self.user, "example.com")
        with mock.patch("apps.sites.middleware.auth_domain.cache.add", side_effect=Exception("cache down")):
            self.assertIsNone(verify_auth_token(token))


# --- F5: integration secrets stay unresolved in cache/context --------------------------


class IntegrationSecretTest(TestCase):
    def setUp(self):
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()
        self.site = Site.objects.create(domain="int.example.com", name="Int")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Int",
            is_active=True,
            is_primary=True,
            integrations={"stripe": {"secret_key": "env:MD_TEST_SECRET", "public_key": "pk_1"}},
        )

    def test_config_dict_keeps_env_placeholder(self):
        os.environ["MD_TEST_SECRET"] = "sk_real"
        try:
            config = self.profile.to_config_dict()
            self.assertEqual(config["integrations"]["stripe"]["secret_key"], "env:MD_TEST_SECRET")
        finally:
            os.environ.pop("MD_TEST_SECRET", None)

    def test_resolve_integration_resolves_at_call_time(self):
        os.environ["MD_TEST_SECRET"] = "sk_real"
        try:
            config = self.profile.to_config_dict()
            resolved = resolve_integration(config, "stripe")
            self.assertEqual(resolved["secret_key"], "sk_real")
            self.assertEqual(resolved["public_key"], "pk_1")
        finally:
            os.environ.pop("MD_TEST_SECRET", None)

    def test_get_integration_still_resolves(self):
        os.environ["MD_TEST_SECRET"] = "sk_real"
        try:
            self.assertEqual(self.profile.get_integration("stripe")["secret_key"], "sk_real")
        finally:
            os.environ.pop("MD_TEST_SECRET", None)


class ContextProcessorExcludesIntegrationsTest(SimpleTestCase):
    def test_integrations_not_in_template_context(self):
        request = RequestFactory().get("/")
        request.site_config = {
            "site_name": "X",
            "theme": "dark",
            "integrations": {"stripe": {"secret_key": "env:SECRET"}},
        }
        context = site_config_cp(request)
        self.assertNotIn("integrations", context["site_config"])
        self.assertEqual(context["site_name"], "X")


# --- F6: template_dir validation + loader traversal defense ----------------------------


class TemplateDirValidationTest(TestCase):
    def setUp(self):
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()
        self.site = Site.objects.create(domain="tpl.example.com", name="Tpl")

    def _profile(self, template_dir):
        return SiteProfile(
            site=self.site,
            site_name="Tpl",
            is_active=True,
            is_primary=True,
            template_dir=template_dir,
        )

    def test_valid_template_dir_passes(self):
        # Should not raise.
        self._profile("my_site-1").full_clean()

    def test_traversal_sequence_rejected(self):
        with self.assertRaises(ValidationError):
            self._profile("../etc").full_clean()

    def test_slash_rejected(self):
        with self.assertRaises(ValidationError):
            self._profile("a/b").full_clean()

    def test_uppercase_rejected(self):
        with self.assertRaises(ValidationError):
            self._profile("MySite").full_clean()


class LoaderSafeJoinTest(SimpleTestCase):
    def tearDown(self):
        from apps.sites.middleware import multi_domain as mw

        mw._thread_locals.site_config = None

    def test_traversal_template_dir_cannot_escape_root(self):
        from apps.sites.middleware import multi_domain as mw

        engine = Engine(
            dirs=["/tmp/md_templates_root"],
            loaders=["apps.sites.template_loader.SiteTemplateLoader"],
        )
        loader = engine.template_loaders[0]
        mw._thread_locals.site_config = {"template_dir": "../../etc"}
        origins = list(loader.get_template_sources("passwd"))
        # Every yielded source must stay inside the configured templates root; the
        # malicious site-specific path is skipped by safe_join.
        for origin in origins:
            self.assertTrue(str(origin.name).startswith("/tmp/md_templates_root"))


# --- F7: atomic, fail-closed rate limiting ---------------------------------------------


@override_settings(CACHES=LOCMEM)
class RateLimitCounterTest(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_allows_up_to_limit_then_blocks(self):
        results = [is_rate_limited("rl-key", 3, 60)[0] for _ in range(3)]
        self.assertEqual(results, [False, False, False])
        # The 4th request within the window is limited.
        self.assertTrue(is_rate_limited("rl-key", 3, 60)[0])

    def test_fail_closed_denies_on_cache_outage(self):
        with mock.patch("apps.sites.ratelimit.cache.add", side_effect=Exception("down")):
            self.assertTrue(is_rate_limited("rl-fc", 3, 60, fail_closed=True)[0])

    def test_fail_open_allows_on_cache_outage(self):
        with mock.patch("apps.sites.ratelimit.cache.add", side_effect=Exception("down")):
            self.assertFalse(is_rate_limited("rl-fo", 3, 60, fail_closed=False)[0])


# --- F8: request-local audit attribution ----------------------------------------------


class CurrentRequestLocalTest(SimpleTestCase):
    def test_request_is_stashed_during_call_and_cleared_after(self):
        captured = {}

        def view(request):
            captured["request"] = get_current_request()
            return HttpResponse("ok")

        req = RequestFactory().get("/")
        ThreadLocalMiddleware(view)(req)

        self.assertIs(captured["request"], req)
        # Cleared in the finally block after the response.
        self.assertIsNone(get_current_request())


# --- F9: production ALLOWED_HOSTS no longer auto-trusts localhost ----------------------


class AllowedHostsProductionTest(SimpleTestCase):
    def _mw(self):
        return DynamicAllowedHostsMiddleware(lambda r: HttpResponse("ok"))

    @override_settings(DEBUG=False, ALLOWED_HOSTS=["example.com"])
    def test_localhost_rejected_in_production(self):
        req = RequestFactory().get("/")
        req.get_host = lambda: "localhost"  # avoid Django's own host validation
        with mock.patch("apps.sites.middleware.allowed_hosts.get_all_site_domains", return_value=[]):
            response = self._mw()(req)
        self.assertEqual(response.status_code, 400)

    @override_settings(DEBUG=True)
    def test_localhost_allowed_in_debug(self):
        req = RequestFactory().get("/")
        req.get_host = lambda: "localhost"
        response = self._mw()(req)
        self.assertEqual(response.status_code, 200)


# --- F10: cache lock helper + health-check recovery ------------------------------------


@override_settings(CACHES=LOCMEM)
class SafeCacheAddTest(SimpleTestCase):
    def setUp(self):
        cache.clear()

    def test_returns_false_on_cache_outage(self):
        with mock.patch.object(cache_mod, "_is_cache_available", return_value=False):
            self.assertFalse(cache_mod._safe_cache_add("lock-key", "1", timeout=5))

    def test_health_check_logs_and_flips_on_recovery(self):
        # Simulate a previously-down cache; a successful check should mark it available.
        cache_mod._cache_available = False
        cache_mod._last_cache_check = 0
        self.assertTrue(cache_mod._is_cache_available())
        self.assertTrue(cache_mod._cache_available)
