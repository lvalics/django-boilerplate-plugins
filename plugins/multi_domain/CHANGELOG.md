# Changelog

All notable changes to the Multi-Domain plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - Ported to django-boilerplate-plugins

### Changed
- **Decoupled from `apps.api`**: the API-key app is now optional and auto-detected. The
  imports in `api.py`, `serializers.py`, `admin.py`, and `tests/test_site_member.py` are
  guarded with `try/except ImportError`. When the app is absent the REST API falls back to
  session authentication (`IsAuthenticated`), the member serializer/admin skip key
  creation gracefully, the admin "API Key" column shows `-`, the key-creation admin action
  reports "API-key app not installed", and the key-dependent test classes skip cleanly.
- **Async-safe request-local storage**: replaced `threading.local()` with
  `asgiref.local.Local()` in `middleware/multi_domain.py` and `template_loader.py` so the
  current-site and template-loading state are correct under both WSGI threads and ASGI
  coroutines. `asgiref` ships with Django — no new dependency.
- **Installer-based wiring**: middleware ordering, template-loader swap, the `site_config`
  context processor, URL includes, and settings are applied by the plugin installer via
  `plugin.toml` (`settings_append`) instead of manual `settings.py` edits.
- **Scrubbed project-specific references**: neutralised a hardcoded real domain in
  `template_loader.py` comments (now uses `mysite`).

### Removed
- **Frontend TypeScript client** (`frontend/`) dropped from the port; the REST API remains
  and can be consumed by any client.

### Notes
- `template_loader.SiteAwareCachedLoader` is currently a thin placeholder over Django's
  cached loader so the production loader stack is valid. Making its cache key site-aware is
  pending Task 2.

## [1.3.5] - 2025-12-26

### Fixed
- **Infinite Recursion in SiteTemplateLoader**: Added thread-local storage to track templates currently being loaded and skip site-specific lookup when already in the loading stack. This prevents `RecursionError: maximum recursion depth exceeded` when site-specific templates extend base templates (e.g., `mysite/web/base.html` extends `web/base.html`).

## [1.3.1] - 2025-12-26

### Fixed
- **DRF Router 403 Error**: Use `SimpleRouter` instead of `DefaultRouter` to avoid creating a root API view that captures "/" and returns 403 Forbidden for unauthenticated users

## [1.3.0] - 2025-12-25

### Security Fixes
- **JWT Replay Prevention**: Added unique `jti` claim to JWT tokens with cache-based blacklist to prevent token reuse attacks
- **Path Traversal Fix**: Normalized paths in exempt path check to prevent bypass via path manipulation (`/static/../admin/`)
- **User ID Assignment**: Fixed potential user impersonation bug in cross-domain auth flow

### Added
- **Audit Logging**: Track all site configuration changes with full audit trail
  - New `SiteAuditLog` model - tracks who, when, what changed, previous/new values
  - Automatic logging via Django signals for create/update/delete operations
  - Read-only admin interface at `/admin/site_management/siteauditlog/`
  - Configurable retention period via `SITES_AUDIT_LOG_RETENTION_DAYS` (default 90 days)
  - `SiteAuditLog.cleanup_old_logs()` for maintenance
- **Cache Resilience**: Graceful fallback when Redis is unavailable
  - Periodic cache health checks with `_is_cache_available()`
  - Safe cache wrappers that catch connection errors
  - Automatic database fallback - site continues working if Redis goes down
  - Auto-recovery when cache becomes available again
- **Origin Normalization**: Consistent CORS/CSRF origin comparison
  - `normalize_origin()` function handles case differences, default ports, trailing slashes
  - `HTTPS://Example.COM:443/` now correctly matches `https://example.com`
  - Applied to both CORS and CSRF middleware

### Improved
- **Cache Stampede Protection**: Added locking to prevent multiple processes loading same config
- **Domain Change Handling**: Old domain cache invalidated when domain is changed
- **Logout Propagation**: User logout propagates across all shared-auth sites
- **Rate Limiting**: Added rate limiting to auth endpoints and public APIs
  - `ratelimit` decorator for views (30/min for auth endpoints)
  - `PublicAPIThrottle` (60/min) and `AuthenticatedAPIThrottle` (120/min) for DRF
  - Rate limit headers in responses (X-RateLimit-Limit, X-RateLimit-Remaining)

### Migration
- New migration `0003_alter_siteprofile_extra_settings_siteauditlog.py`

## [1.2.0] - 2025-12-14

