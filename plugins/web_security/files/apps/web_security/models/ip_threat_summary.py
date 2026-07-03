import logging

from django.core.cache import cache
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel

logger = logging.getLogger(__name__)


class IPThreatSummary(BaseModel):
    """
    Aggregated threat data per IP address.

    Maintains running totals of threat scores and request counts
    for each IP that has triggered security patterns.
    """

    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name=_("IP Address"),
        help_text=_("Client IP address"),
    )
    total_threat_score = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Threat Score"),
        help_text=_("Cumulative threat score"),
    )
    request_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Request Count"),
        help_text=_("Total number of suspicious requests"),
    )
    first_seen = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("First Seen"),
        help_text=_("When IP was first detected"),
    )
    last_seen = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last Seen"),
        help_text=_("When IP was last detected"),
    )
    is_blocked = models.BooleanField(
        default=False,
        verbose_name=_("Blocked"),
        help_text=_("Whether IP is currently blocked"),
        db_index=True,
    )
    blocked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Blocked At"),
        help_text=_("When IP was blocked"),
    )
    blocked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Blocked Until"),
        help_text=_("When block expires"),
    )
    block_reason = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Block Reason"),
        help_text=_("Reason for blocking"),
    )
    firewall_synced = models.BooleanField(
        default=False,
        verbose_name=_("Firewall Synced"),
        help_text=_("Whether block has been synced to firewall"),
    )
    categories_detected = models.JSONField(
        default=list,
        verbose_name=_("Categories Detected"),
        help_text=_("List of threat categories detected from this IP"),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Notes"),
        help_text=_("Admin notes about this IP"),
    )

    BLOCKED_IPS_CACHE_KEY = "web_security:blocked_ips"
    # Cache timeout must be > auto_block task interval (60s) to prevent gaps
    CACHE_TIMEOUT = 120  # 2 minutes

    class Meta:
        verbose_name = _("IP Threat Summary")
        verbose_name_plural = _("IP Threat Summaries")
        ordering = ["-total_threat_score", "-last_seen"]
        indexes = [
            models.Index(fields=["is_blocked", "-total_threat_score"]),
            models.Index(fields=["-total_threat_score"]),
        ]

    def __str__(self):
        status = "BLOCKED" if self.is_blocked else f"score: {self.total_threat_score}"
        return f"{self.ip_address} ({status})"

    def save(self, *args, **kwargs):
        """Clear blocked IPs cache when saving."""
        super().save(*args, **kwargs)
        if self.is_blocked:
            cache.delete(self.BLOCKED_IPS_CACHE_KEY)

    @classmethod
    def _fetch_blocked_ips_from_db(cls):
        """Fetch blocked IPs directly from database."""
        now = timezone.now()
        return set(
            cls.objects.filter(is_blocked=True)
            .filter(models.Q(blocked_until__isnull=True) | models.Q(blocked_until__gt=now))
            .values_list("ip_address", flat=True)
        )

    @classmethod
    def get_blocked_ips(cls):
        """
        Get set of currently blocked IPs with cache and DB fallback.

        Falls back to direct DB query if cache is unavailable,
        ensuring blocked IPs are always enforced even during cache failures.

        Returns:
            set: Set of blocked IP addresses
        """
        try:
            blocked = cache.get(cls.BLOCKED_IPS_CACHE_KEY)
            if blocked is None:
                blocked = cls._fetch_blocked_ips_from_db()
                try:
                    cache.set(cls.BLOCKED_IPS_CACHE_KEY, blocked, cls.CACHE_TIMEOUT)
                except Exception as cache_error:
                    logger.warning("Failed to set blocked IPs cache: %s", cache_error)
            return blocked
        except Exception as e:
            # Cache completely unavailable - fall back to DB
            logger.warning("Cache unavailable for blocked IPs, falling back to DB: %s", e)
            try:
                return cls._fetch_blocked_ips_from_db()
            except Exception as db_error:
                logger.error("Both cache and DB failed for blocked IPs: %s", db_error)
                # Return empty set - fail open to avoid blocking legitimate traffic
                # when both cache and DB are down
                return set()

    @classmethod
    def is_ip_blocked(cls, ip_address):
        """
        Check if an IP is currently blocked.

        Args:
            ip_address: IP address to check

        Returns:
            bool: True if IP is blocked
        """
        return ip_address in cls.get_blocked_ips()

    @classmethod
    def add_threat(cls, ip_address, threat_score, category=None):
        """
        Add threat score for an IP address atomically.

        Uses F() expressions for atomic counter updates to prevent
        race conditions when multiple requests update the same IP.

        Args:
            ip_address: IP address
            threat_score: Score to add
            category: Optional threat category

        Returns:
            IPThreatSummary: Updated or created summary
        """
        with transaction.atomic():
            # Try to create first
            summary, created = cls.objects.get_or_create(
                ip_address=ip_address,
                defaults={"total_threat_score": threat_score, "request_count": 1},
            )

            if not created:
                # Use F() expressions for atomic update - no race condition
                cls.objects.filter(pk=summary.pk).update(
                    total_threat_score=F("total_threat_score") + threat_score,
                    request_count=F("request_count") + 1,
                )

            # Handle category update with row lock to prevent duplicates
            if category:
                # Re-fetch with lock to safely update JSONField
                summary = cls.objects.select_for_update().get(pk=summary.pk)
                if category not in summary.categories_detected:
                    summary.categories_detected = summary.categories_detected + [category]
                    summary.save(update_fields=["categories_detected"])
                return summary

            # Refresh from DB to get updated values if we used F() expression
            if not created:
                summary.refresh_from_db()

            return summary

    @classmethod
    def block_ip(cls, ip_address, reason="", duration_minutes=None):
        """
        Block an IP address.

        Args:
            ip_address: IP address to block
            reason: Reason for blocking
            duration_minutes: How long to block (None = permanent)

        Returns:
            IPThreatSummary: Updated summary
        """
        summary, _ = cls.objects.get_or_create(ip_address=ip_address)
        summary.is_blocked = True
        summary.blocked_at = timezone.now()
        summary.block_reason = reason

        if duration_minutes:
            summary.blocked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        else:
            summary.blocked_until = None

        summary.save()
        cache.delete(cls.BLOCKED_IPS_CACHE_KEY)
        return summary

    @classmethod
    def unblock_ip(cls, ip_address):
        """
        Unblock an IP address.

        Args:
            ip_address: IP address to unblock

        Returns:
            bool: True if IP was unblocked
        """
        updated = cls.objects.filter(ip_address=ip_address, is_blocked=True).update(
            is_blocked=False,
            blocked_until=None,
        )
        if updated:
            cache.delete(cls.BLOCKED_IPS_CACHE_KEY)
        return updated > 0

    @classmethod
    def cleanup_expired_blocks(cls):
        """
        Unblock IPs whose block has expired.

        Returns:
            int: Number of IPs unblocked
        """
        now = timezone.now()
        updated = cls.objects.filter(
            is_blocked=True,
            blocked_until__isnull=False,
            blocked_until__lte=now,
        ).update(is_blocked=False)

        if updated:
            cache.delete(cls.BLOCKED_IPS_CACHE_KEY)
        return updated

    @classmethod
    def get_high_threat_ips(cls, threshold=70):
        """
        Get IPs that exceed the threat threshold but aren't blocked.

        Args:
            threshold: Minimum threat score

        Returns:
            QuerySet: IPs above threshold
        """
        return cls.objects.filter(
            total_threat_score__gte=threshold,
            is_blocked=False,
        ).order_by("-total_threat_score")

    @classmethod
    def get_blocked_not_synced(cls):
        """
        Get blocked IPs that haven't been synced to firewall.

        Returns:
            QuerySet: Blocked IPs needing firewall sync
        """
        return cls.objects.filter(is_blocked=True, firewall_synced=False)
