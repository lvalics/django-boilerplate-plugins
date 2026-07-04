"""
Views for the landing pages plugin.

Renders zone-based landing pages (site-scoped) and handles ORDER_FORM
submissions with Turnstile verification, rate limiting, input sanitization,
and file uploads via Django's default storage.
"""

import html
import logging
import os
import uuid

import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Prefetch
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import get_valid_filename
from django.views.decorators.http import require_POST

from .cache import get_page_id
from .email_utils import validate_and_normalize_email
from .emails import send_submission_notification
from .models import Page, Submission, Zone, SubmissionStatus, ZoneType
from .rate_limiter import RateLimiter, get_client_ip

logger = logging.getLogger(__name__)

# Upload validation defaults (override via settings)
DEFAULT_ALLOWED_UPLOAD_TYPES = [
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
]


def _sanitize_value(value):
    """Sanitize a value for safe storage and display (XSS prevention)."""
    if isinstance(value, str):
        return html.escape(value)
    elif isinstance(value, dict):
        return {k: _sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


def _sanitize_form_data(form_data: dict) -> dict:
    """Sanitize all form data values to prevent XSS attacks."""
    return {key: _sanitize_value(value) for key, value in form_data.items()}


def _current_site_id(request):
    """Django Site id for this request when the multi_domain plugin resolved one."""
    site_config = getattr(request, "site_config", None)
    if site_config:
        return site_config.get("site_id")
    return None


def queryset_for_request(request):
    """
    Active landing pages visible on the current request's site.

    Site-specific pages are preferred over all-sites pages on slug collision.
    This is the single place where per-site page filtering happens.
    """
    return Page.for_site(_current_site_id(request))


def landing_page_view(request, slug):
    """
    Render a landing page.

    Handles:
    - Cached slug -> page id resolution (per site scope)
    - Site-specific access control (site pages only served on their site)
    - Redirect zones
    - Zone rendering
    """
    site_id = _current_site_id(request)
    page_id = get_page_id(slug, site_id)
    if page_id is None:
        raise Http404("Landing page not found")

    # Single ORM fetch for the rendered page, with active zones prefetched in order.
    active_zones = Prefetch(
        "zones",
        queryset=Zone.objects.filter(is_active=True).order_by("order"),
        to_attr="active_zones",
    )
    page = get_object_or_404(
        Page.objects.select_related("site").prefetch_related(active_zones),
        pk=page_id,
        is_active=True,
    )

    # Defense in depth: a site-scoped page must only be served on its site
    # (covers the cache-staleness window after a page is moved between sites).
    if page.site and site_id and page.site.site_id != site_id:
        raise Http404("Landing page not found")

    zones = page.active_zones

    # Redirect zone: send the visitor elsewhere instead of rendering.
    redirect_zone = next((z for z in zones if z.zone_type == ZoneType.REDIRECT), None)
    if redirect_zone:
        # Seed presets use "redirect_url"; accept legacy "url" too.
        redirect_url = redirect_zone.content.get("redirect_url") or redirect_zone.content.get("url")
        if redirect_url:
            config = redirect_zone.config or {}
            try:
                delay = int(config.get("delay", 0) or 0)
            except (TypeError, ValueError):
                delay = 0

            if delay > 0:
                # Render a page with meta refresh
                return render(
                    request,
                    "cms/zones/redirect.html",
                    {
                        "zone": redirect_zone,
                        "content": redirect_zone.content,
                        "config": config,
                    },
                )

            is_permanent = config.get("redirect_type") == "301"
            return redirect(redirect_url, permanent=is_permanent)

    context = {
        "page": page,
        "zones": zones,
        "meta_title": page.get_meta_title(),
        "meta_description": page.meta_description,
        "canonical_url": page.canonical_url or request.build_absolute_uri(),
        "form_disabled": page.form_disabled,
        "turnstile_key": getattr(settings, "TURNSTILE_KEY", None),
    }

    if page.use_site_template:
        template = "cms/landing_page.html"
    else:
        template = "cms/landing_page_standalone.html"

    return render(request, template, context)


def _verify_turnstile(request):
    """
    Verify the Cloudflare Turnstile token when TURNSTILE_SECRET is configured.

    Returns None on success, or a JsonResponse error to return to the client.
    Skipped entirely (returns None) when TURNSTILE_SECRET is empty.
    """
    turnstile_secret = getattr(settings, "TURNSTILE_SECRET", "")
    if not turnstile_secret:
        return None

    turnstile_token = request.POST.get("turnstile_token", "")
    if not turnstile_token:
        return JsonResponse({"error": "Missing captcha. Please try again."}, status=400)

    try:
        turnstile_response = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": turnstile_secret, "response": turnstile_token},
            timeout=10,
        ).json()
        if not turnstile_response.get("success"):
            return JsonResponse({"error": "Invalid captcha. Please try again."}, status=400)
    except requests.Timeout:
        logger.warning("Turnstile verification timed out")
        return JsonResponse({"error": "Captcha verification timed out. Please try again."}, status=400)
    except requests.RequestException as e:
        logger.error("Turnstile verification request failed: %s", e)
        return JsonResponse({"error": "Captcha verification failed. Please try again."}, status=503)
    except Exception as e:
        logger.error("Turnstile verification error: %s", e)
        # Fail closed - reject submission if verification fails
        return JsonResponse({"error": "Captcha verification unavailable. Please try again."}, status=503)

    return None


