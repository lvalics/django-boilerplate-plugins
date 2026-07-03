"""Regression tests for client-IP spoofing hardening (get_client_ip).

Fix #2: CF-Connecting-IP and X-Real-IP must NOT be trusted by default, even when the
immediate peer is a trusted proxy, because a client can spoof them. They are honored
only when the deployment explicitly opts in.
"""

from django.test import SimpleTestCase, override_settings

from apps.web_security.utils import get_client_ip

TRUSTED = ["10.0.0.0/8"]  # the proxy in front of us


class _FakeRequest:
    def __init__(self, meta):
        self.META = meta


@override_settings(WEB_SECURITY_TRUSTED_PROXIES=TRUSTED)
class ClientIPSpoofingTests(SimpleTestCase):
    def _req(self, **headers):
        meta = {"REMOTE_ADDR": "10.0.0.1"}  # request arrives via the trusted proxy
        meta.update(headers)
        return _FakeRequest(meta)

    def test_x_real_ip_not_trusted_by_default(self):
        # A client sets X-Real-IP hoping to control the derived IP.
        ip = get_client_ip(self._req(HTTP_X_REAL_IP="1.2.3.4"))
        self.assertNotEqual(ip, "1.2.3.4")
        self.assertEqual(ip, "10.0.0.1")  # falls back to the real peer

    def test_cf_connecting_ip_not_trusted_by_default(self):
        ip = get_client_ip(self._req(HTTP_CF_CONNECTING_IP="9.9.9.9"))
        self.assertNotEqual(ip, "9.9.9.9")

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=TRUSTED, WEB_SECURITY_TRUST_X_REAL_IP=True)
    def test_x_real_ip_trusted_when_opted_in(self):
        ip = get_client_ip(self._req(HTTP_X_REAL_IP="1.2.3.4"))
        self.assertEqual(ip, "1.2.3.4")

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=TRUSTED, WEB_SECURITY_BEHIND_CLOUDFLARE=True)
    def test_cf_connecting_ip_trusted_when_opted_in(self):
        ip = get_client_ip(self._req(HTTP_CF_CONNECTING_IP="9.9.9.9"))
        self.assertEqual(ip, "9.9.9.9")

    def test_xff_walk_still_used_for_real_client(self):
        # X-Forwarded-For remains the trusted mechanism: rightmost non-proxy is the client.
        ip = get_client_ip(self._req(HTTP_X_FORWARDED_FOR="203.0.113.7, 10.0.0.1"))
        self.assertEqual(ip, "203.0.113.7")

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=[])
    def test_no_trusted_proxies_uses_remote_addr_only(self):
        ip = get_client_ip(self._req(HTTP_X_REAL_IP="1.2.3.4", HTTP_X_FORWARDED_FOR="1.2.3.4"))
        self.assertEqual(ip, "10.0.0.1")
