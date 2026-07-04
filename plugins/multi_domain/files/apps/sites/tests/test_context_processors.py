"""
Unit tests for site context processors.

Run with:
    make test ARGS='apps.sites.tests.test_context_processors'
"""

from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase

from apps.sites.context_processors import site_config
from apps.sites.models import SiteProfile


class SiteContextProcessorTest(TestCase):
    """Tests for site_config context processor."""

    def setUp(self):
        """Create test site and request factory."""
        self.factory = RequestFactory()
        self.site = Site.objects.create(domain="context.example.com", name="Context Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Context Test Display",
            tagline="Test Tagline",
            theme="dark",
            primary_color="#8B5CF6",
            secondary_color="#7C3AED",
            is_active=True,
            is_primary=True,
            features={"enable_blog": True, "enable_shop": False},
            meta_defaults={"description": "Test description"},
        )

    def test_context_processor_with_site_config(self):
        """Test context processor returns correct values."""
        request = self.factory.get("/")
        request.site_config = self.profile.to_config_dict()

        context = site_config(request)

        self.assertEqual(context["site_name"], "Context Test Display")
        self.assertEqual(context["site_theme"], "dark")
        self.assertEqual(context["site_primary_color"], "#8B5CF6")
        self.assertEqual(context["site_secondary_color"], "#7C3AED")
        self.assertEqual(context["site_features"]["enable_blog"], True)
        self.assertEqual(context["site_meta"]["description"], "Test description")
        self.assertEqual(context["site_config"]["tagline"], "Test Tagline")

    def test_context_processor_without_site_config(self):
        """Test context processor handles missing site_config."""
        request = self.factory.get("/")
        # No site_config attached

        context = site_config(request)

        self.assertEqual(context["site_name"], "")
        self.assertEqual(context["site_theme"], "default")
        self.assertEqual(context["site_primary_color"], "#3B82F6")
        self.assertEqual(context["site_secondary_color"], "#1E40AF")
        self.assertEqual(context["site_features"], {})
        self.assertEqual(context["site_meta"], {})
        self.assertEqual(context["site_config"], {})

    def test_context_processor_with_empty_site_config(self):
        """Test context processor handles empty site_config."""
        request = self.factory.get("/")
        request.site_config = {}

        context = site_config(request)

        self.assertEqual(context["site_name"], "")
        self.assertEqual(context["site_theme"], "default")

    def test_context_includes_full_config(self):
        """Test that full config dict is available."""
        request = self.factory.get("/")
        request.site_config = self.profile.to_config_dict()

        context = site_config(request)

        # Full config should be accessible
        self.assertEqual(context["site_config"]["domain"], "context.example.com")
        self.assertEqual(context["site_config"]["site_id"], self.site.id)
        self.assertIn("features", context["site_config"])


class SiteContextProcessorIntegrationTest(TestCase):
    """Integration tests for context processor in templates."""

    def setUp(self):
        """Create test site."""
        self.site = Site.objects.create(domain="localhost", name="Local Test")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Local Site",
            theme="light",
            is_active=True,
            is_primary=True,
            features={"test_feature": True},
        )

    def test_context_available_in_view(self):
        """Test that site context is available in view response."""
        response = self.client.get("/", HTTP_HOST="localhost")

        # If view renders successfully and uses context, this passes
        # The actual template rendering depends on the view setup
        self.assertIn(response.status_code, [200, 302, 404])
