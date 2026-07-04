"""Reusable zone template presets."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel

from .pages import ZoneType


class ZoneTemplate(BaseModel):
    """
    Reusable zone template for quick landing page creation.

    Stores default content and configuration for a zone type. Seed presets are
    installed with the ``install_zone_templates`` management command.
    """

    name = models.CharField(
        max_length=100,
        help_text=_("Template name for easy identification."),
    )
    zone_type = models.CharField(
        max_length=50,
        choices=ZoneType.choices,
        db_index=True,
        help_text=_("Zone type this template applies to."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of what this template provides."),
    )

    # Default content and config
    default_content = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Default content JSON for this template."),
    )
    default_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Default configuration JSON for this template."),
    )

    # Custom template file
    template_file = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Custom template file path."),
    )

    # Preview image (static file path, e.g., "images/landingpages/about-image-left.png")
    preview_image = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text=_("Static file path to preview image (e.g., images/landingpages/template-name.png)."),
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Inactive templates are not available for selection."),
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_zone_templates",
    )

    class Meta:
        verbose_name = _("Zone Template")
        verbose_name_plural = _("Zone Templates")
        ordering = ["zone_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"
