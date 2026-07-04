"""View tests: page rendering, site scoping, and order-form submissions."""

from unittest import mock

from django.contrib.sites.models import Site
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.landing_pages.models import (
    LandingPage,
    LandingPageSubmission,
    LandingPageZone,
    SubmissionStatus,
    ZoneType,
)


def _make_site(domain):
    from apps.sites.models import SiteProfile

    site = Site.objects.create(domain=domain, name=domain)
    return SiteProfile.objects.create(site=site, site_name=domain)


class LandingPageViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.page = LandingPage.objects.create(title="Promo", slug="promo", use_site_template=False)
        LandingPageZone.objects.create(
            landing_page=self.page,
            zone_type=ZoneType.HERO_VIDEO,
            content={"headline": "Hello"},
            order=1,
        )

    def _url(self, slug):
        return reverse("landing_pages:landing_page", kwargs={"slug": slug})

    def test_renders_active_page(self):
        response = self.client.get(self._url("promo"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello")

    def test_unknown_slug_404(self):
        self.assertEqual(self.client.get(self._url("nope")).status_code, 404)

    def test_inactive_page_404(self):
        self.page.is_active = False
        self.page.save()
        self.assertEqual(self.client.get(self._url("promo")).status_code, 404)

    def test_redirect_zone_redirects(self):
        page = LandingPage.objects.create(title="R", slug="go", use_site_template=False)
        LandingPageZone.objects.create(
            landing_page=page,
            zone_type=ZoneType.REDIRECT,
            content={"redirect_url": "https://example.com/"},
        )
        response = self.client.get(self._url("go"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "https://example.com/")

    def test_cache_invalidated_on_save(self):
        # Prime the cache, deactivate the page, and expect a 404 (not a stale hit).
        self.assertEqual(self.client.get(self._url("promo")).status_code, 200)
        self.page.is_active = False
        self.page.save()
        self.assertEqual(self.client.get(self._url("promo")).status_code, 404)


class SubmitOrderFormTest(TestCase):
    def setUp(self):
        cache.clear()
        self.page = LandingPage.objects.create(title="Order", slug="order", use_site_template=False)
        self.zone = LandingPageZone.objects.create(
            landing_page=self.page,
            zone_type=ZoneType.ORDER_FORM,
            content={"form_fields": [{"name": "email", "type": "email"}]},
        )
        self.url = reverse("landing_pages:submit_form", kwargs={"zone_id": self.zone.pk})

    @override_settings(TURNSTILE_SECRET="", LANDING_PAGES_RATE_LIMIT_IP_REQUESTS=100)
    def test_submission_created_and_sanitized(self):
        response = self.client.post(
            self.url,
            {"email": "visitor@example.com", "name": "<b>Eve</b>", "message": "hi"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

        submission = LandingPageSubmission.objects.get(pk=data["submission_id"])
        self.assertEqual(submission.email, "visitor@example.com")
        self.assertEqual(submission.status, SubmissionStatus.NEW)
        # Visitor input is HTML-escaped server-side.
        self.assertNotIn("<b>", submission.name)
        self.assertNotIn("<b>", submission.form_data["name"])

    @override_settings(TURNSTILE_SECRET="", LANDING_PAGES_RATE_LIMIT_IP_REQUESTS=100)
    def test_invalid_email_rejected(self):
        response = self.client.post(self.url, {"email": "user@gmial.com"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(LandingPageSubmission.objects.count(), 0)

    @override_settings(TURNSTILE_SECRET="", LANDING_PAGES_RATE_LIMIT_IP_REQUESTS=1)
    def test_ip_rate_limit(self):
        first = self.client.post(self.url, {"email": "a@example.com"})
        self.assertEqual(first.status_code, 200)
        second = self.client.post(self.url, {"email": "b@example.com"})
        self.assertEqual(second.status_code, 429)

    @override_settings(TURNSTILE_SECRET="", LANDING_PAGES_RATE_LIMIT_IP_REQUESTS=100)
    def test_form_disabled_rejected(self):
        self.page.form_disabled = True
        self.page.save()
        response = self.client.post(self.url, {"email": "a@example.com"})
        self.assertEqual(response.status_code, 403)

    @override_settings(TURNSTILE_SECRET="sekrit", LANDING_PAGES_RATE_LIMIT_IP_REQUESTS=100)
    def test_turnstile_enforced_when_secret_set(self):
        # No token at all -> rejected without calling Cloudflare.
        response = self.client.post(self.url, {"email": "a@example.com"})
        self.assertEqual(response.status_code, 400)

        # Token present -> verified against the siteverify endpoint.
        with mock.patch("apps.landing_pages.views.requests.post") as post:
            post.return_value.json.return_value = {"success": True}
            ok = self.client.post(self.url, {"email": "a@example.com", "turnstile_token": "tok"})
        self.assertEqual(ok.status_code, 200)


class PerSiteResolutionTest(TestCase):
    """Site-scoped pages are only served on their site; all-sites pages everywhere."""

    def setUp(self):
        cache.clear()
        self.profile_a = _make_site("a.example.com")
        self.profile_b = _make_site("b.example.com")
        self.page_a = LandingPage.objects.create(
            title="A", slug="promo", site=self.profile_a, use_site_template=False
        )
        LandingPageZone.objects.create(
            landing_page=self.page_a, zone_type=ZoneType.HERO_VIDEO, content={"headline": "Site A page"}
        )

    def _get(self, slug, site_profile):
        # multi_domain's middleware sets request.site_config; tests hit the domain directly.
        return self.client.get(
            reverse("landing_pages:landing_page", kwargs={"slug": slug}),
            HTTP_HOST=site_profile.site.domain,
        )

    def test_site_page_served_on_its_site(self):
        response = self._get("promo", self.profile_a)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Site A page")

    def test_site_page_not_served_on_other_site(self):
        response = self._get("promo", self.profile_b)
        self.assertEqual(response.status_code, 404)

    def test_all_sites_page_served_everywhere(self):
        page = LandingPage.objects.create(title="G", slug="global", use_site_template=False)
        LandingPageZone.objects.create(
            landing_page=page, zone_type=ZoneType.HERO_VIDEO, content={"headline": "Global page"}
        )
        for profile in (self.profile_a, self.profile_b):
            response = self._get("global", profile)
            self.assertEqual(response.status_code, 200, profile.site.domain)
