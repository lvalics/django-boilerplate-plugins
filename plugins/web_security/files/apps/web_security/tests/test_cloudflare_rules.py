"""Cloudflare ruleset handling: IP parsing (IPv4 + IPv6) and the webhook skip rule."""

from unittest import mock

from django.test import SimpleTestCase, override_settings

from apps.web_security.services.firewall import CloudflareFirewallService

SKIP_DESC = CloudflareFirewallService.SKIP_RULE_DESCRIPTION
BLOCK_DESC = CloudflareFirewallService.CONSOLIDATED_RULE_DESCRIPTION


class _FakeConfig:
    def __init__(self, credentials):
        self.credentials = credentials


def _cf():
    return CloudflareFirewallService(_FakeConfig({"api_token": "t", "zone_id": "z", "ruleset_id": "r"}))


def _block_rule(expression):
    return {"id": "b1", "action": "block", "description": f"{BLOCK_DESC} (2 IPs)", "expression": expression}


class ExtractIpsTests(SimpleTestCase):
    def test_ipv6_addresses_survive_extraction(self):
        ips = _cf()._extract_ips_from_expression("ip.src in { 1.2.3.4 2001:41d0:20a:900::2b4 }")
        self.assertEqual(ips, {"1.2.3.4", "2001:41d0:20a:900::2b4"})

    def test_single_ip_eq_form_is_read(self):
        self.assertEqual(_cf()._extract_ips_from_expression("(ip.src eq 5.6.7.8)"), {"5.6.7.8"})

    def test_sync_keeps_existing_ipv6_in_rebuilt_expression(self):
        svc = _cf()
        rules = [_block_rule("ip.src in { 1.2.3.4 2001:41d0:20a:900::2b4 }")]
        with (
            mock.patch.object(svc, "_get_ruleset", return_value={"rules": rules}),
            mock.patch.object(svc, "_update_ruleset", return_value=True) as update,
        ):
            result = svc.sync_blocks(["9.9.9.9"])
        self.assertEqual(result["added"], 1)
        expression = update.call_args.args[0][0]["expression"]
        self.assertEqual(expression, "ip.src in { 1.2.3.4 2001:41d0:20a:900::2b4 9.9.9.9 }")


@override_settings(WEB_SECURITY_CLOUDFLARE_SKIP_PATHS=["/newsletter/webhook/ses/"])
class SkipRuleTests(SimpleTestCase):
    def test_skip_rule_is_put_first_and_replaces_old_version(self):
        old_skip = {"id": "s0", "action": "skip", "description": SKIP_DESC, "expression": "(old)"}
        rules = _cf()._with_skip_rule([_block_rule("(ip.src eq 1.2.3.4)"), old_skip])
        self.assertEqual([r["description"] for r in rules], [SKIP_DESC, f"{BLOCK_DESC} (2 IPs)"])
        self.assertEqual(rules[0]["expression"], '(starts_with(http.request.uri.path, "/newsletter/webhook/ses/"))')
        self.assertIn("bic", rules[0]["action_parameters"]["products"])

    @override_settings(WEB_SECURITY_CLOUDFLARE_SKIP_PATHS=["/ok/", '/bad") or (true'])
    def test_paths_that_could_break_the_expression_are_dropped(self):
        expression = _cf()._skip_rule()["expression"]
        self.assertEqual(expression, '(starts_with(http.request.uri.path, "/ok/"))')

    @override_settings(WEB_SECURITY_CLOUDFLARE_SKIP_PATHS=[])
    def test_without_paths_the_skip_rule_is_removed(self):
        rules = _cf()._with_skip_rule([{"description": SKIP_DESC}, _block_rule("(ip.src eq 1.2.3.4)")])
        self.assertEqual([r["description"] for r in rules], [f"{BLOCK_DESC} (2 IPs)"])

    def test_ensure_skip_rule_adds_missing_rule(self):
        svc = _cf()
        with (
            mock.patch.object(svc, "_get_ruleset", return_value={"rules": [_block_rule("(ip.src eq 1.2.3.4)")]}),
            mock.patch.object(svc, "_update_ruleset", return_value=True) as update,
        ):
            self.assertTrue(svc.ensure_skip_rule())
        update.assert_called_once()

    def test_ensure_skip_rule_does_nothing_when_in_place(self):
        svc = _cf()
        rules = [svc._skip_rule(), _block_rule("(ip.src eq 1.2.3.4)")]
        with (
            mock.patch.object(svc, "_get_ruleset", return_value={"rules": rules}),
            mock.patch.object(svc, "_update_ruleset") as update,
        ):
            self.assertTrue(svc.ensure_skip_rule())
        update.assert_not_called()

    def test_update_ruleset_sends_skip_rule_first(self):
        svc = _cf()
        with mock.patch("apps.web_security.services.firewall.cloudflare.requests") as requests:
            requests.put.return_value.ok = True
            requests.put.return_value.json.return_value = {"success": True}
            self.assertTrue(svc._update_ruleset([_block_rule("(ip.src eq 1.2.3.4)")]))
        sent = requests.put.call_args.kwargs["json"]["rules"]
        self.assertEqual(sent[0]["description"], SKIP_DESC)
