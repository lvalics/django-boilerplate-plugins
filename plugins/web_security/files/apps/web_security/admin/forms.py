import json

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.web_security.models import FirewallConfig, IPReputationConfig


class FirewallConfigForm(forms.ModelForm):
    """Custom form for FirewallConfig with credential handling."""

    # Use a regular TextField for credentials input (JSON format)
    credentials = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 8, "class": "vLargeTextField"}),
        required=False,
        help_text=_("Enter credentials as JSON. Values are encrypted at rest."),
    )

    class Meta:
        model = FirewallConfig
        fields = ["name", "provider", "is_active", "is_default", "credentials"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Never render decrypted secrets in the admin. Show MASKED current values so an
        # admin can see which keys exist; a blank (or unchanged-masked) submission keeps
        # the existing credentials.
        if self.instance and self.instance.pk and self.instance.credentials:
            self.fields["credentials"].initial = json.dumps(
                self.instance.get_masked_credentials(), indent=2, ensure_ascii=False
            )
            self.fields["credentials"].help_text = _(
                "Showing masked current values. Leave unchanged to keep them, or paste new "
                "JSON to replace. Values are encrypted at rest."
            )

    def clean_credentials(self):
        """Parse JSON credentials; None means 'keep existing' (blank or unchanged mask)."""
        value = self.cleaned_data.get("credentials", "")
        if not value or not value.strip():
            return None

        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as e:
            raise forms.ValidationError(_("Invalid JSON: %(error)s") % {"error": str(e)})
        if not isinstance(parsed, dict):
            raise forms.ValidationError(_("Credentials must be a JSON object"))
        # If the admin submitted the masked placeholder unchanged, keep existing secrets.
        if any(isinstance(v, str) and v and set(v) == {"•"} for v in parsed.values()):
            return None
        return parsed

    def save(self, commit=True):
        """Save with encrypted credentials; blank/unchanged keeps existing values."""
        instance = super().save(commit=False)
        creds = self.cleaned_data.get("credentials")
        if creds is not None:
            instance.credentials = creds  # property setter encrypts
        elif not instance.pk:
            instance.credentials = {}
        if commit:
            instance.save()
        return instance


class IPReputationConfigForm(forms.ModelForm):
    """Custom form for IPReputationConfig that keeps the API key secret."""

    api_key = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text=_("Leave blank to keep the existing key. Stored encrypted at rest."),
    )

    class Meta:
        model = IPReputationConfig
        fields = [
            "name",
            "provider",
            "api_url",
            "is_active",
            "is_default",
            "cache_duration_hours",
            "min_confidence_score",
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_key = self.cleaned_data.get("api_key")
        if new_key:
            instance.api_key = new_key  # property setter encrypts
        if commit:
            instance.save()
        return instance
