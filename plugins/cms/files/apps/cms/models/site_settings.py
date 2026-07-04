"""Per-site CMS settings."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class CMSSettings(BaseModel):
    """
    Per-site settings for the CMS, configurable via admin.
    """

    site = models.OneToOneField(
        "site_management.SiteProfile",
        on_delete=models.CASCADE,
        related_name="cms_settings",
        help_text=_("The site these settings apply to."),
    )

    is_enabled = models.BooleanField(
        default=True,
        help_text=_("Enable landing pages for this site."),
    )

    cache_timeout = models.PositiveIntegerField(
        default=300,
        help_text=_("Cache timeout in seconds (default: 5 minutes)."),
    )

    class Meta:
        verbose_name = _("CMS Settings")
        verbose_name_plural = _("CMS Settings")

    def __str__(self):
        return f"CMS Settings for {self.site.site_name}"

    @classmethod
    def get_for_site(cls, site):
        """Get settings for a site, creating defaults if needed."""
        settings_obj, _created = cls.objects.get_or_create(site=site)
        return settings_obj
