from apps.web_security.models import FirewallConfig

from .base import BaseFirewallService, logger


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
        ip_address = self._validated_ip(ip_address)
        if ip_address is None:
            return False
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
        ip_address = self._validated_ip(ip_address)
        if ip_address is None:
            return False
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
            for ip in self._validated_ips(ip_addresses):
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
