"""Order/contact form submissions from landing page ORDER_FORM zones."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel

from .pages import LandingPage, LandingPageZone


class SubmissionStatus(models.TextChoices):
    """Lightweight triage workflow for form submissions."""

    NEW = "new", _("New")
    SEEN = "seen", _("Seen")
    PROCESSED = "processed", _("Processed")
    SPAM = "spam", _("Spam")


class LandingPageSubmission(BaseModel):
    """
    A visitor submission from an ORDER_FORM zone.

    Stores the sanitized form payload and any uploaded file paths. There is no
    payment/checkout integration: this is a plain order/contact inbox.
    """

    landing_page = models.ForeignKey(
        LandingPage,
        on_delete=models.CASCADE,
        related_name="submissions",
        help_text=_("Landing page that generated this submission."),
    )
    zone = models.ForeignKey(
        LandingPageZone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submissions",
        help_text=_("The ORDER_FORM zone that created this submission."),
    )

    email = models.EmailField(
        blank=True,
        help_text=_("Visitor email (validated and normalized)."),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Visitor name."),
    )
    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Visitor phone number."),
    )

    form_data = models.JSONField(
        default=dict,
        help_text=_("Sanitized form data as JSON."),
    )
    uploaded_files = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Uploaded files as a list of storage paths (with field name and original filename)."),
    )

    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.NEW,
        db_index=True,
        help_text=_("Triage status."),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_("Client IP at submission time (proxy-aware)."),
    )

    class Meta:
        verbose_name = _("Landing Page Submission")
        verbose_name_plural = _("Landing Page Submissions")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        who = self.email or self.name or "anonymous"
        return f"Submission #{self.pk} from {who} ({self.status})"

    def get_form_value(self, key, default=None):
        """Get a value from form_data."""
        return self.form_data.get(key, default)
