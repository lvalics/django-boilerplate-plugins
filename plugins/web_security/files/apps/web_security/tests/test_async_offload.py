"""Tests for pass-4 refactors: async threat writes, SMTP out of the lock, shared lookup."""

from unittest import mock

from django.test import RequestFactory, SimpleTestCase, TestCase

from apps.web_security import utils

TM = "apps.web_security.middleware.threat_monitor"


def _settings(**over):
    s = mock.Mock()
    s.security_enabled = True
    s.threat_detection_enabled = True
    s.ip_reputation_enabled = True
    s.is_path_whitelisted.return_value = False
    s.is_ip_whitelisted.return_value = False
    s.get_enabled_categories.return_value = None
    for k, v in over.items():
        setattr(s, k, v)
    return s


class SharedLookupTests(SimpleTestCase):
    def test_settings_resolved_once_per_request(self):
        req = RequestFactory().get("/")
        with mock.patch("apps.web_security.models.SecuritySettings.get_settings", return_value="S") as gs:
            a = utils.get_cached_settings(req)
            b = utils.get_cached_settings(req)
        self.assertEqual(a, "S")
        self.assertIs(a, b)
        gs.assert_called_once()

    def test_client_ip_resolved_once_per_request(self):
        req = RequestFactory().get("/")
        with mock.patch("apps.web_security.utils.get_client_ip", return_value="1.2.3.4") as gc:
            self.assertEqual(utils.get_cached_client_ip(req), "1.2.3.4")
            self.assertEqual(utils.get_cached_client_ip(req), "1.2.3.4")
        gc.assert_called_once()


_MATCH = {
    "pattern_id": 1,
    "pattern_name": "wp",
    "category": "wordpress",
    "threat_level": "high",
    "threat_score": 20,
    "match_type": "path",
    "matched_value": "/wp-login.php",
}


class ThreatMonitorAsyncTests(TestCase):
    def test_match_dispatches_task_and_writes_nothing_inline(self):
        from apps.web_security.middleware.threat_monitor import ThreatMonitorMiddleware
        from apps.web_security.models import SuspiciousRequest

        req = RequestFactory().get("/wp-login.php")
        mw = ThreatMonitorMiddleware(lambda r: "OK")
        with (
            mock.patch(f"{TM}.get_cached_settings", return_value=_settings()),
            mock.patch(f"{TM}.get_cached_client_ip", return_value="8.8.8.8"),
            mock.patch(f"{TM}.is_private_ip", return_value=False),
            mock.patch(f"{TM}.get_exempt_ips", return_value=set()),
            mock.patch("apps.web_security.models.ThreatPattern.check_request", return_value=[_MATCH]),
            mock.patch("apps.web_security.tasks.record_threat_matches.delay") as delay,
        ):
            resp = mw(req)
        self.assertEqual(resp, "OK")
        delay.assert_called_once()
        args = delay.call_args.args
        self.assertEqual(args[0], "8.8.8.8")
        self.assertEqual(args[1], [_MATCH])
        # the request path must not touch the DB
        self.assertEqual(SuspiciousRequest.objects.count(), 0)

    def test_record_task_persists_and_filters_sensitive_headers(self):
        from apps.web_security.models import SuspiciousRequest
        from apps.web_security.tasks import record_threat_matches

        req_data = {
            "path": "/wp",
            "method": "GET",
            "user_agent": "UA",
            "headers": {"User-Agent": "UA", "Cookie": "secret"},
            "body_preview": "",
        }
        with (
            mock.patch("apps.web_security.models.IPThreatSummary.add_threat") as add,
            mock.patch("apps.web_security.models.IPReputationCache.get_or_queue") as queue,
        ):
            record_threat_matches("8.8.8.8", [_MATCH], req_data, reputation_enabled=True)
        self.assertEqual(SuspiciousRequest.objects.count(), 1)
        sr = SuspiciousRequest.objects.first()
        self.assertEqual(sr.ip_address, "8.8.8.8")
        self.assertNotIn("Cookie", sr.headers)  # record() drops sensitive headers
        self.assertIn("User-Agent", sr.headers)
        add.assert_called_once()
        queue.assert_called_once_with("8.8.8.8")


class AutoBlockNotificationTests(SimpleTestCase):
    def test_notification_task_calls_notify(self):
        from apps.web_security.tasks import send_auto_block_notification

        with (
            mock.patch("apps.web_security.models.SecuritySettings.get_settings", return_value="S"),
            mock.patch("apps.web_security.models.SuspiciousRequest.get_recent_by_ip") as recent,
            mock.patch("apps.web_security.services.notifications.notify_auto_block") as notify,
        ):
            recent.return_value.values.return_value = []
            send_auto_block_notification("8.8.8.8", 100)
        notify.assert_called_once()
        kwargs = notify.call_args.kwargs
        self.assertEqual(kwargs["ip_address"], "8.8.8.8")
        self.assertEqual(kwargs["threat_score"], 100)
