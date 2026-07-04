"""
Application version detection utility.

Detects version from:
1. KAMAL_VERSION environment variable (set during deployment)
2. Git commit hash (for local development)
"""

import os
import subprocess
from functools import lru_cache


@lru_cache(maxsize=1)
def get_version() -> str:
    """
    Get the current application version.

    Returns version from KAMAL_VERSION env var if set,
    otherwise falls back to git commit hash for local dev.
    """
    # Check KAMAL_VERSION first (set during Kamal deployment)
    kamal_version = os.environ.get("KAMAL_VERSION")
    if kamal_version:
        return kamal_version

    # Fall back to git for local development
    try:
        # Try to get the current tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--exact-match"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()

        # Fall back to short commit hash
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            commit = result.stdout.strip()
            return f"dev-{commit}"

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    return "unknown"


@lru_cache(maxsize=1)
def get_environment() -> str:
    """
    Detect the current environment based on settings or env vars.
    """
    # Check Django settings module
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE", "")

    if "production" in settings_module:
        return "production"
    elif "staging" in settings_module:
        return "staging"

    # Check DEBUG setting from environment
    debug = os.environ.get("DEBUG", "").lower()
    if debug in ("true", "1", "yes"):
        return "local"

    # Try Django settings directly (works in running Django app)
    try:
        from django.conf import settings

        if hasattr(settings, "DEBUG") and settings.DEBUG:
            return "local"
    except Exception:
        pass

    # Check ALLOWED_HOSTS for hints
    allowed_hosts = os.environ.get("ALLOWED_HOSTS", "")
    if "staging" in allowed_hosts:
        return "staging"
    elif "localhost" in allowed_hosts or "127.0.0.1" in allowed_hosts:
        return "local"

    return "unknown"


def get_version_display() -> str:
    """
    Get a formatted version string for display.
    """
    version = get_version()
    env = get_environment()

    # Production shows version only, others show version + environment label
    if env == "production":
        return version
    return f"{version} ({env})"


def app_version(request):
    """
    Django template context processor exposing the app version.

    The plugin installer registers this in TEMPLATES; the admin base_site.html
    footer consumes it as {{ app_version }}.
    """
    return {"app_version": get_version_display()}
