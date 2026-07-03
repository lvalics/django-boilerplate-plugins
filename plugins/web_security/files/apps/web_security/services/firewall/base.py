import abc
import logging
import re

from apps.web_security.models import FirewallConfig
from apps.web_security.utils import validate_ip

logger = logging.getLogger(__name__)

# Valid iptables chain name pattern (alphanumeric, underscore, hyphen)
VALID_CHAIN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

# Valid protocols for iptables
VALID_PROTOCOLS = {"tcp", "udp", "icmp", "all"}


class BaseFirewallService(abc.ABC):
    """Abstract base class for firewall services."""

    def __init__(self, config: FirewallConfig):
        self.config = config
        self.credentials = config.credentials

    def _validated_ips(self, ip_addresses):
        """Return only syntactically valid, normalized IPs; log and drop the rest."""
        valid = []
        for ip in ip_addresses:
            v = validate_ip(ip)
            if v is None:
                logger.warning("Skipping invalid IP for %s firewall: %r", type(self).__name__, ip)
            else:
                valid.append(v)
        return valid

    def _validated_ip(self, ip_address):
        """Return a single normalized IP, or None (logging a refusal) if it is invalid."""
        v = validate_ip(ip_address)
        if v is None:
            logger.warning("Refusing invalid IP for %s firewall: %r", type(self).__name__, ip_address)
        return v

    @abc.abstractmethod
    def block_ip(self, ip_address: str, reason: str = "") -> bool:
        """Block an IP address."""
        pass

    @abc.abstractmethod
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock an IP address."""
        pass

    @abc.abstractmethod
    def get_blocked_ips(self) -> list:
        """Get list of blocked IPs."""
        pass

    @abc.abstractmethod
    def sync_blocks(self, ip_addresses: list) -> dict:
        """Sync a list of blocked IPs to the firewall."""
        pass
