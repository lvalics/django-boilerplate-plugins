"""CMS plugin settings, read once with sensible defaults (Victoury conf pattern).

Security-sensitive, test-overridable settings (rate limiting, Turnstile, cache
timeout, uploads) are intentionally read at call time in their own modules
(cache.py, rate_limiter.py, views.py) so ``override_settings`` keeps working and
the hardened BASE behaviour is preserved. This module centralises the CMS/blog
layer settings (URL prefixes, templating, pagination, reserved slugs).
"""

from django.conf import settings

# URL prefixes for the blog + content routes mounted inside apps.cms.urls.
# Normalised (slashes stripped) so the value matches what urls_blog.py mounts and
# what the reserved-slug set below reserves — e.g. "blog/" and "blog" are the same.
POST_URL_PREFIX = getattr(settings, "CMS_POST_URL_PREFIX", "blog").strip("/")
CONTENT_URL_PREFIX = getattr(settings, "CMS_CONTENT_URL_PREFIX", "c").strip("/")

# Blog listing pagination.
POSTS_PER_PAGE = getattr(settings, "CMS_POSTS_PER_PAGE", 12)

# Base template that blog/content templates extend. The boilerplate's site base
# template is ``web/base.html`` (the donor default of "base.html" does not exist
# in this target).
BASE_TEMPLATE = getattr(settings, "CMS_BASE_TEMPLATE", "web/base.html")

# Slugs that must never be assigned to a root-mounted landing page because they
# collide with (or are shadowed by) the project's own top-level URL prefixes.
# Seeded from the boilerplate project/urls.py plus this plugin's own prefixes.
DEFAULT_RESERVED_SLUGS = {
    "admin",
    "accounts",
    "users",
    "api",
    "static",
    "media",
    "sitemap",
    "robots",
    "terms",
    "celery-progress",
    "hijack",
    "__reload__",
}

# Compared case-insensitively against a page's lowercased slug (see Page.clean/save).
RESERVED_SLUGS = {
    s.lower()
    for s in set(getattr(settings, "CMS_RESERVED_SLUGS", DEFAULT_RESERVED_SLUGS))
    | {POST_URL_PREFIX, CONTENT_URL_PREFIX}
}
