from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class WebSecurityAdminMixin:
    """Mixin to add help section to Web Security admin pages."""

    # Override these in subclasses
    page_help_title = ""
    page_help_text = ""

    @admin.display(description="")
    def page_help(self, obj=None):
        """Render the help box at the top of the form."""
        if not self.page_help_title and not self.page_help_text:
            return ""

        title = self.page_help_title or _("Help")
        text = self.page_help_text or ""

        return mark_safe(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h3 style="margin: 0 0 10px 0; font-size: 18px; font-weight: 600;">
                ℹ️ {title}
            </h3>
            <div style="font-size: 14px; line-height: 1.6; opacity: 0.95;">
                {text}
            </div>
        </div>
        """)
