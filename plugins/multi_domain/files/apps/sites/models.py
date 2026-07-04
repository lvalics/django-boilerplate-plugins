import re

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel

# template_dir becomes a filesystem path segment under templates/, so it must be a single
# safe path component: lowercase letters, digits, hyphen, underscore only (no separators,
# dots, or traversal sequences). Enforced in SiteProfile.clean() and re-checked before mkdir.
TEMPLATE_DIR_RE = re.compile(r"^[a-z0-9_-]+$")
TEMPLATE_DIR_MAX_LEN = 50


def _help(title: str, description: str, example: str = "", keys: list = None) -> str:
    """Generate formatted HTML help text for admin fields."""
    html = f'<div class="site-help-box"><strong>{title}</strong>'
    html += f'<div class="purpose">{description}</div>'

    if keys:
        html += '<ul class="keys-list">'
        for key, desc in keys:
            html += f"<li><code>{key}</code> - {desc}</li>"
        html += "</ul>"

    if example:
        html += f"<pre>{example}</pre>"

    html += "</div>"
    return mark_safe(html)


def _resolve_env_values(integrations: dict) -> dict:
    """
    Resolve ``env:VAR_NAME`` placeholders in an integrations dict against the environment.

    Kept as a standalone function so both the model (SiteProfile.get_integration) and
    cached-config consumers (resolve_integration) share one implementation. Resolution
    happens at call time only; resolved secrets are never persisted or cached.
    """
    import os

    resolved = {}
    for key, value in (integrations or {}).items():
        if isinstance(value, dict):
            resolved[key] = {
                k: (os.environ.get(v[4:], "") if isinstance(v, str) and v.startswith("env:") else v)
                for k, v in value.items()
            }
        else:
            resolved[key] = value
    return resolved


def resolve_integration(config: dict, name: str) -> dict:
    """
    Lazily resolve a single integration's secrets from a cached site config dict.

    The cached config (request.site_config) stores integrations UNRESOLVED. Server-side
    callers that need a real secret pass the config and the integration name here to get
    ``env:`` placeholders resolved at call time.
    """
    integrations = (config or {}).get("integrations", {})
    return _resolve_env_values({name: integrations.get(name, {})}).get(name, {})


