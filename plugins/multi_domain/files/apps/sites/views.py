"""
Authentication views for cross-domain SSO.

These views handle the auth domain side of the authentication flow:
1. User logs in on auth domain
2. Auth domain generates JWT token
3. User is redirected back to target site with token

Security:
- Rate limited to prevent brute-force attacks
- JWT tokens with replay protection
"""

import logging
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect

from apps.sites.middleware.auth_domain import create_auth_token
from apps.sites.models import SiteProfile
from apps.sites.ratelimit import ratelimit

logger = logging.getLogger(__name__)


@login_required
@ratelimit(rate="30/m", key="user", fail_closed=True)  # 30/min per user; deny on cache outage
def auth_callback(request):
    """
    Auth domain callback after successful login.

    After allauth completes login, this view:
    1. Validates the 'next' URL belongs to a site in our group
    2. Creates a JWT token for the user
    3. Redirects back to the target site with the token

    URL: /auth/callback/?next=https://site.com/dashboard/
    """
    next_url = request.GET.get("next")
    if not next_url:
        # No redirect target - go to default
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    # Parse target domain
    parsed = urlparse(next_url)
    target_domain = parsed.netloc.split(":")[0]  # Remove port

    # Validate target domain is in our site group
    site_config = getattr(request, "site_config", None)
    if not site_config or not site_config.get("is_auth_domain"):
        logger.error("auth_callback called on non-auth domain")
        return HttpResponseBadRequest("This site is not configured as an auth domain")

    # Check if target domain is in our family (sites that use this auth domain)
    # A site is valid if it has auth_mode="shared" and points to this auth domain
    auth_domain = site_config["domain"]
    valid_domains = list(
        SiteProfile.objects.filter(
            auth_domain__site__domain=auth_domain, auth_mode="shared", is_active=True
        ).values_list("site__domain", flat=True)
    )
    # Include the auth domain itself
    valid_domains.append(auth_domain)

    if target_domain not in valid_domains:
        logger.warning(f"auth_callback: target domain {target_domain} not in allowed domains")
        return HttpResponseBadRequest(f"Target domain '{target_domain}' is not authorized")

    # Create JWT token
    token = create_auth_token(request.user, target_domain)

    # Security tradeoff: the SSO token is delivered as a query-string parameter, so it can
    # leak via browser history, Referer headers, and access logs. It is mitigated by a short
    # (5-min) expiry, single-use jti replay protection, and HTTPS-only delivery. A
    # POST/handoff-code redesign that keeps the token out of the URL is tracked as future work.
    separator = "&" if "?" in next_url else "?"
    redirect_url = f"{next_url}{separator}auth_token={token}"

    logger.info(f"User {request.user.email} authenticated, redirecting to {target_domain}")
    return HttpResponseRedirect(redirect_url)


@login_required
@ratelimit(rate="20/m", key="user", fail_closed=True)  # 20/min per user; deny on cache outage
def auth_token_endpoint(request):
    """
    API endpoint to get auth token for cross-domain navigation.

    For AJAX requests when user is already logged in and needs
    to navigate to another domain in the group.

    URL: /auth/token/?domain=site.com
    Returns: JSON with auth_token
    """
    from django.http import JsonResponse

    target_domain = request.GET.get("domain")
    if not target_domain:
        return JsonResponse({"error": "domain parameter required"}, status=400)

    # Validate target domain is in our family (sites that share authentication)
    site_config = getattr(request, "site_config", None)
    if not site_config:
        return JsonResponse({"error": "Site configuration not found"}, status=500)

    # Check if target domain belongs to the same auth family
    current_domain = site_config["domain"]
    auth_domain = site_config.get("auth_domain_url") or current_domain

    # Valid targets are sites that use the same auth domain
    valid = (
        SiteProfile.objects.filter(
            auth_domain__site__domain=auth_domain, site__domain=target_domain, auth_mode="shared", is_active=True
        ).exists()
        or target_domain == auth_domain
    )

    if not valid:
        return JsonResponse({"error": "Domain not authorized"}, status=403)

    token = create_auth_token(request.user, target_domain)
    return JsonResponse({"auth_token": token})
