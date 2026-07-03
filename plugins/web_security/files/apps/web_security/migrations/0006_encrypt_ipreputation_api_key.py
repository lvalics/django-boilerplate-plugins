from django.db import migrations, models


def encrypt_existing_api_keys(apps, schema_editor):
    """Encrypt any plaintext IPReputationConfig.api_key values in place."""
    from apps.web_security.encryption import encrypt_string, is_encrypted

    IPReputationConfig = apps.get_model("web_security", "IPReputationConfig")
    for config in IPReputationConfig.objects.all():
        value = config.api_key  # historical field is the plain column here
        if value and not is_encrypted(value):
            config.api_key = encrypt_string(value)
            config.save(update_fields=["api_key"])


def decrypt_existing_api_keys(apps, schema_editor):
    """Reverse: decrypt api_key values back to plaintext."""
    from apps.web_security.encryption import decrypt_string, is_encrypted

    IPReputationConfig = apps.get_model("web_security", "IPReputationConfig")
    for config in IPReputationConfig.objects.all():
        value = config.api_key
        if value and is_encrypted(value):
            config.api_key = decrypt_string(value)
            config.save(update_fields=["api_key"])


class Migration(migrations.Migration):

    dependencies = [
        ("web_security", "0005_alter_firewallconfig__credentials"),
    ]

    operations = [
        # Widen the column so encrypted tokens fit, before encrypting existing values.
        migrations.AlterField(
            model_name="ipreputationconfig",
            name="api_key",
            field=models.TextField(
                blank=True,
                default="",
                help_text="API key for the reputation service (encrypted at rest)",
                verbose_name="API Key",
            ),
        ),
        migrations.RunPython(encrypt_existing_api_keys, decrypt_existing_api_keys),
        # Rename to the private field backing the api_key property.
        migrations.RenameField(
            model_name="ipreputationconfig",
            old_name="api_key",
            new_name="_api_key",
        ),
    ]
