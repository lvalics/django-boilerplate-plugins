"""Tests for the landing_pages plugin: manifest, scope cuts, self-containment, landmine fixes."""

import re
from pathlib import Path

from installer import manifest as manifest_mod
from installer import patcher

PLUGINS = Path(__file__).resolve().parents[1] / "plugins"
PLUGIN_DIR = PLUGINS / "landing_pages"
FILES_ROOT = PLUGIN_DIR / "files"
APP_ROOT = FILES_ROOT / "apps/landing_pages"


def _manifest():
    return manifest_mod.load(PLUGIN_DIR / "plugin.toml")


def _payload_files():
    return [p for p in FILES_ROOT.rglob("*") if p.is_file()]


# --- 1. Manifest & file globs ------------------------------------------------


def test_manifest_basics():
    m = _manifest()
    assert m.id == "landing_pages"
    assert m.edition == "free"
    assert m.version == "2.0.0"
    assert m.installed_apps == ["apps.landing_pages"]
    assert m.url_mappings == {"p/": "apps.landing_pages.urls"}


def test_manifest_requires_apps_sites():
    """multi_domain (apps.sites) is a hard prerequisite via the requires marker."""
    m = _manifest()
    assert m.requires == {"any_of": [{"app": "apps.sites"}]}


def test_python_dependencies():
    deps = _manifest().python_dependencies
    assert any(d.lower().startswith("requests") for d in deps), deps
    # PyJWT is multi_domain's dependency, not ours.
    assert not any(d.lower().startswith("pyjwt") for d in deps), deps


def test_files_globs_match_payload():
    m = _manifest()
    assert m.files, "manifest declares no files"
    matched = set()
    for pattern in m.files:
        hits = [p for p in FILES_ROOT.glob(pattern) if p.is_file()]
        assert hits, f"glob {pattern!r} matched no payload files"
        matched.update(hits)
    # Every payload file is covered by some declared glob.
    on_disk = set(_payload_files())
    assert on_disk == matched
    # Spot-check key payload files.
    assert (APP_ROOT / "models/pages.py").is_file()
    assert (APP_ROOT / "management/commands/install_zone_templates.py").is_file()
    assert (FILES_ROOT / "templates/landing_pages/tailwind-safelist.html").is_file()


def test_env_vars_declared():
    names = {v["name"] for v in _manifest().env_vars}
    assert names == {"TURNSTILE_KEY", "TURNSTILE_SECRET"}
    assert all(v.get("required") is False for v in _manifest().env_vars)


# --- 2. settings_append wiring ----------------------------------------------


def test_settings_append_exec():
    """The settings block executes against a fake namespace and lands the settings."""
    ns = {
        "INSTALLED_APPS": [],
        "MIDDLEWARE": [],
        "env": lambda key, default=None: default,
    }
    block = patcher.build_settings_block(_manifest())
    exec(compile(block, "<settings_append>", "exec"), ns)

    assert ns["TURNSTILE_KEY"] == ""
    assert ns["TURNSTILE_SECRET"] == ""
    assert ns["LANDING_PAGES_RATE_LIMIT_IP_REQUESTS"] == 2
    assert ns["LANDING_PAGES_RATE_LIMIT_IP_WINDOW"] == 3600
    assert ns["LANDING_PAGES_RATE_LIMIT_EMAIL_REQUESTS"] == 3
    assert ns["LANDING_PAGES_RATE_LIMIT_EMAIL_WINDOW"] == 86400
    assert ns["LANDING_PAGES_EXEMPT_IPS"] == []
    assert ns["LANDING_PAGES_CACHE_TIMEOUT"] == 300
    # No middleware manipulation from this plugin.
    assert ns["MIDDLEWARE"] == []
    # No celery beat schedule (analytics were dropped).
    assert not _manifest().celery_beat_schedule
    assert "CELERY_BEAT_SCHEDULE" not in ns


# --- 3. Payload self-containment ----------------------------------------------


def test_payload_is_self_contained():
    """Only apps.landing_pages.*, apps.utils.models, and (function-level) apps.sites imports."""
    bad = []
    for py in APP_ROOT.rglob("*.py"):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not (stripped.startswith("from apps.") or stripped.startswith("import apps.")):
                continue
            ok = (
                stripped.startswith("from apps.landing_pages")
                or stripped.startswith("import apps.landing_pages")
                or "apps.utils.models import BaseModel" in stripped
                or "apps.sites" in stripped  # must be function-level; checked below
            )
            if not ok:
                bad.append(f"{py.relative_to(FILES_ROOT)}:{i}: {stripped}")
    assert bad == [], f"non-self-contained imports: {bad}"


