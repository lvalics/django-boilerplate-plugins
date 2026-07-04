"""Page (landing / content / blog post) and zone models."""

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class PageType(models.TextChoices):
    """Types of CMS pages served by this plugin."""

    LANDING = "landing", _("Landing page")
    CONTENT = "content", _("Content page")
    POST = "post", _("Blog post")


class PageQuerySet(models.QuerySet):
    """Query helpers for pages (adopted from the Victoury CMS manager pattern)."""

    def posts(self):
        return self.filter(page_type=PageType.POST)

    def content_pages(self):
        return self.filter(page_type=PageType.CONTENT)

    def published(self):
        """Active pages with a publication date at or before now."""
        return self.filter(
            is_active=True,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        )


class PageManager(models.Manager.from_queryset(PageQuerySet)):
    pass


class ZoneType(models.TextChoices):
    """Available zone types for landing pages."""

    HERO_VIDEO = "hero_video", _("Hero with Video")
    TESTIMONIAL_SINGLE = "testimonial_single", _("Single Testimonial")
    BENEFITS_GRID = "benefits_grid", _("Benefits Grid")
    SOCIAL_PROOF_CTA = "social_proof_cta", _("Social Proof CTA")
    CURRICULUM = "curriculum", _("Curriculum/Outline")
    TESTIMONIALS_GRID = "testimonials_grid", _("Testimonials Grid")
    PRICING = "pricing", _("Pricing Section")
    ABOUT_INSTRUCTOR = "about_instructor", _("About Instructor")
    GUARANTEE = "guarantee", _("Guarantee Section")
    FAQ = "faq", _("FAQ Section")
    FINAL_CTA = "final_cta", _("Final CTA")
    ORDER_FORM = "order_form", _("Order Form")
    CAROUSEL = "carousel", _("Carousel")
    COMPARISON = "comparison", _("Comparison Slider")
    GALLERY = "gallery", _("Gallery")
    JUMBOTRON = "jumbotron", _("Jumbotron")
    QR_CODE = "qr_code", _("QR Code")
    TABLE = "table", _("Table")
    TIMELINE = "timeline", _("Timeline")
    VIDEO = "video", _("Video")
    REDIRECT = "redirect", _("Redirect")
    SHOWCASE = "showcase", _("Showcase")
    BANNER = "banner", _("Banner")
    FOOTER = "footer", _("Footer")

    @classmethod
    def get_template_name(cls, zone_type):
        """Get template path for a zone type."""
        return f"cms/zones/{zone_type}.html"


# Zone template overrides may only point inside the plugin's zone template
# directory. This prevents an editor from turning ``template_name`` into an
# arbitrary ``{% include %}`` of any template on disk (e.g. settings-leaking
# admin or email templates).
ZONE_TEMPLATE_NAME_RE = re.compile(r"^cms/zones/[a-z0-9_/-]+\.html$")

# Schema-lite validation: the minimal top-level ``content`` keys each zone type
# needs to render something meaningful. Derived from the seed presets in
# management/commands/zone_templates/ (only the clearly essential keys).
# Zone types absent from this dict (e.g. testimonial_single, which may render a
# linked Testimonial instead of inline content) are not validated.
REQUIRED_CONTENT_KEYS: dict[str, list[str]] = {
    ZoneType.HERO_VIDEO: ["headline"],
    ZoneType.BENEFITS_GRID: ["items"],
    ZoneType.SOCIAL_PROOF_CTA: ["headline"],
    ZoneType.CURRICULUM: ["modules"],
    ZoneType.TESTIMONIALS_GRID: ["testimonials"],
    ZoneType.PRICING: ["plans"],
    ZoneType.ABOUT_INSTRUCTOR: ["title"],
    ZoneType.GUARANTEE: ["title", "text"],
    ZoneType.FAQ: ["questions"],
    ZoneType.FINAL_CTA: ["headline", "cta_text"],
    ZoneType.ORDER_FORM: ["form_fields"],
    ZoneType.CAROUSEL: ["slides"],
    ZoneType.COMPARISON: ["before_image", "after_image"],
    ZoneType.GALLERY: ["title"],
    ZoneType.JUMBOTRON: ["title"],
    ZoneType.QR_CODE: ["url"],
    ZoneType.TABLE: ["title"],
    ZoneType.TIMELINE: ["items"],
    ZoneType.VIDEO: ["source"],
    ZoneType.REDIRECT: ["redirect_url"],
    ZoneType.SHOWCASE: ["title", "image"],
    ZoneType.BANNER: ["message"],
    ZoneType.FOOTER: ["company_name"],
}


