"""Blog taxonomy: site-scoped Category and Tag models."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class Category(BaseModel):
    """Hierarchical category for CMS pages (site-scoped, like pages themselves)."""

    site = models.ForeignKey(
        "site_management.SiteProfile",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="cms_categories",
        help_text=_("The site this category belongs to. Leave empty for all sites."),
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")

    class Meta:
        unique_together = [("site", "slug")]
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        seen = set()
        cur = self.parent
        while cur:
            if (self.pk is not None and cur.pk == self.pk) or cur.pk in seen:
                raise ValidationError({"parent": _("Category cannot be its own ancestor.")})
            seen.add(cur.pk)
            cur = cur.parent


class Tag(BaseModel):
    """Tag for CMS pages (site-scoped)."""

    site = models.ForeignKey(
        "site_management.SiteProfile",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="cms_tags",
        help_text=_("The site this tag belongs to. Leave empty for all sites."),
    )
    slug = models.SlugField(max_length=200)
    name = models.CharField(max_length=200)

    class Meta:
        unique_together = [("site", "slug")]
        ordering = ["name"]
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    def __str__(self):
        return self.name
