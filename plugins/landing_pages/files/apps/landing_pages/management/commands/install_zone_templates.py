"""
Management command to install default ZoneTemplates for the Landing Pages plugin.

Usage:
    python manage.py install_zone_templates
    python manage.py install_zone_templates --force  # Overwrite existing

Zone templates are defined in the zone_templates/ package, organized by zone type:
    - zone_templates/hero.py
    - zone_templates/carousel.py
    - zone_templates/gallery.py
    - zone_templates/testimonial.py
    - zone_templates/redirect.py
    - zone_templates/jumbotron.py
    - zone_templates/table.py
    - zone_templates/qr_code.py
    - zone_templates/timeline.py
    - zone_templates/video.py
    - zone_templates/comparison.py
    - zone_templates/showcase.py
    - zone_templates/benefits_grid.py
    - zone_templates/social_proof_cta.py
    - zone_templates/curriculum.py
    - zone_templates/testimonials_grid.py
    - zone_templates/pricing.py
    - zone_templates/about_instructor.py
    - zone_templates/guarantee.py
    - zone_templates/faq.py
    - zone_templates/final_cta.py
    - zone_templates/banner.py
    - zone_templates/footer.py
"""

from django.core.management.base import BaseCommand

from apps.landing_pages.models import ZoneTemplate

from .zone_templates import ZONE_TEMPLATES


class Command(BaseCommand):
    help = "Install default ZoneTemplates for the Landing Pages plugin"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing templates with the same name",
        )

    def handle(self, *args, **options):
        force = options["force"]
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.MIGRATE_HEADING("Installing Zone Templates..."))

        for template_data in ZONE_TEMPLATES:
            name = template_data["name"]

            existing = ZoneTemplate.objects.filter(name=name).first()

            if existing:
                if force:
                    # Update existing template
                    for key, value in template_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                    self.stdout.write(f"  Updated: {name}")
                else:
                    skipped_count += 1
                    self.stdout.write(f"  Skipped (exists): {name}")
            else:
                # Create new template
                ZoneTemplate.objects.create(**template_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created: {name}"))

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Done! Created: {created_count}, Updated: {updated_count}, Skipped: {skipped_count}")
        )

        if skipped_count > 0 and not force:
            self.stdout.write(self.style.WARNING("  Use --force to overwrite existing templates"))
