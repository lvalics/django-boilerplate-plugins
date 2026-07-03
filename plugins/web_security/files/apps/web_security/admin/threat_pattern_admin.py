from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import ThreatPattern

from .mixins import WebSecurityAdminMixin


@admin.register(ThreatPattern)
class ThreatPatternAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for threat detection patterns."""

    page_help_title = _("Threat Detection Patterns")
    page_help_text = _(
        "Define <strong>regex patterns</strong> to detect malicious requests. "
        "Patterns can match against URL paths, user agents, headers, or request bodies. "
        "Each pattern has a category, threat level, and score. "
        "Use <code>python manage.py seed_patterns</code> to load default patterns."
    )

    list_display = (
        "name",
        "category",
        "match_type",
        "threat_level_badge",
        "threat_score",
        "is_active",
    )
    list_filter = ("category", "threat_level", "match_type", "is_active")
    search_fields = ("name", "description", "pattern")
    list_editable = ("is_active",)
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
                "fields": ("name", "description", "is_active"),
            },
        ),
        (
            _("Pattern Configuration"),
            {
                "fields": ("pattern", "match_type", "header_name", "case_sensitive"),
                "description": _("Configure the regex pattern and what it matches against."),
            },
        ),
        (
            _("Classification"),
            {
                "fields": ("category", "threat_level", "threat_score"),
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
            obj.get_threat_level_display(),
        )

    actions = ["activate_patterns", "deactivate_patterns"]

    @admin.action(description=_("Activate selected patterns"))
    def activate_patterns(self, request, queryset):
        updated = queryset.update(is_active=True)
        messages.success(request, _("{} patterns activated.").format(updated))

    @admin.action(description=_("Deactivate selected patterns"))
    def deactivate_patterns(self, request, queryset):
        updated = queryset.update(is_active=False)
        messages.success(request, _("{} patterns deactivated.").format(updated))
