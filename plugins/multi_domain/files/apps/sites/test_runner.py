"""Test runner for projects using the multi_domain plugin.

``MultiDomainMiddleware`` raises ``Http404`` when no ``SiteProfile`` resolves for the
request host. Django's test client issues requests against the host ``testserver``,
which does not belong to any configured domain, so every view would 404 in tests unless
a primary ``SiteProfile`` exists. ``ensure_primary_site()`` creates that profile once,
right after the test databases are set up, so it is visible to every test.
"""

from typing import Any

from django.test.runner import DiscoverRunner


def ensure_primary_site() -> Any:
    """Create (idempotently) a primary ``SiteProfile`` for the default ``Site``."""
    from django.contrib.sites.models import Site

    from apps.sites.models import SiteProfile

    site = Site.objects.get_current()
    profile, _ = SiteProfile.objects.get_or_create(
        site=site,
        defaults={"site_name": "Test", "is_primary": True, "is_active": True},
    )
    return profile


class SiteAwareTestRunner(DiscoverRunner):
    """``DiscoverRunner`` that prepares the primary site required by the multi-domain middleware."""

    def setup_databases(self, **kwargs: Any) -> Any:
        old_config = super().setup_databases(**kwargs)
        ensure_primary_site()
        return old_config
