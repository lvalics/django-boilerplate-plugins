from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebSecurityConfig(AppConfig):
    name = "apps.web_security"
    label = "web_security"
    verbose_name = _("Web Security")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        pass
