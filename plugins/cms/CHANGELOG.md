# Changelog

## 2.1.0

Renamed the plugin from `landing_pages` to **`cms`** and adopted the user's later
"Victoury" design (app `apps.cms`, models `Page`/`Zone`), then grafted a
blog/content layer onto the same zone engine. All v2.0.0 security hardening is
preserved verbatim; none of the Victoury subsystems that were previously cut
(analytics, A/B variants, zone history, webhooks, inline editor, ecommerce,
services layer) were reintroduced.

**Fresh migrations required** — this is a pre-release rename with no upgrade
path. The plugin ships only `migrations/__init__.py`; a fresh `0001_initial` is
generated in the target project (`make migrations ARGS='cms' && make migrate`).

### Renamed (Victoury naming)

- App label/name `landing_pages` → `cms` (`apps.cms`); templates
  `templates/landing_pages/**` → `templates/cms/**`; static
  `static/landing_pages/**` → `static/cms/**`
- Models: `LandingPage` → `Page`, `LandingPageZone` → `Zone`,
  `LandingPageSubmission` → `Submission`, `LandingPagesSettings` → `CMSSettings`
  (`Testimonial`, `ZoneTemplate`, `ZoneType` keep their names); constraint names
  `landing_pages_unique_slug_*` → `cms_unique_slug_*`; zone-template whitelist
  regex now `^cms/zones/*.html`
- Settings: `LANDING_PAGES_RATE_LIMIT_*` → `CMS_RATE_LIMIT_*`,
  `LANDING_PAGES_EXEMPT_IPS` → `CMS_EXEMPT_IPS`, `LANDING_PAGES_CACHE_TIMEOUT` →
  `CMS_CACHE_TIMEOUT`, `LANDING_PAGES_{MAX_UPLOAD_MB,ALLOWED_UPLOAD_TYPES}` →
  `CMS_*`. CMS-layer settings are centralised in a new `conf.py`
  (settings-with-defaults pattern); `TURNSTILE_*` names are unchanged.

### Added (blog / content layer)

- `PageType` (`landing` / `content` / `post`) with a `page_type` field on `Page`
- Blog metadata on `Page`: `author`, `published_at`, `excerpt`, `category` FK,
  `tags` M2M; site-scoped `Category` and `Tag` models
- `PageQuerySet`/`PageManager` (`.posts()`, `.content_pages()`, `.published()`)
- Blog + content views/urls (`blog_list`, `blog_detail`, `blog_category`,
  `blog_tag`, `content_page`) under the `cms_blog` namespace, and DaisyUI
  templates that extend `CMS_BASE_TEMPLATE` (default `web/base.html`)
- Admin: page-type/category list filters, tag autocomplete and
  `published_at` date hierarchy on `PageAdmin`; `Category`/`Tag` admins

### Changed (root mount + reserved slugs)

- Dropped the `p/` mount: the plugin now mounts at the project **root**
  (`"" = "apps.cms.urls"`), appended last so all existing project routes win.
  URL map: `/<slug>/` (landing, root catch-all, last pattern), `/blog/…` (posts),
  `/c/<slug>/` (content). Blog/content prefixes configurable via
  `CMS_POST_URL_PREFIX` / `CMS_CONTENT_URL_PREFIX`.
- New `RESERVED_SLUGS` set (conf.py, override via `CMS_RESERVED_SLUGS`) enforced
  in `Page.clean()` so a landing-page slug can't shadow a top-level project route.
- The old optional project-level catch-all recipe is obsolete and removed from
  the README.

## 2.0.0

Lean v1 port of the legacy zone-based landing page CMS into the installer-based
plugin format, decoupled from ecommerce and security-hardened.

### Ported

- Zone engine: 24 zone types, JSON content/config, DaisyUI zone templates,
  zone template presets + `install_zone_templates` command
- Per-site scoping via multi_domain's `SiteProfile` (installer `requires`
  marker on `apps.sites`), with per-site slug uniqueness
