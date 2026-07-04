"""
Signal handlers for the landing pages plugin.

Cache invalidation only: whenever a page or one of its zones changes, the
slug-resolution cache scope for that page's site is version-bumped
(see cache.py). Registered in apps.py ``ready()``.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Page, Zone


def _invalidate_for_page(page):
    from .cache import invalidate_page_cache

    # Cache scopes are keyed by the Django Site id (request.site_config["site_id"]),
    # not the SiteProfile pk. Fall back to the global scope if the profile row is
    # gone (e.g. cascade delete of the site).
    site_id = None
    if page.site_id:
        try:
            site_id = page.site.site_id
        except Exception:
            site_id = None
    invalidate_page_cache(page.slug, site_id)


@receiver(post_save, sender=Page)
def invalidate_page_cache_on_save(sender, instance, **kwargs):
    """Invalidate cache when a landing page is saved."""
    _invalidate_for_page(instance)


@receiver(post_delete, sender=Page)
def invalidate_page_cache_on_delete(sender, instance, **kwargs):
    """Invalidate cache when a landing page is deleted."""
    _invalidate_for_page(instance)


@receiver(post_save, sender=Zone)
def invalidate_zone_cache_on_save(sender, instance, **kwargs):
    """Invalidate the parent page's cache when a zone is saved."""
    if instance.landing_page_id:
        _invalidate_for_page(instance.landing_page)


@receiver(post_delete, sender=Zone)
def invalidate_zone_cache_on_delete(sender, instance, **kwargs):
    """Invalidate the parent page's cache when a zone is deleted."""
    if instance.landing_page_id:
        _invalidate_for_page(instance.landing_page)
