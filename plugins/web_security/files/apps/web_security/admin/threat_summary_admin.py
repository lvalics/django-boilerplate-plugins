from django.contrib import admin, messages
from django.core.cache import cache
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import IPThreatSummary

from .mixins import WebSecurityAdminMixin


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
        blocked = queryset.filter(is_blocked=False).update(
            is_blocked=True,
            blocked_at=timezone.now(),
            block_reason="Manually blocked via admin",
            blocked_until=None,
        )
        if blocked:
            cache.delete(IPThreatSummary.BLOCKED_IPS_CACHE_KEY)
        messages.success(request, _("{} IPs blocked.").format(blocked))

    @admin.action(description=_("Unblock selected IPs"))
    def unblock_ips(self, request, queryset):
        unblocked = queryset.filter(is_blocked=True).update(
            is_blocked=False,
            blocked_until=None,
        )
        if unblocked:
            cache.delete(IPThreatSummary.BLOCKED_IPS_CACHE_KEY)
        messages.success(request, _("{} IPs unblocked.").format(unblocked))

    @admin.action(description=_("Sync to firewall"))
    def sync_to_firewall(self, request, queryset):
        from apps.web_security.services.firewall import FirewallServiceFactory

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
