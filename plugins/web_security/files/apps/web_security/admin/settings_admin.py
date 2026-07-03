from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import SecuritySettings

from .mixins import WebSecurityAdminMixin


@admin.register(SecuritySettings)
class SecuritySettingsAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for global security settings."""

    page_help_title = _("Security Settings")
    page_help_text = _(
        "This is the <strong>central control panel</strong> for all web security features. "
        "Use the master switch to enable/disable security monitoring globally. "
        "Toggle individual features like threat detection, rate limiting, and IP blocking. "
        "Configure auto-block thresholds and notification settings."
    )
    readonly_fields = ("page_help",)

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("Master Control"),
            {
                "fields": ("security_enabled",),
                "description": _("Master switch to enable/disable all security features."),
            },
        ),
        (
            _("Feature Toggles"),
            {
                "fields": (
                    "threat_detection_enabled",
                    "rate_limiting_enabled",
                    "ip_blocking_enabled",
                    "ip_reputation_enabled",
                    "auto_block_enabled",
                    "logging_enabled",
                    "security_headers_enabled",
                ),
                "description": _("Enable or disable individual security features."),
            },
        ),
        (
            _("Threat Categories"),
            {
                "fields": (
                    "detect_wordpress_scans",
                    "detect_php_scans",
                    "detect_sensitive_files",
                    "detect_admin_panels",
                    "detect_scanners",
                    "detect_sql_injection",
                    "detect_path_traversal",
                    "detect_shell_access",
                    "detect_api_abuse",
                ),
                "description": _("Enable or disable detection of specific threat categories."),
                "classes": ("collapse",),
            },
        ),
        (
            _("Thresholds"),
            {
                "fields": ("auto_block_threshold", "block_duration_minutes"),
                "description": _("Configure automatic blocking thresholds."),
            },
        ),
        (
            _("Whitelists"),
            {
                "fields": ("whitelist_ips", "whitelist_paths"),
                "description": _(
                    "Configure exemptions from security checks. "
                    "Private IPs (localhost, Docker, LAN) are automatically exempt."
                ),
            },
        ),
        (
            _("Notifications"),
            {
                "fields": (
                    "notification_email",
                    "notify_on_block",
                    "notify_on_critical",
                ),
                "description": _("Configure email notifications for security events."),
            },
        ),
    )

    def has_add_permission(self, request):
        """Only allow one instance."""
        return not SecuritySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings."""
        return False
