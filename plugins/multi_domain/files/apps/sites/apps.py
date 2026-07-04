from django.apps import AppConfig


class SitesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.sites"
    label = "site_management"  # Unique label to avoid conflict with django.contrib.sites
    verbose_name = "Sites"  # Match Django's sites app section for cleaner admin UI

    def ready(self):
        # Import signals to register them
        from apps.sites import signals  # noqa: F401