class Page(BaseModel):
    """
    A CMS page with modular zones.

    ``page_type`` selects how the page is served:

    - ``landing`` (default): zone-built landing page at ``/<slug>/``
    - ``content``: a static content page at ``/<content-prefix>/<slug>/``
    - ``post``: a blog post at ``/<blog-prefix>/<slug>/`` (uses author,
      published_at, excerpt, category and tags)

    Each page can be scoped to a single site (via SiteProfile from the
    multi_domain plugin) or shown on all sites when ``site`` is empty.
    """

    title = models.CharField(
        max_length=200,
        help_text=_("Internal title for this page."),
    )
    slug = models.SlugField(
        max_length=200,
        help_text=_("URL-friendly identifier. Must be unique per site (and unique among all-sites pages)."),
    )

    page_type = models.CharField(
        max_length=16,
        choices=PageType.choices,
        default=PageType.LANDING,
        db_index=True,
        help_text=_("Type of page: landing, content, or blog post."),
    )

    # Blog / content metadata (used mainly by ``post`` pages).
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_pages",
        help_text=_("Author of this page (used for blog posts)."),
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Publication date (used for blog post ordering and scheduling)."),
    )
    excerpt = models.TextField(
        blank=True,
        default="",
        help_text=_("Short summary used in listings and SEO fallbacks."),
    )
    category = models.ForeignKey(
        "Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pages",
        help_text=_("Primary category for this page."),
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name="pages",
        help_text=_("Tags associated with this page."),
    )

    # Site relationship - provided by the multi_domain plugin (apps.sites).
    # If null, the landing page is accessible on all sites.
    site = models.ForeignKey(
        "site_management.SiteProfile",
        on_delete=models.CASCADE,
        related_name="cms_pages",
        null=True,
        blank=True,
        help_text=_("The site this landing page belongs to. Leave empty to show on all sites."),
    )

    # SEO fields
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        help_text=_("SEO title (max 70 chars). Defaults to title if empty."),
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text=_("SEO description (max 160 chars)."),
    )
    canonical_url = models.URLField(
        blank=True,
        help_text=_("Canonical URL if different from page URL."),
    )

    # Template settings
    use_site_template = models.BooleanField(
        default=True,
        help_text=_("Use the site's base template. Uncheck for standalone pages."),
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Inactive pages return 404."),
    )
    form_disabled = models.BooleanField(
        default=False,
        help_text=_("Disable form submissions on this page."),
    )

    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_cms_pages",
        help_text=_("User who created this page."),
    )

    objects = PageManager()

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "slug"],
                name="cms_unique_slug_per_site",
            ),
            models.UniqueConstraint(
                fields=["slug"],
                condition=Q(site__isnull=True),
                name="cms_unique_slug_all_sites",
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.slug})"

    def clean(self):
        """Reject slugs that would be shadowed by reserved top-level URL prefixes."""
        super().clean()
        from .. import conf

        if self.slug and self.slug in conf.RESERVED_SLUGS:
            raise ValidationError(
                {
                    "slug": _(
                        '"%(slug)s" is a reserved URL path and would conflict with an existing route. '
                        "Choose a different slug (see CMS_RESERVED_SLUGS)."
                    )
                    % {"slug": self.slug}
                }
            )

    def get_absolute_url(self):
        from django.urls import NoReverseMatch, reverse

        try:
            if self.page_type == PageType.POST:
                return reverse("cms_blog:blog_detail", kwargs={"slug": self.slug})
            if self.page_type == PageType.CONTENT:
                return reverse("cms_blog:content_page", kwargs={"slug": self.slug})
            return reverse("cms:page", kwargs={"slug": self.slug})
        except NoReverseMatch:
            return f"/{self.slug}/"

    def get_meta_title(self):
        """Get SEO title with fallback to page title."""
        return self.meta_title or self.title

    def get_active_zones(self):
        """Get all active zones ordered by position."""
        return self.zones.filter(is_active=True).order_by("order")

    @classmethod
    def for_site(cls, site_id=None):
        """
        Active pages visible for the given Django Site id, best match first.

        With a site id: site-specific pages and all-sites pages, site-specific
        preferred on slug collision. Without a site id: all active pages,
        all-sites pages preferred. Use ``.filter(slug=...).first()`` to resolve.
        """
        qs = cls.objects.filter(is_active=True)
        if site_id:
            return qs.filter(Q(site__isnull=True) | Q(site__site_id=site_id)).order_by(
                F("site_id").asc(nulls_last=True), "-created_at"
            )
        return qs.order_by(F("site_id").asc(nulls_first=True), "-created_at")


