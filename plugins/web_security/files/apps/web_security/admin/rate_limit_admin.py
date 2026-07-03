from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import RateLimitRule

from .mixins import WebSecurityAdminMixin


@admin.register(RateLimitRule)
class RateLimitRuleAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for rate limit rules."""

    page_help_title = _("Rate Limiting Rules")
    page_help_text = _(
        "Protect endpoints from <strong>brute force and DDoS attacks</strong>. "
        "Define rules matching URL patterns and HTTP methods. "
        "Set request limits (e.g., 10 requests/60 seconds) and actions when exceeded. "
        "Higher priority rules are evaluated first."
    )

    list_display = (
        "name",
        "path_pattern",
        "http_method",
        "rate_display",
        "action",
        "is_active",
        "priority",
    )
    list_filter = ("http_method", "action", "is_active")
    search_fields = ("name", "description", "path_pattern")
    list_editable = ("is_active", "priority")
    readonly_fields = ("page_help", "created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("Basic Info"),
            {
                "fields": ("name", "description", "is_active", "priority"),
            },
        ),
        (
            _("Matching"),
            {
                "fields": ("path_pattern", "http_method"),
                "description": _("Configure which requests this rule applies to."),
            },
        ),
        (
            _("Rate Limit"),
            {
                "fields": ("max_requests", "time_window_seconds"),
            },
        ),
        (
            _("Action"),
            {
                "fields": ("action", "block_duration_minutes"),
                "description": _("What to do when limit is exceeded."),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Rate"))
    def rate_display(self, obj):
        return f"{obj.max_requests}/{obj.time_window_seconds}s"
