# CMS (Landing Pages + Blog)

A zone-based CMS for the django-boilerplate, scoped per site. Staff compose
pages in the Django admin from 20+ reusable zone types (hero, pricing, FAQ,
testimonials, order form, ...), each rendered by a DaisyUI/Tailwind template and
configured with JSON content. Alongside zone-built **landing pages**, the plugin
serves static **content pages** and a small **blog** (posts with author,
publish date, excerpt, categories and tags) built on the same zone engine.

**Requires the `multi_domain` plugin** (`apps.sites`): pages are scoped to its
`SiteProfile` model and the installer refuses to install without it.

## Page types

Every page has a `page_type` (`PageType`):

| `page_type` | Served at              | Notes                                            |
| ----------- | ---------------------- | ------------------------------------------------ |
| `landing`   | `/<slug>/`             | zone-built landing page (default, root catch-all) |
| `content`   | `/c/<slug>/`           | static content page built from zones             |
| `post`      | `/blog/<slug>/`        | blog post (uses author/published_at/excerpt/etc) |

## Features

- **Zone engine**: 24 zone types, each a Django template driven by per-zone JSON
  `content` (text, images, CTAs) and `config` (styling, behavior)
- **Zone template presets**: 90+ ready-made presets installed with one command
- **Blog**: posts, categories and tags, publish scheduling (`published_at`),
  excerpts, related posts and pagination
- **Per-site scoping**: pages belong to one site or to all sites, with
  site-specific pages winning on slug collisions
- **Order/contact forms**: ORDER_FORM zones store submissions with file uploads,
  Cloudflare Turnstile verification, rate limiting, and email notifications
- **Testimonials**: managed in admin, rendered with Schema.org Review markup
- **Caching**: slug resolution cached (Redis or any Django cache backend) with
  automatic invalidation on save
- **Redirect zones**: turn a page into a 301/302 or delayed redirect

### Not included (dropped from the legacy/Victoury plugin)

Analytics/visitor tracking, A/B testing variants, AI content generation, zone
edit history, inbound/outbound webhooks, the inline frontend editor, and the
ecommerce/Stripe integration are **not** part of this lean version.

## Installation

```bash
python installer/install.py cms --target /path/to/your/project
```

The multi_domain plugin must already be installed (the installer enforces this
via the `requires` marker on `apps.sites`). Then:

```bash
make migrations ARGS='cms'
make migrate
make manage ARGS='install_zone_templates'   # seed the 90+ zone presets
```

## URL map and the root mount

The plugin is mounted at the **project root** (empty prefix). The installer
appends the plugin's URL include at the **end** of the project `urlpatterns`, so
every existing project route (admin, accounts, api, the home page, ...) always
matches first; only unmatched paths fall through to this plugin. Inside the
plugin, explicit prefixes come first and the landing-page `<slug>` catch-all is
the final pattern:

```
/blog/                     blog list
/blog/<slug>/              blog post detail
/blog/category/<slug>/     posts in a category
/blog/tag/<slug>/          posts with a tag
/c/<slug>/                 content pages
/<slug>/                   landing pages (root catch-all; unknown slug → 404)
```

The blog and content prefixes are configurable:

- `CMS_POST_URL_PREFIX` (default `"blog"`)
- `CMS_CONTENT_URL_PREFIX` (default `"c"`)

### Reserved slugs

Because landing pages live at `/<slug>/`, a page whose slug collides with a
top-level project route would be permanently shadowed. `Page.clean()` therefore
rejects reserved slugs on save. The default set (from `conf.py`) covers `admin`,
`accounts`, `users`, `api`, `static`, `media`, `sitemap`, `robots`, `terms`,
`celery-progress`, `hijack`, and the blog/content prefixes. Override it with:

```python
CMS_RESERVED_SLUGS = {"admin", "accounts", "api", "shop", ...}
```

(The plugin always also reserves the configured blog/content prefixes.)

## Zone types

`hero_video`, `jumbotron`, `banner`, `showcase`, `benefits_grid`,
`social_proof_cta`, `curriculum`, `pricing`, `comparison`, `carousel`,
`gallery`, `video`, `table`, `timeline`, `qr_code`, `faq`, `guarantee`,
`about_instructor`, `testimonial_single`, `testimonials_grid`, `final_cta`,
`order_form`, `redirect`, `footer`.

## Creating pages

1. **Admin > CMS > Pages > Add**: title, slug, **Page type**, site
   (empty = all sites), SEO fields. For landing pages, `use_site_template`
   renders inside your site's `web/base.html`; unchecked pages render standalone.
2. Save, then add zones in the inline (type, order, active). Open each zone to
   edit its JSON `content`/`config` - copy a starting point from
   **Admin > Zone Templates** (`default_content` / `default_config`).
3. Landing pages are served at `/<slug>/`, content pages at `/c/<slug>/`.

Zone JSON is validated on save: each zone type requires a couple of essential
content keys (e.g. `hero_video` needs `"headline"`, `pricing` needs `"plans"`);
empty content is allowed so you can save first and fill in later.

## Creating blog posts

1. Set the page's **Page type** to *Blog post*.
2. Fill the **Blog / content** section: **Author**, **Published date**
   (a post is only visible once `published_at` is set and not in the future),
   **Excerpt** (used in listings and SEO fallbacks), **Category**, **Tags**.
3. Add zones for the body just like any other page. Blog templates extend
   `CMS_BASE_TEMPLATE` (default `web/base.html`) and use static DaisyUI classes.
4. Manage **Categories** and **Tags** under **Admin > CMS**. Both are
   site-scoped (unique per site). Listing pagination is `CMS_POSTS_PER_PAGE`
   (default 12).

