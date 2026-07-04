"""Regression tests for the CMS security review (blog/content surface)."""

from datetime import timedelta

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.cms.models import Category, Page, PageType, Tag
from apps.cms.tests.base import ensure_primary_site


class EmbargoBypassTest(TestCase):
    """The root catch-all must never serve posts/content pages (published gating)."""

    def setUp(self):
        cache.clear()
        ensure_primary_site()

    def test_draft_post_not_served_via_root_catchall(self):
        # is_active defaults True; a post with no published_at is a draft.
        Page.objects.create(title="Scoop", slug="scoop", page_type=PageType.POST, published_at=None)
        # Correctly gated on the blog route...
        self.assertEqual(self.client.get("/blog/scoop/").status_code, 404)
        # ...and must NOT leak through the landing catch-all.
        self.assertEqual(self.client.get("/scoop/").status_code, 404)

    def test_future_post_not_served_via_root_catchall(self):
        Page.objects.create(
            title="Later", slug="later", page_type=PageType.POST,
            published_at=timezone.now() + timedelta(days=5),
        )
        self.assertEqual(self.client.get("/later/").status_code, 404)

    def test_content_page_not_served_via_root_catchall(self):
        Page.objects.create(title="About", slug="about", page_type=PageType.CONTENT)
        self.assertEqual(self.client.get("/c/about/").status_code, 200)
        self.assertEqual(self.client.get("/about/").status_code, 404)

    def test_landing_page_still_served_at_root(self):
        Page.objects.create(title="Promo", slug="promo", page_type=PageType.LANDING, use_site_template=False)
        self.assertEqual(self.client.get("/promo/").status_code, 200)


class ReservedSlugEnforcementTest(TestCase):
    def test_reserved_slug_rejected_on_create(self):
        # save() must enforce it even when full_clean() is skipped.
        with self.assertRaises(ValidationError):
            Page.objects.create(title="X", slug="admin", page_type=PageType.LANDING)

    def test_reserved_slug_case_insensitive(self):
        with self.assertRaises(ValidationError):
            Page.objects.create(title="X", slug="Admin", page_type=PageType.LANDING)

    def test_blog_prefix_slug_reserved(self):
        with self.assertRaises(ValidationError):
            Page.objects.create(title="X", slug="blog", page_type=PageType.LANDING)

    @override_settings(CMS_POST_URL_PREFIX="blog/")
    def test_prefix_with_slash_still_reserves_bare_name(self):
        # conf strips the slash, so "blog" is reserved even if configured as "blog/".
        from apps.cms import conf
        import importlib

        importlib.reload(conf)
        try:
            self.assertIn("blog", conf.RESERVED_SLUGS)
        finally:
            importlib.reload(conf)


class TaxonomyUniquenessTest(TestCase):
    def test_all_sites_category_slug_unique(self):
        Category.objects.create(name="News", slug="news")  # all-sites
        with self.assertRaises(Exception):
            Category.objects.create(name="News 2", slug="news")

    def test_all_sites_tag_slug_unique(self):
        Tag.objects.create(name="Django", slug="django")
        with self.assertRaises(Exception):
            Tag.objects.create(name="Django 2", slug="django")
