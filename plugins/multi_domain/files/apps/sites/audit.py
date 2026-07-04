"""
Audit logging for site configuration changes.

Tracks:
- Site configuration changes (who, when, what changed)
- Member additions/removals
- Authentication events (optional)
"""

import logging
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel

logger = logging.getLogger(__name__)

# How long to keep audit logs (default 90 days)
AUDIT_LOG_RETENTION_DAYS = getattr(settings, "SITES_AUDIT_LOG_RETENTION_DAYS", 90)


class SiteAuditLog(BaseModel):
    """
    Audit log entry for site configuration changes.

    Tracks who made what changes and when.
    """

    class Action(models.TextChoices):
        CREATE = "create", _("Created")
        UPDATE = "update", _("Updated")
        DELETE = "delete", _("Deleted")
        MEMBER_ADD = "member_add", _("Member Added")
        MEMBER_REMOVE = "member_remove", _("Member Removed")
        MEMBER_UPDATE = "member_update", _("Member Updated")
        OWNER_TRANSFER = "owner_transfer", _("Owner Transferred")
        CACHE_INVALIDATE = "cache_invalidate", _("Cache Invalidated")

    site_id = models.IntegerField(_("Site ID"), db_index=True)
    site_domain = models.CharField(_("Site Domain"), max_length=255)
    action = models.CharField(_("Action"), max_length=20, choices=Action.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="site_audit_logs",
        verbose_name=_("User"),
    )
    user_email = models.EmailField(_("User Email"), blank=True)
    ip_address = models.GenericIPAddressField(_("IP Address"), null=True, blank=True)

    # What changed
    changes = models.JSONField(_("Changes"), default=dict, blank=True)
    previous_values = models.JSONField(_("Previous Values"), default=dict, blank=True)
    new_values = models.JSONField(_("New Values"), default=dict, blank=True)

    # Additional context
    notes = models.TextField(_("Notes"), blank=True)

    class Meta:
        verbose_name = _("Site Audit Log")
        verbose_name_plural = _("Site Audit Logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["site_id", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.site_domain} - {self.get_action_display()} by {self.user_email or 'System'}"

    @classmethod
    def log(
        cls,
        site_id: int,
        site_domain: str,
        action: str,
        user=None,
        ip_address: str = None,
        changes: dict = None,
        previous_values: dict = None,
        new_values: dict = None,
        notes: str = "",
    ) -> "SiteAuditLog":
        """
        Create an audit log entry.

        Args:
            site_id: The site ID
            site_domain: The site domain
            action: Action type (use Action choices)
            user: User who made the change (optional)
            ip_address: IP address of the request (optional)
            changes: Dict of field names that changed
            previous_values: Previous values of changed fields
            new_values: New values of changed fields
            notes: Additional context

        Returns:
            Created SiteAuditLog instance
        """
        user_email = ""
        if user:
            user_email = getattr(user, "email", str(user))

        entry = cls.objects.create(
            site_id=site_id,
            site_domain=site_domain,
            action=action,
            user=user if user and hasattr(user, "pk") else None,
            user_email=user_email,
            ip_address=ip_address,
            changes=changes or {},
            previous_values=previous_values or {},
            new_values=new_values or {},
            notes=notes,
        )

        logger.info(
            f"Audit: {action} on {site_domain} by {user_email or 'System'} - {changes or 'no details'}"
        )

        return entry

    @classmethod
    def cleanup_old_logs(cls, days: int = None) -> int:
        """
        Delete audit logs older than specified days.

        Args:
            days: Number of days to keep (default from settings)

        Returns:
            Number of deleted entries
        """
        days = days or AUDIT_LOG_RETENTION_DAYS
        cutoff = timezone.now() - timedelta(days=days)
        count, _ = cls.objects.filter(created_at__lt=cutoff).delete()
        logger.info(f"Cleaned up {count} audit logs older than {days} days")
        return count


def get_model_changes(instance, fields_to_track: list = None) -> tuple[dict, dict]:
    """
    Get changes between instance and database version.

    Args:
        instance: Model instance being saved
        fields_to_track: List of field names to track (all if None)

    Returns:
        Tuple of (previous_values, new_values) dicts
    """
    if not instance.pk:
        return {}, {}

    try:
        model_class = instance.__class__
        db_instance = model_class.objects.get(pk=instance.pk)
    except model_class.DoesNotExist:
        return {}, {}

    previous = {}
    new = {}

    # Get all field names if not specified
    if fields_to_track is None:
        fields_to_track = [f.name for f in instance._meta.fields]

    for field_name in fields_to_track:
        try:
            old_value = getattr(db_instance, field_name)
            new_value = getattr(instance, field_name)

            # Convert to JSON-serializable format
            old_value = _serialize_value(old_value)
            new_value = _serialize_value(new_value)

            if old_value != new_value:
                previous[field_name] = old_value
                new[field_name] = new_value
        except AttributeError:
            continue

    return previous, new


def _serialize_value(value: Any) -> Any:
    """Convert value to JSON-serializable format."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    if hasattr(value, "pk"):
        return {"id": value.pk, "str": str(value)}
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)
