import subprocess

from apps.web_security.models import FirewallConfig
from apps.web_security.utils import validate_ip

from .base import VALID_CHAIN_PATTERN, VALID_PROTOCOLS, BaseFirewallService, logger


class IptablesFirewallService(BaseFirewallService):
    """iptables firewall integration service."""

    def __init__(self, config: FirewallConfig):
        super().__init__(config)

        # Validate and set chain name (prevent injection via config)
        chain = self.credentials.get("chain", "INPUT")
        if not VALID_CHAIN_PATTERN.match(chain):
            raise ValueError(f"Invalid iptables chain name: {chain}")
        self.chain = chain

        # Validate protocol
        protocol = self.credentials.get("protocol", "tcp").lower()
        if protocol not in VALID_PROTOCOLS:
            raise ValueError(f"Invalid protocol: {protocol}")
        self.protocol = protocol

        # Validate port (must be integer 1-65535 or None)
        port = self.credentials.get("port")
        if port is not None:
            try:
                port = int(port)
                if not 1 <= port <= 65535:
                    raise ValueError(f"Port out of range: {port}")
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid port: {port}") from e
        self.port = port

    def _run_iptables(self, args: list) -> tuple[bool, str]:
        """Run iptables command."""
        try:
            cmd = ["iptables"] + args
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stderr
        except Exception as e:
            return False, str(e)

    def block_ip(self, ip_address: str, reason: str = "") -> bool:
        """Add iptables DROP rule for IP."""
        # Validate IP address to prevent command injection
        validated_ip = validate_ip(ip_address)
        if not validated_ip:
            logger.error(f"Invalid IP address rejected: {ip_address[:50]}")
            return False

        args = ["-A", self.chain, "-s", validated_ip, "-j", "DROP"]
        if self.port:
            args = ["-A", self.chain, "-s", validated_ip, "-p", self.protocol, "--dport", str(self.port), "-j", "DROP"]

        success, error = self._run_iptables(args)
        if success:
            logger.info(f"Blocked IP {validated_ip} with iptables")
        else:
            logger.error(f"Failed to block IP {validated_ip} with iptables: {error}")
        return success

    def unblock_ip(self, ip_address: str) -> bool:
        """Remove iptables DROP rule for IP."""
        # Validate IP address to prevent command injection
        validated_ip = validate_ip(ip_address)
        if not validated_ip:
            logger.error(f"Invalid IP address rejected: {ip_address[:50]}")
            return False

        args = ["-D", self.chain, "-s", validated_ip, "-j", "DROP"]
        if self.port:
            args = ["-D", self.chain, "-s", validated_ip, "-p", self.protocol, "--dport", str(self.port), "-j", "DROP"]

        success, error = self._run_iptables(args)
        if success:
            logger.info(f"Unblocked IP {validated_ip} with iptables")
        else:
            logger.error(f"Failed to unblock IP {validated_ip} with iptables: {error}")
        return success

    def get_blocked_ips(self) -> list:
        """Get blocked IPs from iptables."""
        try:
            result = subprocess.run(
                ["iptables", "-L", self.chain, "-n"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return []

            ips = []
            for line in result.stdout.split("\n"):
                if "DROP" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        ips.append(parts[3])  # Source IP
            return ips
        except Exception as e:
            logger.error(f"Error getting blocked IPs from iptables: {e}")
            return []

    def sync_blocks(self, ip_addresses: list) -> dict:
        """Sync blocked IPs to iptables."""
        results = {"added": 0, "failed": 0, "already_blocked": 0}
        existing = set(self.get_blocked_ips())

        for ip in ip_addresses:
            if ip in existing:
                results["already_blocked"] += 1
                continue
            if self.block_ip(ip):
                results["added"] += 1
            else:
                results["failed"] += 1

        return results
