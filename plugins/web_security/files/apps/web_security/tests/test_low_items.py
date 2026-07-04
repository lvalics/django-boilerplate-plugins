"""Regression tests for two small fixes:

1. tasks_security_report: raw exception text and third-party correspondent email
   addresses must never leak into the emailed security report body.
2. IPReputationCache.calculate_threat_score: score bands must scale with the
   reputation config's min_confidence_score instead of hardcoded 75/50 bands,
   matching the behavior already honored by `is_suspicious`.
"""

from unittest import mock, skipUnless

from django.test import SimpleTestCase, TestCase, override_settings

from apps.web_security.models.ip_reputation import IPReputationCache, IPReputationConfig
from apps.web_security.tasks_security_report import _mask_email, send_security_report

try:
    import httpx  # noqa: F401

    _HAS_HTTPX = True
except ImportError:
    # The security-report Mandrill check imports httpx lazily and degrades gracefully
    # without it; its tests are skipped where httpx is not installed.
    _HAS_HTTPX = False


class MaskEmailTests(SimpleTestCase):
    def test_masks_local_part(self):
        self.assertEqual(_mask_email("john.doe@example.com"), "***@example.com")

    def test_handles_missing_or_invalid_input(self):
        self.assertEqual(_mask_email(""), "?")
        self.assertEqual(_mask_email(None), "?")
        self.assertEqual(_mask_email("not-an-email"), "not-an-email")


@skipUnless(_HAS_HTTPX, "httpx not installed (security-report Mandrill check unavailable)")
@override_settings(
    MANDRILL_API_KEY="fake-mandrill-key",
    SECURITY_REPORT_RECIPIENTS=["admin@example.com"],
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
class SecurityReportSanitizationTests(TestCase):
    """Exercises the real task with outbound I/O mocked, to prove the emailed
    report never carries raw exception text or unmasked correspondent addresses.
    """

    def _run_report(self, mandrill_side_effect=None, mandrill_return_value=None):
        captured = {}

        def fake_send_mail(email):
            captured["body"] = email.body
            captured["recipients"] = email.to
            return True

        with (
            mock.patch("httpx.post", side_effect=mandrill_side_effect, return_value=mandrill_return_value),
            mock.patch(
                "apps.web_security.tasks_security_report.safe_send_email",
                side_effect=fake_send_mail,
            ),
        ):
            send_security_report()

        return captured

    def test_report_hides_exception_details_on_mandrill_error(self):
        sensitive_error = RuntimeError("connection to db-primary-internal.prod.local:5432 refused")

        captured = self._run_report(mandrill_side_effect=sensitive_error)
        body = captured["body"]

        # The raw exception text (which could carry internal hostnames/paths) must not leak.
        self.assertNotIn("db-primary-internal.prod.local", body)
        self.assertIn("Error checking Mandrill (see server logs).", body)

        # Recipients/behavior otherwise untouched.
        self.assertEqual(captured["recipients"], ["admin@example.com"])

    def test_report_masks_correspondent_email_addresses(self):
        fake_messages = [
            {
                "state": "sent",
                "email": "victim.person@personal-domain.com",
                "subject": "You won free bitcoin!!!",
                "opens": 0,
            }
        ]
        fake_response = mock.Mock()
        fake_response.status_code = 200
        fake_response.json.return_value = fake_messages

        captured = self._run_report(mandrill_return_value=fake_response)
        body = captured["body"]

        self.assertNotIn("victim.person@personal-domain.com", body)
        self.assertIn("***@personal-domain.com", body)


class ThreatScoreBandsTests(SimpleTestCase):
    """Bands are now derived from IPReputationConfig.min_confidence_score."""

    def test_low_threshold_config_lowers_high_band_trigger(self):
        config = IPReputationConfig(min_confidence_score=30)
        entry = IPReputationCache(abuse_confidence_score=30)

        # Previously this required abuse_confidence_score >= 75 to hit the high band.
        self.assertEqual(entry.calculate_threat_score(config=config), 20)

    def test_medium_band_scales_with_threshold_too(self):
        config = IPReputationConfig(min_confidence_score=30)
        # medium band threshold = 30 * 2 // 3 = 20
        entry = IPReputationCache(abuse_confidence_score=20)

        self.assertEqual(entry.calculate_threat_score(config=config), 10)

    def test_default_threshold_preserves_previous_bands(self):
        config = IPReputationConfig(min_confidence_score=75)

        self.assertEqual(IPReputationCache(abuse_confidence_score=75).calculate_threat_score(config=config), 20)
        self.assertEqual(IPReputationCache(abuse_confidence_score=50).calculate_threat_score(config=config), 10)
        self.assertEqual(IPReputationCache(abuse_confidence_score=49).calculate_threat_score(config=config), 0)
