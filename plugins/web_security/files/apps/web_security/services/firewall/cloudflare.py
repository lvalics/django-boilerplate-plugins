import time

import requests

from apps.web_security.models import FirewallConfig

from .base import BaseFirewallService, logger


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
        ip_address = self._validated_ip(ip_address)
        if ip_address is None:
            return False

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
        ip_address = self._validated_ip(ip_address)
        if ip_address is None:
            return False
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

        # Defense in depth: never let a raw/malformed value reach the WAF expression.
        valid_ips = set(self._validated_ips(ip_addresses))
        if not valid_ips:
            return results

        try:
            consolidated_rule, rules = self._get_consolidated_rule()

            if consolidated_rule:
                existing_ips = self._extract_ips_from_expression(consolidated_rule.get("expression", ""))
            else:
                existing_ips = set()

            new_ips = valid_ips - existing_ips
            results["already_blocked"] = len(valid_ips & existing_ips)

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