def test_no_module_level_apps_sites_import():
    """apps.sites may only be imported inside a function body (plugin stays importable without it)."""
    offenders = []
    for py in APP_ROOT.rglob("*.py"):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            if "apps.sites" not in line:
                continue
            stripped = line.strip()
            if stripped.startswith("#") or not (
                stripped.startswith("from apps.sites") or stripped.startswith("import apps.sites")
            ):
                continue
            # Module-level imports start at column 0; function-level ones are indented.
            if not line[0].isspace():
                offenders.append(f"{py.relative_to(FILES_ROOT)}:{i}: {stripped}")
    assert offenders == [], f"module-level apps.sites imports: {offenders}"


# --- 4. Scope cuts: no dropped-feature leftovers -------------------------------


DROPPED_FEATURE_WORDS = [
    "openai",
    "boto3",
    "webhook",
    "analytics",
    "execCommand",
    "PurchaseExtension",
    "zones_override",
    "ecommerce",
]


def test_no_dropped_feature_leftovers():
    """The payload contains no trace of dropped features (CHANGELOG/README may mention them)."""
    offenders = []
    for path in _payload_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        lowered = text.lower()
        for word in DROPPED_FEATURE_WORDS:
            if word.lower() in lowered:
                offenders.append(f"{path.relative_to(FILES_ROOT)}: {word}")
    assert offenders == [], f"dropped-feature leftovers: {offenders}"


def test_no_dropped_modules_shipped():
    """Dropped legacy modules are not part of the payload."""
    for name in (
        "api_editor.py",
        "serializers_editor.py",
        "urls_catchall.py",
        "tasks.py",
        "permissions.py",
        "services",
    ):
        assert not (APP_ROOT / name).exists(), f"{name} should not ship in lean v1"
    for js in ("analytics.js", "inline-editor.js"):
        assert not (APP_ROOT / "static/landing_pages/js" / js).exists(), js
    assert not (APP_ROOT / "static/landing_pages/admin").exists(), "admin JS/CSS was dropped"


def test_no_binary_locale_or_migration_files():
    """No .mo binaries, no generated migrations, no __pycache__."""
    assert not [p for p in _payload_files() if p.suffix == ".mo"]
    migrations = sorted(p.name for p in (APP_ROOT / "migrations").glob("*.py"))
    assert migrations == ["__init__.py"], migrations
    assert not [p for p in FILES_ROOT.rglob("__pycache__") if p.exists()]
    # Only the en catalog ships.
    locales = sorted(p.name for p in (APP_ROOT / "locale").iterdir())
    assert locales == ["en"], locales


# --- 5. Landmine fixes (source-level) ------------------------------------------


def test_zone_template_whitelist_regex_present():
    src = (APP_ROOT / "models/pages.py").read_text(encoding="utf-8")
    assert r"^landing_pages/zones/[a-z0-9_/-]+\.html$" in src
    # get_template_name only honors whitelisted overrides.
    assert "ZONE_TEMPLATE_NAME_RE.match" in src


def test_per_site_unique_constraints_present():
    src = (APP_ROOT / "models/pages.py").read_text(encoding="utf-8")
    assert 'UniqueConstraint(\n                fields=["site", "slug"]' in src.replace("\r\n", "\n")
    assert "condition=Q(site__isnull=True)" in src
    # Slug is no longer globally unique.
    assert "unique=True" not in src


def test_required_content_keys_schema():
    src = (APP_ROOT / "models/pages.py").read_text(encoding="utf-8")
    assert "REQUIRED_CONTENT_KEYS" in src
    assert 'ZoneType.HERO_VIDEO: ["headline"]' in src
    views = (APP_ROOT / "views.py").read_text(encoding="utf-8")
    # Redirect zones read the key the presets actually use.
    assert 'content.get("redirect_url")' in views


def test_cache_is_actually_used_by_view():
    views = (APP_ROOT / "views.py").read_text(encoding="utf-8")
    assert "get_landing_page_id(slug, site_id)" in views
    cache_src = (APP_ROOT / "cache.py").read_text(encoding="utf-8")
    assert "delete_pattern" not in cache_src, "django-redis-specific API must not be used"
    assert "_bump_version" in cache_src


def test_rate_limiter_honors_trusted_proxy_count():
    src = (APP_ROOT / "rate_limiter.py").read_text(encoding="utf-8")
    assert "SITES_TRUSTED_PROXY_COUNT" in src
    assert "def get_client_ip" in src
    # The plugin must not import the helper from apps.sites.
    assert "apps.sites" not in src


def test_tailwind_safelist_shipped():
    safelist = (FILES_ROOT / "templates/landing_pages/tailwind-safelist.html").read_text(encoding="utf-8")
    assert "btn-primary" in safelist
    assert "bg-accent" in safelist
    assert "text-base-300" in safelist
    tags = (APP_ROOT / "templatetags/landing_page_tags.py").read_text(encoding="utf-8")
    assert "ALLOWED_COLORS" in tags
    # DaisyUI 4 variable syntax must be gone (Tailwind 4 / DaisyUI 5 target).
    assert "var(--p)" not in tags


