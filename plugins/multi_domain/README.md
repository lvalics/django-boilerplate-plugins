# Multi-Domain Sites

Database-driven multi-domain support for
[django-boilerplate](https://github.com/saaspegasus/django-boilerplate): serve many
domains from one project with per-site branding, templates, feature flags, per-site
CORS/CSRF, and optional cross-domain single sign-on (SSO) — all configured from the
Django admin, no code changes per site.

Self-contained: the only project dependency is `apps.utils.models.BaseModel` (already in
the boilerplate). Integration with an API-key app (`apps.api`) is optional and
auto-detected; when it is absent the API and admin fall back to session authentication.

## Install

The installer copies the payload and wires up middleware, template loaders, the context
processor, URLs, and settings for you:

```bash
python install.py multi_domain /path/to/your/project            # dry-run (shows the plan)
python install.py multi_domain /path/to/your/project --apply    # apply
```

After applying:

```bash
make migrate   # create the SiteProfile / SiteMember / SiteAuditLog tables
```

Then create or edit a Site + Site Profile in the Django admin (see below). The plugin's
Python dependencies (`PyJWT`, `pillow`) are printed as `uv add` commands by the installer.

## Features

- **Database configuration** — add/configure domains via Django admin, no code changes.
- **Per-site templates** — custom templates, nav, and footer per domain.
- **Per-site branding** — logo, favicon, colors, and theme per domain.
- **Feature flags** — enable/disable features per site.
- **Cross-domain SSO** — optional single sign-on across domains with JWT replay
  protection.
- **Per-site CORS/CSRF** — configure allowed origins per domain (no `.env` changes).
- **Audit logging** — track all site configuration changes with a full audit trail.
- **Cache resilience** — automatic DB fallback when Redis is unavailable.
- **Rate limiting** — protect auth endpoints and APIs from abuse.
- **Path prefix routing** — test multiple sites on localhost in development.

## Architecture

```
Request → DynamicAllowedHostsMiddleware → DynamicCsrfMiddleware
                                          ↓
                                    MultiDomainMiddleware
                                          ↓
                                    Redis cache lookup
                                          ↓
                                    request.site_config = {...}
                                          ↓
                                    DynamicCorsMiddleware
                                          ↓
                            AuthDomainMiddleware (SSO redirect)
                                          ↓
                                View → SiteTemplateLoader
```

The installer inserts each middleware at the correct position in the stack (before
`SecurityMiddleware`, replacing `CsrfViewMiddleware`, after `AuthenticationMiddleware`
and after allauth's `AccountMiddleware`) and swaps the template loaders to put the
site-aware loader first. In production (cached loaders) the site-aware loader is wrapped
in a cached loader so per-site lookups are still cached.

## Requirements

- Redis (for caching; already part of django-boilerplate).
- `PyJWT` (for SSO tokens) and `pillow` (for logo/favicon uploads) — installed as plugin
  dependencies.
- `django.contrib.sites` with `SITE_ID` set (already configured in the boilerplate).

The app registers under the Django app label `site_management` to avoid clashing with
`django.contrib.sites`.

## Configuration

### Site Profile fields

| Field | Description |
|-------|-------------|
| `site_name` | Display name shown to users |
| `tagline` | Short description/slogan |
| `theme` | DaisyUI theme name |
| `template_dir` | Template subdirectory (per-site overrides live here) |
| `logo` / `favicon` | Site branding images |
| `primary_color` / `secondary_color` | Brand colors (hex) |
| `meta_defaults` | SEO meta tags (JSON) |
| `head_scripts` / `body_scripts` | External scripts (JSON) |
| `features` | Feature flags (JSON) |
| `integrations` | Third-party configs (JSON) |
| `auth_mode` | `isolated` or `shared` (SSO) |
| `is_active` | Enable/disable site |
| `is_primary` | Default site when no match |
| `path_prefix` | Dev-only path routing |

### Template variables

Available in all templates via the `site_config` context processor:

```html
{{ site_name }}              {# Display name #}
{{ site_config.tagline }}    {# Tagline #}
{{ site_config.logo_url }}   {# Logo URL #}
{{ site_config.theme }}      {# Theme name #}
{{ site_config.features }}   {# Feature flags dict #}
```

### Optional settings

The installer sets `SITE_CACHE_TIMEOUT = 300` and `AUTH_TOKEN_EXPIRY_MINUTES = 5`. You
can also set `SITES_AUDIT_LOG_RETENTION_DAYS` (default 90) to control audit-log
retention.

## Per-site CORS & CSRF

Configure CORS and CSRF origins per site without modifying `.env`. Set them in the Django
admin under Sites → Site → CORS/CSRF & Extra Settings:

```json
{
  "frontend_address": "https://app.example.com",
  "cors_allowed_origins": ["https://app.example.com", "https://admin.example.com"],
  "csrf_trusted_origins": ["https://app.example.com"]
}
```

| Key | Description |
|-----|-------------|
| `frontend_address` | Main frontend URL (auto-included in CORS) |
| `cors_allowed_origins` | List of origins allowed for CORS |
| `csrf_trusted_origins` | List of origins trusted for CSRF |

Security: wildcards are rejected, HTTPS is required in production (`DEBUG=False`), only
`scheme://host:port` is accepted (no paths), origins are normalized for comparison, and
every CORS/CSRF grant is audit-logged. `DynamicCsrfMiddleware` replaces Django's
`CsrfViewMiddleware`; `DynamicCorsMiddleware` runs after `MultiDomainMiddleware`. Both
read `request.site_config.extra_settings` and fall back to the global settings when no
per-site config exists.

## Per-site templates

Create a directory under `templates/<template_dir>/` (matching the Site Profile's
`template_dir`). Templates placed there override the default of the same name for that
site only; the site-aware loader falls back to the default when no per-site version
exists.

```
templates/mysite/
└── web/
    ├── base.html           # extends web/base.html
    ├── landing_page.html   # custom landing
    └── components/
        ├── top_nav.html    # custom nav
        └── footer.html     # custom footer
```

```html
{% extends "web/base.html" %}

{% block top_nav %}
  {% include "mysite/web/components/top_nav.html" %}
{% endblock %}

{% block footer %}
  {% include "mysite/web/components/footer.html" %}
{% endblock %}
```

Use `{{ site_name }}` in per-site templates for the site's display name.

## Cross-domain SSO

1. Create an auth domain with `is_auth_domain=True`.
2. For the other sites, set `auth_mode='shared'` and point `auth_domain` at the auth
   site.

```
User visits site1.com (not logged in)
  → redirect to auth.example.com/accounts/login/
  → user logs in
  → redirect back with a short-lived JWT (AUTH_TOKEN_EXPIRY_MINUTES, default 5)
  → user logged in on site1.com
```

## Development testing

### Path prefix routing

Test multiple sites on localhost without editing `/etc/hosts`:

1. Set `path_prefix='mysite'` in the Site Profile.
2. Access at `http://localhost:8000/mysite/` (also works through ngrok).

### Local domains

```bash
# /etc/hosts
127.0.0.1 mysite.local
127.0.0.1 auth.local
```

## Caching

Site configs are cached in Redis (`SITE_CACHE_TIMEOUT`, default 300s). Clear the cache
after config changes:

```python
from apps.sites.cache import invalidate_all_site_cache
invalidate_all_site_cache()
```

Or use the admin action **Refresh cache for selected sites**. When Redis is unavailable
the app falls back to the database automatically and recovers when the cache returns.

## Audit logging

All site configuration changes are logged (create/update/delete, changed fields with
previous/new values, user, IP, timestamp). View them in Django admin → Site Management →
Site Audit Logs. Prune old entries:

```python
from apps.sites.audit import SiteAuditLog
SiteAuditLog.cleanup_old_logs()  # deletes logs older than SITES_AUDIT_LOG_RETENTION_DAYS
```

## Optional API-key integration

The site management REST API and the member admin can issue per-user API keys when an
`apps.api` app providing `UserAPIKey` / `IsAuthenticatedOrHasUserAPIKey` is installed.
This is auto-detected: when that app is absent, the API uses session authentication, the
admin "API Key" column shows `-`, and the key-creation admin action reports that the
API-key app is not installed. No configuration is required either way.

## Troubleshooting

### Site not found / 404

- Check the domain exists in Sites admin.
- Check the Site Profile has `is_active=True`.
- Clear the cache: `invalidate_all_site_cache()`.

### Templates not loading

- Check `template_dir` is set correctly.
- Verify templates exist in `templates/{template_dir}/`.
- Check `ThreadLocalMiddleware` is in the middleware stack (the installer adds it).

### SSO not working

- Verify `auth_mode='shared'` on all non-auth sites.
- Check one site has `is_auth_domain=True`.
- Verify the `auth_domain` FK is set on the other sites.
- Inspect JWT tokens in the browser network tab.

## License

MIT License
