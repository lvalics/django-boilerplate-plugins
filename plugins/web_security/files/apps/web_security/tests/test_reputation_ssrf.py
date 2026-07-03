"""Security tests for IP reputation services.

Covers:
- SSRF guard on CustomAPIService (admin-controlled api_url carrying a Bearer key).
- allow_redirects=False on outbound reputation requests.
- API key not leaking into IPQualityScore log records (key lives in the URL path).

These use SimpleTestCase and mock requests.get / socket.getaddrinfo, so no DB is touched.
"""

from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from apps.web_security.services.ip_reputation import (
    CustomAPIService,
    IPQualityScoreService,
    _is_safe_outbound_url,
)

LOGGER_NAME = "apps.web_security.services.ip_reputation"


def _fake_config(**overrides):
    """Duck-typed stand-in for IPReputationConfig (avoids the DB)."""
    base = {
        "api_key": "SECRET-API-KEY-1234567890",
        "cache_duration_hours": 24,
        "api_url": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class CustomAPIServiceSSRFTests(SimpleTestCase):
    def test_private_target_is_not_requested(self):
        """api_url resolving to a private/link-local IP must not issue a request."""
        service = CustomAPIService(_fake_config(api_url="http://169.254.169.254/latest/{ip}"))

        with (
            mock.patch("apps.web_security.services.ip_reputation.requests.get") as mock_get,
            mock.patch.object(CustomAPIService, "update_cache") as mock_update_cache,
        ):
            result = service.check_ip("8.8.8.8")

        mock_get.assert_not_called()
        mock_update_cache.assert_not_called()
        self.assertIn("error", result)

    def test_https_host_resolving_private_is_blocked(self):
        """Even an https host is blocked when DNS resolves it to a private IP."""
        service = CustomAPIService(_fake_config(api_url="https://internal.example.com/lookup/{ip}"))

        with (
            mock.patch(
                "apps.web_security.services.ip_reputation.socket.getaddrinfo",
                return_value=[(2, 1, 6, "", ("10.0.0.5", 443))],
            ),
            mock.patch("apps.web_security.services.ip_reputation.requests.get") as mock_get,
            mock.patch.object(CustomAPIService, "update_cache") as mock_update_cache,
        ):
            result = service.check_ip("8.8.8.8")

        mock_get.assert_not_called()
        mock_update_cache.assert_not_called()
        self.assertIn("error", result)

    def test_public_https_target_is_requested_without_redirects(self):
        """A public https target is allowed and must be fetched with allow_redirects=False."""
        service = CustomAPIService(_fake_config(api_url="https://api.example.com/lookup/{ip}"))

        fake_response = mock.Mock()
        fake_response.raise_for_status.return_value = None
        fake_response.json.return_value = {"abuse_confidence_score": 0}

        with (
            mock.patch(
                "apps.web_security.services.ip_reputation.socket.getaddrinfo",
                return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
            ),
            mock.patch(
                "apps.web_security.services.ip_reputation.requests.get",
                return_value=fake_response,
            ) as mock_get,
            mock.patch.object(CustomAPIService, "update_cache"),
        ):
            service.check_ip("8.8.8.8")

        mock_get.assert_called_once()
        self.assertFalse(mock_get.call_args.kwargs.get("allow_redirects", True))


class IsSafeOutboundUrlTests(SimpleTestCase):
    def test_non_https_scheme_rejected(self):
        self.assertFalse(_is_safe_outbound_url("http://example.com/x"))

    def test_public_https_allowed(self):
        with mock.patch(
            "apps.web_security.services.ip_reputation.socket.getaddrinfo",
            return_value=[(2, 1, 6, "", ("93.184.216.34", 443))],
        ):
            self.assertTrue(_is_safe_outbound_url("https://example.com/x"))

    def test_any_private_resolution_rejected(self):
        with mock.patch(
            "apps.web_security.services.ip_reputation.socket.getaddrinfo",
            return_value=[
                (2, 1, 6, "", ("93.184.216.34", 443)),
                (2, 1, 6, "", ("127.0.0.1", 443)),
            ],
        ):
            self.assertFalse(_is_safe_outbound_url("https://example.com/x"))


class IPQualityScoreLoggingTests(SimpleTestCase):
    def test_api_key_not_leaked_to_logs_on_error(self):
        """The key sits in the request URL path; the error log must not contain it."""
        api_key = "SECRET-API-KEY-1234567890"
        service = IPQualityScoreService(_fake_config(api_key=api_key))

        # A real requests exception embeds the full URL (including the key) in its message.
        import requests

        leaky_message = f"Connection refused for url: https://ipqualityscore.com/api/json/ip/{api_key}/8.8.8.8"
        exc = requests.exceptions.ConnectionError(leaky_message)

        with mock.patch(
            "apps.web_security.services.ip_reputation.requests.get",
            side_effect=exc,
        ):
            with self.assertLogs(LOGGER_NAME, level="ERROR") as captured:
                result = service.check_ip("8.8.8.8")

        log_output = "\n".join(captured.output)
        self.assertNotIn(api_key, log_output)
        self.assertNotIn(api_key, result.get("error", ""))