def _validate_upload(uploaded_file) -> tuple[bool, str]:
    """Validate an uploaded file's size and declared content type."""
    max_size_mb = getattr(settings, "CMS_MAX_UPLOAD_MB", 10)
    allowed_types = getattr(settings, "CMS_ALLOWED_UPLOAD_TYPES", DEFAULT_ALLOWED_UPLOAD_TYPES)

    if uploaded_file.size > max_size_mb * 1024 * 1024:
        return False, f"File too large. Maximum size is {max_size_mb}MB."

    content_type = getattr(uploaded_file, "content_type", None)
    if not content_type or content_type not in allowed_types:
        return False, f"File type {content_type or 'unknown'} is not allowed."

    return True, ""


def _store_uploads(request, zone) -> list[dict]:
    """
    Validate and store request.FILES via Django's default storage.

    Returns a list of {"field", "path", "name"} dicts (path is the storage
    path, resolvable with default_storage.url()). Raises ValueError with a
    user-facing message when a file fails validation.
    """
    uploaded_files = []
    folder = f"cms/submissions/{zone.page.slug}/{zone.pk}"

    for key, uploaded_file in request.FILES.items():
        is_valid, error = _validate_upload(uploaded_file)
        if not is_valid:
            raise ValueError(f"Invalid file {key}: {error}")

        safe_name = get_valid_filename(os.path.basename(uploaded_file.name)) or "upload"
        path = default_storage.save(f"{folder}/{uuid.uuid4().hex[:8]}_{safe_name}", uploaded_file)
        uploaded_files.append({"field": key, "path": path, "name": uploaded_file.name})

    return uploaded_files


@require_POST
def submit_order_form(request, zone_id):
    """
    Submit an order/contact form from an ORDER_FORM zone.

    Handles rate limiting (IP + email), Turnstile verification, server-side
    sanitization, file uploads (default storage), and notification email.
    """
    zone = get_object_or_404(
        Zone.objects.select_related("page"),
        id=zone_id,
        zone_type=ZoneType.ORDER_FORM,
    )

    if zone.page.form_disabled:
        return JsonResponse({"error": "Form submissions are disabled"}, status=403)

    # Rate limiting (trusted-proxy-aware client IP)
    rate_limiter = RateLimiter()
    ip_address = get_client_ip(request)
    is_limited, message = rate_limiter.check_limit(ip_address)
    if is_limited:
        return JsonResponse({"error": message}, status=429)

    # Turnstile captcha validation (skipped when TURNSTILE_SECRET is empty)
    turnstile_error = _verify_turnstile(request)
    if turnstile_error is not None:
        return turnstile_error

    try:
        # Parse and sanitize form data (XSS prevention)
        form_data = {key: value for key, value in request.POST.items()}
        form_data.pop("csrfmiddlewaretoken", None)
        form_data.pop("turnstile_token", None)
        form_data = _sanitize_form_data(form_data)

        # Validate and normalize email
        raw_email = form_data.get("email", "").strip()
        email = ""
        if raw_email:
            normalized_email, email_error = validate_and_normalize_email(raw_email)
            if email_error:
                return JsonResponse({"error": email_error, "field": "email"}, status=400)
            email = normalized_email
            form_data["email"] = email  # Store normalized email

            # Check email rate limit
            is_limited, message = rate_limiter.check_email_limit(email)
            if is_limited:
                return JsonResponse({"error": message}, status=429)

        # Handle file uploads via default storage
        try:
            uploaded_files = _store_uploads(request, zone)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)

        submission = Submission.objects.create(
            page=zone.page,
            zone=zone,
            email=email,
            name=form_data.get("name", "")[:255],
            phone=form_data.get("phone", "")[:50],
            form_data=form_data,
            uploaded_files=uploaded_files,
            status=SubmissionStatus.NEW,
            ip_address=ip_address if ip_address != "unknown" else None,
        )

        # Send notification email if configured (never blocks the response)
        try:
            send_submission_notification(zone, submission)
        except Exception as e:
            logger.warning("Failed to send notification email: %s", e)

        return JsonResponse({"success": True, "submission_id": submission.pk})

    except Exception as e:
        logger.error("Failed to process form submission: %s", e)
        return JsonResponse({"error": "Failed to process submission"}, status=500)
