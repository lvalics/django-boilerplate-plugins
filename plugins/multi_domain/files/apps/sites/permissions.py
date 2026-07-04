"""
Permission classes for site access control.

These permissions work with both session authentication and API keys
by checking the user attached to the request (populated by HasUserAPIKey).
"""

from rest_framework.permissions import BasePermission

from apps.sites.models import SiteMember, SiteProfile


class IsSuperUser(BasePermission):
    """
    Allow only authenticated superusers.

    Used to gate site create/destroy: creating or deleting a SiteProfile is a
    superuser-only operation. Site admins must not be able to fall back through
    request.site_config to create or destroy sites.
    """

    message = "Only superusers may perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class HasSiteAccess(BasePermission):
    """
    Check if the authenticated user has any access to the requested site.

    Works with both session auth and API keys (API keys inherit user access).
    Superusers have access to all sites.

    Expects either:
    - pk in view kwargs (URL parameter for /api/sites/{pk}/)
    - site_pk in view kwargs
    - request.site_config (from middleware, for current domain)
    """

    message = "You do not have access to this site."

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers bypass all checks
        if request.user.is_superuser:
            return True

        # Get site from various sources
        site_profile = self._get_site_profile(request, view)
        if not site_profile:
            # For list views, allow - filtering handles access
            return view.action == "list"

        # Check membership
        return SiteMember.objects.filter(site_profile=site_profile, user=request.user).exists()

    def _get_site_profile(self, request, view):
        """Extract SiteProfile from request context."""
        # 1. From URL kwargs (e.g., /api/sites/{pk}/)
        site_pk = view.kwargs.get("pk") or view.kwargs.get("site_pk")
        if site_pk:
            # Validate pk is a valid integer
            try:
                int(site_pk)
            except (ValueError, TypeError):
                from rest_framework.exceptions import ValidationError

                raise ValidationError(
                    {
                        "detail": f"Invalid site_id: '{site_pk}'. Must be a valid integer.",
                        "error": "invalid_site_id",
                    }
                ) from None
            try:
                return SiteProfile.objects.get(pk=site_pk, is_active=True)
            except SiteProfile.DoesNotExist:
                return None

        # 2. From middleware (current domain)
        site_config = getattr(request, "site_config", None)
        if site_config:
            try:
                return SiteProfile.objects.get(site_id=site_config.get("site_id"))
            except SiteProfile.DoesNotExist:
                return None

        return None


class HasSiteAdminAccess(HasSiteAccess):
    """
    Check if the authenticated user is an admin for the requested site.

    Inherits site resolution from HasSiteAccess.
    Superusers are treated as admins for all sites.
    """

    message = "You must be a site admin to perform this action."

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers bypass all checks
        if request.user.is_superuser:
            return True

        # Get site
        site_profile = self._get_site_profile(request, view)
        if not site_profile:
            return False

        # Check admin membership
        return SiteMember.objects.filter(
            site_profile=site_profile, user=request.user, role=SiteMember.Role.ADMIN
        ).exists()


class IsSiteMemberOrReadOnly(HasSiteAccess):
    """
    Allow read access for viewers, write access only for admins.

    - GET, HEAD, OPTIONS: Any site member
    - POST, PUT, PATCH, DELETE: Admin only
    """

    SAFE_METHODS = ("GET", "HEAD", "OPTIONS")

    def has_permission(self, request, view):
        # Must have basic site access first
        if not super().has_permission(request, view):
            return False

        # Safe methods allowed for any member
        if request.method in self.SAFE_METHODS:
            return True

        # Write methods require admin
        site_profile = self._get_site_profile(request, view)
        if not site_profile:
            return False

        return (
            request.user.is_superuser
            or SiteMember.objects.filter(
                site_profile=site_profile, user=request.user, role=SiteMember.Role.ADMIN
            ).exists()
        )
