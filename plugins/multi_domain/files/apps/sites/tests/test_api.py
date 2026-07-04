"""
Unit tests for Site Config API endpoints.

Run with:
    make test ARGS='apps.sites.tests.test_api'
"""

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.sites.models import SiteProfile

# URL names use "sites" namespace
URL_CONFIG = "sites:site_config_api"
URL_BRANDING = "sites:site_branding_api"
URL_FEATURES = "sites:site_features_api"


class SiteConfigAPITest(TestCase):
    """Tests for /api/sites/config/ endpoint."""

    def setUp(self):
        """Create test site and profile."""
        self.client = APIClient()
        self.site = Site.objects.create(domain="api-test.example.com", name="API Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="API Test Site Display",
            tagline="Welcome to API Test",
            theme="dark",
            primary_color="#10B981",
            secondary_color="#059669",
            is_active=True,
            is_primary=True,
            features={"enable_blog": True, "enable_shop": False},
            default_language="en",
            available_languages=["en", "de"],
            integrations={"stripe": {"secret_key": "sk_test_secret"}},
            auth_settings={"session_timeout": 3600},
        )

    def test_get_site_config(self):
        """Test GET /api/sites/config/ returns public config."""
        url = reverse(URL_CONFIG)
        response = self.client.get(url, HTTP_HOST="api-test.example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["site_id"], self.site.id)
        self.assertEqual(data["site_name"], "API Test Site Display")
        self.assertEqual(data["tagline"], "Welcome to API Test")
        self.assertEqual(data["theme"], "dark")
        self.assertEqual(data["primary_color"], "#10B981")
        self.assertEqual(data["features"]["enable_blog"], True)
        self.assertEqual(data["default_language"], "en")

    def test_config_excludes_sensitive_fields(self):
        """Test that sensitive fields are not exposed."""
        url = reverse(URL_CONFIG)
        response = self.client.get(url, HTTP_HOST="api-test.example.com")

        data = response.json()

        # These should NOT be in the response
        self.assertNotIn("integrations", data)
        self.assertNotIn("auth_settings", data)
        self.assertNotIn("email_settings", data)
        self.assertNotIn("head_scripts", data)
        self.assertNotIn("body_scripts", data)

    def test_config_cache_headers(self):
        """Test that response includes proper cache headers."""
        url = reverse(URL_CONFIG)
        response = self.client.get(url, HTTP_HOST="api-test.example.com")

        self.assertIn("Cache-Control", response)
        self.assertIn("max-age=300", response["Cache-Control"])
        self.assertIn("Host", response["Vary"])

    def test_config_404_for_unknown_domain(self):
        """Test that unknown domain returns 404."""
        url = reverse(URL_CONFIG)
        response = self.client.get(url, HTTP_HOST="unknown.example.com")

        # Should return 404 or use default site
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK])


class SiteBrandingAPITest(TestCase):
    """Tests for /api/sites/branding/ endpoint."""

    def setUp(self):
        """Create test site and profile."""
        self.client = APIClient()
        self.site = Site.objects.create(domain="branding-test.example.com", name="Branding Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Branding Test",
            theme="custom",
            primary_color="#EF4444",
            secondary_color="#DC2626",
            is_active=True,
            is_primary=True,
        )

    def test_get_site_branding(self):
        """Test GET /api/sites/branding/ returns branding only."""
        url = reverse(URL_BRANDING)
        response = self.client.get(url, HTTP_HOST="branding-test.example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["site_name"], "Branding Test")
        self.assertEqual(data["theme"], "custom")
        self.assertEqual(data["primary_color"], "#EF4444")
        self.assertEqual(data["secondary_color"], "#DC2626")
        self.assertIsNone(data["logo_url"])

    def test_branding_excludes_other_fields(self):
        """Test that branding endpoint only returns branding fields."""
        url = reverse(URL_BRANDING)
        response = self.client.get(url, HTTP_HOST="branding-test.example.com")

        data = response.json()

        # Should NOT include these
        self.assertNotIn("features", data)
        self.assertNotIn("tagline", data)
        self.assertNotIn("default_language", data)


class SiteFeaturesAPITest(TestCase):
    """Tests for /api/sites/features/ endpoint."""

    def setUp(self):
        """Create test site and profile."""
        self.client = APIClient()
        self.site = Site.objects.create(domain="features-test.example.com", name="Features Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Features Test",
            is_active=True,
            is_primary=True,
            features={
                "enable_blog": True,
                "enable_shop": False,
                "enable_chat": True,
                "maintenance_mode": False,
            },
        )

    def test_get_site_features(self):
        """Test GET /api/sites/features/ returns features only."""
        url = reverse(URL_FEATURES)
        response = self.client.get(url, HTTP_HOST="features-test.example.com")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data["enable_blog"], True)
        self.assertEqual(data["enable_shop"], False)
        self.assertEqual(data["enable_chat"], True)
        self.assertEqual(data["maintenance_mode"], False)

    def test_features_excludes_other_fields(self):
        """Test that features endpoint only returns feature flags."""
        url = reverse(URL_FEATURES)
        response = self.client.get(url, HTTP_HOST="features-test.example.com")

        data = response.json()

        # Should NOT include these
        self.assertNotIn("site_name", data)
        self.assertNotIn("theme", data)
        self.assertNotIn("primary_color", data)


class SiteConfigAPIPublicAccessTest(TestCase):
    """Tests for public access to API endpoints."""

    def setUp(self):
        """Create test site."""
        self.client = APIClient()
        self.site = Site.objects.create(domain="public.example.com", name="Public")
        SiteProfile.objects.create(
            site=self.site,
            site_name="Public Site",
            is_active=True,
            is_primary=True,
        )

    def test_config_accessible_without_auth(self):
        """Test that config endpoint is accessible without authentication."""
        url = reverse(URL_CONFIG)
        response = self.client.get(url, HTTP_HOST="public.example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_branding_accessible_without_auth(self):
        """Test that branding endpoint is accessible without authentication."""
        url = reverse(URL_BRANDING)
        response = self.client.get(url, HTTP_HOST="public.example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_features_accessible_without_auth(self):
        """Test that features endpoint is accessible without authentication."""
        url = reverse(URL_FEATURES)
        response = self.client.get(url, HTTP_HOST="public.example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
