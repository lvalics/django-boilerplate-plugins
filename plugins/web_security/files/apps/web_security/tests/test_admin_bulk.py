"""Regression tests for bulk IP block/unblock admin actions.

Fix: IPThreatSummaryAdmin.block_ips / unblock_ips used to loop over the selected
queryset doing a per-row `.save()` (via `IPThreatSummary.block_ip`/`unblock_ip`) plus a
per-row cache invalidation. For N selected rows that's N writes and N cache deletes.
The fix replaces the loop with a single `queryset.update(...)` and a single cache
invalidation after the bulk write.
"""

from django.contrib import admin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.cache import cache
from django.test import RequestFactory, TestCase

from apps.web_security.admin import IPThreatSummaryAdmin
from apps.web_security.models import IPThreatSummary


class IPThreatSummaryBulkActionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.model_admin = IPThreatSummaryAdmin(IPThreatSummary, admin.site)
        cache.delete(IPThreatSummary.BLOCKED_IPS_CACHE_KEY)

    def _request(self):
        request = self.factory.post("/admin/web_security/ipthreatsummary/")
        # Smallest seam to make `messages.success(request, ...)` work outside
        # the full middleware stack.
        setattr(request, "session", "session")
        messages_storage = FallbackStorage(request)
        setattr(request, "_messages", messages_storage)
        return request

    def test_block_ips_bulk_updates_all_rows(self):
        ips = [
            IPThreatSummary.objects.create(ip_address="203.0.113.1"),
            IPThreatSummary.objects.create(ip_address="203.0.113.2"),
            IPThreatSummary.objects.create(ip_address="203.0.113.3"),
        ]
        # Warm the cache so we can assert it gets cleared by the action.
        cache.set(IPThreatSummary.BLOCKED_IPS_CACHE_KEY, {"stale"}, 120)

        queryset = IPThreatSummary.objects.filter(pk__in=[ip.pk for ip in ips])
        request = self._request()

        self.model_admin.block_ips(request, queryset)

        for ip in ips:
            ip.refresh_from_db()
            self.assertTrue(ip.is_blocked)
            self.assertEqual(ip.block_reason, "Manually blocked via admin")
            self.assertIsNotNone(ip.blocked_at)
            self.assertIsNone(ip.blocked_until)

        self.assertIsNone(cache.get(IPThreatSummary.BLOCKED_IPS_CACHE_KEY))

    def test_unblock_ips_bulk_updates_all_rows(self):
        ips = [
            IPThreatSummary.objects.create(ip_address="198.51.100.1", is_blocked=True),
            IPThreatSummary.objects.create(ip_address="198.51.100.2", is_blocked=True),
        ]
        cache.set(IPThreatSummary.BLOCKED_IPS_CACHE_KEY, {"198.51.100.1", "198.51.100.2"}, 120)

        queryset = IPThreatSummary.objects.filter(pk__in=[ip.pk for ip in ips])
        request = self._request()

        self.model_admin.unblock_ips(request, queryset)

        for ip in ips:
            ip.refresh_from_db()
            self.assertFalse(ip.is_blocked)
            self.assertIsNone(ip.blocked_until)

        self.assertIsNone(cache.get(IPThreatSummary.BLOCKED_IPS_CACHE_KEY))

    def test_block_ips_uses_single_bulk_update_query(self):
        """The old implementation issued one UPDATE per selected row (plus a
        get_or_create SELECT). The bulk version should issue exactly one UPDATE."""
        ips = [
            IPThreatSummary.objects.create(ip_address="192.0.2.10"),
            IPThreatSummary.objects.create(ip_address="192.0.2.11"),
            IPThreatSummary.objects.create(ip_address="192.0.2.12"),
        ]
        queryset = IPThreatSummary.objects.filter(pk__in=[ip.pk for ip in ips])
        request = self._request()

        with self.assertNumQueries(1):
            self.model_admin.block_ips(request, queryset)
