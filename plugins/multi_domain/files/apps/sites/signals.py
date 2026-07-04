"""
Signal handlers for cache invalidation when Site/SiteProfile changes.

Handles:
- Domain changes (invalidates both old and new domain)
- SiteProfile updates
- Site deletion
- User logout propagation across sites
- Password change session invalidation
- Audit logging for all site configuration changes
"""

import logging

from asgiref.local import Local
from django.contrib.auth.signals import user_logged_out
from django.contrib.sites.models import Site
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.sites.audit import SiteAuditLog, get_model_changes
from apps.sites.cache import invalidate_site_cache
from apps.sites.middleware.multi_domain import get_current_request
from apps.sites.ratelimit import get_client_ip

logger = logging.getLogger(__name__)


def _request_ip(request):
    """Client IP for audit attribution, honoring the trusted-proxy setting (F3 helper)."""
    if not request:
        return None
    ip = get_client_ip(request)
    return ip if ip and ip != "unknown" else None

# Per-context (async-safe) storage for state passed between pre_save and post_save.
# Replaces module-level dicts, which raced across concurrent threads/coroutines. Each
# execution context (request/task) gets isolated storage, keyed by instance pk within it.
_signal_locals = Local()


def _old_domains() -> dict:
    """Per-context map of Site pk -> previous domain, populated during pre_save."""
    if not hasattr(_signal_locals, "old_domains"):
        _signal_locals.old_domains = {}
    return _signal_locals.old_domains


def _pending_changes() -> dict:
    """Per-context map of change-key -> (previous, new) field values for audit logging."""
    if not hasattr(_signal_locals, "pending_changes"):
        _signal_locals.pending_changes = {}
    return _signal_locals.pending_changes


@receiver(pre_save, sender=Site)
def capture_old_domain(sender, instance, **kwargs):
    """
    Capture old domain before save to handle domain changes.
    """
    if instance.pk:
        try:
            old_instance = Site.objects.get(pk=instance.pk)
            if old_instance.domain != instance.domain:
                # Domain is changing - store old domain for post_save
                _old_domains()[instance.pk] = old_instance.domain
                logger.debug(f"Domain changing: {old_instance.domain} -> {instance.domain}")
        except Site.DoesNotExist:
            pass


@receiver(post_save, sender=Site)
def invalidate_cache_on_site_save(sender, instance, **kwargs):
    """
    Invalidate cache when Django Site is saved.
    Also invalidates old domain if domain changed.
    """
    # Check if there was an old domain to invalidate
    old_domain = _old_domains().pop(instance.pk, None)

    if old_domain:
        logger.info(f"Domain changed from {old_domain} to {instance.domain}, invalidating both")
        invalidate_site_cache(site_id=instance.id, domain=old_domain)

    invalidate_site_cache(site_id=instance.id, domain=instance.domain)
    logger.debug(f"Site saved: {instance.domain}")


@receiver(post_delete, sender=Site)
def invalidate_cache_on_site_delete(sender, instance, **kwargs):
    """
    Invalidate cache when Django Site is deleted.
    """
    # Clean up any pending old domain
    _old_domains().pop(instance.pk, None)

    logger.debug(f"Site deleted: {instance.domain}")
    invalidate_site_cache(site_id=instance.id, domain=instance.domain)


@receiver(post_save, sender="site_management.SiteProfile")
def invalidate_cache_on_profile_save(sender, instance, **kwargs):
    """
    Invalidate cache when SiteProfile is saved.
    """
    logger.debug(f"SiteProfile saved: {instance.site.domain}")
    invalidate_site_cache(site_id=instance.site_id, domain=instance.site.domain)


@receiver(post_delete, sender="site_management.SiteProfile")
def invalidate_cache_on_profile_delete(sender, instance, **kwargs):
    """
    Invalidate cache when SiteProfile is deleted.
    """
    logger.debug(f"SiteProfile deleted: {instance.site.domain}")
    invalidate_site_cache(site_id=instance.site_id, domain=instance.site.domain)


# =============================================================================
# User Session Signals
# =============================================================================


@receiver(user_logged_out)
def propagate_logout(sender, request, user, **kwargs):
    """
    Propagate logout across all sites when user logs out.

    This invalidates the user's sessions on all sites in the shared auth group.
    """
    if user is None:
        return

    # Check if this is a shared auth site
    site_config = getattr(request, "site_config", None) if request else None
    if site_config and site_config.get("auth_mode") == "shared":
        from apps.sites.middleware.auth_domain import invalidate_user_sessions

        invalidate_user_sessions(user.id)
        logger.info(f"User {user.id} logout propagated across sites")


# =============================================================================
# Audit Logging Signals
# =============================================================================

# Fields to track for audit logging
SITE_PROFILE_AUDIT_FIELDS = [
    "site_name",
    "tagline",
    "theme",
    "logo",
    "primary_color",
    "secondary_color",
    "features",
    "meta_defaults",
    "auth_mode",
    "is_active",
    "is_primary",
]


@receiver(pre_save, sender="site_management.SiteProfile")
def capture_profile_changes(sender, instance, **kwargs):
    """
    Capture SiteProfile changes before save for audit logging.
    """
    if instance.pk:
        previous, new = get_model_changes(instance, SITE_PROFILE_AUDIT_FIELDS)
        if previous:
            _pending_changes()[f"profile:{instance.pk}"] = (previous, new)


@receiver(post_save, sender="site_management.SiteProfile")
def audit_profile_save(sender, instance, created, **kwargs):
    """
    Log SiteProfile creation or updates.
    """
    request = get_current_request()
    user = getattr(request, "user", None) if request else None
    ip_address = _request_ip(request)

    if created:
        SiteAuditLog.log(
            site_id=instance.site_id,
            site_domain=instance.site.domain,
            action=SiteAuditLog.Action.CREATE,
            user=user if user and user.is_authenticated else None,
            ip_address=ip_address,
            notes="Site profile created",
        )
    else:
        # Check for pending changes
        change_key = f"profile:{instance.pk}"
        pending = _pending_changes()
        if change_key in pending:
            previous, new = pending.pop(change_key)
            SiteAuditLog.log(
                site_id=instance.site_id,
                site_domain=instance.site.domain,
                action=SiteAuditLog.Action.UPDATE,
                user=user if user and user.is_authenticated else None,
                ip_address=ip_address,
                changes={"fields": list(previous.keys())},
                previous_values=previous,
                new_values=new,
            )


@receiver(post_delete, sender="site_management.SiteProfile")
def audit_profile_delete(sender, instance, **kwargs):
    """
    Log SiteProfile deletion.
    """
    request = get_current_request()
    user = getattr(request, "user", None) if request else None

    SiteAuditLog.log(
        site_id=instance.site_id,
        site_domain=instance.site.domain,
        action=SiteAuditLog.Action.DELETE,
        user=user if user and user.is_authenticated else None,
        ip_address=_request_ip(request),
        notes="Site profile deleted",
    )