- Order-form submissions as a new standalone `LandingPageSubmission` model
  (new/seen/processed/spam workflow), replacing the Stripe-coupled
  `PurchaseExtension`
- Turnstile verification, IP/email rate limiting, server-side input
  sanitization, email validation (vendored `email_utils`)
- Testimonials with Schema.org markup; redirect zones; Redis caching

### Removed (deliberate scope cut)

- Analytics and visitor tracking (models, endpoints, JS)
- A/B testing variants (`zones override` logic and traffic splitting)
- AI content generation and its admin JS
- Zone edit history model and admin restore/preview
- Inbound/outbound webhook system (fields, endpoints, logs, service, tasks)
- Inline frontend editor (API, serializers, permissions plumbing, JS/CSS)
- Ecommerce coupling: `product_configuration` FKs, Stripe metadata,
  checkout session ids, order status workflow
- Pluggable services layer (storage/email/... service classes); S3/boto3
  upload path (Django `default_storage` only); demo page importer;
  JSON import/export admin actions; auto user creation on submission

### Fixed (legacy landmines)

- **Tailwind 4 JIT**: color-ish config values constrained to the DaisyUI enum
  (plus Tailwind core black/white/transparent and fixed-step opacity suffixes)
  with safe fallbacks; hex colors always inline styles; DaisyUI 5 CSS variables
  (`--color-*` + `color-mix`) instead of DaisyUI 4 `var(--p)`; shipped
  `templates/landing_pages/tailwind-safelist.html` so the classes survive the
  JIT scan
- **Tailwind 4 JIT (fix pass)**: every color-class interpolation in the zone
  templates now goes through validated filters (`bg_color`, `text_color`,
  `btn_color`, `border_color`, `badge_color`, `ring_color`, gradient stops,
  DaisyUI input variants, ...) instead of raw `bg-{{ config.x }}` string
  interpolation (470 sites converted); the safelist was regenerated
  mechanically to cover the full color cross-product plus every size/spacing
  class implied by template defaults and shipped preset values (~900 classes)
  and is enforced by a repo test that re-derives the implied classes from the
  templates; non-enum color defaults/presets (`gray-700`, `gray-300`,
  `btn-white`, `#e8e8e8` banner background) mapped to enum equivalents; fixed
  a latent `TemplateSyntaxError` in `banner.html` (Jinja-style conditional
  expressions) and a bogus `max-w-800px` class in `comparison.html`
- **Standalone template CDN**: `landing_page_standalone.html` now pins the
  Tailwind 4 browser build (`@tailwindcss/browser@4`) + DaisyUI 5 CDN CSS
  (was the Tailwind 3 Play CDN + DaisyUI 4) and is documented as a
  debug/preview convenience, not the production path
- **Broken root catch-all** (`urls_catchall.py`) deleted; pages mount under
  `p/` and the README documents an optional project-level catch-all
- **`template_name` whitelist**: zone template overrides are validated against
  `landing_pages/zones/*.html` (no arbitrary `{% include %}`)
- **Schema-lite JSON validation**: per-zone-type required content keys enforced
  in `clean()` with clear errors
- **Cache correctness**: the page view now actually uses the cache (slug -> id
  resolution, single ORM fetch); backend-specific `delete_pattern` replaced
  with version-bump invalidation; the inconsistent slug/id invalidation task
  path removed with the tasks module
- **Redirect zones**: view reads the `redirect_url` content key the presets and
  template actually use (legacy view read `url` and always fell through)
- **Client IP**: honors `SITES_TRUSTED_PROXY_COUNT` (same trusted-proxy logic
  as multi_domain) instead of blindly trusting `X-Forwarded-For`; rate-limit
  counters are atomic (`add` + `incr`)

## Legacy (pre-port) summary

- 1.1.0 - zone history + restore, AI content generation, demo importer,
  JSON import/export, per-page editor groups
- 1.0.x - initial zone engine, 24 zone types, presets, order forms with
  Stripe/ecommerce coupling, webhooks, analytics, A/B variants, inline editor
