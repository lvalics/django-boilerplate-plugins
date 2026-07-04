"""
URL configuration for sites app.

Includes:
- Authentication callback URLs for cross-domain SSO
- Site configuration API endpoints for frontend/mobile integration
- Site management API endpoints (authenticated, API key support)
"""

from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter

from apps.sites import api, views

app_name = "sites"

# DRF Router for management API (authenticated endpoints)
# Note: Use SimpleRouter instead of DefaultRouter to avoid creating a root API view
# that would capture "/" and show 403 Forbidden for unauthenticated users
router = SimpleRouter()
router.register("api/sites/manage", api.SiteViewSet, basename="site")

urlpatterns = [
    # Cross-domain auth callback (called after login on auth domain)
    path("auth/callback/", views.auth_callback, name="auth_callback"),
    # API endpoint to get auth token for cross-domain navigation
    path("auth/token/", views.auth_token_endpoint, name="auth_token"),
    # Site configuration API endpoints (public, no auth required)
    path("api/sites/config/", api.SiteConfigAPIView.as_view(), name="site_config_api"),
    path("api/sites/branding/", api.SiteBrandingAPIView.as_view(), name="site_branding_api"),
    path("api/sites/features/", api.SiteFeaturesAPIView.as_view(), name="site_features_api"),
    # Catch invalid management URLs with empty site_id (must be before router)
    re_path(
        r"^api/sites/manage//",
        api.invalid_site_id_view,
        name="invalid_site_id",
    ),
    # Management API (authenticated, API key support)
    path("", include(router.urls)),
]
