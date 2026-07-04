"""Customer testimonials displayed in testimonial zones."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class Testimonial(BaseModel):
    """
    Customer testimonial with auto-generated Schema.org Review markup.

    Testimonials are created by staff in the admin and can be linked to
    testimonial zones.
    """

    text = models.TextField(
        help_text=_("The testimonial content."),
    )
    author_name = models.CharField(
        max_length=100,
        help_text=_("Name of the person giving the testimonial."),
    )
    author_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Title or role (e.g., 'CEO at Company')."),
    )
    author_photo = models.ImageField(
        upload_to="testimonials/photos/",
        blank=True,
        null=True,
        help_text=_("Photo of the testimonial author."),
    )

    # Rating
    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text=_("Rating from 1-5 stars."),
    )

    # Verification
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Verified customer testimonial."),
    )

    # Media
    video_url = models.URLField(
        blank=True,
        help_text=_("URL to video testimonial (YouTube, Vimeo, etc.)."),
    )
    proof_image = models.ImageField(
        upload_to="testimonials/proofs/",
        blank=True,
        null=True,
        help_text=_("Screenshot or proof image."),
    )

    # Schema.org markup (auto-generated)
    schema_markup = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Auto-generated Schema.org Review markup."),
    )

    class Meta:
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name}: {self.text[:50]}..."

    def save(self, *args, **kwargs):
        # Auto-generate Schema.org markup
        self.schema_markup = self._generate_schema_markup()
        super().save(*args, **kwargs)

    def _generate_schema_markup(self):
        """Generate Schema.org Review markup."""
        return {
            "@context": "https://schema.org",
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(self.rating),
                "bestRating": "5",
            },
            "author": {
                "@type": "Person",
                "name": self.author_name,
            },
            "reviewBody": self.text,
        }
