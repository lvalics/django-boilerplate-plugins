import json

from django import forms
from django.contrib import admin, messages
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (
    FirewallConfig,
    IPReputationCache,
    IPReputationConfig,
    IPThreatSummary,
    RateLimitRule,
    SecuritySettings,
    SuspiciousRequest,
    ThreatPattern,
)


class FirewallConfigForm(forms.ModelForm):
    """Custom form for FirewallConfig with credential handling."""

    # Use a regular TextField for credentials input (JSON format)
    credentials = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 8, "class": "vLargeTextField"}),
        required=False,
        help_text=_("Enter credentials as JSON. Values are encrypted at rest."),
    )

    class Meta:
        model = FirewallConfig
        fields = ["name", "provider", "is_active", "is_default", "credentials"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate with decrypted credentials (pretty-printed JSON)
        if self.instance and self.instance.pk:
            creds = self.instance.credentials
            if creds:
                self.fields["credentials"].initial = json.dumps(creds, indent=2)

    def clean_credentials(self):
        """Validate and parse JSON credentials."""
        value = self.cleaned_data.get("credentials", "")
        if not value or not value.strip():
            return {}

        try:
            parsed = json.loads(value)
            if not isinstance(parsed, dict):
                raise forms.ValidationError(_("Credentials must be a JSON object"))
            return parsed
        except json.JSONDecodeError as e:
            raise forms.ValidationError(_("Invalid JSON: %(error)s") % {"error": str(e)})

    def save(self, commit=True):
        """Save with encrypted credentials."""
        instance = super().save(commit=False)
        # The property setter handles encryption
        instance.credentials = self.cleaned_data.get("credentials", {})
        if commit:
            instance.save()
        return instance


class WebSecurityAdminMixin:
    """Mixin to add help section to Web Security admin pages."""

    # Override these in subclasses
    page_help_title = ""
    page_help_text = ""

    @admin.display(description="")
    def page_help(self, obj=None):
        """Render the help box at the top of the form."""
        if not self.page_help_title and not self.page_help_text:
            return ""

        title = self.page_help_title or _("Help")
        text = self.page_help_text or ""

        return mark_safe(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 600;">
                ℹ️ {title}
            </h3>
            <div style="font-size: 14px; line-height: 1.6; opacity: 0.95;">
                {text}
            </div>
        </div>
        """)


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


@admin.register(FirewallConfig)
class FirewallConfigAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for firewall configurations."""

    form = FirewallConfigForm

    page_help_title = _("Firewall Configuration")
    page_help_text = _(
        "Configure external firewall providers to <strong>automatically block malicious IPs</strong>. "
        "Supported providers: <strong>Cloudflare</strong> (recommended), <strong>AWS WAF</strong>, "
        "<strong>Nginx</strong>, and <strong>iptables</strong>. "
        "Set one configuration as default for auto-blocking. "
        "See JSON examples below for each provider's required credentials. "
        "<strong>Note:</strong> Credentials are encrypted at rest."
    )

    list_display = ("name", "provider", "is_active", "is_default", "created_at")
    list_filter = ("provider", "is_active", "is_default")
    search_fields = ("name",)
    readonly_fields = ("page_help", "created_at", "updated_at", "credentials_help")

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("Configuration"),
            {
                "fields": ("name", "provider", "is_active", "is_default"),
            },
        ),
        (
            _("Credentials"),
            {
                "fields": ("credentials", "credentials_help"),
                "description": _(
                    "Provider-specific credentials in JSON format. Copy the example below and fill in your values."
                ),
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

    @admin.display(description=_("JSON Examples for Each Provider"))
    def credentials_help(self, obj):
        """Display JSON examples for each provider type."""
        providers = {
            "cloudflare": {
                "example": """{
    "api_token": "your-cloudflare-api-token",
    "zone_id": "your-zone-id",
    "ruleset_id": "your-ruleset-id"
}""",
                "color": "#f48120",
                "icon": "☁️",
                "note": "Recommended for most deployments. Works via API from anywhere.",
            },
            "aws_waf": {
                "example": """{
    "access_key": "AKIAIOSFODNN7EXAMPLE",
    "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "region": "us-east-1",
    "web_acl_arn": "arn:aws:wafv2:us-east-1:123456789:regional/webacl/my-acl/abc123",
    "ip_set_arn": "arn:aws:wafv2:us-east-1:123456789:regional/ipset/blocked-ips/def456"
}""",
                "color": "#ff9900",
                "icon": "🔶",
                "note": "Requires boto3 installed. Works via API from anywhere.",
            },
            "nginx": {
                "example": """{
    "config_path": "/etc/nginx/conf.d/blocklist.conf",
    "reload_command": "nginx -s reload"
}""",
                "color": "#009639",
                "icon": "🟢",
                "note": None,
                "warning": """⚠️ <strong>Docker Users:</strong> Commands run inside the container.
Mount the host config directory in docker-compose.yml:
<pre style='background: #fff3cd; padding: 8px; margin: 5px 0; border-radius: 4px;'>volumes:
  - /etc/nginx/conf.d:/etc/nginx/conf.d</pre>
You may need to reload nginx on the host separately.""",
            },
            "iptables": {
                "example": """{
    "chain": "INPUT",
    "protocol": "tcp",
    "port": 80
}""",
                "color": "#c9211e",
                "icon": "🔴",
                "note": None,
                "warning": """⚠️ <strong>Docker Users:</strong> iptables commands run inside the container
and do NOT affect the host firewall. This provider is only suitable for
non-Docker deployments or containers with <code>--privileged</code> mode.
<br><br>💡 <strong>Recommendation:</strong> Use Cloudflare or AWS WAF for Docker deployments.""",
            },
        }

        html = "<div style='font-family: sans-serif; padding: 10px;'>"
        html += "<strong>Provider Configuration Examples:</strong><br><br>"

        for provider, config in providers.items():
            is_selected = obj and obj.provider == provider
            border_color = config["color"] if is_selected else "#ddd"
            bg_color = "#f8f9fa" if is_selected else "#fff"

            html += f"""
            <div style='border: 2px solid {border_color}; border-radius: 8px;
                        padding: 12px; margin-bottom: 12px; background: {bg_color};'>
                <strong style='color: {config["color"]}; font-size: 14px;'>
                    {config["icon"]} {provider.upper()}
                    {
                "<span style='background: " + config["color"] + "; color: white; "
                "padding: 2px 8px; border-radius: 10px; font-size: 11px; "
                "margin-left: 8px;'>SELECTED</span>"
                if is_selected
                else ""
            }
                </strong>
            """

            if config.get("note"):
                html += "<p style='margin: 8px 0 0 0; font-size: 12px; color: #666;'>"
                html += f"{config['note']}</p>"

            escaped_example = escape(config["example"])
            html += f"""
                <pre style='background: #fff; padding: 10px; border: 1px solid #e0e0e0;
                            border-radius: 4px; margin: 10px 0 0 0; font-family: monospace;
                            font-size: 12px; overflow-x: auto;'>{escaped_example}</pre>
            """

            if config.get("warning"):
                html += f"""
                <div style='background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px;
                            padding: 10px; margin-top: 10px; font-size: 12px;'>
                    {config["warning"]}
                </div>
                """

            html += "</div>"

        html += "</div>"
        return mark_safe(html)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.is_default:
            messages.success(
                request,
                _("This firewall is now set as the default for auto-blocking."),
            )


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


@admin.register(IPReputationConfig)
class IPReputationConfigAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for IP reputation service configurations."""

    page_help_title = _("IP Reputation Service")
    page_help_text = _(
        "Check IP addresses against <strong>threat intelligence databases</strong>. "
        "<strong>AbuseIPDB</strong> is recommended (free tier: 1,000 lookups/day). "
        "IPs are checked asynchronously and results are cached. "
        "High-risk IPs can trigger automatic blocking."
    )

    list_display = ("name", "provider", "is_active", "is_default", "cache_duration_hours")
    list_filter = ("provider", "is_active", "is_default")
    search_fields = ("name",)
    readonly_fields = ("page_help", "created_at", "updated_at", "setup_help")

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("Configuration"),
            {
                "fields": ("name", "provider", "is_active", "is_default"),
            },
        ),
        (
            _("API Configuration"),
            {
                "fields": ("api_key", "api_url", "setup_help"),
                "description": _("API credentials. api_url only needed for custom provider."),
            },
        ),
        (
            _("Settings"),
            {
                "fields": ("cache_duration_hours", "min_confidence_score"),
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

    @admin.display(description=_("Setup Instructions"))
    def setup_help(self, obj):
        """Display dynamic setup instructions based on selected provider."""
        current_provider = obj.provider if obj else "abuseipdb"

        json_example = escape("""{
    "abuse_confidence_score": 85,
    "is_tor_node": false,
    "is_vpn": true,
    "country_code": "US"
}""")

        html = f"""
        <div id="provider-help-container" style="font-family: sans-serif;">

        <!-- AbuseIPDB Help -->
        <div id="help-abuseipdb" class="provider-help"
             style="background: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 4px solid #4caf50;
                    {"display: block;" if current_provider == "abuseipdb" else "display: none;"}">
            <strong style="color: #2e7d32;">🛡️ AbuseIPDB Setup</strong>
            <span style="background: #4caf50; color: white; padding: 2px 8px; border-radius: 10px;
                         font-size: 11px; margin-left: 10px;">FREE: 1,000/day</span>
            <ol style="margin: 10px 0; padding-left: 20px;">
                <li>Register at <a href="https://www.abuseipdb.com/" target="_blank"
                    style="color: #1976d2;">abuseipdb.com</a></li>
                <li>Go to <strong>Account → API → Create Key</strong></li>
                <li>Copy the API key and paste it in the field above</li>
            </ol>
            <pre style="background: #fff; padding: 10px; border: 1px solid #c8e6c9;
                        font-family: monospace; font-size: 12px;">API Key: abc123def456ghi789...</pre>
            <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                <strong>Note:</strong> Leave "API URL" empty - it's not needed for AbuseIPDB.
            </p>
        </div>

        <!-- IPQualityScore Help -->
        <div id="help-ipqualityscore" class="provider-help"
             style="background: #e3f2fd; padding: 15px; border-radius: 5px; border-left: 4px solid #2196f3;
                    {"display: block;" if current_provider == "ipqualityscore" else "display: none;"}">
            <strong style="color: #1565c0;">🔍 IPQualityScore Setup</strong>
            <span style="background: #2196f3; color: white; padding: 2px 8px; border-radius: 10px;
                         font-size: 11px; margin-left: 10px;">FREE: 5,000/month</span>
            <ol style="margin: 10px 0; padding-left: 20px;">
                <li>Register at <a href="https://www.ipqualityscore.com/" target="_blank"
                    style="color: #1976d2;">ipqualityscore.com</a></li>
                <li>Go to <strong>API Settings</strong> in your dashboard</li>
                <li>Copy your <strong>Private Key</strong> and paste it above</li>
            </ol>
            <pre style="background: #fff; padding: 10px; border: 1px solid #bbdefb;
                        font-family: monospace; font-size: 12px;">API Key: aBcDeFgHiJkLmNoPqRsTuVwXyZ123456</pre>
            <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                <strong>Features:</strong> Fraud score, VPN/proxy detection, bot detection, Tor detection.
            </p>
        </div>

        <!-- Custom API Help -->
        <div id="help-custom" class="provider-help"
             style="background: #fff3e0; padding: 15px; border-radius: 5px; border-left: 4px solid #ff9800;
                    {"display: block;" if current_provider == "custom" else "display: none;"}">
            <strong style="color: #e65100;">⚙️ Custom API Setup</strong>
            <p style="margin: 10px 0;">Enter your API URL with <code>{{ip}}</code> placeholder:</p>
            <pre style="background: #fff; padding: 10px; border: 1px solid #ffe0b2;
                        font-family: monospace; font-size: 12px;">https://api.example.com/check?ip={{ip}}</pre>
            <p style="margin: 10px 0;"><strong>Expected JSON response format:</strong></p>
            <pre style="background: #fff; padding: 10px; border: 1px solid #ffe0b2;
                        font-family: monospace; font-size: 12px;">{json_example}</pre>
            <p style="margin: 10px 0 0 0; font-size: 12px; color: #666;">
                <strong>Auth:</strong> API key sent as Bearer token in Authorization header.
            </p>
        </div>

        </div>

        <script>
        (function() {{
            function updateProviderHelp() {{
                var providerSelect = document.getElementById('id_provider');
                if (!providerSelect) return;

                var provider = providerSelect.value;
                var helpDivs = document.querySelectorAll('.provider-help');

                helpDivs.forEach(function(div) {{
                    div.style.display = 'none';
                }});

                var helpDiv = document.getElementById('help-' + provider);
                if (helpDiv) {{
                    helpDiv.style.display = 'block';
                }}

                // Show/hide API URL field based on provider
                var apiUrlRow = document.querySelector('.field-api_url');
                if (apiUrlRow) {{
                    apiUrlRow.style.display = (provider === 'custom') ? '' : 'none';
                }}
            }}

            // Run on page load
            document.addEventListener('DOMContentLoaded', function() {{
                updateProviderHelp();

                var providerSelect = document.getElementById('id_provider');
                if (providerSelect) {{
                    providerSelect.addEventListener('change', updateProviderHelp);
                }}
            }});

            // Also run immediately if DOM is already loaded
            if (document.readyState !== 'loading') {{
                updateProviderHelp();
                var providerSelect = document.getElementById('id_provider');
                if (providerSelect) {{
                    providerSelect.addEventListener('change', updateProviderHelp);
                }}
            }}
        }})();
        </script>
        """

        return mark_safe(html)


@admin.register(IPReputationCache)
class IPReputationCacheAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for IP reputation cache entries."""

    page_help_title = _("IP Reputation Cache")
    page_help_text = _(
        "View <strong>cached IP reputation data</strong> from external services. "
        "Entries are created automatically when IPs are checked. "
        "Use actions to re-check IPs or clean up expired entries. "
        "Entries are read-only - data comes from reputation services."
    )

    list_display = (
        "ip_address",
        "abuse_confidence_score",
        "is_tor_node",
        "is_vpn",
        "country_code",
        "is_expired_display",
        "check_pending",
    )
    list_filter = ("is_tor_node", "is_vpn", "is_datacenter", "check_pending")
    search_fields = ("ip_address", "isp", "domain")
    readonly_fields = (
        "page_help",
        "ip_address",
        "abuse_confidence_score",
        "is_tor_node",
        "is_vpn",
        "is_datacenter",
        "country_code",
        "isp",
        "domain",
        "total_reports",
        "last_reported_at",
        "raw_response",
        "expires_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("IP Information"),
            {
                "fields": ("ip_address", "country_code", "isp", "domain"),
            },
        ),
        (
            _("Reputation Data"),
            {
                "fields": (
                    "abuse_confidence_score",
                    "is_tor_node",
                    "is_vpn",
                    "is_datacenter",
                    "total_reports",
                    "last_reported_at",
                ),
            },
        ),
        (
            _("Cache Status"),
            {
                "fields": ("expires_at", "check_pending"),
            },
        ),
        (
            _("Raw Response"),
            {
                "fields": ("raw_response",),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description=_("Expired"), boolean=True)
    def is_expired_display(self, obj):
        return obj.is_expired

    def has_add_permission(self, request):
        """Cache entries are created automatically."""
        return False

    actions = ["queue_for_recheck", "delete_expired"]

    @admin.action(description=_("Queue for re-check"))
    def queue_for_recheck(self, request, queryset):
        updated = queryset.update(check_pending=True)
        messages.success(request, _("{} IPs queued for reputation re-check.").format(updated))

    @admin.action(description=_("Delete expired entries"))
    def delete_expired(self, request, queryset):
        from .models import IPReputationCache

        deleted = IPReputationCache.cleanup_expired()
        messages.success(request, _("{} expired entries deleted.").format(deleted))


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


@admin.register(IPThreatSummary)
class IPThreatSummaryAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for IP threat summaries."""

    page_help_title = _("IP Threat Summaries")
    page_help_text = _(
        "Aggregated threat data <strong>per IP address</strong>. "
        "Shows total threat score, request count, and block status. "
        "Use actions to manually block/unblock IPs or sync to firewall. "
        "IPs exceeding the auto-block threshold are automatically blocked."
    )

    list_display = (
        "ip_address",
        "total_threat_score",
        "request_count",
        "is_blocked",
        "firewall_synced",
        "last_seen",
    )
    list_filter = ("is_blocked", "firewall_synced", "last_seen")
    search_fields = ("ip_address", "block_reason", "notes")
    readonly_fields = (
        "page_help",
        "ip_address",
        "total_threat_score",
        "request_count",
        "first_seen",
        "last_seen",
        "categories_detected",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            None,
            {
                "fields": ("page_help",),
            },
        ),
        (
            _("IP Information"),
            {
                "fields": ("ip_address", "total_threat_score", "request_count"),
            },
        ),
        (
            _("Block Status"),
            {
                "fields": (
                    "is_blocked",
                    "blocked_at",
                    "blocked_until",
                    "block_reason",
                    "firewall_synced",
                ),
            },
        ),
        (
            _("Detection Details"),
            {
                "fields": ("categories_detected", "first_seen", "last_seen"),
            },
        ),
        (
            _("Admin Notes"),
            {
                "fields": ("notes",),
            },
        ),
    )

    actions = ["block_ips", "unblock_ips", "sync_to_firewall"]

    @admin.action(description=_("Block selected IPs"))
    def block_ips(self, request, queryset):
        blocked = 0
        for summary in queryset.filter(is_blocked=False):
            IPThreatSummary.block_ip(
                summary.ip_address,
                reason="Manually blocked via admin",
            )
            blocked += 1
        messages.success(request, _("{} IPs blocked.").format(blocked))

    @admin.action(description=_("Unblock selected IPs"))
    def unblock_ips(self, request, queryset):
        unblocked = 0
        for summary in queryset.filter(is_blocked=True):
            if IPThreatSummary.unblock_ip(summary.ip_address):
                unblocked += 1
        messages.success(request, _("{} IPs unblocked.").format(unblocked))

    @admin.action(description=_("Sync to firewall"))
    def sync_to_firewall(self, request, queryset):
        from .services.firewall import FirewallServiceFactory

        service = FirewallServiceFactory.get_default_service()
        if service is None:
            messages.error(request, _("No firewall service configured."))
            return

        blocked_ips = list(queryset.filter(is_blocked=True).values_list("ip_address", flat=True))
        if not blocked_ips:
            messages.warning(request, _("No blocked IPs selected."))
            return

        result = service.sync_blocks(blocked_ips)
        queryset.filter(is_blocked=True).update(firewall_synced=True)

        messages.success(
            request,
            _("Synced {added} IPs to firewall ({already} already blocked, {failed} failed).").format(
                added=result.get("added", 0),
                already=result.get("already_blocked", 0),
                failed=result.get("failed", 0),
            ),
        )
