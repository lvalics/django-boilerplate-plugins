import abc
import logging
import re
import subprocess
import time

import requests

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


class CloudflareFirewallService(BaseFirewallService):
    """
    Cloudflare firewall integration service using WAF Custom Rules.

    Uses a consolidated rule approach where all blocked IPs are stored
    in a single WAF rule with an expression like:
    ip.src in { IP1 IP2 IP3 ... }

    This is more efficient than individual Access Rules and avoids
    hitting Cloudflare's rule limits.

    Note: WAF expressions have a ~4KB limit (~300-500 IPs with this syntax).
    For larger blocklists, consider using Cloudflare IP Lists API which
    supports up to 10,000 IPs per list.

    TODO: Implement Cloudflare IP Lists for large-scale blocking (10K+ IPs)
    See: https://developers.cloudflare.com/waf/tools/lists/custom-lists/
    """

    BASE_URL = "https://api.cloudflare.com/client/v4"
    CONSOLIDATED_RULE_DESCRIPTION = "Consolidated auto-block rule"
    MAX_RETRIES = 3  # Retry attempts for handling race conditions

    def __init__(self, config: FirewallConfig):
        super().__init__(config)
        self.api_token = self.credentials.get("api_token", "")
        self.zone_id = self.credentials.get("zone_id", "")
        self.ruleset_id = self.credentials.get("ruleset_id", "")

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    def _get_ruleset(self) -> dict | None:
        """Get the WAF ruleset."""
        try:
            url = f"{self.BASE_URL}/zones/{self.zone_id}/rulesets/{self.ruleset_id}"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                return result.get("result", {})
            return None
        except Exception as e:
            logger.error(f"Error getting Cloudflare ruleset: {e}")
            return None

    def _get_consolidated_rule(self) -> tuple[dict | None, list]:
        """
        Get the consolidated block rule and all rules.

        Returns:
            Tuple of (consolidated_rule or None, all_rules list)
        """
        ruleset = self._get_ruleset()
        if not ruleset:
            return None, []

        rules = ruleset.get("rules", [])
        for rule in rules:
            if self.CONSOLIDATED_RULE_DESCRIPTION in rule.get("description", ""):
                return rule, rules

        return None, rules

    def _extract_ips_from_expression(self, expression: str) -> set:
        """Extract IP addresses from WAF rule expression (ip.src in { } format)."""
        import re

        ips = set()
        in_match = re.search(r"ip\.src in \{([^}]+)\}", expression)
        if in_match:
            ip_list = in_match.group(1)
            ips.update(re.findall(r"[\d\.]+", ip_list))
        return ips

    def _build_expression(self, ip_addresses: set) -> str:
        """Build a WAF expression for multiple IPs using 'ip.src in { }' syntax."""
        if not ip_addresses:
            return ""
        sorted_ips = sorted(ip_addresses)
        return f"ip.src in {{ {' '.join(sorted_ips)} }}"

    def _update_ruleset(self, rules: list) -> bool:
        """Update the entire ruleset with new rules."""
        try:
            url = f"{self.BASE_URL}/zones/{self.zone_id}/rulesets/{self.ruleset_id}"
            data = {"rules": rules}
            response = requests.put(url, headers=self._get_headers(), json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result.get("success", False)
        except Exception as e:
            logger.error(f"Error updating Cloudflare ruleset: {e}")
            return False

    def block_ip(self, ip_address: str, reason: str = "") -> bool:
        """
        Block an IP using Cloudflare WAF consolidated rule.

        Uses retry logic with exponential backoff to handle race conditions
        when multiple workers attempt to update the ruleset simultaneously.
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                # Get fresh rules on each attempt to avoid stale data
                consolidated_rule, rules = self._get_consolidated_rule()

                if consolidated_rule:
                    # Check if IP already blocked
                    existing_ips = self._extract_ips_from_expression(consolidated_rule.get("expression", ""))
                    if ip_address in existing_ips:
                        logger.info(f"IP {ip_address} already blocked in Cloudflare")
                        return True

                    # Add IP to existing rule
                    existing_ips.add(ip_address)
                    new_expression = self._build_expression(existing_ips)

                    # Update the rule in the rules list
                    for rule in rules:
                        if rule.get("id") == consolidated_rule["id"]:
                            rule["expression"] = new_expression
                            rule["description"] = f"{self.CONSOLIDATED_RULE_DESCRIPTION} ({len(existing_ips)} IPs)"
                            break
                else:
                    # Create new consolidated rule
                    new_rule = {
                        "action": "block",
                        "description": f"{self.CONSOLIDATED_RULE_DESCRIPTION} (1 IP)",
                        "enabled": True,
                        "expression": f"(ip.src eq {ip_address})",
                    }
                    rules = [new_rule] + rules

                if self._update_ruleset(rules):
                    logger.info(f"Blocked IP {ip_address} on Cloudflare WAF")
                    return True

                # Update failed, retry with backoff
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2**attempt  # 1s, 2s, 4s
                    logger.warning(
                        f"Failed to block {ip_address} (attempt {attempt + 1}/{self.MAX_RETRIES}), "
                        f"retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue

                return False

            except Exception as e:
                logger.error(f"Error blocking IP {ip_address} on Cloudflare: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    wait_time = 2**attempt
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                return False

        return False

    def unblock_ip(self, ip_address: str) -> bool:
        """Remove an IP from the Cloudflare WAF consolidated rule."""
        try:
            consolidated_rule, rules = self._get_consolidated_rule()

            if not consolidated_rule:
                logger.warning("No consolidated rule found on Cloudflare")
                return False

            existing_ips = self._extract_ips_from_expression(consolidated_rule.get("expression", ""))

            if ip_address not in existing_ips:
                logger.info(f"IP {ip_address} not in Cloudflare block list")
                return True

            existing_ips.discard(ip_address)

            if not existing_ips:
                # Remove the rule entirely if no IPs left
                rules = [r for r in rules if r.get("id") != consolidated_rule["id"]]
            else:
                # Update the rule with remaining IPs
                new_expression = self._build_expression(existing_ips)
                for rule in rules:
                    if rule.get("id") == consolidated_rule["id"]:
                        rule["expression"] = new_expression
                        rule["description"] = f"{self.CONSOLIDATED_RULE_DESCRIPTION} ({len(existing_ips)} IPs)"
                        break

            if self._update_ruleset(rules):
                logger.info(f"Unblocked IP {ip_address} on Cloudflare WAF")
                return True

            return False
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address} on Cloudflare: {e}")
            return False

    def get_blocked_ips(self) -> list:
        """Get list of blocked IPs from the Cloudflare WAF consolidated rule."""
        try:
            consolidated_rule, _ = self._get_consolidated_rule()
            if consolidated_rule:
                return list(self._extract_ips_from_expression(consolidated_rule.get("expression", "")))
            return []
        except Exception as e:
            logger.error(f"Error getting blocked IPs from Cloudflare: {e}")
            return []

    def sync_blocks(self, ip_addresses: list) -> dict:
        """
        Sync blocked IPs to Cloudflare WAF consolidated rule.

        This is more efficient than individual block_ip calls as it
        updates the rule once with all IPs.
        """
        results = {"added": 0, "failed": 0, "already_blocked": 0}

        if not ip_addresses:
            return results

        try:
            consolidated_rule, rules = self._get_consolidated_rule()

            if consolidated_rule:
                existing_ips = self._extract_ips_from_expression(consolidated_rule.get("expression", ""))
            else:
                existing_ips = set()

            new_ips = set(ip_addresses) - existing_ips
            results["already_blocked"] = len(set(ip_addresses) & existing_ips)

            if not new_ips:
                logger.info("All IPs already blocked in Cloudflare")
                return results

            # Combine existing and new IPs
            all_ips = existing_ips | new_ips
            new_expression = self._build_expression(all_ips)

            if consolidated_rule:
                # Update existing rule
                for rule in rules:
                    if rule.get("id") == consolidated_rule["id"]:
                        rule["expression"] = new_expression
                        rule["description"] = f"{self.CONSOLIDATED_RULE_DESCRIPTION} ({len(all_ips)} IPs)"
                        break
            else:
                # Create new consolidated rule
                new_rule = {
                    "action": "block",
                    "description": f"{self.CONSOLIDATED_RULE_DESCRIPTION} ({len(all_ips)} IPs)",
                    "enabled": True,
                    "expression": new_expression,
                }
                rules = [new_rule] + rules

            if self._update_ruleset(rules):
                results["added"] = len(new_ips)
                logger.info(f"Synced {len(new_ips)} new IPs to Cloudflare WAF (total: {len(all_ips)} IPs)")
            else:
                results["failed"] = len(new_ips)

            return results

        except Exception as e:
            logger.error(f"Error syncing blocks to Cloudflare: {e}")
            results["failed"] = len(ip_addresses)
            return results


class AWSWAFFirewallService(BaseFirewallService):
    """AWS WAF firewall integration service."""

    def __init__(self, config: FirewallConfig):
        super().__init__(config)
        self.access_key = self.credentials.get("access_key", "")
        self.secret_key = self.credentials.get("secret_key", "")
        self.region = self.credentials.get("region", "us-east-1")
        self.web_acl_arn = self.credentials.get("web_acl_arn", "")
        self.ip_set_arn = self.credentials.get("ip_set_arn", "")
        self._client = None

    def _get_client(self):
        """Get boto3 WAFv2 client."""
        if self._client is None:
            try:
                import boto3

                self._client = boto3.client(
                    "wafv2",
                    aws_access_key_id=self.access_key,
                    aws_secret_access_key=self.secret_key,
                    region_name=self.region,
                )
            except ImportError:
                logger.error("boto3 not installed. Install with: pip install boto3")
                raise
        return self._client

    def _get_ip_set(self):
        """Get IP set details."""
        client = self._get_client()
        # Extract name and scope from ARN
        arn_parts = self.ip_set_arn.split("/")
        name = arn_parts[-1] if arn_parts else ""
        scope = "REGIONAL" if "regional" in self.ip_set_arn else "CLOUDFRONT"

        response = client.get_ip_set(Name=name, Scope=scope, Id=self.ip_set_arn.split("/")[-2])
        return response["IPSet"], response["LockToken"]

    def block_ip(self, ip_address: str, reason: str = "") -> bool:
        """Add IP to AWS WAF IP set."""
        try:
            client = self._get_client()
            ip_set, lock_token = self._get_ip_set()

            addresses = set(ip_set.get("Addresses", []))
            cidr = f"{ip_address}/32"

            if cidr in addresses:
                return True  # Already blocked

            addresses.add(cidr)

            arn_parts = self.ip_set_arn.split("/")
            name = arn_parts[-1]
            scope = "REGIONAL" if "regional" in self.ip_set_arn else "CLOUDFRONT"

            client.update_ip_set(
                Name=name,
                Scope=scope,
                Id=arn_parts[-2],
                Addresses=list(addresses),
                LockToken=lock_token,
            )
            logger.info(f"Blocked IP {ip_address} on AWS WAF")
            return True
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address} on AWS WAF: {e}")
            return False

    def unblock_ip(self, ip_address: str) -> bool:
        """Remove IP from AWS WAF IP set."""
        try:
            client = self._get_client()
            ip_set, lock_token = self._get_ip_set()

            addresses = set(ip_set.get("Addresses", []))
            cidr = f"{ip_address}/32"

            if cidr not in addresses:
                return True  # Already not blocked

            addresses.discard(cidr)

            arn_parts = self.ip_set_arn.split("/")
            name = arn_parts[-1]
            scope = "REGIONAL" if "regional" in self.ip_set_arn else "CLOUDFRONT"

            client.update_ip_set(
                Name=name,
                Scope=scope,
                Id=arn_parts[-2],
                Addresses=list(addresses),
                LockToken=lock_token,
            )
            logger.info(f"Unblocked IP {ip_address} on AWS WAF")
            return True
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address} on AWS WAF: {e}")
            return False

    def get_blocked_ips(self) -> list:
        """Get blocked IPs from AWS WAF IP set."""
        try:
            ip_set, _ = self._get_ip_set()
            # Remove /32 suffix from CIDRs
            return [addr.replace("/32", "") for addr in ip_set.get("Addresses", [])]
        except Exception as e:
            logger.error(f"Error getting blocked IPs from AWS WAF: {e}")
            return []

    def sync_blocks(self, ip_addresses: list) -> dict:
        """Sync blocked IPs to AWS WAF."""
        results = {"added": 0, "failed": 0, "already_blocked": 0}

        try:
            client = self._get_client()
            ip_set, lock_token = self._get_ip_set()
            existing = set(ip_set.get("Addresses", []))

            new_addresses = set(existing)
            for ip in ip_addresses:
                cidr = f"{ip}/32"
                if cidr in existing:
                    results["already_blocked"] += 1
                else:
                    new_addresses.add(cidr)
                    results["added"] += 1

            if results["added"] > 0:
                arn_parts = self.ip_set_arn.split("/")
                name = arn_parts[-1]
                scope = "REGIONAL" if "regional" in self.ip_set_arn else "CLOUDFRONT"

                client.update_ip_set(
                    Name=name,
                    Scope=scope,
                    Id=arn_parts[-2],
                    Addresses=list(new_addresses),
                    LockToken=lock_token,
                )
        except Exception as e:
            logger.error(f"Error syncing blocks to AWS WAF: {e}")
            results["failed"] = len(ip_addresses)

        return results


class NginxFirewallService(BaseFirewallService):
    """Nginx firewall integration service."""

    def __init__(self, config: FirewallConfig):
        super().__init__(config)
        self.config_path = self.credentials.get("config_path", "/etc/nginx/conf.d/blocklist.conf")
        self.reload_command = self.credentials.get("reload_command", "nginx -s reload")

    def _read_blocked_ips(self) -> set:
        """Read blocked IPs from nginx config file."""
        try:
            with open(self.config_path) as f:
                content = f.read()
            # Parse deny directives
            ips = set()
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("deny ") and line.endswith(";"):
                    ip = line[5:-1].strip()
                    ips.add(ip)
            return ips
        except FileNotFoundError:
            return set()
        except Exception as e:
            logger.error(f"Error reading nginx blocklist: {e}")
            return set()

    def _write_blocked_ips(self, ips: set) -> bool:
        """Write blocked IPs to nginx config file."""
        try:
            content = "# Auto-generated by web_security plugin\n"
            content += "# Do not edit manually\n\n"
            for ip in sorted(ips):
                content += f"deny {ip};\n"

            with open(self.config_path, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing nginx blocklist: {e}")
            return False

    def _reload_nginx(self) -> bool:
        """Reload nginx to apply changes."""
        try:
            result = subprocess.run(
                self.reload_command.split(),
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                logger.info("Nginx reloaded successfully")
                return True
            logger.error(f"Nginx reload failed: {result.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error reloading nginx: {e}")
            return False

    def block_ip(self, ip_address: str, reason: str = "") -> bool:
        """Add IP to nginx blocklist."""
        ips = self._read_blocked_ips()
        if ip_address in ips:
            return True  # Already blocked

        ips.add(ip_address)
        if self._write_blocked_ips(ips):
            logger.info(f"Blocked IP {ip_address} on Nginx")
            return self._reload_nginx()
        return False

    def unblock_ip(self, ip_address: str) -> bool:
        """Remove IP from nginx blocklist."""
        ips = self._read_blocked_ips()
        if ip_address not in ips:
            return True  # Already not blocked

        ips.discard(ip_address)
        if self._write_blocked_ips(ips):
            logger.info(f"Unblocked IP {ip_address} on Nginx")
            return self._reload_nginx()
        return False

    def get_blocked_ips(self) -> list:
        """Get blocked IPs from nginx config."""
        return list(self._read_blocked_ips())

    def sync_blocks(self, ip_addresses: list) -> dict:
        """Sync blocked IPs to nginx config."""
        results = {"added": 0, "failed": 0, "already_blocked": 0}
        existing = self._read_blocked_ips()

        new_ips = set(existing)
        for ip in ip_addresses:
            if ip in existing:
                results["already_blocked"] += 1
            else:
                new_ips.add(ip)
                results["added"] += 1

        if results["added"] > 0:
            if self._write_blocked_ips(new_ips) and self._reload_nginx():
                pass  # Success
            else:
                results["failed"] = results["added"]
                results["added"] = 0

        return results


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
