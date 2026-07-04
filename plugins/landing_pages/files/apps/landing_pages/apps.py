from django.apps import AppConfig


class LandingPagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.landing_pages"
    label = "landing_pages"
    verbose_name = "Landing Pages"

    def ready(self):
        # Import signals to register them
        from apps.landing_pages import signals  # noqa: F401
