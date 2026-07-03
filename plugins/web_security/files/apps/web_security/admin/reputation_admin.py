from django.contrib import admin, messages
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import IPReputationCache, IPReputationConfig

from .forms import IPReputationConfigForm
from .mixins import WebSecurityAdminMixin


@admin.register(IPReputationConfig)
class IPReputationConfigAdmin(WebSecurityAdminMixin, admin.ModelAdmin):
    """Admin for IP reputation service configurations."""

    form = IPReputationConfigForm

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
        from apps.web_security.models import IPReputationCache

        deleted = IPReputationCache.cleanup_expired()
        messages.success(request, _("{} expired entries deleted.").format(deleted))
