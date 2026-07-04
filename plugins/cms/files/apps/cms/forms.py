"""Forms for the landing pages plugin."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .email_utils import validate_and_normalize_email


class OrderFormBase(forms.Form):
    """Base form for order submissions."""

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "input input-bordered w-full", "placeholder": _("Your email")}),
    )

    name = forms.CharField(
        label=_("Name"),
        max_length=255,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": _("Your name")}),
    )

    def clean_email(self):
        """Validate email for typos, disposable domains, and role-based addresses."""
        email = self.cleaned_data.get("email")
        normalized, error = validate_and_normalize_email(email)
        if error:
            raise forms.ValidationError(error)
        return normalized


class FileUploadForm(forms.Form):
    """Form for file uploads in order forms."""

    file = forms.FileField(
        label=_("Upload file"),
        widget=forms.FileInput(attrs={"class": "file-input file-input-bordered w-full"}),
    )

    def __init__(self, *args, allowed_types=None, max_size_mb=10, **kwargs):
        super().__init__(*args, **kwargs)
        self.allowed_types = allowed_types or ["image/jpeg", "image/png", "application/pdf"]
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def clean_file(self):
        """Validate uploaded file."""
        uploaded_file = self.cleaned_data.get("file")

        if not uploaded_file:
            return uploaded_file

        # Check file size
        if uploaded_file.size > self.max_size_bytes:
            raise forms.ValidationError(
                _("File size exceeds maximum allowed (%(max)s MB).") % {"max": self.max_size_bytes / (1024 * 1024)}
            )

        # Check file type
        if self.allowed_types and uploaded_file.content_type not in self.allowed_types:
            raise forms.ValidationError(
                _("File type not allowed. Allowed types: %(types)s") % {"types": ", ".join(self.allowed_types)}
            )

        return uploaded_file
