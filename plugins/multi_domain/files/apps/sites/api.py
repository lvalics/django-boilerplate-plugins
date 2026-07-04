"""
REST API views for Site Configuration.

Public endpoints expose public-safe site configuration for:
- Mobile applications
- Standalone React SPAs
- Third-party integrations

Management endpoints require authentication (session or API key):
- List sites user has access to
- CRUD operations on sites (admin only)
- Member management (admin only)

The site is determined by the request's Host header, which is resolved
by MultiDomainMiddleware before these views are called.

Security:
- Public endpoints are rate limited (60/minute per IP)
- Management endpoints are rate limited per user
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView


class PublicAPIThrottle(AnonRateThrottle):
    """Rate limit for public API endpoints: 60/minute per IP."""

    rate = "60/m"


class AuthenticatedAPIThrottle(UserRateThrottle):
    """Rate limit for authenticated API endpoints: 120/minute per user."""

    rate = "120/m"

try:
    # Optional integration: the API-key app is not part of the free boilerplate.
    from apps.api.permissions import IsAuthenticatedOrHasUserAPIKey
except ImportError:
    # Session-auth fallback when the API-key app is absent.
    from rest_framework.permissions import IsAuthenticated as IsAuthenticatedOrHasUserAPIKey
from apps.sites.models import SiteMember, SiteProfile
from apps.sites.permissions import HasSiteAccess, HasSiteAdminAccess
from apps.sites.serializers import (
    PublicSiteConfigSerializer,
    SiteBrandingSerializer,
    SiteDetailSerializer,
    SiteFeaturesSerializer,
    SiteFeaturesUpdateSerializer,
    SiteListSerializer,
    SiteMemberCreateResponseSerializer,
    SiteMemberCreateSerializer,
    SiteMemberSerializer,
    SiteMemberUpdateSerializer,
    SiteUpdateSerializer,
)


class SiteConfigAPIView(APIView):
    """
    GET /api/sites/config/

    Returns public site configuration for the current domain.

    The domain is determined by the request Host header and resolved
    by MultiDomainMiddleware. No authentication required.

    Response includes:
    - site_id, site_name, tagline
    - theme, colors, logo
    - feature flags
    - language settings
    - public meta defaults

    Excludes (for security):
    - integrations (API keys)
    - auth_settings
    - email_settings
    - scripts/CSS (XSS risk)
    """

    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        site_config = getattr(request, "site_config", None)

        if not site_config:
            return Response({"error": "Site configuration not found"}, status=404)

        # Get the SiteProfile to use its public config method
        try:
            profile = SiteProfile.objects.select_related("site").get(site_id=site_config.get("site_id"))
            data = profile.to_public_config_dict()
        except SiteProfile.DoesNotExist:
            return Response({"error": "Site profile not found"}, status=404)

        serializer = PublicSiteConfigSerializer(data)
        response = Response(serializer.data)

        # Add cache headers for CDN/browser caching
        # 5 minutes cache, vary by Host for multi-domain support
        response["Cache-Control"] = "public, max-age=300"
        response["Vary"] = "Host"

        return response


class SiteBrandingAPIView(APIView):
    """
    GET /api/sites/branding/

    Returns lightweight branding-only configuration.

    Use for bandwidth-sensitive clients that only need:
    - site_name
    - theme
    - logo_url
    - primary_color
    - secondary_color
    """

    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        site_config = getattr(request, "site_config", None)

        if not site_config:
            return Response({"error": "Site configuration not found"}, status=404)

        try:
            profile = SiteProfile.objects.select_related("site").get(site_id=site_config.get("site_id"))
            data = profile.to_branding_dict()
        except SiteProfile.DoesNotExist:
            return Response({"error": "Site profile not found"}, status=404)

        serializer = SiteBrandingSerializer(data)
        response = Response(serializer.data)

        response["Cache-Control"] = "public, max-age=300"
        response["Vary"] = "Host"

        return response


class SiteFeaturesAPIView(APIView):
    """
    GET /api/sites/features/

    Returns feature flags only.

    Response is a flat dictionary of feature flag names to boolean values:
    {
        "enable_blog": true,
        "enable_chat": false,
        "maintenance_mode": false
    }
    """

    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIThrottle]

    def get(self, request):
        site_config = getattr(request, "site_config", None)

        if not site_config:
            return Response({"error": "Site configuration not found"}, status=404)

        try:
            profile = SiteProfile.objects.get(site_id=site_config.get("site_id"))
            data = profile.to_features_dict()
        except SiteProfile.DoesNotExist:
            return Response({"error": "Site profile not found"}, status=404)

        serializer = SiteFeaturesSerializer(data)
        response = Response(serializer.data)

        response["Cache-Control"] = "public, max-age=300"
        response["Vary"] = "Host"

        return response


# === Error Handling ===


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
def invalid_site_id_view(request):
    """
    Return a 400 error when site_id is missing or empty in management URLs.

    This catches URLs like /api/sites/manage//members/ where site_id is empty.
    """
    return Response(
        {
            "detail": "site_id is required. Use GET /api/sites/manage/ to list available sites.",
            "error": "missing_site_id",
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


# === Management API (authenticated) ===


@extend_schema_view(
    list=extend_schema(
        operation_id="sites_list",
        summary="List sites user has access to",
        description="Returns all sites the authenticated user has access to. Superusers see all active sites.",
    ),
    retrieve=extend_schema(
        operation_id="sites_retrieve",
        summary="Get site details",
        description="Returns full site configuration for users with access.",
    ),
    update=extend_schema(
        operation_id="sites_update",
        summary="Update site configuration",
        description="Update site settings. Requires admin role.",
    ),
    partial_update=extend_schema(
        operation_id="sites_partial_update",
        summary="Partially update site configuration",
        description="Partially update site settings. Requires admin role.",
    ),
)
class SiteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for site management.

    Supports:
    - List sites user has access to
    - Retrieve site details (any member)
    - Update site configuration (admin only)
    - Feature flag updates (admin only)
    - Member management (admin only)
    """

    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]
    throttle_classes = [AuthenticatedAPIThrottle]

    def get_permissions(self):
        """
        Assign permissions based on action:
        - list: authenticated (shows only accessible sites)
        - retrieve: HasSiteAccess
        - update/partial_update: HasSiteAdminAccess
        - member actions: HasSiteAdminAccess
        """
        if self.action == "list":
            return [IsAuthenticatedOrHasUserAPIKey()]
        elif self.action == "retrieve":
            return [IsAuthenticatedOrHasUserAPIKey(), HasSiteAccess()]
        else:
            return [IsAuthenticatedOrHasUserAPIKey(), HasSiteAdminAccess()]

    def get_queryset(self):
        """Filter sites based on user access."""
        user = self.request.user

        if not user.is_authenticated:
            return SiteProfile.objects.none()

        if user.is_superuser:
            return SiteProfile.objects.filter(is_active=True).select_related("site").order_by("-is_primary", "id")

        return (
            SiteProfile.objects.filter(members__user=user, is_active=True)
            .select_related("site")
            .order_by("-is_primary", "id")
            .distinct()
        )

    def get_serializer_class(self):
        if self.action == "list":
            return SiteListSerializer
        elif self.action in ["update", "partial_update"]:
            return SiteUpdateSerializer
        return SiteDetailSerializer

    def get_object(self):
        """
        Override to handle invalid site_id values gracefully.

        Returns 400 for non-numeric site_id instead of 500 ValueError.
        """
        pk = self.kwargs.get("pk")

        # Validate pk is a valid integer
        try:
            int(pk)
        except (ValueError, TypeError):
            from rest_framework.exceptions import ValidationError

            raise ValidationError(
                {
                    "detail": f"Invalid site_id: '{pk}'. Must be a valid integer.",
                    "error": "invalid_site_id",
                }
            ) from None

        return super().get_object()

    @extend_schema(
        operation_id="sites_update_features",
        summary="Update feature flags",
        description="Merge provided feature flags with existing. Requires admin role.",
        request=SiteFeaturesUpdateSerializer,
        responses={200: SiteDetailSerializer},
    )
    @action(detail=True, methods=["patch"], url_path="features")
    def update_features(self, request, pk=None):
        """PATCH /api/sites/{id}/features/ - Update feature flags."""
        site = self.get_object()

        serializer = SiteFeaturesUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Merge with existing features
        current_features = site.features or {}
        current_features.update(serializer.validated_data["features"])
        site.features = current_features
        site.save(update_fields=["features", "updated_at"])

        return Response(SiteDetailSerializer(site, context={"request": request}).data)

    # === Member Management Actions ===

    @extend_schema(
        operation_id="sites_list_members",
        summary="List site members",
        description="List all members of a site. Requires admin role.",
        responses={200: SiteMemberSerializer(many=True)},
    )
    @action(detail=True, methods=["get"], url_path="members")
    def list_members(self, request, pk=None):
        """GET /api/sites/{id}/members/ - List site members."""
        site = self.get_object()
        members = site.members.select_related("user").all()
        serializer = SiteMemberSerializer(members, many=True)
        return Response(serializer.data)

    @extend_schema(
        operation_id="sites_add_member",
        summary="Add site member",
        description="Add a user as a site member by email. Requires admin role. "
        "Automatically creates an API key for the user if they don't have one. "
        "The API key is returned in the response (shown only once).",
        request=SiteMemberCreateSerializer,
        responses={201: SiteMemberCreateResponseSerializer},
    )
    @action(detail=True, methods=["post"], url_path="members/add")
    def add_member(self, request, pk=None):
        """POST /api/sites/{id}/members/add/ - Add a member with auto-created API key."""
        site = self.get_object()

        serializer = SiteMemberCreateSerializer(data=request.data, context={"request": request, "site_profile": site})
        serializer.is_valid(raise_exception=True)
        member = serializer.save()

        # Use response serializer that includes the API key
        return Response(SiteMemberCreateResponseSerializer(member).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        operation_id="sites_update_member",
        summary="Update site member",
        description="Update a member's role. Requires admin role. Cannot demote owner.",
        request=SiteMemberUpdateSerializer,
        responses={200: SiteMemberSerializer},
    )
    @action(detail=True, methods=["patch"], url_path=r"members/(?P<user_id>\d+)")
    def update_member(self, request, pk=None, user_id=None):
        """PATCH /api/sites/{id}/members/{user_id}/ - Update member role."""
        site = self.get_object()
        member = get_object_or_404(site.members, user_id=user_id)

        serializer = SiteMemberUpdateSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(SiteMemberSerializer(member).data)

    @extend_schema(
        operation_id="sites_remove_member",
        summary="Remove site member",
        description="Remove a member from the site. Requires admin role. Cannot remove owner.",
        responses={204: None},
    )
    @action(detail=True, methods=["delete"], url_path=r"members/(?P<user_id>\d+)/remove")
    def remove_member(self, request, pk=None, user_id=None):
        """DELETE /api/sites/{id}/members/{user_id}/remove/ - Remove a member."""
        site = self.get_object()
        member = get_object_or_404(site.members, user_id=user_id)

        if member.is_owner:
            return Response({"detail": "Cannot remove the site owner."}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent removal of last admin
        admin_count = site.members.filter(role=SiteMember.Role.ADMIN).count()
        if member.role == SiteMember.Role.ADMIN and admin_count <= 1:
            return Response({"detail": "Cannot remove the last admin."}, status=status.HTTP_400_BAD_REQUEST)

        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
