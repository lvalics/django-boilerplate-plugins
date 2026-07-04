"""
Unit tests for the site-aware cached template loader.

Run with:
    make test ARGS='apps.sites.tests.test_template_loader'
"""

from django.template import Engine
from django.test import SimpleTestCase

from apps.sites.middleware import multi_domain as mw
from apps.sites.template_loader import SiteAwareCachedLoader


def _make_loader():
    """Build a SiteAwareCachedLoader the way Django's engine does."""
    engine = Engine(
        dirs=[],
        loaders=[
            (
                "apps.sites.template_loader.SiteAwareCachedLoader",
                ["django.template.loaders.filesystem.Loader"],
            )
        ],
    )
    loader = engine.template_loaders[0]
    assert isinstance(loader, SiteAwareCachedLoader)
    return loader


class SiteAwareCacheKeyTest(SimpleTestCase):
    """Tests for SiteAwareCachedLoader.cache_key site namespacing."""

    def setUp(self):
        self.loader = _make_loader()

    def _set_site_config(self, config):
        """Set the middleware thread-local site config (mirrors ThreadLocalMiddleware)."""
        mw._thread_locals.site_config = config

    def tearDown(self):
        # Always clear the thread-local so tests do not leak state.
        mw._thread_locals.site_config = None

    def test_cache_key_differs_between_sites(self):
        """Same template name yields distinct keys under different site configs."""
        try:
            self._set_site_config({"template_dir": "site_a"})
            key_a = self.loader.cache_key("web/base.html")

            self._set_site_config({"template_dir": "site_b"})
            key_b = self.loader.cache_key("web/base.html")
        finally:
            self._set_site_config(None)

        self.assertNotEqual(key_a, key_b)
        self.assertTrue(key_a.startswith("site_a::"))
        self.assertTrue(key_b.startswith("site_b::"))

    def test_cache_key_without_site_is_stable_and_empty_prefixed(self):
        """No site config yields a stable empty-prefixed key, distinct from site keys."""
        try:
            self._set_site_config(None)
            key_none_1 = self.loader.cache_key("web/base.html")
            key_none_2 = self.loader.cache_key("web/base.html")

            self._set_site_config({"template_dir": "site_a"})
            key_a = self.loader.cache_key("web/base.html")

            self._set_site_config({"template_dir": "site_b"})
            key_b = self.loader.cache_key("web/base.html")
        finally:
            self._set_site_config(None)

        self.assertEqual(key_none_1, key_none_2)
        self.assertTrue(key_none_1.startswith("::"))
        self.assertNotEqual(key_none_1, key_a)
        self.assertNotEqual(key_none_1, key_b)

    def test_cache_key_without_template_dir_uses_empty_prefix(self):
        """A site config lacking template_dir behaves like the empty-prefix default."""
        try:
            self._set_site_config({"site_id": 1})
            key = self.loader.cache_key("web/base.html")
        finally:
            self._set_site_config(None)

        self.assertTrue(key.startswith("::"))

    def test_cache_key_incorporates_parent_key(self):
        """The parent cache_key (and its skip semantics) is preserved in the result."""
        try:
            self._set_site_config({"template_dir": "site_a"})
            parent_key = super(SiteAwareCachedLoader, self.loader).cache_key("web/base.html")
            key = self.loader.cache_key("web/base.html")
        finally:
            self._set_site_config(None)

        self.assertTrue(key.endswith(parent_key))
        self.assertEqual(key, f"site_a::{parent_key}")
