"""
Admin interface for Site configuration management.
"""

from django.contrib import admin, messages
from django.contrib.sites.admin import SiteAdmin
from django.contrib.sites.models import Site
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

try:
    # Optional integration: the API-key app is not part of the free boilerplate.
    from apps.api.models import UserAPIKey
except ImportError:
    UserAPIKey = None
from apps.sites.audit import SiteAuditLog
from apps.sites.cache import warm_site_cache
from apps.sites.models import SiteMember, SiteProfile


def create_api_key_for_member(user, site_profile):
    """
    Create an API key for a user if they don't have one.
    Returns (api_key_instance, key_string) or (None, None) if user already has a key
    or the API-key app is not installed.
    """
    if UserAPIKey is None:
        return None, None
    existing_key = UserAPIKey.objects.filter(user=user, revoked=False).first()
    if existing_key:
        return None, None

    return UserAPIKey.objects.create_key(
        name=f"Site Access - {site_profile.site_name}",
        user=user,
    )


class SiteProfileInline(admin.StackedInline):
    """
    Inline admin for SiteProfile on the Site admin page.
    """

    model = SiteProfile
    can_delete = False
    verbose_name_plural = _("Site Profile")
    fk_name = "site"

    class Media:
        css = {"all": ("admin/sites/css/admin.css",)}

    fieldsets = (
        (
            _("Branding"),
            {
                "fields": (
                    "site_name",
                    "tagline",
                    "theme",
                    "template_dir",
                    ("logo", "favicon"),
                    ("primary_color", "secondary_color"),
                ),
            },
        ),
        (
            _("SEO & Meta"),
            {
                "fields": ("meta_defaults",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Scripts & Styles"),
            {
                "fields": ("head_scripts", "body_scripts", "custom_css"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Localization"),
            {
                "fields": ("default_language", "available_languages", "timezone"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Features & Integrations"),
            {
                "fields": ("features", "integrations"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Email Settings"),
            {
                "fields": ("email_settings",),
                "classes": ("collapse",),
            },
        ),
        (
            _("Authentication"),
            {
                "fields": (
                    "auth_mode",
                    "auth_domain",
                    "is_auth_domain",
                    "social_auth_providers",
                    "auth_settings",
                ),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active", "is_primary", "path_prefix"),
            },
        ),
        (
            _("CORS/CSRF & Extra Settings"),
            {
                "fields": ("extra_settings",),
                "classes": ("collapse",),
                "description": _(
                    "Configure per-site CORS and CSRF origins here. "
                    "These override global settings from .env for this site only."
                ),
            },
        ),
    )


class ExtendedSiteAdmin(SiteAdmin):
    """
    Extended Site admin with SiteProfile inline.
    """

    inlines = [SiteProfileInline]
    list_display = ["domain", "name", "get_is_active", "get_is_primary", "get_auth_mode"]
    list_filter = ["profile__is_active", "profile__is_primary", "profile__auth_mode"]
    search_fields = ["domain", "name", "profile__site_name"]
    actions = ["refresh_cache", "warm_all_caches"]

    def response_add(self, request, obj, post_url_continue=None):
        """Show setup instructions after creating a new site."""
        response = super().response_add(request, obj, post_url_continue)

        # Show setup instructions for the new site
        if hasattr(obj, "profile"):
            template_dir = obj.profile.get_template_dir()
            setup_message = format_html(
                "<strong>Next steps to set up this site:</strong><br>"
                "1. <strong>Create app:</strong> <code>python manage.py startapp {0} apps/{0}</code><br>"
                "2. <strong>Templates:</strong> <code>mkdir -p templates/{0}/web/components</code><br>"
                "3. <strong>Add to INSTALLED_APPS</strong> and include URLs in urls.py<br>"
                "4. <strong>Dev testing:</strong> Set path_prefix='{0}' to access via /{0}/<br>"
                "See docs/multi-domain.md for full guide.",
                template_dir,
            )
            self.message_user(request, setup_message, messages.WARNING)

        return response

    def get_is_active(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.is_active
        return None

    get_is_active.short_description = _("Active")
    get_is_active.boolean = True

    def get_is_primary(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.is_primary
        return None

    get_is_primary.short_description = _("Primary")
    get_is_primary.boolean = True

    def get_auth_mode(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.auth_mode
        return None

    get_auth_mode.short_description = _("Auth Mode")

    @admin.action(description=_("Refresh cache for selected sites"))
    def refresh_cache(self, request, queryset):
        from apps.sites.cache import invalidate_site_cache

        count = 0
        for site in queryset:
            invalidate_site_cache(site_id=site.id, domain=site.domain)
            count += 1
        self.message_user(request, _("Refreshed cache for %d sites") % count, messages.SUCCESS)

    @admin.action(description=_("Warm all site caches"))
    def warm_all_caches(self, request, queryset):
        count = warm_site_cache()
        self.message_user(request, _("Warmed cache for %d sites") % count, messages.SUCCESS)


# Re-register Site with extended admin
admin.site.unregister(Site)
admin.site.register(Site, ExtendedSiteAdmin)


# === Site Member Admin ===


class SiteMemberInline(admin.TabularInline):
    """
    Inline admin for managing site members on the SiteProfile admin page.
    """

    model = SiteMember
    extra = 1
    autocomplete_fields = ["user"]
    readonly_fields = ["created_at"]
    fields = ["user", "role", "is_owner", "created_at"]

    def has_delete_permission(self, request, obj=None):
        # Allow deletion but model validation will prevent owner removal
        return True


@admin.register(SiteMember)
class SiteMemberAdmin(admin.ModelAdmin):
    """
    Standalone admin for SiteMember model.

    Automatically creates an API key for new members if they don't have one.
    """

    list_display = ["user", "site_profile", "role", "is_owner", "has_api_key", "created_at"]
    list_filter = ["role", "is_owner", "site_profile"]
    search_fields = ["user__email", "user__username", "site_profile__site__domain"]
    autocomplete_fields = ["user", "site_profile"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["create_api_keys"]

    fieldsets = (
        (
            None,
            {
                "fields": ("site_profile", "user", "role", "is_owner"),
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_api_key(self, obj):
        """Show if user has an active API key ('-' when the API-key app is absent)."""
        if UserAPIKey is None:
            return "-"
        return UserAPIKey.objects.filter(user=obj.user, revoked=False).exists()

    has_api_key.short_description = _("API Key")
    # Render as a boolean icon only when the API-key app is installed; otherwise the
    # method returns "-" and must be shown as plain text (boolean rendering would crash).
    has_api_key.boolean = UserAPIKey is not None

    def save_model(self, request, obj, form, change):
        """Create API key for new members."""
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)

        if is_new:
            api_key, key_string = create_api_key_for_member(obj.user, obj.site_profile)
            if key_string:
                self.message_user(
                    request,
                    format_html(
                        "<strong>API Key created for {}</strong><br>"
                        '<code style="background: #f0f0f0; padding: 5px; font-size: 14px;">{}</code><br>'
                        '<span style="color: red;">Copy this key now - it will not be shown again!</span>',
                        obj.user.email,
                        key_string,
                    ),
                    messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    f"User {obj.user.email} already has an API key.",
                    messages.INFO,
                )

    @admin.action(description=_("Create API keys for selected members"))
    def create_api_keys(self, request, queryset):
        """Admin action to create API keys for members who don't have one."""
        if UserAPIKey is None:
            self.message_user(request, _("API-key app not installed."), messages.WARNING)
            return
        created = 0
        already_have = 0
        for member in queryset:
            api_key, key_string = create_api_key_for_member(member.user, member.site_profile)
            if key_string:
                self.message_user(
                    request,
                    format_html(
                        "<strong>API Key for {}:</strong> <code>{}</code>",
                        member.user.email,
                        key_string,
                    ),
                    messages.SUCCESS,
                )
                created += 1
            else:
                already_have += 1

        if already_have > 0:
            self.message_user(
                request,
                f"{already_have} member(s) already have API keys.",
                messages.INFO,
            )


@admin.register(SiteProfile)
class SiteProfileAdmin(admin.ModelAdmin):
    """
    Standalone admin for SiteProfile with member management.

    Automatically creates API keys for new members added via inline.
    """

    list_display = ["site", "site_name", "is_active", "is_primary", "auth_mode", "member_count"]
    list_filter = ["is_active", "is_primary", "auth_mode"]
    search_fields = ["site__domain", "site_name"]
    autocomplete_fields = ["auth_domain"]
    inlines = [SiteMemberInline]

    def member_count(self, obj):
        return obj.members.count()

    member_count.short_description = _("Members")

    def save_formset(self, request, form, formset, change):
        """Create API keys for new members added via inline."""
        instances = formset.save(commit=False)

        # Track which instances are new
        new_members = []
        for instance in instances:
            is_new = instance.pk is None
            instance.save()
            if is_new and isinstance(instance, SiteMember):
                new_members.append(instance)

        formset.save_m2m()

        # Handle deletions
        for obj in formset.deleted_objects:
            obj.delete()

        # Create API keys for new members
        for member in new_members:
            api_key, key_string = create_api_key_for_member(member.user, member.site_profile)
            if key_string:
                self.message_user(
                    request,
                    format_html(
                        "<strong>API Key created for {}</strong><br>"
                        '<code style="background: #f0f0f0; padding: 5px; font-size: 14px;">{}</code><br>'
                        '<span style="color: red;">Copy this key now - it will not be shown again!</span>',
                        member.user.email,
                        key_string,
                    ),
                    messages.WARNING,
                )
            else:
                self.message_user(
                    request,
                    f"User {member.user.email} already has an API key.",
                    messages.INFO,
                )


# === Audit Log Admin ===


@admin.register(SiteAuditLog)
class SiteAuditLogAdmin(admin.ModelAdmin):
    """
    Read-only admin for viewing site configuration audit logs.
    """

    list_display = [
        "created_at",
        "site_domain",
        "action",
        "user_email",
        "get_changed_fields",
        "ip_address",
    ]
    list_filter = ["action", "site_domain", "created_at"]
    search_fields = ["site_domain", "user_email", "notes"]
    readonly_fields = [
        "site_id",
        "site_domain",
        "action",
        "user",
        "user_email",
        "ip_address",
        "changes",
        "previous_values",
        "new_values",
        "notes",
        "created_at",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        (
            _("Event"),
            {
                "fields": ("site_domain", "site_id", "action", "created_at"),
            },
        ),
        (
            _("User"),
            {
                "fields": ("user", "user_email", "ip_address"),
            },
        ),
        (
            _("Changes"),
            {
                "fields": ("changes", "previous_values", "new_values", "notes"),
            },
        ),
    )

    def get_changed_fields(self, obj):
        """Display changed fields as a comma-separated list."""
        if obj.changes and "fields" in obj.changes:
            fields = obj.changes["fields"]
            if len(fields) > 3:
                return f"{', '.join(fields[:3])} +{len(fields) - 3} more"
            return ", ".join(fields)
        return "-"

    get_changed_fields.short_description = _("Changed Fields")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete audit logs
        return request.user.is_superuser
