# Landing Pages CMS

A zone-based landing page builder for the django-boilerplate, scoped per site.
Staff compose pages in the Django admin from 20+ reusable zone types (hero,
pricing, FAQ, testimonials, order form, ...), each rendered by a DaisyUI/Tailwind
template and configured with JSON content.

**Requires the `multi_domain` plugin** (`apps.sites`): pages are scoped to its
`SiteProfile` model and the installer refuses to install without it.

## Features

- **Zone engine**: 24 zone types, each a Django template driven by per-zone JSON
  `content` (text, images, CTAs) and `config` (styling, behavior)
- **Zone template presets**: 90+ ready-made presets installed with one command
- **Per-site scoping**: pages belong to one site or to all sites, with
  site-specific pages winning on slug collisions
- **Order/contact forms**: ORDER_FORM zones store submissions with file uploads,
  Cloudflare Turnstile verification, rate limiting, and email notifications
- **Testimonials**: managed in admin, rendered with Schema.org Review markup
- **Caching**: slug resolution cached (Redis or any Django cache backend) with
  automatic invalidation on save
- **Redirect zones**: turn a page into a 301/302 or delayed redirect

### Not in v1 (dropped from the legacy plugin)

Analytics/visitor tracking, A/B testing variants, AI content generation, zone
edit history, inbound/outbound webhooks, the inline frontend editor, and the
ecommerce/Stripe integration are **not** part of this lean version. An Articles
module is planned as the next phase.

## Installation

```bash
python installer/install.py landing_pages --target /path/to/your/project
```

The multi_domain plugin must already be installed (the installer enforces this
via the `requires` marker on `apps.sites`). Then:

```bash
make migrations ARGS='landing_pages'
make migrate
make manage ARGS='install_zone_templates'   # seed the 90+ zone presets
```

## Zone types

`hero_video`, `jumbotron`, `banner`, `showcase`, `benefits_grid`,
`social_proof_cta`, `curriculum`, `pricing`, `comparison`, `carousel`,
`gallery`, `video`, `table`, `timeline`, `qr_code`, `faq`, `guarantee`,
`about_instructor`, `testimonial_single`, `testimonials_grid`, `final_cta`,
`order_form`, `redirect`, `footer`.

## Creating pages

1. **Admin > Landing Pages > Landing Pages > Add**: title, slug, site
   (empty = all sites), SEO fields. `use_site_template` renders inside your
   site's `web/base.html`; unchecked pages render standalone.
2. Save, then add zones in the inline (type, order, active). Open each zone to
   edit its JSON `content`/`config` - copy a starting point from
   **Admin > Zone Templates** (`default_content` / `default_config`).
3. Pages are served at `/p/<slug>/`.

Zone JSON is validated on save: each zone type requires a couple of essential
content keys (e.g. `hero_video` needs `"headline"`, `pricing` needs `"plans"`);
empty content is allowed so you can save first and fill in later.

### Per-site scoping and slug rules

- Slugs are unique **per site**, and unique among all-sites pages.
- The same slug may exist as a site page on site A and another on site B.
- On a request, the current site's page wins over an all-sites page with the
  same slug. A page assigned to site A 404s on site B.

## Order forms and submissions

An ORDER_FORM zone (one per page) renders a configurable form
(`content.form_fields`) that POSTs to the plugin API and stores a
`LandingPageSubmission` (status workflow: new / seen / processed / spam) - see
**Admin > Landing Page Submissions**. Features:

- **Turnstile**: set `TURNSTILE_KEY` / `TURNSTILE_SECRET` in `.env`. With an
  empty secret, verification is skipped (useful in dev).
- **Rate limiting**: per-IP (default 2/hour) and per-email (default 3/day),
  configurable via `LANDING_PAGES_RATE_LIMIT_*` settings.
- **Email validation**: typo suggestions, disposable-domain blocking
  (vendored `email_utils`).
- **File uploads**: stored via Django `default_storage` under
  `landing_pages/submissions/<page-slug>/<zone-id>/`; type/size limited via
  `LANDING_PAGES_ALLOWED_UPLOAD_TYPES` / `LANDING_PAGES_MAX_UPLOAD_MB`
  (defaults: images + PDF, 10 MB).
- **Notifications**: set `notification_email_enabled`, `notification_email_to`,
  `notification_email_cc`, `notification_email_subject` in the zone's `config`
  to get a plain-text email per submission (falls back to `DEFAULT_FROM_EMAIL`
  as recipient).

## Template overrides

Every zone template can be overridden per project the normal Django way: copy
`templates/landing_pages/zones/<type>.html` into your project and edit. A zone
can also point at an alternative template via its `template_name` field, which
is **whitelisted** to `landing_pages/zones/*.html` paths - create e.g.
`templates/landing_pages/zones/hero_video_dark.html` and set
`template_name: landing_pages/zones/hero_video_dark.html`.

With multi_domain's per-site template dirs you can override zone templates for
a single site (e.g. `templates/<template_dir>/landing_pages/zones/faq.html`).

## tailwind-safelist.html (do not delete)

Tailwind 4's JIT compiler only emits classes it sees as literals in scanned
files. Zone styling classes are assembled from editor-configured values
(`bg-primary`, `btn-accent`, ...), so they never appear literally in templates.
`templates/landing_pages/tailwind-safelist.html` lists every class the zone
templates can produce inside an HTML comment - the full color cross-product of
the validated color filters, the color/opacity combinations used by template
defaults and shipped presets, and every size/spacing/typography class implied
by template defaults and preset values. Because it lives in `templates/`, the
Tailwind scan picks it up and keeps those classes in your CSS build. Deleting
it ships unstyled pages in production builds.

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

## Optional root catch-all

Pages are mounted at `/p/<slug>/`. If you want bare `/<slug>/` URLs, add a
catch-all to your **project** `urls.py` as the **LAST** urlpattern (anything
after it is unreachable):

```python
from apps.landing_pages import views as lp_views

urlpatterns = [
    # ... all existing routes, including the installed "p/" include ...
    path("<slug:slug>/", lp_views.landing_page_view, name="landing_page_catchall"),  # MUST BE LAST
]
```

Keep the `p/` include too - the order-form API posts there.

## Security notes

- **Editor trust model**: zone `content`/`config` are rendered with `|safe` in
  several zone templates by design (rich text, embeds). Only staff can edit
  zones - treat zone JSON as trusted, admin-only input and do not expose zone
  editing to untrusted users.
- **Visitor input** is server-side sanitized (`html.escape`, recursively) before
  storage, and re-escaped in the admin.
- **template_name whitelist** prevents zones from `{% include %}`-ing arbitrary
  templates: only `landing_pages/zones/*.html` paths are accepted.
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
  inactive, or the slug resolution is cached - saving the page invalidates the
  cache (timeout 300s, `LANDING_PAGES_CACHE_TIMEOUT`).
- **"Only one Order Form zone is allowed"**: a page can hold a single
  ORDER_FORM zone; deactivate/delete the existing one first.
- **Zone save rejected with missing content keys**: each zone type requires a
  minimal set of keys (see the error message); copy the preset from Zone
  Templates as a starting point.
- **Submissions rejected with 429**: rate limit hit - raise
  `LANDING_PAGES_RATE_LIMIT_*` or add your IP to `LANDING_PAGES_EXEMPT_IPS`
  while testing.
- **i18n**: templates and models are `gettext`-wrapped; only the `en` catalog
  ships. Run `manage.py compilemessages` (optional) after adding translations.
