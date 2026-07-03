"""Regression tests for bounded request-body inspection in ThreatMonitorMiddleware.

Fix: the middleware used to do `request.body.decode(...)[:5000]` on every POST/PUT/PATCH.
`request.body` materializes the ENTIRE request body into memory before the slice is
applied, so a large upload (e.g. 100MB+) was fully buffered on the hot path (a
memory-exhaustion DoS vector), and accessing it also consumes the request stream
(breaking streaming/upload views). The fix inspects Content-Length first and skips
`request.body` entirely when it exceeds MAX_BODY_INSPECTION_SIZE.
"""

from unittest.mock import MagicMock, PropertyMock, patch

from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, SimpleTestCase

from apps.web_security.middleware.threat_monitor import ThreatMonitorMiddleware
from apps.web_security.models.threat_pattern import MAX_BODY_INSPECTION_SIZE


def _dummy_get_response(request):
    return HttpResponse("ok")


def _mock_security_settings():
    """Build a MagicMock standing in for SecuritySettings.get_settings() that lets
    every non-body-related check in the middleware pass through."""
    settings = MagicMock()
    settings.security_enabled = True
    settings.threat_detection_enabled = True
    settings.is_path_whitelisted.return_value = False
    settings.is_ip_whitelisted.return_value = False
    settings.get_enabled_categories.return_value = None
    settings.ip_reputation_enabled = False
    return settings


class BodyInspectionTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = ThreatMonitorMiddleware(get_response=_dummy_get_response)

        patchers = [
            patch(
                "apps.web_security.middleware.threat_monitor.SecuritySettings.get_settings",
                return_value=_mock_security_settings(),
            ),
            patch(
                "apps.web_security.middleware.threat_monitor.get_client_ip",
                return_value="203.0.113.5",
            ),
            patch(
                "apps.web_security.middleware.threat_monitor.is_private_ip",
                return_value=False,
            ),
            patch(
                "apps.web_security.middleware.threat_monitor.get_exempt_ips",
                return_value=set(),
            ),
        ]
        for p in patchers:
            p.start()
            self.addCleanup(p.stop)

        check_request_patcher = patch(
            "apps.web_security.middleware.threat_monitor.ThreatPattern.check_request",
            return_value=[],
        )
        self.mock_check_request = check_request_patcher.start()
        self.addCleanup(check_request_patcher.stop)

    def test_large_content_length_skips_body_inspection_without_reading_body(self):
        """A POST declaring a huge Content-Length must never touch request.body."""
        request = self.factory.post(
            "/some/path/", data="small-payload", content_type="text/plain"
        )
        # Simulate a 200MB upload by overriding the declared Content-Length; the
        # actual body bytes stay tiny so the test itself doesn't buffer 200MB.
        request.META["CONTENT_LENGTH"] = str(200 * 1024 * 1024)

        # Prove request.body is never accessed: any read of it raises.
        with patch.object(
            HttpRequest,
            "body",
            new_callable=PropertyMock,
            side_effect=AssertionError("request.body must not be read for oversized uploads"),
        ):
            self.middleware(request)

        self.mock_check_request.assert_called_once()
        self.assertEqual(self.mock_check_request.call_args.kwargs["body"], "")

    def test_small_body_within_bound_is_still_inspected(self):
        """A small POST body must still be read and passed through for inspection."""
        payload = "<script>alert(1)</script>"
        request = self.factory.post("/some/path/", data=payload, content_type="text/plain")

        self.assertLess(int(request.META["CONTENT_LENGTH"]), MAX_BODY_INSPECTION_SIZE)

        self.middleware(request)

        self.mock_check_request.assert_called_once()
        self.assertEqual(self.mock_check_request.call_args.kwargs["body"], payload)
