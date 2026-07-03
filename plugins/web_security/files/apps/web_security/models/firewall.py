from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel
from apps.web_security.encryption import decrypt_data, encrypt_data, mask_credentials


class FirewallConfig(BaseModel):
    """
    Configuration for firewall integrations.

    Supports multiple firewall providers: Cloudflare, AWS WAF, Nginx, iptables.
    Each provider has different credential requirements stored encrypted at rest.

    Credentials are encrypted using Fernet with key derived from SECRET_KEY.
    Access via the `credentials` property for transparent decrypt/encrypt.
    """

    class Provider(models.TextChoices):
        CLOUDFLARE = "cloudflare", _("Cloudflare")
        AWS_WAF = "aws_waf", _("AWS WAF")
        NGINX = "nginx", _("Nginx")
        IPTABLES = "iptables", _("iptables")

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Descriptive name for this firewall configuration"),
    )
    provider = models.CharField(
        max_length=20,
        choices=Provider.choices,
        verbose_name=_("Provider"),
        help_text=_("Firewall provider type"),
    )
    # Store encrypted credentials as text (not JSONField)
    _credentials = models.TextField(
        default="",
        blank=True,
        db_column="credentials",
        verbose_name=_("Credentials"),
        help_text=_("Provider-specific credentials (encrypted at rest)"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Whether this firewall config is active"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default"),
        help_text=_("Use this firewall for automatic blocking"),
    )

    @property
    def credentials(self) -> dict:
        """Decrypt and return credentials."""
        return decrypt_data(self._credentials)

    @credentials.setter
    def credentials(self, value: dict):
        """Encrypt and store credentials."""
        if value:
            self._credentials = encrypt_data(value)
        else:
            self._credentials = ""

    def get_masked_credentials(self) -> dict:
        """Get credentials with sensitive values masked for display."""
        return mask_credentials(self.credentials)

    def __repr__(self):
        """Prevent credential leakage in logs/debug output."""
        return f"<FirewallConfig: {self.name} ({self.provider})>"

    CACHE_KEY_PREFIX = "web_security:firewall:"
    CACHE_TIMEOUT = 300

    class Meta:
        verbose_name = _("Firewall Configuration")
        verbose_name_plural = _("Firewall Configurations")
        ordering = ["-is_default", "name"]

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        default = " (default)" if self.is_default else ""
        return f"{self.name} - {self.get_provider_display()} ({status}){default}"

    def save(self, *args, **kwargs):
        """Ensure only one default firewall exists."""
        if self.is_default:
            # Set all other configs to non-default
            FirewallConfig.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
        # Clear cache
        cache.delete(f"{self.CACHE_KEY_PREFIX}default")

    @classmethod
    def get_default(cls):
        """
        Get the default firewall configuration.

        Returns:
            FirewallConfig or None: The default active firewall config
        """
        cache_key = f"{cls.CACHE_KEY_PREFIX}default"
        config = cache.get(cache_key)
        if config is None:
            config = cls.objects.filter(is_active=True, is_default=True).first()
            if config:
                cache.set(cache_key, config, cls.CACHE_TIMEOUT)
        return config

    @classmethod
    def get_credential_schema(cls, provider):
        """
        Get the JSON schema for credentials based on provider.

        Args:
            provider: The provider type

        Returns:
            dict: JSON schema for the credentials field
        """
        schemas = {
            cls.Provider.CLOUDFLARE: {
                "type": "object",
                "properties": {
                    "api_token": {
                        "type": "string",
                        "title": "API Token",
                        "description": "Cloudflare API token with firewall permissions",
                    },
                    "zone_id": {
                        "type": "string",
                        "title": "Zone ID",
                        "description": "Cloudflare Zone ID",
                    },
                    "ruleset_id": {
                        "type": "string",
                        "title": "Ruleset ID",
                        "description": "WAF ruleset ID for custom rules",
                    },
                },
                "required": ["api_token", "zone_id"],
            },
            cls.Provider.AWS_WAF: {
                "type": "object",
                "properties": {
                    "access_key": {
                        "type": "string",
                        "title": "Access Key",
                        "description": "AWS Access Key ID",
                    },
                    "secret_key": {
                        "type": "string",
                        "title": "Secret Key",
                        "description": "AWS Secret Access Key",
                    },
                    "region": {
                        "type": "string",
                        "title": "Region",
                        "description": "AWS Region (e.g., us-east-1)",
                    },
                    "web_acl_arn": {
                        "type": "string",
                        "title": "Web ACL ARN",
                        "description": "ARN of the Web ACL",
                    },
                    "ip_set_arn": {
                        "type": "string",
                        "title": "IP Set ARN",
                        "description": "ARN of the IP Set for blocking",
                    },
                },
                "required": ["access_key", "secret_key", "region", "web_acl_arn"],
            },
            cls.Provider.NGINX: {
                "type": "object",
                "properties": {
                    "config_path": {
                        "type": "string",
                        "title": "Config Path",
                        "description": "Path to nginx blocklist include file",
                        "default": "/etc/nginx/conf.d/blocklist.conf",
                    },
                    "reload_command": {
                        "type": "string",
                        "title": "Reload Command",
                        "description": "Command to reload nginx",
                        "default": "nginx -s reload",
                    },
                },
                "required": ["config_path"],
            },
            cls.Provider.IPTABLES: {
                "type": "object",
                "properties": {
                    "chain": {
                        "type": "string",
                        "title": "Chain",
                        "description": "iptables chain name",
                        "default": "INPUT",
                    },
                    "protocol": {
                        "type": "string",
                        "title": "Protocol",
                        "description": "Protocol to block",
                        "default": "tcp",
                    },
                    "port": {
                        "type": "integer",
                        "title": "Port",
                        "description": "Port to block (default: all)",
                    },
                },
                "required": [],
            },
        }
        return schemas.get(provider, {"type": "object", "properties": {}})
