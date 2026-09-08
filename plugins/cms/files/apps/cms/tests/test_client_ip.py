"""Tests for get_client_ip's web_security delegation behind Cloudflare/kamal-proxy."""

import sys
from unittest import mock

from django.test import RequestFactory, SimpleTestCase, override_settings

from apps.cms.rate_limiter import get_client_ip


class ClientIpBehindProxyTests(SimpleTestCase):
    """On live, requests arrive through Cloudflare and kamal-proxy: the real IP is in
    CF-Connecting-IP, not REMOTE_ADDR."""

    def _request(self, **meta):
        return RequestFactory().post("/api/zone/1/submit-form/", **meta)

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=["172.16.0.0/12"], WEB_SECURITY_BEHIND_CLOUDFLARE=True)
    def test_uses_cloudflare_header_when_peer_is_trusted_proxy(self):
        request = self._request(
            REMOTE_ADDR="172.18.0.2",
            HTTP_CF_CONNECTING_IP="86.123.136.22",
            HTTP_X_FORWARDED_FOR="86.123.136.22",
        )
        self.assertEqual(get_client_ip(request), "86.123.136.22")

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=["172.16.0.0/12"], WEB_SECURITY_BEHIND_CLOUDFLARE=True)
    def test_header_from_untrusted_peer_is_ignored(self):
        request = self._request(REMOTE_ADDR="8.8.8.8", HTTP_CF_CONNECTING_IP="1.2.3.4")
        self.assertEqual(get_client_ip(request), "8.8.8.8")

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=[], SITES_TRUSTED_PROXY_COUNT=0)
    def test_without_configuration_falls_back_to_remote_addr(self):
        request = self._request(REMOTE_ADDR="10.0.0.5", HTTP_X_FORWARDED_FOR="1.2.3.4")
        self.assertEqual(get_client_ip(request), "10.0.0.5")

    @override_settings(WEB_SECURITY_TRUSTED_PROXIES=["172.16.0.0/12"])
    def test_web_security_absent_falls_back_to_sites_trusted_proxy_count(self):
        """web_security is a soft dependency: if the plugin isn't installed, the
        ImportError is swallowed and the existing SITES_TRUSTED_PROXY_COUNT / XFF
        logic still applies."""
        with mock.patch.dict(sys.modules, {"apps.web_security.utils": None}):
            with override_settings(SITES_TRUSTED_PROXY_COUNT=1):
                request = self._request(REMOTE_ADDR="172.18.0.2", HTTP_X_FORWARDED_FOR="86.123.136.22")
                self.assertEqual(get_client_ip(request), "86.123.136.22")
