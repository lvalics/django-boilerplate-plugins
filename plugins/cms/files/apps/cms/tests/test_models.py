"""Model tests: per-site slug constraints, template whitelist, schema-lite validation."""

from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.cms.models import Page, Zone, ZoneType


def _make_site(domain):
    from apps.sites.models import SiteProfile

    site = Site.objects.create(domain=domain, name=domain)
    return SiteProfile.objects.create(site=site, site_name=domain)


class PageSlugConstraintTest(TestCase):
    def setUp(self):
        self.site_a = _make_site("a.example.com")
        self.site_b = _make_site("b.example.com")

    def test_same_slug_allowed_on_different_sites(self):
        Page.objects.create(title="A", slug="promo", site=self.site_a)
        Page.objects.create(title="B", slug="promo", site=self.site_b)
        self.assertEqual(Page.objects.filter(slug="promo").count(), 2)

    def test_duplicate_slug_on_same_site_rejected(self):
        Page.objects.create(title="A", slug="promo", site=self.site_a)
        with self.assertRaises(IntegrityError):
            Page.objects.create(title="A2", slug="promo", site=self.site_a)

    def test_duplicate_all_sites_slug_rejected(self):
        Page.objects.create(title="G", slug="promo")
        with self.assertRaises(IntegrityError):
            Page.objects.create(title="G2", slug="promo")

    def test_for_site_prefers_site_specific_page(self):
        global_page = Page.objects.create(title="G", slug="promo")
        site_page = Page.objects.create(title="A", slug="promo", site=self.site_a)

        resolved = Page.for_site(self.site_a.site_id).filter(slug="promo").first()
        self.assertEqual(resolved.pk, site_page.pk)

        # Other sites only see the all-sites page.
        resolved_b = Page.for_site(self.site_b.site_id).filter(slug="promo").first()
        self.assertEqual(resolved_b.pk, global_page.pk)

    def test_for_site_excludes_other_sites_pages(self):
        Page.objects.create(title="A", slug="only-a", site=self.site_a)
        self.assertIsNone(Page.for_site(self.site_b.site_id).filter(slug="only-a").first())


class ReservedSlugTest(TestCase):
    def test_reserved_slug_rejected(self):
        for slug in ("admin", "blog", "c", "api"):
            page = Page(title="X", slug=slug)
            with self.assertRaises(ValidationError, msg=slug):
                page.full_clean()

    def test_non_reserved_slug_ok(self):
        Page(title="X", slug="my-promo").full_clean()  # must not raise


class ZoneValidationTest(TestCase):
    def setUp(self):
        self.page = Page.objects.create(title="Page", slug="page")

    def _zone(self, **kwargs):
        kwargs.setdefault("landing_page", self.page)
        kwargs.setdefault("zone_type", ZoneType.HERO_VIDEO)
        return Zone(**kwargs)

    def test_template_name_outside_whitelist_rejected(self):
        for bad in (
            "web/base.html",
            "cms/zones/../../../settings.html",
            "cms/zones/Evil.html",
            "admin/index.html",
        ):
            zone = self._zone(template_name=bad, content={"headline": "x"})
            with self.assertRaises(ValidationError, msg=bad):
                zone.full_clean()

    def test_template_name_inside_whitelist_accepted(self):
        zone = self._zone(template_name="cms/zones/hero_video.html", content={"headline": "x"})
        zone.full_clean()  # must not raise

    def test_get_template_name_ignores_non_whitelisted_override(self):
        zone = self._zone(template_name="web/base.html")
        self.assertEqual(zone.get_template_name(), "cms/zones/hero_video.html")

    def test_required_content_keys_enforced_when_content_present(self):
        zone = self._zone(content={"subheadline": "no headline here"})
        with self.assertRaises(ValidationError):
            zone.full_clean()

    def test_empty_content_is_allowed(self):
        # Zones can be created empty (e.g. from the admin inline) and filled later.
        zone = self._zone(content={})
        zone.full_clean()  # must not raise

    def test_single_order_form_per_page(self):
        Zone.objects.create(
            landing_page=self.page, zone_type=ZoneType.ORDER_FORM, content={"form_fields": []}
        )
        duplicate = self._zone(zone_type=ZoneType.ORDER_FORM, content={"form_fields": []})
        with self.assertRaises(ValidationError):
            duplicate.full_clean()
