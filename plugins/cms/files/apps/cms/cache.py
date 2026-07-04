"""
Caching for landing page slug resolution.

The view caches only the slug -> page id resolution (a tiny dict), then fetches
the ORM object once per request. Invalidation uses version-bump keys instead of
backend-specific cache-key pattern deletion, so any Django cache backend works:

- ``cms:version:all`` is bumped when an all-sites page changes; it is
  part of every lookup key, so bumping it invalidates every cached resolution.
- ``cms:version:<site_id>`` is bumped when a site-scoped page
  changes; it invalidates that site's cached resolutions only.

Edge case: requests without a site context (``request.site_config`` missing)
use the ``all`` scope; a site-scoped page change leaves those entries to expire
naturally (CACHE_TIMEOUT, default 300s). With the required multi_domain plugin
installed this scope is a rare fallback.
"""

import logging

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Cache timeout from settings (default 5 minutes)
CACHE_TIMEOUT = getattr(settings, "CMS_CACHE_TIMEOUT", 300)

_MISS = 0  # sentinel id stored for "slug does not resolve" (page ids are >= 1)


def _version_key(site_id) -> str:
    return f"cms:version:{site_id or 'all'}"


def _get_version(site_id) -> int:
    key = _version_key(site_id)
    version = cache.get(key)
    if version is None:
        cache.add(key, 1, timeout=None)
        version = cache.get(key, 1)
    return version


def _bump_version(site_id) -> None:
    key = _version_key(site_id)
    try:
        cache.incr(key)
    except ValueError:
        # Key expired/evicted; seed a fresh version.
        cache.set(key, 2, timeout=None)


def _page_key(slug: str, site_id) -> str:
    global_version = _get_version(None)
    site_version = _get_version(site_id) if site_id else 0
    return f"cms:page:g{global_version}:s{site_version}:{site_id or 'all'}:{slug}"


def get_page_id(slug: str, site_id=None):
    """
    Resolve a slug (within the given Django Site id scope) to a Page id.

    Returns the page id or None. Site-specific pages win over all-sites pages
    on slug collision. Negative results are cached too, so unknown slugs do not
    hit the database on every request.
    """
    key = _page_key(slug, site_id)
    cached = cache.get(key)
    if cached is not None:
        page_id = cached.get("id", _MISS)
        logger.debug("Cache hit for landing page %s (site %s)", slug, site_id)
        return page_id or None

    from .models import Page

    page = Page.for_site(site_id).filter(slug=slug).only("id").first()
    page_id = page.id if page else _MISS
    cache.set(key, {"id": page_id}, timeout=CACHE_TIMEOUT)
    logger.debug("Cached landing page resolution %s (site %s) -> %s", slug, site_id, page_id or None)
    return page_id or None


def invalidate_page_cache(slug: str, site_id=None) -> None:
    """
    Invalidate cached resolutions after a page (or its zones) changed.

    Bumps the site's version key for site-scoped pages, or the global version
    key for all-sites pages (which participates in every lookup key).
    """
    _bump_version(site_id if site_id else None)
    logger.debug("Invalidated landing page cache for %s (site %s)", slug, site_id)