Posts with no `published_at`, a future `published_at`, or `is_active=False`
return 404 and are excluded from listings.

### Per-site scoping and slug rules

- Slugs are unique **per site**, and unique among all-sites pages.
- The same slug may exist as a site page on site A and another on site B.
- On a request, the current site's page wins over an all-sites page with the
  same slug. A page assigned to site A 404s on site B.

## Order forms and submissions

An ORDER_FORM zone (one per page) renders a configurable form
(`content.form_fields`) that POSTs to the plugin API and stores a
`Submission` (status workflow: new / seen / processed / spam) - see
**Admin > Submissions**. Features:

- **Turnstile**: set `TURNSTILE_KEY` / `TURNSTILE_SECRET` in `.env`. With an
  empty secret, verification is skipped (useful in dev).
- **Rate limiting**: per-IP (default 2/hour) and per-email (default 3/day),
  configurable via `CMS_RATE_LIMIT_*` settings.
- **Email validation**: typo suggestions, disposable-domain blocking
  (vendored `email_utils`).
- **File uploads**: stored via Django `default_storage` under
  `cms/submissions/<page-slug>/<zone-id>/`; type/size limited via
  `CMS_ALLOWED_UPLOAD_TYPES` / `CMS_MAX_UPLOAD_MB` (defaults: images + PDF, 10 MB).
- **Notifications**: set `notification_email_enabled`, `notification_email_to`,
  `notification_email_cc`, `notification_email_subject` in the zone's `config`
  to get a plain-text email per submission (falls back to `DEFAULT_FROM_EMAIL`
  as recipient).

## Template overrides

Every zone template can be overridden per project the normal Django way: copy
`templates/cms/zones/<type>.html` into your project and edit. A zone can also
point at an alternative template via its `template_name` field, which is
**whitelisted** to `cms/zones/*.html` paths - create e.g.
`templates/cms/zones/hero_video_dark.html` and set
`template_name: cms/zones/hero_video_dark.html`.

With multi_domain's per-site template dirs you can override zone templates for
a single site (e.g. `templates/<template_dir>/cms/zones/faq.html`).

## tailwind-safelist.html (do not delete)

Tailwind 4's JIT compiler only emits classes it sees as literals in scanned
files. Zone styling classes are assembled from editor-configured values
(`bg-primary`, `btn-accent`, ...), so they never appear literally in templates.
`templates/cms/tailwind-safelist.html` lists every class the zone templates can
produce inside an HTML comment - the full color cross-product of the validated
color filters, the color/opacity combinations used by template defaults and
shipped presets, and every size/spacing/typography class implied by template
defaults and preset values. Because it lives in `templates/`, the Tailwind scan
picks it up and keeps those classes in your CSS build. Deleting it ships
unstyled pages in production builds.

The safelist is **test-enforced**: a repo test parses every remaining
`prefix-{{ ...|default:'x' }}` interpolation in the zone templates and asserts
the implied class is present, so template edits cannot silently reintroduce
missing classes.

Color-ish zone config values are constrained to the DaisyUI semantic palette
(`primary`, `secondary`, `accent`, `neutral`, `info`, `success`, `warning`,
`error`, `base-100/200/300` and their `-content` variants) plus Tailwind core
`black`/`white`/`transparent`, optionally with a fixed-step opacity suffix
(e.g. `base-content/70`). Unknown values fall back to a safe default. Arbitrary
hex colors are supported and rendered as inline styles (never classes). Custom
color/opacity combinations beyond the shipped set must be appended to the
safelist manually.

## Security notes

- **Editor trust model**: zone `content`/`config` are rendered with `|safe` in
  several zone templates by design (rich text, embeds). Only staff can edit
  zones - treat zone JSON as trusted, admin-only input and do not expose zone
  editing to untrusted users.
- **Visitor input** is server-side sanitized (`html.escape`, recursively) before
  storage, and re-escaped in the admin.
- **template_name whitelist** prevents zones from `{% include %}`-ing arbitrary
  templates: only `cms/zones/*.html` paths are accepted.
- **Reserved slugs** stop a landing page from shadowing a project route.
- **Rate limits** protect the submission endpoint per-IP and per-email; both use
  atomic cache counters.
- **Trusted proxies**: client IPs honor `SITES_TRUSTED_PROXY_COUNT` (shared with
  multi_domain) - set it to your real reverse-proxy depth in production,
  otherwise `X-Forwarded-For` is ignored.
- **Turnstile** fails closed: if verification errors out, the submission is
  rejected.

## Troubleshooting

- **Pages render unstyled**: `tailwind-safelist.html` was deleted or your
  Tailwind config does not scan `templates/` - restore the file and rebuild
  (`make npm-build`).
- **404 on a page that exists**: the page is assigned to a different site, is
  inactive, or (for posts) has no/future `published_at`; slug resolution is
  cached - saving the page invalidates the cache (timeout 300s,
  `CMS_CACHE_TIMEOUT`).
- **Cannot save a page - "slug is reserved"**: the slug collides with a
  top-level project route; pick another or adjust `CMS_RESERVED_SLUGS`.
- **"Only one Order Form zone is allowed"**: a page can hold a single
  ORDER_FORM zone; deactivate/delete the existing one first.
- **Zone save rejected with missing content keys**: each zone type requires a
  minimal set of keys (see the error message); copy the preset from Zone
  Templates as a starting point.
- **Submissions rejected with 429**: rate limit hit - raise
  `CMS_RATE_LIMIT_*` or add your IP to `CMS_EXEMPT_IPS` while testing.
- **i18n**: templates and models are `gettext`-wrapped; only the `en` catalog
  ships. Run `manage.py compilemessages` (optional) after adding translations.
