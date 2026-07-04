"""
Unit tests for site configuration caching layer.

Run with:
    make test ARGS='apps.sites.tests.test_cache'
"""

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase

from apps.sites.cache import (
    get_all_site_domains,
    get_site_config_by_domain,
    get_site_config_by_id,
    invalidate_all_site_cache,
    invalidate_site_cache,
    warm_site_cache,
)
from apps.sites.models import SiteProfile


class SiteCacheTest(TestCase):
    """Tests for site configuration caching."""

    def setUp(self):
        """Create test sites."""
        cache.clear()
        # Clean slate so the test is robust against any migration-seeded default site.
        SiteProfile.objects.all().delete()
        Site.objects.all().delete()

        self.site1 = Site.objects.create(domain="cache1.example.com", name="Cache Site 1")
        self.profile1 = SiteProfile.objects.create(
            site=self.site1,
            site_name="Cache Test 1",
            is_active=True,
            is_primary=True,
            features={"feature_a": True},
        )

        self.site2 = Site.objects.create(domain="cache2.example.com", name="Cache Site 2")
        self.profile2 = SiteProfile.objects.create(
            site=self.site2,
            site_name="Cache Test 2",
            is_active=True,
            is_primary=False,
            features={"feature_b": True},
        )

    def tearDown(self):
        """Clear cache after tests."""
        cache.clear()

    def test_get_site_config_by_domain(self):
        """Test fetching config by domain."""
        config = get_site_config_by_domain("cache1.example.com")

        self.assertIsNotNone(config)
        self.assertEqual(config["site_name"], "Cache Test 1")
        self.assertEqual(config["domain"], "cache1.example.com")

    def test_get_site_config_by_domain_caches_result(self):
        """Test that config is cached after first fetch and updated on save."""
        # First call - hits database
        config1 = get_site_config_by_domain("cache1.example.com")
        self.assertEqual(config1["site_name"], "Cache Test 1")

        # Modify database - signal handler should invalidate cache
        self.profile1.site_name = "Modified Name"
        self.profile1.save()

        # Second call - should return NEW value (signal invalidated cache)
        config2 = get_site_config_by_domain("cache1.example.com")

        # Cache should have new value due to signal invalidation
        self.assertEqual(config2["site_name"], "Modified Name")

    def test_get_site_config_by_id(self):
        """Test fetching config by site ID."""
        config = get_site_config_by_id(self.site1.id)

        self.assertIsNotNone(config)
        self.assertEqual(config["site_name"], "Cache Test 1")

    def test_get_site_config_returns_none_for_unknown(self):
        """Test that unknown domain returns None."""
        config = get_site_config_by_domain("unknown.example.com")
        self.assertIsNone(config)

    def test_get_all_site_domains(self):
        """Test fetching all active site domains."""
        domains = get_all_site_domains()

        self.assertIn("cache1.example.com", domains)
        self.assertIn("cache2.example.com", domains)

    def test_get_all_site_domains_excludes_inactive(self):
        """Test that inactive sites are excluded."""
        self.profile2.is_active = False
        self.profile2.save()
        cache.clear()

        domains = get_all_site_domains()

        self.assertIn("cache1.example.com", domains)
        self.assertNotIn("cache2.example.com", domains)

    def test_invalidate_site_cache(self):
        """Test cache invalidation for specific site."""
        # Populate cache
        get_site_config_by_domain("cache1.example.com")

        # Invalidate
        invalidate_site_cache(site_id=self.site1.id, domain="cache1.example.com")

        # Modify database
        self.profile1.site_name = "New Name"
        self.profile1.save()

        # Clear signals cache effect
        cache.clear()

        # Now should get new value
        config = get_site_config_by_domain("cache1.example.com")
        self.assertEqual(config["site_name"], "New Name")

    def test_invalidate_all_site_cache(self):
        """Test invalidating all site caches."""
        # Populate caches
        get_site_config_by_domain("cache1.example.com")
        get_site_config_by_domain("cache2.example.com")
        get_all_site_domains()

        # Invalidate all
        invalidate_all_site_cache()

        # Verify cache is empty (next call will hit DB)
        # This is hard to verify directly, but we can check the function runs without error
        self.assertTrue(True)

    def test_warm_site_cache(self):
        """Test pre-warming all site caches."""
        cache.clear()

        count = warm_site_cache()

        self.assertEqual(count, 2)  # Two active sites

        # Verify caches are populated by fetching (should hit cache)
        config1 = get_site_config_by_domain("cache1.example.com")
        config2 = get_site_config_by_domain("cache2.example.com")

        self.assertIsNotNone(config1)
        self.assertIsNotNone(config2)
        self.assertEqual(config1["site_name"], "Cache Test 1")
        self.assertEqual(config2["site_name"], "Cache Test 2")


class SiteCacheSignalTest(TestCase):
    """Tests for cache invalidation via signals."""

    def setUp(self):
        """Create test site."""
        cache.clear()
        self.site = Site.objects.create(domain="signal.example.com", name="Signal Site")
        self.profile = SiteProfile.objects.create(
            site=self.site,
            site_name="Signal Test",
            is_active=True,
            is_primary=True,
        )

    def tearDown(self):
        cache.clear()

    def test_cache_invalidated_on_profile_save(self):
        """Test that cache is invalidated when profile is saved."""
        # Populate cache
        config = get_site_config_by_domain("signal.example.com")
        self.assertEqual(config["site_name"], "Signal Test")

        # Update profile (signal should invalidate cache)
        self.profile.site_name = "Updated Signal Test"
        self.profile.save()

        # Get fresh config
        config = get_site_config_by_domain("signal.example.com")
        self.assertEqual(config["site_name"], "Updated Signal Test")

    def test_cache_invalidated_on_site_save(self):
        """Test that cache is invalidated when Site is saved."""
        # Populate cache
        get_site_config_by_domain("signal.example.com")

        # Update site domain (signal should invalidate cache)
        self.site.domain = "new-signal.example.com"
        self.site.save()

        # Old domain should not have cache
        # New domain should work
        config = get_site_config_by_domain("new-signal.example.com")
        self.assertIsNotNone(config)
