"""Defense-in-depth IP validation tests for the Cloudflare and AWS WAF firewall services.

The Cloudflare service interpolates IPs into a WAF expression string and AWS passes raw
addresses to the API, so a malformed value that reached them could produce a WAF-expression
injection or a malformed rule. These tests assert that invalid IPs are rejected at entry and
never reach the expression builder / API call, while valid IPs still flow through.
"""

from unittest import mock

from django.test import SimpleTestCase

from apps.web_security.services.firewall import AWSWAFFirewallService, CloudflareFirewallService

REQUESTS = "apps.web_security.services.firewall.cloudflare.requests"


class _FakeConfig:
    """Duck-typed stand-in for FirewallConfig (only `.credentials` is read)."""

    def __init__(self, credentials):
        self.credentials = credentials


def _cf(**creds):
    creds.setdefault("api_token", "token")
    creds.setdefault("zone_id", "zone")
    creds.setdefault("ruleset_id", "ruleset")
    return CloudflareFirewallService(_FakeConfig(creds))


def _aws(**creds):
    creds.setdefault("access_key", "ak")
    creds.setdefault("secret_key", "sk")
    creds.setdefault("ip_set_arn", "arn:aws:wafv2:us-east-1:1:regional/ipset/name/the-id")
    return AWSWAFFirewallService(_FakeConfig(creds))


class CloudflareValidationTests(SimpleTestCase):
    def test_block_ip_rejects_waf_injection_and_makes_no_call(self):
        svc = _cf()
        with (
            mock.patch(REQUESTS) as requests,
            mock.patch.object(svc, "_update_ruleset") as update,
        ):
            result = svc.block_ip("1.1.1.1) or (true")
        self.assertFalse(result)
        update.assert_not_called()  # expression never built/sent
        requests.get.assert_not_called()
        requests.put.assert_not_called()

    def test_unblock_ip_rejects_invalid_without_call(self):
        svc = _cf()
        with mock.patch.object(svc, "_get_consolidated_rule") as get_rule:
            result = svc.unblock_ip("bad;value")
        self.assertFalse(result)
        get_rule.assert_not_called()

    def test_sync_blocks_drops_invalid_before_building_expression(self):
        svc = _cf()
        with (
            mock.patch.object(svc, "_get_consolidated_rule", return_value=(None, [])),
            mock.patch.object(svc, "_update_ruleset", return_value=True) as update,
        ):
            results = svc.sync_blocks(["1.2.3.4", "bad;value"])
        update.assert_called_once()
        sent_rules = update.call_args.args[0]
        expression = sent_rules[0]["expression"]
        self.assertIn("1.2.3.4", expression)
        self.assertNotIn("bad;value", expression)
        self.assertEqual(results["added"], 1)

    def test_valid_ip_flows_through(self):
        svc = _cf()
        with (
            mock.patch.object(svc, "_get_consolidated_rule", return_value=(None, [])),
            mock.patch.object(svc, "_update_ruleset", return_value=True) as update,
        ):
            result = svc.block_ip("8.8.8.8")
        self.assertTrue(result)
        update.assert_called_once()
        sent_rules = update.call_args.args[0]
        self.assertIn("8.8.8.8", sent_rules[0]["expression"])


class AWSWafValidationTests(SimpleTestCase):
    def test_block_ip_rejects_invalid_without_client(self):
        svc = _aws()
        with mock.patch.object(svc, "_get_client") as client:
            result = svc.block_ip("bad;value")
        self.assertFalse(result)
        client.assert_not_called()

    def test_sync_blocks_drops_invalid_from_payload(self):
        svc = _aws()
        fake_client = mock.Mock()
        with (
            mock.patch.object(svc, "_get_client", return_value=fake_client),
            mock.patch.object(svc, "_get_ip_set", return_value=({"Addresses": []}, "lock")),
        ):
            results = svc.sync_blocks(["1.2.3.4", "bad;value"])
        addresses = fake_client.update_ip_set.call_args.kwargs["Addresses"]
        self.assertIn("1.2.3.4/32", addresses)
        self.assertNotIn("bad;value/32", addresses)
        self.assertEqual(results["added"], 1)
