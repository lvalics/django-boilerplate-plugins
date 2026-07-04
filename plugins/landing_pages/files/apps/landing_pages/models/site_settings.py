"""Per-site landing pages settings."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class LandingPagesSettings(BaseModel):
    """
    Per-site settings for landing pages, configurable via admin.
    """

    site = models.OneToOneField(
        "site_management.SiteProfile",
        on_delete=models.CASCADE,
        related_name="landing_pages_settings",
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
        verbose_name = _("Landing Pages Settings")
        verbose_name_plural = _("Landing Pages Settings")

    def __str__(self):
        return f"Landing Pages Settings for {self.site.site_name}"

    @classmethod
    def get_for_site(cls, site):
        """Get settings for a site, creating defaults if needed."""
        settings_obj, _created = cls.objects.get_or_create(site=site)
        return settings_obj
