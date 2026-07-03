"""Regression tests for secrets-at-rest hardening (pass 2b).

- encryption: dedicated key support + string encrypt/decrypt round-trip
- IPReputationConfig.api_key encrypted at rest via a decrypting property
- admin forms never render decrypted secrets and keep existing values on blank submit
"""

from cryptography.fernet import Fernet
from django.test import SimpleTestCase, override_settings

from apps.web_security.admin import FirewallConfigForm, IPReputationConfigForm
from apps.web_security.encryption import (
    ENCRYPTED_PREFIX,
    decrypt_string,
    encrypt_string,
    mask_credentials,
)
from apps.web_security.models import FirewallConfig, IPReputationConfig

DEDICATED_KEY = Fernet.generate_key().decode()


class EncryptionTests(SimpleTestCase):
    def test_string_round_trip(self):
        token = encrypt_string("super-secret-key")
        self.assertTrue(token.startswith(ENCRYPTED_PREFIX))
        self.assertNotIn("super-secret-key", token)
        self.assertEqual(decrypt_string(token), "super-secret-key")

    def test_empty_values(self):
        self.assertEqual(encrypt_string(""), "")
        self.assertEqual(decrypt_string(""), "")

    def test_legacy_plaintext_passthrough(self):
        # A value without the prefix is treated as legacy plaintext, returned as-is.
        self.assertEqual(decrypt_string("plain-legacy-key"), "plain-legacy-key")

    @override_settings(WEB_SECURITY_ENCRYPTION_KEY=DEDICATED_KEY)
    def test_dedicated_key_round_trip(self):
        token = encrypt_string("k")
        self.assertEqual(decrypt_string(token), "k")

    def test_mask_credentials_reveals_no_prefix(self):
        masked = mask_credentials({"api_token": "abcd1234efgh", "region": "us-east-1"})
        self.assertEqual(masked["api_token"], "•" * 8)
        self.assertNotIn("abcd", masked["api_token"])
        self.assertEqual(masked["region"], "us-east-1")  # non-sensitive untouched


class ApiKeyAtRestTests(SimpleTestCase):
    def test_api_key_property_encrypts_and_decrypts(self):
        config = IPReputationConfig(name="x", provider="abuseipdb")
        config.api_key = "MY-API-KEY"
        self.assertTrue(config._api_key.startswith(ENCRYPTED_PREFIX))
        self.assertNotIn("MY-API-KEY", config._api_key)
        self.assertEqual(config.api_key, "MY-API-KEY")

    def test_masked_api_key(self):
        config = IPReputationConfig(name="x", provider="abuseipdb")
        self.assertEqual(config.get_masked_api_key(), "")
        config.api_key = "secret"
        self.assertEqual(config.get_masked_api_key(), "•" * 8)


def _rep_data(**over):
    data = {
        "name": "x",
        "provider": "abuseipdb",
        "api_url": "",
        "cache_duration_hours": "24",
        "min_confidence_score": "75",
    }
    data.update(over)
    return data


class IPReputationConfigFormTests(SimpleTestCase):
    def test_blank_api_key_keeps_existing(self):
        instance = IPReputationConfig(name="x", provider="abuseipdb")
        instance.api_key = "EXISTING"
        form = IPReputationConfigForm(data=_rep_data(api_key=""), instance=instance)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save(commit=False)
        self.assertEqual(saved.api_key, "EXISTING")

    def test_new_api_key_is_encrypted(self):
        instance = IPReputationConfig(name="x", provider="abuseipdb")
        form = IPReputationConfigForm(data=_rep_data(api_key="BRAND-NEW"), instance=instance)
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save(commit=False)
        self.assertEqual(saved.api_key, "BRAND-NEW")
        self.assertTrue(saved._api_key.startswith(ENCRYPTED_PREFIX))


class FirewallConfigFormMaskingTests(SimpleTestCase):
    def test_form_initial_shows_masked_not_plaintext(self):
        instance = FirewallConfig(name="fw", provider="cloudflare")
        instance.pk = 1  # make the masking branch run without a DB save
        instance.credentials = {"api_token": "TOP-SECRET-TOKEN"}
        form = FirewallConfigForm(instance=instance)
        initial = form.fields["credentials"].initial
        self.assertNotIn("TOP-SECRET-TOKEN", initial)
        self.assertIn("•", initial)

    def test_unchanged_masked_submission_keeps_existing(self):
        instance = FirewallConfig(name="fw", provider="cloudflare")
        instance.pk = 1
        instance.credentials = {"api_token": "TOP-SECRET-TOKEN"}
        import json

        masked_json = json.dumps(instance.get_masked_credentials())
        form = FirewallConfigForm(
            data={
                "name": "fw",
                "provider": "cloudflare",
                "is_active": "on",
                "is_default": "",
                "credentials": masked_json,
            },
            instance=instance,
        )
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["credentials"])  # sentinel: keep existing