def test_email_utils_vendored():
    assert (APP_ROOT / "email_utils.py").is_file()
    for py in ("views.py", "forms.py"):
        src = (APP_ROOT / py).read_text(encoding="utf-8")
        assert "from .email_utils import validate_and_normalize_email" in src, py
        assert "apps.utils.email_utils" not in src, py


def test_payload_python_compiles():
    # compile() only (no .pyc written), so the payload tree stays free of __pycache__.
    for py in APP_ROOT.rglob("*.py"):
        compile(py.read_text(encoding="utf-8"), str(py), "exec")


def test_gettext_kept():
    """i18n wrapping is retained in models and views-facing code."""
    src = (APP_ROOT / "models/pages.py").read_text(encoding="utf-8")
    assert "gettext_lazy" in src
    assert re.search(r"\b_\(", src)


# --- 6. Tailwind safelist completeness (self-verifying, F1/F2 fix pass) --------


TEMPLATES_ROOT = FILES_ROOT / "templates/landing_pages"
ZONES_ROOT = TEMPLATES_ROOT / "zones"

# prefix-{{ ... default:'value' }} interpolations remaining in zone templates
# (color sites go through validated filters after F1 and no longer match).
CLASS_INTERP_RE = re.compile(r"([a-z][a-z0-9-]*)-\{\{[^}]*default:'([a-z0-9/.-]+)'")

# DOM id / JS hook prefixes, not Tailwind utilities.
NON_UTILITY_PREFIXES = {
    "field",
    "zone",
    "carousel",
    "carousel-modal",
    "faq-accordion",
    "gallery",
    "lightbox",
    "order-form",
    "pricing-toggle",
}


def _safelist_classes():
    text = (TEMPLATES_ROOT / "tailwind-safelist.html").read_text(encoding="utf-8")
    body = text.split("<!--", 1)[1].split("-->", 1)[0]
    return {
        line.strip()
        for line in body.splitlines()
        if line.strip() and " " not in line.strip() and not line.strip().startswith("=")
    }


def test_safelist_covers_all_template_interpolations():
    """Every literal class implied by a prefix-{{ ...|default:'x' }} site is safelisted."""
    safelist = _safelist_classes()
    implied = set()
    for tpl in sorted(ZONES_ROOT.glob("*.html")):
        for prefix, value in CLASS_INTERP_RE.findall(tpl.read_text(encoding="utf-8")):
            if prefix not in NON_UTILITY_PREFIXES:
                implied.add(f"{prefix}-{value}")
    assert len(implied) > 100, f"suspiciously few interpolated classes found ({len(implied)})"
    missing = sorted(implied - safelist)
    assert missing == [], f"classes implied by zone templates but missing from tailwind-safelist.html: {missing}"


def test_safelist_keeps_color_enum_cross_product():
    """Spot-check the enum cross-product (incl. the black/white/transparent core extension)."""
    safelist = _safelist_classes()
    missing = [
        cls
        for cls in (
            "bg-primary", "bg-accent", "bg-base-200", "bg-black", "bg-white", "bg-transparent",
            "text-base-300", "text-white", "text-base-content", "text-primary-content",
            "border-base-300", "border-secondary", "btn-primary", "btn-outline", "btn-ghost",
            "badge-accent", "badge-outline", "ring-primary", "link-primary", "divide-base-300",
            "from-primary", "via-base-100", "to-secondary", "checkbox-primary", "radio-primary",
            "toggle-primary", "alert-info",
            # variant + opacity combos used by the shipped presets/defaults
            "hover:bg-base-200/50", "text-base-content/70", "peer-checked:bg-primary",
            "file:text-primary-content", "focus:ring-primary/50",
        )
        if cls not in safelist
    ]
    assert missing == [], f"expected safelist entries missing: {missing}"


def test_zone_templates_use_color_filters():
    """No raw color-class interpolation survives F1 (colors go through validated filters)."""
    offenders = []
    for tpl in sorted(ZONES_ROOT.glob("*.html")):
        text = tpl.read_text(encoding="utf-8")
        for needle in ("bg-{{", "btn-{{", "badge-{{", "border-{{"):
            if needle in text:
                offenders.append(f"{tpl.name}: {needle}")
    assert offenders == [], f"raw color interpolations remain: {offenders}"
    tags = (APP_ROOT / "templatetags/landing_page_tags.py").read_text(encoding="utf-8")
    for filter_name in ("bg_color", "text_color", "btn_color", "border_color", "badge_color", "text_content_color"):
        assert f'"{filter_name}"' in tags or f"def {filter_name}" in tags, filter_name
