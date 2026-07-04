"""Shared test helpers for the CMS payload tests."""

from django.contrib.sites.models import Site


def ensure_primary_site():
    """Create a primary SiteProfile for the default Site.

    The multi_domain plugin's MultiDomainMiddleware raises Http404 when no
    SiteProfile resolves for a request; test-client requests (host
    "testserver") need a primary profile to fall back to.
    """
    from apps.sites.models import SiteProfile

    site = Site.objects.get_current()
    profile, _ = SiteProfile.objects.get_or_create(
        site=site,
        defaults={"site_name": "Test", "is_primary": True, "is_active": True},
    )
    return profile
