"""Blog/content view tests: published gating, category/tag filtering, per-site visibility, pagination."""

from datetime import timedelta

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cms.tests.base import ensure_primary_site
from apps.cms.models import Category, Page, PageType, Tag


def _make_site(domain):
    from apps.sites.models import SiteProfile

    site = Site.objects.create(domain=domain, name=domain)
    return SiteProfile.objects.create(site=site, site_name=domain)


def _post(slug, **kwargs):
    kwargs.setdefault("title", slug)
    kwargs.setdefault("page_type", PageType.POST)
    kwargs.setdefault("published_at", timezone.now() - timedelta(days=1))
    return Page.objects.create(slug=slug, **kwargs)


class BlogPublishGatingTest(TestCase):
    def setUp(self):
        ensure_primary_site()

    def test_published_post_listed_and_detail_ok(self):
        _post("hello")
        listing = self.client.get(reverse("cms:blog_list"))
        self.assertEqual(listing.status_code, 200)
        self.assertContains(listing, "hello")
        detail = self.client.get(reverse("cms:blog_detail", kwargs={"slug": "hello"}))
        self.assertEqual(detail.status_code, 200)

    def test_future_published_at_is_404(self):
        _post("future", published_at=timezone.now() + timedelta(days=3))
        self.assertEqual(
            self.client.get(reverse("cms:blog_detail", kwargs={"slug": "future"})).status_code,
            404,
        )

    def test_unpublished_post_is_404(self):
        _post("draft", published_at=None)
        self.assertEqual(
            self.client.get(reverse("cms:blog_detail", kwargs={"slug": "draft"})).status_code,
            404,
        )

    def test_inactive_post_is_404(self):
        _post("gone", is_active=False)
        self.assertEqual(
            self.client.get(reverse("cms:blog_detail", kwargs={"slug": "gone"})).status_code,
            404,
        )


class BlogTaxonomyFilterTest(TestCase):
    def setUp(self):
        ensure_primary_site()
        self.cat = Category.objects.create(slug="news", name="News")
        self.tag = Tag.objects.create(slug="django", name="Django")
        self.in_cat = _post("in-cat", category=self.cat)
        self.in_cat.tags.add(self.tag)
        _post("other")

    def test_category_filter(self):
        resp = self.client.get(reverse("cms:blog_category", kwargs={"slug": "news"}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "in-cat")
        self.assertNotContains(resp, "other")

    def test_tag_filter(self):
        resp = self.client.get(reverse("cms:blog_tag", kwargs={"slug": "django"}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "in-cat")
        self.assertNotContains(resp, "other")


class BlogPaginationTest(TestCase):
    def setUp(self):
        ensure_primary_site()

    def test_pagination_splits_pages(self):
        from apps.cms import conf

        for i in range(conf.POSTS_PER_PAGE + 3):
            _post(f"post-{i}", published_at=timezone.now() - timedelta(days=i + 1))
        page2 = self.client.get(reverse("cms:blog_list"), {"page": 2})
        self.assertEqual(page2.status_code, 200)
        self.assertEqual(len(page2.context["posts"]), 3)


class BlogPerSiteVisibilityTest(TestCase):
    def setUp(self):
        ensure_primary_site()
        self.profile_a = _make_site("a.example.com")
        self.profile_b = _make_site("b.example.com")
        _post("site-a-post", site=self.profile_a)

    def _get(self, slug, profile):
        return self.client.get(
            reverse("cms:blog_detail", kwargs={"slug": slug}),
            HTTP_HOST=profile.site.domain,
        )

    def test_site_post_served_on_its_site(self):
        self.assertEqual(self._get("site-a-post", self.profile_a).status_code, 200)

    def test_site_post_not_served_on_other_site(self):
        self.assertEqual(self._get("site-a-post", self.profile_b).status_code, 404)


class ContentPageTest(TestCase):
    def setUp(self):
        ensure_primary_site()

    def test_content_page_renders(self):
        Page.objects.create(title="About", slug="about", page_type=PageType.CONTENT)
        resp = self.client.get(reverse("cms:content_page", kwargs={"slug": "about"}))
        self.assertEqual(resp.status_code, 200)

    def test_landing_page_not_served_as_content(self):
        Page.objects.create(title="Promo", slug="promo", page_type=PageType.LANDING)
        self.assertEqual(
            self.client.get(reverse("cms:content_page", kwargs={"slug": "promo"})).status_code,
            404,
        )
