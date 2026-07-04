"""
Unit tests for SiteProfile model.

Run with:
    make test ARGS='apps.sites.tests.test_models'
"""

from django.contrib.sites.models import Site
from django.test import TestCase

from apps.sites.models import SiteProfile


class SiteProfileModelTest(TestCase):
    """Tests for SiteProfile model methods."""

    def setUp(self):
        """Create test site and profile."""
        # Clean slate so the test is robust against any migration-seeded default site.
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()
        self.site = Site.objects.create(domain="test.example.com", name="Test Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Test Site Display",
            tagline="Welcome to Test Site",
            theme="light",
            primary_color="#3B82F6",
            secondary_color="#1E40AF",
            auth_mode="isolated",
            is_active=True,
            is_primary=True,
            features={"enable_blog": True, "enable_chat": False},
            default_language="en",
            available_languages=["en", "es", "fr"],
        )

    def test_to_config_dict(self):
        """Test full config dict generation."""
        config = self.profile.to_config_dict()

        self.assertEqual(config["site_id"], self.site.id)
        self.assertEqual(config["domain"], "test.example.com")
        self.assertEqual(config["site_name"], "Test Site Display")
        self.assertEqual(config["tagline"], "Welcome to Test Site")
        self.assertEqual(config["theme"], "light")
        self.assertEqual(config["primary_color"], "#3B82F6")
        self.assertEqual(config["secondary_color"], "#1E40AF")
        self.assertEqual(config["features"]["enable_blog"], True)
        self.assertEqual(config["features"]["enable_chat"], False)
        self.assertEqual(config["default_language"], "en")
        self.assertIn("en", config["available_languages"])

    def test_to_public_config_dict(self):
        """Test public config dict excludes sensitive fields."""
        # Add sensitive data
        self.profile.integrations = {"stripe": {"secret_key": "sk_test_xxx"}}
        self.profile.auth_settings = {"session_timeout": 3600}
        self.profile.email_settings = {"smtp_password": "secret"}
        self.profile.save()

        public_config = self.profile.to_public_config_dict()

        # Should include public fields
        self.assertEqual(public_config["site_id"], self.site.id)
        self.assertEqual(public_config["site_name"], "Test Site Display")
        self.assertEqual(public_config["features"]["enable_blog"], True)

        # Should NOT include sensitive fields
        self.assertNotIn("integrations", public_config)
        self.assertNotIn("auth_settings", public_config)
        self.assertNotIn("email_settings", public_config)
        self.assertNotIn("auth_domain_url", public_config)

    def test_to_branding_dict(self):
        """Test branding-only dict."""
        branding = self.profile.to_branding_dict()

        self.assertEqual(branding["site_name"], "Test Site Display")
        self.assertEqual(branding["theme"], "light")
        self.assertEqual(branding["primary_color"], "#3B82F6")
        self.assertEqual(branding["secondary_color"], "#1E40AF")
        self.assertIsNone(branding["logo_url"])

        # Should NOT include other fields
        self.assertNotIn("features", branding)
        self.assertNotIn("tagline", branding)

    def test_to_features_dict(self):
        """Test features-only dict."""
        features = self.profile.to_features_dict()

        self.assertEqual(features["enable_blog"], True)
        self.assertEqual(features["enable_chat"], False)
        self.assertEqual(len(features), 2)

    def test_get_feature(self):
        """Test get_feature helper method."""
        self.assertTrue(self.profile.get_feature("enable_blog"))
        self.assertFalse(self.profile.get_feature("enable_chat"))
        self.assertFalse(self.profile.get_feature("nonexistent"))
        self.assertTrue(self.profile.get_feature("nonexistent", default=True))

    def test_get_template_dir(self):
        """Test template directory resolution."""
        # Default: uses domain prefix
        self.assertEqual(self.profile.get_template_dir(), "test")

        # Custom template_dir
        self.profile.template_dir = "custom_theme"
        self.assertEqual(self.profile.get_template_dir(), "custom_theme")


class SiteProfileValidationTest(TestCase):
    """Tests for SiteProfile validation."""

    def setUp(self):
        """Create initial site."""
        # Clean slate so the test is robust against any migration-seeded default site.
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()
        self.site = Site.objects.create(domain="primary.example.com", name="Primary")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Primary Site",
            is_active=True,
            is_primary=True,
        )

    def test_cannot_deactivate_last_active_site(self):
        """Test that last active site cannot be deactivated."""
        from django.core.exceptions import ValidationError

        self.profile.is_active = False
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_at_least_one_primary_site(self):
        """Test that at least one site must be primary."""
        from django.core.exceptions import ValidationError

        self.profile.is_primary = False
        with self.assertRaises(ValidationError):
            self.profile.full_clean()

    def test_only_one_primary_site(self):
        """Test that setting a new primary unsets old primary."""
        site2 = Site.objects.create(domain="secondary.example.com", name="Secondary")
        profile2 = SiteProfile.objects.create(
            site=site2,
            site_name="Secondary Site",
            is_active=True,
            is_primary=True,  # This should unset profile1's is_primary
        )

        self.profile.refresh_from_db()
        self.assertFalse(self.profile.is_primary)
        self.assertTrue(profile2.is_primary)
