from django.contrib import admin
from django.utils.html import escape, format_html
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import SuspiciousRequest

from .mixins import WebSecurityAdminMixin


@admin.register(SuspiciousRequest)
class SuspiciousRequestAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for suspicious request logs."""

    page_help_title = _("Suspicious Requests Log")
    page_help_text = _(
        "View <strong>all detected threats in real-time</strong>. "
        "Each entry shows the request details, matched pattern, threat level, and action taken. "
        "Use filters to analyze specific threat categories or time periods. "
        "Logs are read-only - created automatically by threat detection."
    )

    list_display = (
        "created_at",
        "ip_address_with_lookup",
        "method",
        "path_truncated",
        "category",
        "threat_level_badge",
        "threat_score",
        "action_taken",
    )
    list_filter = ("category", "threat_level", "method", "action_taken", "created_at")
    search_fields = ("ip_address", "path", "pattern_name", "user_agent")
    readonly_fields = (
        "page_help",
        "ip_address_detail",
        "path",
        "method",
        "user_agent",
        "headers",
        "body_preview",
        "pattern_id",
        "pattern_name",
        "category",
        "threat_level",
        "threat_score",
        "matched_value",
        "response_code",
        "action_taken",
        "created_at",
    )
    date_hierarchy = "created_at"

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("Request Details"),
            {
                "fields": ("ip_address_detail", "method", "path", "user_agent"),
            },
        ),
        (
            _("Threat Information"),
            {
                "fields": (
                    "pattern_name",
                    "category",
                    "threat_level",
                    "threat_score",
                    "matched_value",
                ),
            },
        ),
        (
            _("Response"),
            {
                "fields": ("response_code", "action_taken"),
            },
        ),
        (
            _("Full Request Data"),
            {
                "fields": ("headers", "body_preview"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at",),
            },
        ),
    )

    class Media:
        js = ("admin/js/ip_lookup.js",)

    @admin.display(description=_("IP Address"), ordering="ip_address")
    def ip_address_with_lookup(self, obj):
        """IP address with hover tooltip for geolocation (list view)."""
        return format_html(
            '<span data-ip="{}">{}</span>',
            escape(obj.ip_address),
            escape(obj.ip_address),
        )

    @admin.display(description=_("IP Address"))
    def ip_address_detail(self, obj):
        """IP address with hover tooltip for geolocation (detail/change view)."""
        return format_html(
            '<span data-ip="{}">{}</span>',
            escape(obj.ip_address),
            escape(obj.ip_address),
        )

    @admin.display(description=_("Path"))
    def path_truncated(self, obj):
        return obj.path[:50] + "..." if len(obj.path) > 50 else obj.path

    @admin.display(description=_("Threat Level"))
    def threat_level_badge(self, obj):
        colors = {
            "low": "#28a745",
            "medium": "#ffc107",
            "high": "#fd7e14",
            "critical": "#dc3545",
        }
        color = colors.get(obj.threat_level, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.threat_level.upper() if obj.threat_level else "N/A",
        )

    def has_add_permission(self, request):
        """Logs are created automatically."""
        return False

    def has_change_permission(self, request, obj=None):
        """Logs should not be modified."""
        return False
