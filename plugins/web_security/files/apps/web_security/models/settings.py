from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class SecuritySettings(BaseModel):
    """
    Singleton model for global security settings.

    Controls which security features are enabled/disabled
    and provides global configuration for the security system.
    """

    # Master switch
    security_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Security Enabled"),
        help_text=_("Master switch to enable/disable all security monitoring"),
    )

    # Feature toggles
    threat_detection_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Threat Detection"),
        help_text=_("Enable detection of malicious requests via patterns"),
    )
    rate_limiting_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Rate Limiting"),
        help_text=_("Enable rate limiting for endpoints"),
    )
    ip_blocking_enabled = models.BooleanField(
        default=True,
        verbose_name=_("IP Blocking"),
        help_text=_("Enable automatic IP blocking"),
    )
    ip_reputation_enabled = models.BooleanField(
        default=False,
        verbose_name=_("IP Reputation Checking"),
        help_text=_("Enable IP reputation lookup via external services"),
    )
    auto_block_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Auto-Block"),
        help_text=_("Automatically block IPs that exceed threat threshold"),
    )
    logging_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Request Logging"),
        help_text=_("Log all requests for analysis"),
    )
    security_headers_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Security Headers"),
        help_text=_("Add security headers to responses"),
    )

    # Threat category toggles
    detect_wordpress_scans = models.BooleanField(
        default=True,
        verbose_name=_("WordPress Scans"),
        help_text=_("Detect WordPress-related scanning attempts"),
    )
    detect_php_scans = models.BooleanField(
        default=True,
        verbose_name=_("PHP Scans"),
        help_text=_("Detect PHP file scanning attempts"),
    )
    detect_sensitive_files = models.BooleanField(
        default=True,
        verbose_name=_("Sensitive Files"),
        help_text=_("Detect access attempts to sensitive files (.env, .git, etc.)"),
    )
    detect_admin_panels = models.BooleanField(
        default=True,
        verbose_name=_("Admin Panels"),
        help_text=_("Detect admin panel scanning (phpmyadmin, etc.)"),
    )
    detect_scanners = models.BooleanField(
        default=True,
        verbose_name=_("Vulnerability Scanners"),
        help_text=_("Detect known vulnerability scanner user agents"),
    )
    detect_sql_injection = models.BooleanField(
        default=True,
        verbose_name=_("SQL Injection"),
        help_text=_("Detect SQL injection attempts"),
    )
    detect_path_traversal = models.BooleanField(
        default=True,
        verbose_name=_("Path Traversal"),
        help_text=_("Detect directory traversal attempts"),
    )
    detect_shell_access = models.BooleanField(
        default=True,
        verbose_name=_("Shell/Webshell Access"),
        help_text=_("Detect webshell and shell access attempts"),
    )
    detect_api_abuse = models.BooleanField(
        default=True,
        verbose_name=_("API Abuse"),
        help_text=_("Detect API endpoint abuse"),
    )

    # Thresholds
    auto_block_threshold = models.PositiveIntegerField(
        default=70,
        verbose_name=_("Auto-Block Threshold"),
        help_text=_("Threat score threshold for automatic blocking (0-100)"),
    )
    block_duration_minutes = models.PositiveIntegerField(
        default=1440,
        verbose_name=_("Block Duration (minutes)"),
        help_text=_("How long to block IPs (default: 24 hours)"),
    )

    # Whitelist
    whitelist_ips = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Whitelisted IPs"),
        help_text=_("Comma-separated list of IPs that should never be blocked"),
    )
    # Default paths that commonly need whitelisting
    DEFAULT_WHITELIST_PATHS = "/api/webhook/,/stripe/webhook/,/health/,/healthz/"

    whitelist_paths = models.TextField(
        blank=True,
        default=DEFAULT_WHITELIST_PATHS,
        verbose_name=_("Whitelisted Paths"),
        help_text=_(
            "Comma-separated list of URL path prefixes that bypass security checks. "
            "Default: /api/webhook/, /stripe/webhook/, /health/, /healthz/"
        ),
    )

    # Notifications
    notification_email = models.EmailField(
        blank=True,
        default="",
        verbose_name=_("Notification Email"),
        help_text=_("Email address for security notifications"),
    )
    notify_on_block = models.BooleanField(
        default=False,
        verbose_name=_("Notify on Block"),
        help_text=_("Send email notification when an IP is auto-blocked"),
    )
    notify_on_critical = models.BooleanField(
        default=True,
        verbose_name=_("Notify on Critical"),
        help_text=_("Send email notification for critical threats"),
    )

    CACHE_KEY = "web_security:settings"
    CACHE_KEY_PATHS = "web_security:whitelist_paths"
    CACHE_TIMEOUT = 300  # 5 minutes

    class Meta:
        verbose_name = _("Security Settings")
        verbose_name_plural = _("Security Settings")

    def __str__(self):
        status = "enabled" if self.security_enabled else "disabled"
        return f"Security Settings ({status})"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists and clear cache on save."""
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.CACHE_KEY)
        cache.delete(self.CACHE_KEY_PATHS)

    def delete(self, *args, **kwargs):
        """Prevent deletion of singleton."""
        pass

    @classmethod
    def get_settings(cls):
        """
        Get the singleton settings instance.

        Returns cached instance if available, otherwise fetches from DB
        or creates default settings.
        """
        settings = cache.get(cls.CACHE_KEY)
        if settings is None:
            settings, _ = cls.objects.get_or_create(pk=1)
            cache.set(cls.CACHE_KEY, settings, cls.CACHE_TIMEOUT)
        return settings

    def get_enabled_categories(self):
        """
        Return a list of enabled threat pattern categories.

        Returns:
            list: Category names that are enabled for detection
        """
        categories = []
        category_mapping = {
            "wordpress": self.detect_wordpress_scans,
            "php": self.detect_php_scans,
            "sensitive": self.detect_sensitive_files,
            "admin": self.detect_admin_panels,
            "scanner": self.detect_scanners,
            "injection": self.detect_sql_injection,
            "traversal": self.detect_path_traversal,
            "shell": self.detect_shell_access,
            "api": self.detect_api_abuse,
        }
        for category, enabled in category_mapping.items():
            if enabled:
                categories.append(category)
        return categories

    def get_whitelist_ips(self):
        """
        Parse whitelist_ips field into a set of IP addresses.

        Returns:
            set: Set of whitelisted IP addresses
        """
        if not self.whitelist_ips:
            return set()
        return {ip.strip() for ip in self.whitelist_ips.split(",") if ip.strip()}

    def is_ip_whitelisted(self, ip_address):
        """
        Check if an IP address is whitelisted.

        Args:
            ip_address: IP address to check

        Returns:
            bool: True if IP is whitelisted
        """
        return ip_address in self.get_whitelist_ips()

    def get_whitelist_paths(self):
        """
        Parse whitelist_paths field into a set of path prefixes.

        Results are cached for performance on high-traffic sites.

        Returns:
            set: Set of whitelisted path prefixes
        """
        paths = cache.get(self.CACHE_KEY_PATHS)
        if paths is None:
            if not self.whitelist_paths:
                paths = set()
            else:
                paths = {path.strip() for path in self.whitelist_paths.split(",") if path.strip()}
            cache.set(self.CACHE_KEY_PATHS, paths, self.CACHE_TIMEOUT)
        return paths

    def is_path_whitelisted(self, request_path):
        """
        Check if a request path matches any whitelisted path prefix.

        Args:
            request_path: The request path to check

        Returns:
            bool: True if path starts with any whitelisted prefix
        """
        for path in self.get_whitelist_paths():
            if request_path.startswith(path):
                return True
        return False
