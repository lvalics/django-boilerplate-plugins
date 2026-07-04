"""
Unit tests for per-site CORS and CSRF middleware.

Run with:
    make test ARGS='apps.sites.tests.test_cors_csrf'
"""

from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase, override_settings

from apps.sites.middleware.cors import DynamicCorsMiddleware
from apps.sites.middleware.csrf import DynamicCsrfMiddleware
from apps.sites.models import SiteProfile


@override_settings(DEBUG=True)
class DynamicCorsMiddlewareTest(TestCase):
    """Tests for DynamicCorsMiddleware."""

    def setUp(self):
        """Create test site with CORS config."""
        self.factory = RequestFactory()
        self.site = Site.objects.create(domain="cors-test.example.com", name="CORS Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="CORS Test",
            is_active=True,
            is_primary=True,
            extra_settings={
                "frontend_address": "http://localhost:5174",
                "cors_allowed_origins": ["http://localhost:5174", "http://localhost:3000"],
            },
        )

        # Create middleware instance
        self.middleware = DynamicCorsMiddleware(lambda request: self._dummy_response())

    def _dummy_response(self):
        """Return a dummy response."""
        from django.http import HttpResponse

        return HttpResponse("OK")

    def _attach_site_config(self, request):
        """Attach site_config to request."""
        request.site_config = self.profile.to_config_dict()
        return request

    def test_cors_headers_added_for_allowed_origin(self):
        """Test that CORS headers are added for allowed origins."""
        request = self.factory.get("/api/test/", HTTP_ORIGIN="http://localhost:5174")
        request = self._attach_site_config(request)

        response = self.middleware(request)

        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:5174")
        self.assertEqual(response["Access-Control-Allow-Credentials"], "true")

    def test_cors_headers_not_added_for_disallowed_origin(self):
        """Test that CORS headers are NOT added for disallowed origins."""
        request = self.factory.get("/api/test/", HTTP_ORIGIN="http://evil.com")
        request = self._attach_site_config(request)

        response = self.middleware(request)

        self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_cors_preflight_allowed_origin(self):
        """Test OPTIONS preflight response for allowed origin."""
        request = self.factory.options(
            "/api/test/",
            HTTP_ORIGIN="http://localhost:5174",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        request = self._attach_site_config(request)

        response = self.middleware(request)

        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:5174")
        self.assertIn("POST", response["Access-Control-Allow-Methods"])

    def test_cors_preflight_disallowed_origin(self):
        """Test OPTIONS preflight for disallowed origin falls through."""
        request = self.factory.options(
            "/api/test/",
            HTTP_ORIGIN="http://evil.com",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
        )
        request = self._attach_site_config(request)

        response = self.middleware(request)

        # Should not have CORS headers from our middleware
        self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_frontend_address_included_automatically(self):
        """Test that frontend_address is included in allowed origins."""
        # frontend_address is http://localhost:5174, which is also in cors_allowed_origins
        # Test with just the frontend_address
        self.profile.extra_settings = {
            "frontend_address": "http://localhost:9999",
            "cors_allowed_origins": [],  # Empty, but frontend_address should work
        }
        self.profile.save()

        request = self.factory.get("/api/test/", HTTP_ORIGIN="http://localhost:9999")
        request.site_config = self.profile.to_config_dict()

        response = self.middleware(request)

        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:9999")

    def test_no_origin_header_passthrough(self):
        """Test that requests without Origin header pass through."""
        request = self.factory.get("/api/test/")
        request = self._attach_site_config(request)

        response = self.middleware(request)

        # No CORS headers should be added
        self.assertNotIn("Access-Control-Allow-Origin", response)
        self.assertEqual(response.content, b"OK")


@override_settings(DEBUG=True)
class DynamicCsrfMiddlewareTest(TestCase):
    """Tests for DynamicCsrfMiddleware."""

    def setUp(self):
        """Create test site with CSRF config."""
        self.factory = RequestFactory()
        self.site = Site.objects.create(domain="csrf-test.example.com", name="CSRF Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="CSRF Test",
            is_active=True,
            is_primary=True,
            extra_settings={
                "csrf_trusted_origins": ["http://localhost:5174", "http://localhost:3000"],
            },
        )

        # Create middleware instance
        self.middleware = DynamicCsrfMiddleware(lambda request: self._dummy_response())

    def _dummy_response(self):
        """Return a dummy response."""
        from django.http import HttpResponse

        return HttpResponse("OK")

    def _attach_site_config(self, request):
        """Attach site_config to request."""
        request.site_config = self.profile.to_config_dict()
        return request

    def test_origin_verified_for_trusted_origin(self):
        """Test that trusted origins are verified."""
        request = self.factory.post("/api/test/")
        request.META["HTTP_ORIGIN"] = "http://localhost:5174"
        request = self._attach_site_config(request)

        result = self.middleware._origin_verified(request)

        self.assertTrue(result)

    def test_origin_not_verified_for_untrusted_origin(self):
        """Test that untrusted origins are not verified (falls back to Django)."""
        request = self.factory.post("/api/test/")
        request.META["HTTP_ORIGIN"] = "http://evil.com"
        request = self._attach_site_config(request)

        # This should return False from our check, and fall back to Django's check
        # which will also return False for an untrusted origin
        result = self.middleware._origin_verified(request)

        self.assertFalse(result)

    def test_no_origin_header_falls_through(self):
        """Test that requests without Origin fall through to Django's check."""
        request = self.factory.post("/api/test/")
        request = self._attach_site_config(request)

        # Without Origin header, should fall through to Django's default
        result = self.middleware._origin_verified(request)

        # Django's default will handle it
        self.assertFalse(result)  # No referer or origin means False by default


class OriginValidationTest(TestCase):
    """Tests for origin validation in middleware."""

    def setUp(self):
        """Create middleware instances for validation testing."""
        self.cors_middleware = DynamicCorsMiddleware(lambda r: None)
        self.csrf_middleware = DynamicCsrfMiddleware(lambda r: None)

    def test_valid_https_origin(self):
        """Test that valid HTTPS origin passes validation."""
        self.assertTrue(self.cors_middleware._is_valid_origin("https://example.com"))
        self.assertTrue(self.csrf_middleware._is_valid_origin("https://example.com"))

    def test_valid_http_origin_in_debug(self):
        """Test that HTTP origin passes in DEBUG mode."""
        with override_settings(DEBUG=True):
            self.assertTrue(self.cors_middleware._is_valid_origin("http://localhost:5174"))
            self.assertTrue(self.csrf_middleware._is_valid_origin("http://localhost:5174"))

    @override_settings(DEBUG=False)
    def test_http_origin_rejected_in_production(self):
        """Test that HTTP origin is rejected in production."""
        self.assertFalse(self.cors_middleware._is_valid_origin("http://example.com"))
        self.assertFalse(self.csrf_middleware._is_valid_origin("http://example.com"))

    def test_wildcard_origin_rejected(self):
        """Test that wildcard origins are rejected."""
        self.assertFalse(self.cors_middleware._is_valid_origin("*"))
        self.assertFalse(self.cors_middleware._is_valid_origin("*.example.com"))
        self.assertFalse(self.csrf_middleware._is_valid_origin("*"))

    def test_origin_with_path_rejected(self):
        """Test that origins with paths are rejected."""
        self.assertFalse(self.cors_middleware._is_valid_origin("https://example.com/api"))
        self.assertFalse(self.csrf_middleware._is_valid_origin("https://example.com/api"))

    def test_origin_without_scheme_rejected(self):
        """Test that origins without scheme are rejected."""
        self.assertFalse(self.cors_middleware._is_valid_origin("example.com"))
        self.assertFalse(self.csrf_middleware._is_valid_origin("example.com"))

    def test_empty_origin_rejected(self):
        """Test that empty origins are rejected."""
        self.assertFalse(self.cors_middleware._is_valid_origin(""))
        self.assertFalse(self.cors_middleware._is_valid_origin(None))
        self.assertFalse(self.csrf_middleware._is_valid_origin(""))
        self.assertFalse(self.csrf_middleware._is_valid_origin(None))

    def test_origin_with_trailing_slash_accepted(self):
        """Test that origin with trailing slash (root path) is accepted."""
        self.assertTrue(self.cors_middleware._is_valid_origin("https://example.com/"))
        self.assertTrue(self.csrf_middleware._is_valid_origin("https://example.com/"))


class SiteProfileValidationTest(TestCase):
    """Tests for CORS/CSRF validation in SiteProfile model."""

    def setUp(self):
        """Create test site."""
        self.site = Site.objects.create(domain="validation-test.example.com", name="Validation Test")

    def test_valid_cors_origins_accepted(self):
        """Test that valid CORS origins are accepted."""
        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "cors_allowed_origins": ["http://localhost:5174", "https://app.example.com"],
            },
        )
        # Should not raise
        profile.full_clean()

    def test_wildcard_origin_rejected(self):
        """Test that wildcard origins are rejected in model validation."""
        from django.core.exceptions import ValidationError

        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "cors_allowed_origins": ["*"],
            },
        )
        with self.assertRaises(ValidationError) as ctx:
            profile.full_clean()
        self.assertIn("Wildcards", str(ctx.exception))

    def test_origin_with_path_rejected(self):
        """Test that origins with paths are rejected in model validation."""
        from django.core.exceptions import ValidationError

        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "cors_allowed_origins": ["https://example.com/api"],
            },
        )
        with self.assertRaises(ValidationError) as ctx:
            profile.full_clean()
        self.assertIn("should not include a path", str(ctx.exception))

    def test_invalid_url_format_rejected(self):
        """Test that invalid URL formats are rejected in model validation."""
        from django.core.exceptions import ValidationError

        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "cors_allowed_origins": ["not-a-url"],
            },
        )
        with self.assertRaises(ValidationError) as ctx:
            profile.full_clean()
        self.assertIn("not a valid URL", str(ctx.exception))

    def test_non_list_origins_rejected(self):
        """Test that non-list cors_allowed_origins is rejected."""
        from django.core.exceptions import ValidationError

        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "cors_allowed_origins": "https://example.com",  # String, not list
            },
        )
        with self.assertRaises(ValidationError) as ctx:
            profile.full_clean()
        self.assertIn("must be a list", str(ctx.exception))

    def test_valid_frontend_address_accepted(self):
        """Test that valid frontend_address is accepted."""
        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "frontend_address": "https://app.example.com",
            },
        )
        # Should not raise
        profile.full_clean()

    def test_invalid_frontend_address_rejected(self):
        """Test that invalid frontend_address is rejected."""
        from django.core.exceptions import ValidationError

        profile = SiteProfile(
            site=self.site,
            site_name="Test",
            is_active=True,
            extra_settings={
                "frontend_address": "not-a-url",
            },
        )
        with self.assertRaises(ValidationError) as ctx:
            profile.full_clean()
        self.assertIn("not a valid URL", str(ctx.exception))
