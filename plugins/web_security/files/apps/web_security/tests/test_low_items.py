"""Regression tests for:

1. tasks_security_report: sends via the project's configured email backend (no provider
   lock-in) and no longer carries user-specific integrations.
2. IPReputationCache.calculate_threat_score: score bands scale with the reputation config's
   min_confidence_score instead of hardcoded 75/50 bands.
"""

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings

from apps.web_security.models.ip_reputation import IPReputationCache, IPReputationConfig
from apps.web_security.tasks_security_report import _mask_email, send_security_report


class MaskEmailTests(SimpleTestCase):
    def test_masks_local_part(self):
        self.assertEqual(_mask_email("john.doe@example.com"), "***@example.com")

    def test_handles_missing_or_invalid_input(self):
        self.assertEqual(_mask_email(""), "?")
        self.assertEqual(_mask_email(None), "?")
        self.assertEqual(_mask_email("not-an-email"), "not-an-email")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    SECURITY_REPORT_RECIPIENTS=["admin@example.com"],
    DEFAULT_FROM_EMAIL="noreply@example.com",
)
class SecurityReportSendTests(TestCase):
    """The report is emailed through whatever EMAIL_BACKEND the project configures."""

    def test_report_sends_via_project_email_backend(self):
        result = send_security_report(hours=12)

        self.assertTrue(result["sent"])
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, ["admin@example.com"])
        self.assertEqual(msg.from_email, "noreply@example.com")
        self.assertEqual(msg.content_subtype, "html")
        # General web_security sections are present; user-specific integrations are gone.
        self.assertIn("IP Blocking", msg.body)
        self.assertIn("Suspicious Requests", msg.body)
        self.assertIn("Rate Limiting", msg.body)
        self.assertNotIn("Mandrill", msg.body)


class ThreatScoreBandsTests(SimpleTestCase):
    """Bands are derived from IPReputationConfig.min_confidence_score."""

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
