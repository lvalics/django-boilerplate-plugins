from django.apps import AppConfig


class CMSConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cms"
    label = "cms"
    verbose_name = "CMS"

    def ready(self):
        # Import signals to register them
        from apps.cms import signals  # noqa: F401
