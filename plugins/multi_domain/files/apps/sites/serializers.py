"""
Serializers for Site Configuration API.

These serializers expose public-safe site configuration for:
- Mobile applications
- Standalone React SPAs
- Third-party integrations

SECURITY NOTE: These serializers intentionally exclude sensitive fields.
See SiteProfile.to_public_config_dict() for the filtering logic.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.sites.models import SiteMember, SiteProfile

User = get_user_model()


class PublicSiteConfigSerializer(serializers.Serializer):
    """
    Full public site configuration.

    Excludes sensitive fields:
    - integrations (API keys)
    - auth_settings (internal config)
    - email_settings (SMTP credentials)
    - head_scripts, body_scripts, custom_css (XSS risk)
    """

    site_id = serializers.IntegerField(read_only=True)
    site_name = serializers.CharField(read_only=True)
    tagline = serializers.CharField(read_only=True, allow_blank=True)
    theme = serializers.CharField(read_only=True)
    logo_url = serializers.CharField(read_only=True, allow_null=True)
    favicon_url = serializers.CharField(read_only=True, allow_null=True)
    primary_color = serializers.CharField(read_only=True)
    secondary_color = serializers.CharField(read_only=True)
    features = serializers.DictField(read_only=True)
    default_language = serializers.CharField(read_only=True)
    available_languages = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
    )
    meta_defaults = serializers.DictField(read_only=True)


class SiteBrandingSerializer(serializers.Serializer):
    """
    Lightweight branding-only configuration.

    Use for bandwidth-sensitive clients that only need theming info.
    """

    site_name = serializers.CharField(read_only=True)
    theme = serializers.CharField(read_only=True)
    logo_url = serializers.CharField(read_only=True, allow_null=True)
    primary_color = serializers.CharField(read_only=True)
    secondary_color = serializers.CharField(read_only=True)


class SiteFeaturesSerializer(serializers.Serializer):
    """
    Feature flags only.

    Dynamic serializer that passes through all feature flags.
    """

    def to_representation(self, instance):
        """Pass through the features dict directly."""
        return instance


# === Management API Serializers ===


class SiteListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing sites user has access to.
    """

    domain = serializers.CharField(source="site.domain", read_only=True)
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = SiteProfile
        fields = [
            "id",
            "domain",
            "site_name",
            "tagline",
            "theme",
            "logo",
            "is_active",
            "is_primary",
            "user_role",
        ]
        read_only_fields = fields

    def get_user_role(self, obj):
        """Get the requesting user's role for this site."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if request.user.is_superuser:
            return "superuser"
        try:
            membership = obj.members.get(user=request.user)
            return membership.role
        except SiteMember.DoesNotExist:
            return None


class SiteDetailSerializer(serializers.ModelSerializer):
    """
    Full site configuration for authorized users.
    """

    domain = serializers.CharField(source="site.domain", read_only=True)
    user_role = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = SiteProfile
        fields = [
            "id",
            "domain",
            "site_name",
            "tagline",
            "theme",
            "template_dir",
            "logo",
            "favicon",
            "primary_color",
            "secondary_color",
            "meta_defaults",
            "default_language",
            "available_languages",
            "timezone",
            "features",
            "auth_mode",
            "is_auth_domain",
            "social_auth_providers",
            "is_active",
            "is_primary",
            "path_prefix",
            "user_role",
            "member_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "domain",
            "user_role",
            "member_count",
            "created_at",
            "updated_at",
        ]

    def get_user_role(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if request.user.is_superuser:
            return "superuser"
        try:
            membership = obj.members.get(user=request.user)
            return membership.role
        except SiteMember.DoesNotExist:
            return None

    def get_member_count(self, obj):
        return obj.members.count()


class SiteAdminUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for site admins (non-superusers) updating a site.

    Restricted to branding, SEO, localization, and feature fields. Security-critical
    fields (scripts, custom_css, extra_settings, auth_*, integrations, email_settings,
    is_active, is_primary, path_prefix, template_dir) are intentionally excluded and can
    only be edited by superusers via SiteUpdateSerializer. See the ViewSet's
    get_serializer_class, which selects the serializer by request.user.is_superuser.
    """

    class Meta:
        model = SiteProfile
        fields = [
            "site_name",
            "tagline",
            "theme",
            "logo",
            "favicon",
            "primary_color",
            "secondary_color",
            "meta_defaults",
            "default_language",
            "available_languages",
            "timezone",
            "features",
        ]


