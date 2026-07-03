from django.contrib import admin, messages
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import FirewallConfig

from .forms import FirewallConfigForm
from .mixins import WebSecurityAdminMixin


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
