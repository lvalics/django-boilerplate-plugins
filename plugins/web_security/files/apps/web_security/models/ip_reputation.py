from django.core.cache import cache
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class IPReputationConfig(BaseModel):
    """
    Configuration for IP reputation services.

    Supports multiple reputation providers like AbuseIPDB.
    """

    class Provider(models.TextChoices):
        ABUSEIPDB = "abuseipdb", _("AbuseIPDB")
        IPQUALITYSCORE = "ipqualityscore", _("IPQualityScore")
        CUSTOM = "custom", _("Custom API")

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Descriptive name for this configuration"),
    )
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        default=Provider.ABUSEIPDB,
        verbose_name=_("Provider"),
        help_text=_("IP reputation service provider"),
    )
    api_key = models.CharField(
        max_length=255,
        verbose_name=_("API Key"),
        help_text=_("API key for the reputation service"),
    )
    api_url = models.URLField(
        blank=True,
        default="",
        verbose_name=_("API URL"),
        help_text=_("Custom API URL (only for custom provider)"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this configuration is active"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default"),
        help_text=_("Use this as the default reputation service"),
    )
    cache_duration_hours = models.PositiveIntegerField(
        default=24,
        verbose_name=_("Cache Duration (hours)"),
        help_text=_("How long to cache reputation results"),
    )
    min_confidence_score = models.PositiveIntegerField(
        default=75,
        verbose_name=_("Min Confidence Score"),
        help_text=_("Minimum abuse confidence score to consider IP as bad (0-100)"),
    )

    CACHE_KEY_PREFIX = "web_security:ip_reputation_config:"
    CACHE_TIMEOUT = 300

    class Meta:
        verbose_name = _("IP Reputation Configuration")
        verbose_name_plural = _("IP Reputation Configurations")
        ordering = ["-is_default", "name"]

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        default = " (default)" if self.is_default else ""
        return f"{self.name} - {self.get_provider_display()} ({status}){default}"

    def save(self, *args, **kwargs):
        """Ensure only one default configuration exists."""
        if self.is_default:
            IPReputationConfig.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
        cache.delete(f"{self.CACHE_KEY_PREFIX}default")

    @classmethod
    def get_default(cls):
        """
        Get the default active reputation configuration.

        Returns:
            IPReputationConfig or None: The default active config
        """
        cache_key = f"{cls.CACHE_KEY_PREFIX}default"
        config = cache.get(cache_key)
        if config is None:
            config = cls.objects.filter(is_active=True, is_default=True).first()
            if config:
                cache.set(cache_key, config, cls.CACHE_TIMEOUT)
        return config


class IPReputationCache(BaseModel):
    """
    Cached IP reputation data.

    Stores reputation lookup results to avoid repeated API calls.
    """

    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name=_("IP Address"),
        help_text=_("IP address that was checked"),
    )
    abuse_confidence_score = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Abuse Confidence Score"),
        help_text=_("Confidence score that IP is abusive (0-100)"),
    )
    is_tor_node = models.BooleanField(
        default=False,
        verbose_name=_("Tor Exit Node"),
        help_text=_("Whether IP is a known Tor exit node"),
    )
    is_vpn = models.BooleanField(
        default=False,
        verbose_name=_("VPN/Proxy"),
        help_text=_("Whether IP is a known VPN or proxy"),
    )
    is_datacenter = models.BooleanField(
        default=False,
        verbose_name=_("Datacenter"),
        help_text=_("Whether IP belongs to a datacenter"),
    )
    country_code = models.CharField(
        max_length=2,
        blank=True,
        default="",
        verbose_name=_("Country Code"),
        help_text=_("Two-letter country code"),
    )
    isp = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("ISP"),
        help_text=_("Internet Service Provider"),
    )
    domain = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Domain"),
        help_text=_("Domain associated with IP"),
    )
    total_reports = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Reports"),
        help_text=_("Number of abuse reports for this IP"),
    )
    last_reported_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Reported"),
        help_text=_("When IP was last reported for abuse"),
    )
    raw_response = models.JSONField(
        default=dict,
        verbose_name=_("Raw Response"),
        help_text=_("Full API response data"),
    )
    expires_at = models.DateTimeField(
        verbose_name=_("Expires At"),
        help_text=_("When this cache entry expires"),
    )
    check_pending = models.BooleanField(
        default=False,
        verbose_name=_("Check Pending"),
        help_text=_("Whether a reputation check is queued"),
    )

    class Meta:
        verbose_name = _("IP Reputation Cache")
        verbose_name_plural = _("IP Reputation Cache")
        ordering = ["-abuse_confidence_score", "-created_at"]
        indexes = [
            models.Index(fields=["ip_address"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["check_pending"]),
        ]

    def __str__(self):
        return f"{self.ip_address} (score: {self.abuse_confidence_score})"

    @property
    def is_expired(self):
        """Check if cache entry has expired."""
        return timezone.now() > self.expires_at

    @property
    def is_suspicious(self):
        """Check if IP should be considered suspicious based on cached data."""
        config = IPReputationConfig.get_default()
        min_score = config.min_confidence_score if config else 75
        return self.abuse_confidence_score >= min_score

    def calculate_threat_score(self):
        """
        Calculate threat score contribution from reputation data.

        Returns:
            int: Threat score to add
        """
        score = 0
        if self.abuse_confidence_score >= 75:
            score += 20
        elif self.abuse_confidence_score >= 50:
            score += 10
        if self.is_tor_node:
            score += 15
        if self.is_vpn:
            score += 10
        return score

    @classmethod
    def get_or_queue(cls, ip_address):
        """
        Get cached reputation or queue for checking.

        Args:
            ip_address: IP address to look up

        Returns:
            tuple: (IPReputationCache or None, needs_check bool)
        """
        try:
            entry = cls.objects.get(ip_address=ip_address)
            if entry.is_expired:
                # Mark for re-check
                entry.check_pending = True
                entry.save(update_fields=["check_pending", "updated_at"])
                return entry, True
            return entry, False
        except cls.DoesNotExist:
            # Create placeholder and queue for check
            config = IPReputationConfig.get_default()
            if config:
                expires_at = timezone.now() + timezone.timedelta(hours=config.cache_duration_hours)
            else:
                expires_at = timezone.now() + timezone.timedelta(hours=24)

            entry = cls.objects.create(
                ip_address=ip_address,
                expires_at=expires_at,
                check_pending=True,
            )
            return entry, True

    @classmethod
    def cleanup_expired(cls):
        """
        Delete expired cache entries.

        Returns:
            int: Number of deleted entries
        """
        deleted, _ = cls.objects.filter(expires_at__lt=timezone.now()).delete()
        return deleted