### Added
- **Per-Site CORS Configuration**: Configure CORS allowed origins per domain via Django Admin
  - `DynamicCorsMiddleware` - Handles per-site CORS headers
  - `cors_allowed_origins` in `extra_settings` JSON field
  - `frontend_address` automatically included in allowed origins
  - Preflight (OPTIONS) request handling
- **Per-Site CSRF Configuration**: Configure CSRF trusted origins per domain
  - `DynamicCsrfMiddleware` - Extends Django's CsrfViewMiddleware
  - `csrf_trusted_origins` in `extra_settings` JSON field
  - Falls back to global `CSRF_TRUSTED_ORIGINS` if not configured
- **Unit Tests**: Test suite for CORS/CSRF middleware
  - `apps/sites/tests/test_cors_csrf.py` - 24 tests covering all scenarios

### Security
- **Origin Validation**: Strict validation for all configured origins
  - No wildcards (`*`, `*.example.com`) allowed
  - HTTPS required in production (DEBUG=False)
  - No paths allowed (only `scheme://host:port`)
  - Audit logging for all CORS/CSRF grants
- **Model Validation**: Invalid origins rejected at save time in admin

### Changed
- **Middleware Stack**: Updated recommended middleware configuration
  - Replace `django.middleware.csrf.CsrfViewMiddleware` with `DynamicCsrfMiddleware`
  - Add `DynamicCorsMiddleware` after `MultiDomainMiddleware`
- **Admin Interface**: Renamed "Extra" fieldset to "CORS/CSRF & Extra Settings"
  - Added description explaining per-site CORS/CSRF configuration

### Documentation
- Updated `docs/multi-domain.md` with Phase 12: Per-Site CORS & CSRF Configuration
- Updated README with CORS/CSRF setup instructions
- Added JSON examples for admin configuration

## [1.1.0] - 2025-12-14

### Added
- **Site Config API**: REST endpoints for frontend and mobile app integration
  - `GET /api/sites/config/` - Full public configuration for current domain
  - `GET /api/sites/branding/` - Lightweight theme/colors/logo endpoint
  - `GET /api/sites/features/` - Feature flags only endpoint
- **TypeScript Support**: Frontend module for standalone React SPAs
  - `frontend/src/lib/multi-site/types.ts` - Type definitions for SiteConfig
  - `frontend/src/lib/multi-site/api.ts` - API fetch functions
  - `frontend/src/lib/multi-site/index.ts` - Module re-exports
- **Serializers**: DRF serializers for API responses
  - `PublicSiteConfigSerializer` - Filters sensitive fields from API exposure
  - `SiteBrandingSerializer` - Lightweight branding-only serializer
  - `SiteFeaturesSerializer` - Feature flags serializer
- **Model Enhancement**: Public API methods on SiteProfile
  - `to_public_config_dict()` - Safe subset for public API exposure
  - `to_branding_dict()` - Lightweight branding-only data
  - `to_features_dict()` - Feature flags only
- **Unit Tests**: Comprehensive test suite (36 tests)
  - `apps/sites/tests/test_models.py` - Model tests
  - `apps/sites/tests/test_api.py` - API endpoint tests
  - `apps/sites/tests/test_cache.py` - Cache layer tests
  - `apps/sites/tests/test_context_processors.py` - Context processor tests
- **Testing Documentation**
  - `docs/multi-domain-testing.md` - Testing guide
  - `docs/postman/multi-domain.json` - Postman collection for API testing

### Architecture
- **Django templates**: Use direct context from middleware (zero HTTP overhead)
- **Standalone SPAs/Mobile**: Use REST API endpoints
- **Simplified approach**: No json_script injection or complex React hooks

### Security
- API endpoints explicitly filter sensitive configuration fields
- HTTP cache headers include `Cache-Control: public, max-age=300`
- Response headers include `Vary: Host` for proper multi-domain caching
- Documentation includes security best practices for frontend integration

## [1.0.0] - 2025-12-14

### Added
- Initial release of Multi-Domain plugin
- Database-driven multi-domain configuration via Django Admin
- Per-site templates with custom nav and footer support
- Per-site branding (logo, colors, theme)
- Feature flags for enabling/disabling features per site
- Cross-domain SSO (Single Sign-On) with JWT tokens
- Redis caching with configurable TTL for high performance
- Path prefix routing for local development testing
- DynamicAllowedHostsMiddleware for automatic host validation
- MultiDomainMiddleware for site configuration injection
- AuthDomainMiddleware for SSO redirects
- SiteTemplateLoader for per-site template resolution
- Context processor for site config in templates
- Admin interface for site management
- Template tags for site-specific content
