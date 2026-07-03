"""
Data migration to encrypt existing firewall credentials.

This migration:
1. Changes the credentials field from JSONField to TextField (same column)
2. Encrypts any existing plaintext JSON credentials
"""
import json

from django.db import migrations, models


def encrypt_existing_credentials(apps, schema_editor):
    """Encrypt any existing plaintext credentials."""
    # Import here to avoid circular imports during migration
    from apps.web_security.encryption import encrypt_data, is_encrypted

    FirewallConfig = apps.get_model("web_security", "FirewallConfig")

    for config in FirewallConfig.objects.all():
        # Access the raw database value
        raw_value = config.credentials

        # Skip if already encrypted or empty
        if not raw_value:
            continue

        if isinstance(raw_value, str) and is_encrypted(raw_value):
            continue

        # Handle both dict (from JSONField) and string representations
        if isinstance(raw_value, dict):
            credentials_dict = raw_value
        elif isinstance(raw_value, str):
            try:
                credentials_dict = json.loads(raw_value)
            except json.JSONDecodeError:
                continue
        else:
            continue

        # Encrypt and save
        if credentials_dict:
            config.credentials = encrypt_data(credentials_dict)
            config.save(update_fields=["credentials"])


def decrypt_existing_credentials(apps, schema_editor):
    """Reverse migration - decrypt credentials back to JSON."""
    from apps.web_security.encryption import decrypt_data, is_encrypted

    FirewallConfig = apps.get_model("web_security", "FirewallConfig")

    for config in FirewallConfig.objects.all():
        raw_value = config.credentials

        if not raw_value or not isinstance(raw_value, str):
            continue

        if is_encrypted(raw_value):
            decrypted = decrypt_data(raw_value)
            config.credentials = decrypted
            config.save(update_fields=["credentials"])


class Migration(migrations.Migration):

    dependencies = [
        ("web_security", "0003_alter_securitysettings_whitelist_paths"),
    ]

    operations = [
        # Change field type from JSONField to TextField while keeping same column
        migrations.AlterField(
            model_name="firewallconfig",
            name="credentials",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Provider-specific credentials (encrypted at rest)",
                verbose_name="Credentials",
            ),
        ),
        # Encrypt existing plaintext credentials
        migrations.RunPython(
            encrypt_existing_credentials,
            decrypt_existing_credentials,
        ),
        # Rename field to match new model (internal name change only)
        migrations.RenameField(
            model_name="firewallconfig",
            old_name="credentials",
            new_name="_credentials",
        ),
    ]