class SiteUpdateSerializer(serializers.ModelSerializer):
    """
    Full update serializer for superusers only.

    Includes security-critical fields (scripts, custom_css, extra_settings, auth_*,
    integrations, email_settings, is_active, path_prefix, template_dir). The ViewSet
    only hands this serializer to superusers; site admins get SiteAdminUpdateSerializer.
    """

    class Meta:
        model = SiteProfile
        fields = [
            "site_name",
            "tagline",
            "theme",
            "template_dir",
            "logo",
            "favicon",
            "primary_color",
            "secondary_color",
            "meta_defaults",
            "head_scripts",
            "body_scripts",
            "custom_css",
            "default_language",
            "available_languages",
            "timezone",
            "features",
            "integrations",
            "email_settings",
            "auth_mode",
            "auth_domain",
            "is_auth_domain",
            "social_auth_providers",
            "auth_settings",
            "extra_settings",
            "is_active",
            "path_prefix",
        ]


class SiteFeaturesUpdateSerializer(serializers.Serializer):
    """
    Serializer for partial feature flag updates.
    Accepts a dict and merges with existing features.
    """

    features = serializers.DictField(
        child=serializers.BooleanField(),
        help_text="Feature flags to update. Will be merged with existing.",
    )


# === Member Management Serializers ===


class SiteMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for listing/reading site members.
    """

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = SiteMember
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "role",
            "is_owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_email", "user_name", "is_owner", "created_at", "updated_at"]

    def get_user_name(self, obj):
        return obj.user.get_display_name() if hasattr(obj.user, "get_display_name") else str(obj.user)


class SiteMemberCreateSerializer(serializers.Serializer):
    """
    Serializer for adding a new site member.

    Adds an existing user to the site with a role. API-key provisioning is intentionally
    NOT part of this path: minting/returning a plaintext key for an arbitrary user here
    would allow account takeover. API keys are provisioned only via the Django admin
    (superuser) flow.
    """

    email = serializers.EmailField(help_text="Email of the user to add.")
    role = serializers.ChoiceField(
        choices=SiteMember.Role.choices,
        default=SiteMember.Role.VIEWER,
    )

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist as err:
            raise serializers.ValidationError("User with this email does not exist.") from err

        # Store the user for create()
        self._user = user
        return value

    def validate(self, attrs):
        site_profile = self.context.get("site_profile")
        if not site_profile:
            raise serializers.ValidationError("Site profile not provided.")

        # Check if already a member
        if SiteMember.objects.filter(site_profile=site_profile, user=self._user).exists():
            raise serializers.ValidationError({"email": "This user is already a member of this site."})

        return attrs

    def create(self, validated_data):
        site_profile = self.context["site_profile"]

        # Create the site member. No API key is minted here (see class docstring).
        return SiteMember.objects.create(
            site_profile=site_profile,
            user=self._user,
            role=validated_data["role"],
        )


class SiteMemberCreateResponseSerializer(serializers.ModelSerializer):
    """
    Response serializer for a newly created site member.

    Does NOT expose an API key: key provisioning is not part of the member-add API path.
    """

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = SiteMember
        fields = [
            "id",
            "user_id",
            "email",
            "user_name",
            "role",
            "is_owner",
            "created_at",
        ]

    def get_user_name(self, obj):
        return obj.user.get_display_name() if hasattr(obj.user, "get_display_name") else str(obj.user)


class SiteMemberUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a site member's role.
    """

    class Meta:
        model = SiteMember
        fields = ["role"]

    def validate_role(self, value):
        if self.instance and self.instance.is_owner and value != SiteMember.Role.ADMIN:
            raise serializers.ValidationError("Site owner must remain an admin.")
        return value