class Zone(BaseModel):
    """
    A section/zone within a landing page.

    Each zone has a type that determines its template and stores its content
    and configuration as JSON.
    """

    landing_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="zones",
        help_text=_("The landing page this zone belongs to."),
    )

    zone_type = models.CharField(
        max_length=50,
        choices=ZoneType.choices,
        db_index=True,
        help_text=_("Type of zone determines the template used."),
    )

    title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Short title for this zone (max 100 chars). Shown in admin listings for easy identification."),
    )

    description = models.TextField(
        blank=True,
        help_text=_("Help text and documentation for this zone. Describes expected content structure."),
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text=_("Display order (lower numbers first)."),
    )

    # Content and configuration as JSON
    content = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Zone content (text, images, etc.) as JSON."),
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Zone configuration (styling, behavior) as JSON."),
    )

    # Template override (restricted to the plugin's zone template directory)
    template_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Custom template path. Must match "cms/zones/<name>.html". Leave empty for default.'),
    )

    # Optional testimonial link (for testimonial zones)
    testimonial = models.ForeignKey(
        "Testimonial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="zones",
        help_text=_("Linked testimonial for testimonial zone types."),
    )

    is_active = models.BooleanField(
        default=True,
        help_text=_("Inactive zones are not rendered."),
    )

    class Meta:
        verbose_name = _("Landing Page Zone")
        verbose_name_plural = _("Landing Page Zones")
        ordering = ["landing_page", "order"]

    def __str__(self):
        return f"{self.landing_page.title} - {self.get_zone_type_display()} (#{self.order})"

    def clean(self):
        """Validate zone constraints, template whitelist, and required content keys."""
        from django.core.exceptions import ValidationError

        super().clean()

        # Only one ORDER_FORM zone allowed per landing page
        if self.zone_type == ZoneType.ORDER_FORM and self.landing_page_id:
            existing = Zone.objects.filter(
                landing_page=self.landing_page,
                zone_type=ZoneType.ORDER_FORM,
            ).exclude(pk=self.pk)

            if existing.exists():
                raise ValidationError(
                    _("Only one Order Form zone is allowed per landing page. This page already has an Order Form zone.")
                )

        # Template override whitelist: only zone templates may be included.
        if self.template_name and not ZONE_TEMPLATE_NAME_RE.match(self.template_name):
            raise ValidationError(
                {
                    "template_name": _(
                        'Custom templates must match "cms/zones/<name>.html" '
                        "(lowercase letters, digits, hyphens, underscores)."
                    )
                }
            )

        # Schema-lite content validation. Only enforced when content is
        # provided, so zones can be created empty and filled in afterwards.
        if self.content:
            if not isinstance(self.content, dict):
                raise ValidationError({"content": _("Zone content must be a JSON object.")})
            missing = [key for key in REQUIRED_CONTENT_KEYS.get(self.zone_type, []) if key not in self.content]
            if missing:
                raise ValidationError(
                    {
                        "content": _('Zone type "%(zone_type)s" requires the content key(s): %(keys)s.')
                        % {"zone_type": self.get_zone_type_display(), "keys": ", ".join(missing)}
                    }
                )

    def get_template_name(self):
        """Get template path for this zone (whitelisted override or type default)."""
        if self.template_name and ZONE_TEMPLATE_NAME_RE.match(self.template_name):
            return self.template_name
        return ZoneType.get_template_name(self.zone_type)
