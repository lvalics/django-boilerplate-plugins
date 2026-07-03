from apps.web_security.models import FirewallConfig

from .aws import AWSWAFFirewallService
from .base import BaseFirewallService
from .cloudflare import CloudflareFirewallService
from .iptables import IptablesFirewallService
from .nginx import NginxFirewallService


class FirewallServiceFactory:
    """Factory for creating firewall service instances."""

    _services = {
        FirewallConfig.Provider.CLOUDFLARE: CloudflareFirewallService,
        FirewallConfig.Provider.AWS_WAF: AWSWAFFirewallService,
        FirewallConfig.Provider.NGINX: NginxFirewallService,
        FirewallConfig.Provider.IPTABLES: IptablesFirewallService,
    }

    @classmethod
    def create(cls, config: FirewallConfig) -> BaseFirewallService:
        """
        Create a firewall service instance for the given config.

        Args:
            config: FirewallConfig instance

        Returns:
            Firewall service instance

        Raises:
            ValueError: If provider is not supported
        """
        service_class = cls._services.get(config.provider)
        if service_class is None:
            raise ValueError(f"Unsupported firewall provider: {config.provider}")
        return service_class(config)

    @classmethod
    def get_default_service(cls) -> BaseFirewallService | None:
        """
        Get the default firewall service.

        Returns:
            Default firewall service or None if not configured
        """
        config = FirewallConfig.get_default()
        if config is None:
            return None
        return cls.create(config)
