"""Regression tests for three small polish fixes:

1. views.ip_lookup_view now validates `ip_address` (via `validate_ip`) before it is
   interpolated into an outbound request path / cache key, rejecting invalid input
   with a 400 and never reaching the outbound lookup helpers.
2. middleware.security_headers.SecurityHeadersMiddleware now sets the deprecated
   `X-XSS-Protection` header to "0" instead of "1; mode=block".
3. services.notifications.notify_critical_threat no longer crashes when
   `threat_info["matched_value"]` is present but `None` (dict.get's default only
   applies when the key is absent, not when its value is None).
"""

from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from apps.web_security.middleware.security_headers import SecurityHeadersMiddleware
from apps.web_security.services.notifications import notify_critical_threat
from apps.web_security.views import ip_lookup_view


def _dummy_get_response(request):
    return HttpResponse("ok")


class SecurityHeadersXSSProtectionTests(SimpleTestCase):
    def test_x_xss_protection_is_disabled(self):
        middleware = SecurityHeadersMiddleware(get_response=_dummy_get_response)
        settings_obj = MagicMock(security_enabled=True, security_headers_enabled=True)

        with patch(
            "apps.web_security.middleware.security_headers.SecuritySettings.get_settings",
            return_value=settings_obj,
        ):
            request = RequestFactory().get("/")
            response = middleware(request)

        self.assertEqual(response["X-XSS-Protection"], "0")


class NotifyCriticalThreatNoneValueTests(SimpleTestCase):
    @patch("apps.web_security.services.notifications.send_mail")
    def test_none_matched_value_does_not_raise(self, mock_send_mail):
        settings_obj = MagicMock(notify_on_critical=True, notification_email="admin@example.com")
        threat_info = {
            "pattern_name": "SQLi",
            "threat_level": "critical",
            "category": "injection",
            "path": "/login/",
            "method": "POST",
            "matched_value": None,
        }

        # Should not raise, and should actually attempt to send the email.
        notify_critical_threat(settings_obj, "203.0.113.5", threat_info)

        mock_send_mail.assert_called_once()
        message = mock_send_mail.call_args.kwargs["message"]
        self.assertIsInstance(message, str)
        self.assertIn("Matched Value: N/A", message)


class IPLookupViewInvalidIPTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _staff_request(self, path):
        request = self.factory.get(path)
        request.user = MagicMock(is_active=True, is_staff=True)
        return request

    @patch("apps.web_security.views._lookup_ip_api")
    @patch("apps.web_security.views._lookup_whatismyip")
    @patch("apps.web_security.views.cache")
    def test_invalid_ip_rejected_before_outbound_call(self, mock_cache, mock_whatismyip, mock_ip_api):
        request = self._staff_request("/web-security/ip-lookup/not-an-ip/")

        response = ip_lookup_view(request, "not-an-ip")

        self.assertEqual(response.status_code, 400)
        mock_ip_api.assert_not_called()
        mock_whatismyip.assert_not_called()
        mock_cache.get.assert_not_called()
        mock_cache.set.assert_not_called()
