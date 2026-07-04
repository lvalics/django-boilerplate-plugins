"""Admin for the landing pages plugin (lean: stock JSON editing, no custom JS)."""

import json

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    LandingPage,
    LandingPagesSettings,
    LandingPageSubmission,
    LandingPageZone,
    Testimonial,
    ZoneTemplate,
    ZoneType,
)

# Stock JSONField editing via a plain (larger) textarea - no custom JS editors.
JSON_WIDGET_OVERRIDES = {
    models.JSONField: {"widget": forms.Textarea(attrs={"rows": 20, "cols": 100, "class": "vLargeTextField"})},
}


class LandingPageZoneInline(admin.TabularInline):
    """Inline admin for zones within a landing page (reorder + toggle; edit via change link)."""

    model = LandingPageZone
    extra = 0
    ordering = ["order"]
    fields = ["zone_type", "title", "order", "is_active"]
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        """Only allow adding zones once the parent landing page is saved."""
        if obj is None or obj.pk is None:
            return False
        return super().has_add_permission(request, obj)


@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    """Admin for landing pages."""

    list_display = ["title", "slug", "site", "is_active", "zone_count", "view_page", "created_at"]
    list_filter = ["is_active", "site", "created_at"]
    search_fields = ["title", "slug", "meta_title", "meta_description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at", "created_by"]
    inlines = [LandingPageZoneInline]
    actions = ["duplicate_page"]

    fieldsets = (
        (None, {"fields": ("title", "slug", "site")}),
        (
            _("SEO"),
            {
                "fields": ("meta_title", "meta_description", "canonical_url"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Settings"),
            {"fields": ("use_site_template", "is_active", "form_disabled")},
        ),
        (
            _("Tracking"),
            {
                "fields": ("created_by", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Zones"))
    def zone_count(self, obj):
        """Display active zone count."""
        count = obj.zones.filter(is_active=True).count()
        total = obj.zones.count()
        return f"{count}/{total}"

    @admin.display(description=_("Actions"))
    def view_page(self, obj):
        """Link to view the landing page."""
        if not obj.slug:
            return "-"
        url = reverse("landing_pages:landing_page", kwargs={"slug": obj.slug})
        return format_html('<a href="{}" target="_blank">{}</a>', url, _("View page"))

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description=_("Duplicate selected pages"))
    def duplicate_page(self, request, queryset):
        """Clone landing pages with all zones (copies are created inactive)."""
        for page in queryset:
            zones = list(page.zones.all())
            page.pk = None
            page.slug = f"{page.slug}-copy"
            page.title = f"{page.title} (Copy)"
            page.is_active = False
            page.save()

            for zone in zones:
                zone.pk = None
                zone.landing_page = page
                zone.save()

        self.message_user(
            request, _("%(count)d page(s) duplicated (inactive).") % {"count": queryset.count()}
        )


@admin.register(LandingPageZone)
class LandingPageZoneAdmin(admin.ModelAdmin):
    """Admin for individual zones (stock JSON editing)."""

    formfield_overrides = JSON_WIDGET_OVERRIDES
    list_display = ["landing_page", "zone_type", "title", "order", "is_active", "has_testimonial"]
    list_filter = ["zone_type", "is_active", "landing_page__site", "landing_page"]
    list_select_related = ["landing_page"]
    search_fields = ["landing_page__title", "landing_page__slug", "title", "description"]
    ordering = ["landing_page", "order"]
    raw_id_fields = ["landing_page", "testimonial"]
    actions = ["duplicate_zone", "delete_inactive_zones"]

    def get_fieldsets(self, request, obj=None):
        """Show the testimonial field only for TESTIMONIAL_SINGLE zones."""
        fieldsets = [
            (None, {"fields": ("landing_page", "zone_type", "title", "order", "is_active")}),
            (
                _("Zone Description"),
                {
                    "fields": ("description",),
                    "classes": ("collapse",),
                    "description": _("Help text describing this zone's expected content structure."),
                },
            ),
            (
                _("Content"),
                {
                    "fields": ("content", "config"),
                    "classes": ("wide",),
                },
            ),
        ]

        if obj and obj.zone_type == ZoneType.TESTIMONIAL_SINGLE:
            fieldsets.append((_("Testimonial"), {"fields": ("testimonial",)}))

        fieldsets.append(
            (
                _("Advanced"),
                {
                    "fields": ("template_name",),
                    "classes": ("collapse",),
                },
            )
        )

        return fieldsets

    @admin.display(description=_("Testimonial"), boolean=True)
    def has_testimonial(self, obj):
        """Show if zone has an associated testimonial."""
        return obj.testimonial_id is not None

    @admin.action(description=_("Duplicate selected zones (inactive)"))
    def duplicate_zone(self, request, queryset):
        """Clone selected zones to the end of their landing page's zone list."""
        for zone in queryset:
            max_order = (
                LandingPageZone.objects.filter(landing_page=zone.landing_page).aggregate(models.Max("order"))[
                    "order__max"
                ]
                or 0
            )

            zone.pk = None
            zone.order = max_order + 1
            zone.is_active = False  # Inactive by default
            zone.save()

        self.message_user(
            request, _("%(count)d zone(s) duplicated (inactive).") % {"count": queryset.count()}
        )

    @admin.action(description=_("Delete inactive zones only"))
    def delete_inactive_zones(self, request, queryset):
        """Delete only inactive zones from the selection."""
        inactive_zones = queryset.filter(is_active=False)
        active_count = queryset.filter(is_active=True).count()
        inactive_count = inactive_zones.count()

        inactive_zones.delete()

        if inactive_count > 0:
            self.message_user(request, _("%(count)d inactive zone(s) deleted.") % {"count": inactive_count})
        if active_count > 0:
            messages.warning(
                request,
                _("%(count)d active zone(s) were skipped. Deactivate first.") % {"count": active_count},
            )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for testimonials."""

    list_display = ["author_name", "author_title", "rating", "is_verified", "created_at"]
    list_filter = ["is_verified", "rating"]
    search_fields = ["author_name", "text"]
    readonly_fields = ["schema_markup", "created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("text", "author_name", "author_title", "author_photo")}),
        (_("Rating & Verification"), {"fields": ("rating", "is_verified")}),
        (
            _("Media"),
            {
                "fields": ("video_url", "proof_image"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Schema"),
            {
                "fields": ("schema_markup",),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ZoneTemplate)
class ZoneTemplateAdmin(admin.ModelAdmin):
    """Admin for zone template presets (seed with `manage.py install_zone_templates`)."""

    formfield_overrides = JSON_WIDGET_OVERRIDES
    list_display = ["name", "zone_type", "is_active", "created_by"]
    list_filter = ["zone_type", "is_active"]
    search_fields = ["name", "description"]

    fieldsets = (
        (None, {"fields": ("name", "zone_type", "description", "preview_image", "is_active")}),
        (
            _("Default Content & Config"),
            {
                "fields": ("default_content", "default_config"),
                "classes": ("wide",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(LandingPageSubmission)
class LandingPageSubmissionAdmin(admin.ModelAdmin):
    """Admin for form submissions (read-mostly inbox; only status is editable)."""

    list_display = ["id", "email", "name", "landing_page", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["status", "landing_page", "created_at"]
    search_fields = ["email", "name", "phone", "landing_page__title", "landing_page__slug"]
    date_hierarchy = "created_at"
    raw_id_fields = ["landing_page", "zone"]
    readonly_fields = [
        "landing_page",
        "zone",
        "email",
        "name",
        "phone",
        "form_data_pretty",
        "uploaded_files_pretty",
        "ip_address",
        "created_at",
        "updated_at",
    ]
    actions = ["mark_as_seen", "mark_as_processed", "mark_as_spam"]

    fieldsets = (
        (None, {"fields": ("status", "email", "name", "phone")}),
        (_("Source"), {"fields": ("landing_page", "zone", "ip_address")}),
        (_("Form Data"), {"fields": ("form_data_pretty",)}),
        (_("Uploaded Files"), {"fields": ("uploaded_files_pretty",)}),
        (_("Timestamps"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request):
        return False

    @admin.display(description=_("Form Data"))
    def form_data_pretty(self, obj):
        """Pretty-printed, escaped form data (values are already server-side sanitized)."""
        return format_html("<pre>{}</pre>", json.dumps(obj.form_data or {}, indent=2, ensure_ascii=False))

    @admin.display(description=_("Uploaded Files"))
    def uploaded_files_pretty(self, obj):
        """Pretty-printed uploaded file storage paths."""
        return format_html("<pre>{}</pre>", json.dumps(obj.uploaded_files or [], indent=2, ensure_ascii=False))

    @admin.action(description=_("Mark selected submissions as seen"))
    def mark_as_seen(self, request, queryset):
        from .models import SubmissionStatus

        count = queryset.update(status=SubmissionStatus.SEEN)
        self.message_user(request, _("Marked %(count)d submission(s) as seen.") % {"count": count})

    @admin.action(description=_("Mark selected submissions as processed"))
    def mark_as_processed(self, request, queryset):
        from .models import SubmissionStatus

        count = queryset.update(status=SubmissionStatus.PROCESSED)
        self.message_user(request, _("Marked %(count)d submission(s) as processed.") % {"count": count})

    @admin.action(description=_("Mark selected submissions as spam"))
    def mark_as_spam(self, request, queryset):
        from .models import SubmissionStatus

        count = queryset.update(status=SubmissionStatus.SPAM)
        self.message_user(request, _("Marked %(count)d submission(s) as spam.") % {"count": count})


@admin.register(LandingPagesSettings)
class LandingPagesSettingsAdmin(admin.ModelAdmin):
    """Admin for per-site landing pages settings."""

    list_display = ["site", "is_enabled", "cache_timeout"]
    list_filter = ["is_enabled"]
    search_fields = ["site__site_name", "site__site__domain"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filter the site dropdown to sites without settings yet."""
        if db_field.name == "site":
            from apps.sites.models import SiteProfile

            existing_site_ids = LandingPagesSettings.objects.values_list("site_id", flat=True)
            kwargs["queryset"] = SiteProfile.objects.exclude(id__in=existing_site_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