class SiteProfile(BaseModel):
    """
    Extended configuration for a Django Site.
    Stores all domain-specific settings including branding, SEO, auth, and features.
    """

    # === Core Relationship ===
    site = models.OneToOneField(
        Site,
        on_delete=models.CASCADE,
        related_name="profile",
        help_text=_("The Django Site this profile extends. Each Site can have one profile."),
    )

    # === Branding & Theme ===
    site_name = models.CharField(
        max_length=100,
        help_text=_("Display name shown to users. Can differ from Site.name (e.g., 'My Awesome App')."),
    )
    tagline = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Short slogan or description (e.g., 'The best way to manage your tasks')."),
    )
    theme = models.CharField(
        max_length=50,
        default="default",
        help_text=_("Theme identifier used for CSS styling. Maps to DaisyUI theme or custom CSS class."),
    )
    template_dir = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Template subdirectory name under templates/. If empty, defaults to first part of domain "
            "(e.g., 'mysite' for mysite.example.com). Templates here override defaults."
        ),
    )
    logo = models.ImageField(
        upload_to="sites/logos/",
        blank=True,
        null=True,
        help_text=_("Site logo image. Recommended: SVG or PNG with transparent background, min 200px wide."),
    )
    favicon = models.ImageField(
        upload_to="sites/favicons/",
        blank=True,
        null=True,
        help_text=_("Browser favicon. Recommended: 32x32 or 64x64 PNG, or ICO format."),
    )
    primary_color = models.CharField(
        max_length=7,
        default="#3B82F6",
        help_text=_("Primary brand color in hex format (e.g., #3B82F6). Used for buttons, links, accents."),
    )
    secondary_color = models.CharField(
        max_length=7, default="#1E40AF", help_text=_("Secondary brand color in hex format. Used for hover states, etc.")
    )

    # === SEO & Meta Headers ===
    meta_defaults = models.JSONField(
        default=dict,
        blank=True,
        help_text=_help(
            "SEO Meta Tags",
            "Default meta tags applied to all pages. Individual pages can override these values.",
            """{
  "title_suffix": " | My Site",
  "description": "Your site description for search engines",
  "og:image": "/static/images/og-default.jpg",
  "twitter:card": "summary_large_image",
  "robots": "index, follow"
}""",
            keys=[
                ("title_suffix", "Appended to page titles"),
                ("description", "Default meta description"),
                ("og:image", "Default Open Graph image for social sharing"),
                ("twitter:card", "Twitter card type: summary, summary_large_image"),
                ("robots", "Search engine indexing: index/noindex, follow/nofollow"),
            ],
        ),
    )

    # === External Scripts (JS/CSS Injection) ===
    head_scripts = models.JSONField(
        default=list,
        blank=True,
        help_text=_help(
            "Head Scripts & Styles",
            "External scripts and stylesheets injected into &lt;head&gt;. Use for analytics, fonts, CSS.",
            """[
  {"type": "script", "src": "https://www.googletagmanager.com/gtag/js?id=GA-XXX", "async": true},
  {"type": "inline", "content": "window.dataLayer = window.dataLayer || [];"},
  {"type": "link", "rel": "stylesheet", "href": "https://fonts.googleapis.com/css2?family=Inter"}
]""",
            keys=[
                ("type", "script (external JS), inline (inline JS), or link (CSS/preload)"),
                ("src", "URL for external scripts"),
                ("href", "URL for link tags (CSS, fonts)"),
                ("content", "JavaScript code for inline scripts"),
                ("async", "true/false - load script asynchronously"),
                ("defer", "true/false - defer script execution"),
            ],
        ),
    )
    body_scripts = models.JSONField(
        default=list,
        blank=True,
        help_text=_help(
            "Body Scripts",
            "Scripts injected at the end of &lt;body&gt;. Use for chat widgets, tracking pixels, etc.",
            """[
  {"type": "script", "src": "https://widget.example.com/chat.js", "defer": true},
  {"type": "inline", "content": "console.log('Page loaded');"}
]""",
        ),
    )
    custom_css = models.TextField(
        blank=True,
        help_text=_(
            "Custom CSS styles for this site. Injected inline in &lt;head&gt;. "
            "Use for color overrides, custom fonts, or site-specific tweaks."
        ),
    )

    # === Localization ===
    default_language = models.CharField(
        max_length=10,
        default="en",
        help_text=_("Default language code (ISO 639-1). Examples: en, ro, fr, de, es."),
    )
    available_languages = models.JSONField(
        default=list,
        blank=True,
        help_text=_help(
            "Available Languages",
            "List of language codes users can switch between. Leave empty for single-language sites.",
            '["en", "ro", "fr", "de"]',
        ),
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text=_("Default timezone for this site. Examples: UTC, Europe/Bucharest, America/New_York."),
    )

    # === Feature Flags ===
    features = models.JSONField(
        default=dict,
        blank=True,
        help_text=_help(
            "Feature Flags",
            "Toggle features on/off per site. Access in templates: {{ site_config.features.enable_blog }}",
            """{
  "enable_blog": true,
  "enable_shop": false,
  "enable_comments": true,
  "maintenance_mode": false,
  "beta_features": false
}""",
            keys=[
                ("enable_*", "Enable/disable specific features"),
                ("maintenance_mode", "Show maintenance page to non-staff users"),
                ("beta_features", "Enable experimental features"),
            ],
        ),
    )

    # === Integrations (Hybrid Security) ===
    integrations = models.JSONField(
        default=dict,
        blank=True,
        help_text=_help(
            "Third-Party Integrations",
            "API keys and configs for external services. Use 'env:VAR_NAME' for secrets (loaded from environment).",
            """{
  "google_analytics": {
    "id": "G-XXXXXXXXXX",
    "enabled": true
  },
  "stripe": {
    "public_key": "pk_live_xxx",
    "secret_key": "env:STRIPE_SECRET_KEY"
  },
  "sentry": {
    "dsn": "env:SENTRY_DSN"
  }
}""",
            keys=[
                ("google_analytics.id", "GA4 measurement ID"),
                ("stripe.public_key", "Stripe publishable key (safe to expose)"),
                ("stripe.secret_key", "Use env:VAR_NAME for secrets!"),
                ("sentry.dsn", "Sentry error tracking DSN"),
            ],
        ),
    )

    # === Email Settings ===
    email_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text=_help(
            "Email Configuration",
            "Customize email sender details for this site. Overrides default Django email settings.",
            """{
  "from_email": "noreply@mysite.com",
  "from_name": "My Site",
  "reply_to": "support@mysite.com"
}""",
            keys=[
                ("from_email", "Email address shown as sender"),
                ("from_name", "Display name for sender"),
                ("reply_to", "Reply-to address for user responses"),
            ],
        ),
    )

    # === Authentication Configuration ===
    AUTH_MODE_CHOICES = [
        ("isolated", _("Isolated - Each domain has its own users")),
        ("shared", _("Shared - Cross-domain authentication via auth domain")),
    ]
    auth_mode = models.CharField(
        max_length=20,
        choices=AUTH_MODE_CHOICES,
        default="isolated",
        help_text=_(
            "<strong>Isolated:</strong> Users are separate per domain. "
            "<strong>Shared:</strong> Single sign-on across domains via a central auth domain."
        ),
    )
    auth_domain = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="authenticated_sites",
        help_text=_(
            "For shared auth mode: select the SiteProfile that handles login. "
            "Users will be redirected there to authenticate, then back with a JWT token."
        ),
    )
    is_auth_domain = models.BooleanField(
        default=False,
        help_text=_(
            "Check this if this site is the central authentication provider. "
            "Other sites in shared mode will redirect here for login."
        ),
    )
    social_auth_providers = models.JSONField(
        default=list,
        blank=True,
        help_text=_help(
            "Social Auth Providers",
            "List of enabled OAuth providers. Must be configured in allauth settings.",
            '["google", "facebook", "github", "twitter"]',
        ),
    )
    auth_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text=_help(
            "Authentication Settings",
            "Fine-tune authentication behavior for this site.",
            """{
  "allow_registration": true,
  "require_email_verification": true,
  "login_redirect_url": "/dashboard/",
  "logout_redirect_url": "/",
  "session_cookie_age": 1209600
}""",
            keys=[
                ("allow_registration", "Allow new user signups (true/false)"),
                ("require_email_verification", "Require email verification before login"),
                ("login_redirect_url", "Where to redirect after successful login"),
                ("logout_redirect_url", "Where to redirect after logout"),
                ("session_cookie_age", "Session duration in seconds (1209600 = 2 weeks)"),
            ],
        ),
    )

    # === Extra Settings (Catch-all) ===
    extra_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text=_help(
            "Extra Settings",
            "Custom JSON settings including CORS/CSRF configuration. Access via site_config.extra_settings in code.",
            """{
  "frontend_address": "https://app.example.com",
  "cors_allowed_origins": ["https://app.example.com", "https://admin.example.com"],
  "csrf_trusted_origins": ["https://app.example.com"],
  "custom_footer_text": "© 2025 My Company",
  "support_email": "help@example.com"
}""",
            keys=[
                ("frontend_address", "Frontend/SPA URL for redirects and email links"),
                ("cors_allowed_origins", "List of origins allowed to make cross-origin requests"),
                ("csrf_trusted_origins", "List of origins trusted for CSRF validation"),
                ("*", "Any custom key-value pairs for site-specific needs"),
            ],
        ),
    )

    # === Status ===
    is_active = models.BooleanField(
        default=True,
        help_text=_("Inactive sites return 404. At least one site must remain active."),
    )
    is_primary = models.BooleanField(
        default=False,
        help_text=_("The primary/default site. Used when no domain matches. Only one site can be primary."),
    )
    path_prefix = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Development only: access this site via path prefix (e.g., '/mysite' for localhost:8000/mysite/). "
            "Leave empty for production domain-based routing."
        ),
    )

    class Meta:
        verbose_name = _("Site Profile")
        verbose_name_plural = _("Site Profiles")

    def __str__(self):
        return f"{self.site.domain} Profile"

    def clean(self):
        """Validate model before saving."""
        from urllib.parse import urlparse

        from django.core.exceptions import ValidationError

        # Prevent deactivating the last active site
        if not self.is_active and self.pk:
            active_count = SiteProfile.objects.filter(is_active=True).exclude(pk=self.pk).count()
            if active_count == 0:
                raise ValidationError(
                    {"is_active": _("Cannot deactivate the last active site. At least one site must remain active.")}
                )

        # If this is the only site, it must be primary
        if self.pk is None:  # New site
            if SiteProfile.objects.count() == 0:
                self.is_primary = True
        elif self.is_primary is False:
            # Check if this was the only primary
            other_primary = SiteProfile.objects.filter(is_primary=True).exclude(pk=self.pk).exists()
            if not other_primary:
                raise ValidationError({"is_primary": _("Cannot unset primary. At least one site must be primary.")})

        # Validate template_dir: it is joined into a filesystem path, so it must be a single
        # safe path segment to prevent path traversal (e.g. "../../etc").
        if self.template_dir:
            if len(self.template_dir) > TEMPLATE_DIR_MAX_LEN or not TEMPLATE_DIR_RE.match(self.template_dir):
                raise ValidationError(
                    {
                        "template_dir": _(
                            "template_dir may contain only lowercase letters, digits, hyphens, and "
                            "underscores (no dots or slashes), max %(max)d characters."
                        )
                        % {"max": TEMPLATE_DIR_MAX_LEN}
                    }
                )

        # Validate CORS/CSRF origins in extra_settings
        extra = self.extra_settings or {}
        self._validate_origins(extra.get("cors_allowed_origins"), "cors_allowed_origins", urlparse, ValidationError)
        self._validate_origins(extra.get("csrf_trusted_origins"), "csrf_trusted_origins", urlparse, ValidationError)
        self._validate_origin(extra.get("frontend_address"), "frontend_address", urlparse, ValidationError)

    def _validate_origin(self, origin, field_name, urlparse, ValidationError):
        """Validate a single origin URL for security."""
        if not origin:
            return

        if not isinstance(origin, str):
            raise ValidationError(
                {"extra_settings": _(f"{field_name} must be a string URL, not {type(origin).__name__}")}
            )

        if "*" in origin:
            raise ValidationError(
                {"extra_settings": _(f"{field_name}: Wildcards are not allowed for security reasons.")}
            )

        try:
            parsed = urlparse(origin)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(
                    {
                        "extra_settings": _(
                            f"{field_name}: '{origin}' is not a valid URL. Must include scheme (http/https)."
                        )
                    }
                )
            if parsed.scheme not in ("http", "https"):
                raise ValidationError({"extra_settings": _(f"{field_name}: '{origin}' must use http or https scheme.")})
            if parsed.path and parsed.path != "/":
                raise ValidationError(
                    {
                        "extra_settings": _(
                            f"{field_name}: '{origin}' should not include a path. Use origin only (e.g., https://example.com)."
                        )
                    }
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError({"extra_settings": _(f"{field_name}: '{origin}' is not a valid URL: {e}")}) from None

    def _validate_origins(self, origins, field_name, urlparse, ValidationError):
        """Validate a list of origin URLs for security."""
        if not origins:
            return

        if not isinstance(origins, list):
            raise ValidationError(
                {"extra_settings": _(f"{field_name} must be a list of URLs, not {type(origins).__name__}")}
            )

        for origin in origins:
            self._validate_origin(origin, field_name, urlparse, ValidationError)

    def save(self, *args, **kwargs):
        # Run validation
        self.full_clean()

        # Ensure only one primary site
        if self.is_primary:
            SiteProfile.objects.filter(is_primary=True).exclude(pk=self.pk).update(is_primary=False)

        is_new = self.pk is None
        super().save(*args, **kwargs)

        # Create template directory structure for new sites
        if is_new:
            self._create_template_directory()

    def _create_template_directory(self):
        """
        Create template directory structure for this site.

        Opt-in via SITES_AUTO_CREATE_TEMPLATE_DIRS = True (default False): filesystem
        writes at model-save time only land on the server that handled the save and
        pollute the project when the test suite runs, so this is disabled by default.

        Note: Only creates empty directories. Templates are NOT auto-generated
        because sites work fine with default framework templates via SiteTemplateLoader.
        Developers can add custom templates when needed.
        """
        import logging
        from pathlib import Path

        from django.conf import settings

        logger = logging.getLogger(__name__)

        if not getattr(settings, "SITES_AUTO_CREATE_TEMPLATE_DIRS", False):
            return

        template_dir_name = self.get_template_dir()

        # Defense in depth: re-validate the resolved directory name (which may derive from the
        # domain prefix, not just the validated template_dir field) before creating any
        # directories, so an unexpected value can never be joined into a traversal path.
        if len(template_dir_name) > TEMPLATE_DIR_MAX_LEN or not TEMPLATE_DIR_RE.match(template_dir_name):
            logger.warning("Skipping template directory creation for unsafe name: %r", template_dir_name)
            return

        base_template_dir = Path(settings.BASE_DIR) / "templates" / template_dir_name

        # Only create directory structure - no template files
        directories = [
            base_template_dir,
            base_template_dir / "web",
            base_template_dir / "web" / "components",
        ]

        for directory in directories:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created template directory: {directory}")

    def get_template_dir(self):
        """Returns template directory, defaulting to domain prefix."""
        if self.template_dir:
            return self.template_dir
        return self.site.domain.split(".")[0]

    def to_config_dict(self):
        """
        Convert to configuration dict for middleware/caching.
        This is the structure stored in Redis and attached to request.site_config.
        """
        config = {
            # Core
            "site_id": self.site.id,
            "domain": self.site.domain,
            "site_name": self.site_name,
            "tagline": self.tagline,
            # Branding
            "template_dir": self.get_template_dir(),
            "theme": self.theme,
            "logo_url": self.logo.url if self.logo else None,
            "favicon_url": self.favicon.url if self.favicon else None,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            # SEO
            "meta_defaults": self.meta_defaults or {},
            "head_scripts": self.head_scripts or [],
            "body_scripts": self.body_scripts or [],
            "custom_css": self.custom_css,
            # Localization
            "default_language": self.default_language,
            "available_languages": self.available_languages or [],
            "timezone": self.timezone,
            # Features
            "features": self.features or {},
            # Integrations: stored UNRESOLVED (env: placeholders kept intact) so that
            # resolved secrets never sit in the Redis cache or leak into template context.
            # Server-side consumers resolve lazily via get_integration() /
            # resolve_integration(config, name).
            "integrations": self.integrations or {},
            # Email
            "email_settings": self.email_settings or {},
            # Authentication
            "auth_mode": self.auth_mode,
            "is_auth_domain": self.is_auth_domain,
            "auth_domain_url": self.auth_domain.site.domain if self.auth_domain else None,
            "auth_domain_id": self.auth_domain.site.id if self.auth_domain else None,
            "social_auth_providers": self.social_auth_providers or [],
            "auth_settings": self.auth_settings or {},
            # Status
            "is_active": self.is_active,
            "is_primary": self.is_primary,
            "path_prefix": self.path_prefix,
            # Extra
            "extra_settings": self.extra_settings or {},
        }

        return config

    def _resolve_integrations(self):
        """Resolve env: references in this profile's integrations."""
        return _resolve_env_values(self.integrations)

    def get_feature(self, name, default=False):
        """Check if a feature is enabled."""
        return (self.features or {}).get(name, default)

    def get_integration(self, name):
        """Get resolved integration config."""
        return self._resolve_integrations().get(name, {})

    def get_auth_setting(self, name, default=None):
        """Get an auth setting value."""
        return (self.auth_settings or {}).get(name, default)

    def get_meta(self, name, default=""):
        """Get a meta default value."""
        return (self.meta_defaults or {}).get(name, default)

    def to_public_config_dict(self):
        """
        Convert to public-safe configuration dict for API exposure.

        This is a filtered subset of to_config_dict() that excludes sensitive fields
        like integrations (API keys), auth_settings, email_settings, etc.

        Use this for:
        - REST API responses
        - Mobile app configuration
        - Any client-side exposure

        Returns:
            dict: Public-safe site configuration
        """
        return {
            # Core
            "site_id": self.site.id,
            "site_name": self.site_name,
            "tagline": self.tagline,
            # Branding
            "theme": self.theme,
            "logo_url": self.logo.url if self.logo else None,
            "favicon_url": self.favicon.url if self.favicon else None,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            # Features (safe to expose)
            "features": self.features or {},
            # Localization
            "default_language": self.default_language,
            "available_languages": self.available_languages or [],
            # Public meta (filtered - no internal SEO configs)
            "meta_defaults": {
                k: v
                for k, v in (self.meta_defaults or {}).items()
                if k in ("title_suffix", "description", "og:image", "twitter:card")
            },
            # NOTE: Explicitly excluded for security:
            # - integrations (contains API keys)
            # - auth_settings (internal config)
            # - email_settings (SMTP credentials)
            # - auth_domain_url, auth_domain_id, is_auth_domain (internal routing)
            # - extra_settings (may contain sensitive data)
            # - template_dir, path_prefix (internal)
            # - head_scripts, body_scripts, custom_css (XSS risk if exposed via API)
        }

    def to_branding_dict(self):
        """
        Lightweight branding-only configuration for bandwidth-sensitive clients.

        Returns:
            dict: Minimal branding configuration
        """
        return {
            "site_name": self.site_name,
            "theme": self.theme,
            "logo_url": self.logo.url if self.logo else None,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
        }

    def to_features_dict(self):
        """
        Feature flags only.

        Returns:
            dict: Feature flags configuration
        """
        return self.features or {}


class SiteMember(BaseModel):
    """
    Links a User to a SiteProfile with a specific role.

    Allows users to be members of multiple sites with different access levels.
    Used for API access control and site management permissions.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", _("Admin")
        VIEWER = "viewer", _("Viewer")

    site_profile = models.ForeignKey(
        SiteProfile,
        on_delete=models.CASCADE,
        related_name="members",
        help_text=_("The site this membership belongs to."),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="site_memberships",
        help_text=_("The user who has access to this site."),
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        help_text=_("User's role on this site. Admin has full access, Viewer is read-only."),
    )
    is_owner = models.BooleanField(
        default=False,
        help_text=_("If true, this user is the site owner and cannot be removed."),
    )

    class Meta:
        verbose_name = _("Site Member")
        verbose_name_plural = _("Site Members")
        unique_together = [("site_profile", "user")]
        ordering = ["-is_owner", "role", "user__email"]

    def __str__(self):
        return f"{self.user.email} - {self.site_profile.site.domain} ({self.role})"

    def clean(self):
        """Validate member data before saving."""
        from django.core.exceptions import ValidationError

        # Prevent demoting or removing owners
        if self.pk:
            try:
                original = SiteMember.objects.get(pk=self.pk)
                if original.is_owner and not self.is_owner:
                    raise ValidationError({"is_owner": _("Cannot remove owner status. Transfer ownership first.")})
                if original.is_owner and self.role != self.Role.ADMIN:
                    raise ValidationError({"role": _("Site owner must be an admin.")})
            except SiteMember.DoesNotExist:
                pass

    def save(self, *args, **kwargs):
        # Validate FIRST to catch invalid operations like demoting owner
        self.full_clean()
        # Owner must always be admin (auto-correct for new records)
        if self.is_owner:
            self.role = self.Role.ADMIN
        super().save(*args, **kwargs)
