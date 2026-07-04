"""Tests for the multi_domain plugin: manifest, apps.api decoupling, and settings wiring."""

from pathlib import Path

from installer import manifest as manifest_mod
from installer import patcher

PLUGINS = Path(__file__).resolve().parents[1] / "plugins"
PLUGIN_DIR = PLUGINS / "multi_domain"
FILES_ROOT = PLUGIN_DIR / "files"


def _manifest():
    return manifest_mod.load(PLUGIN_DIR / "plugin.toml")


# The real boilerplate MIDDLEWARE order (see the task brief / target settings.py).
BASE_MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "waffle.middleware.WaffleMiddleware",
]

_DEBUG_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
_PROD_LOADERS = [("django.template.loaders.cached.Loader", list(_DEBUG_LOADERS))]


def _fake_settings(loaders):
    return {
        "MIDDLEWARE": list(BASE_MIDDLEWARE),
        "INSTALLED_APPS": [],
        "TEMPLATES": [{"OPTIONS": {"loaders": list(loaders), "context_processors": []}}],
    }


def _exec_settings_block(loaders):
    ns = _fake_settings(loaders)
    block = patcher.build_settings_block(_manifest())
    exec(compile(block, "<settings_append>", "exec"), ns)
    return ns


# --- 1. Manifest & file globs ------------------------------------------------


def test_manifest_basics():
    m = _manifest()
    assert m.id == "multi_domain"
    assert m.edition == "free"
    assert m.version == "1.5.0"
    assert m.installed_apps == ["apps.sites"]
    assert m.url_mappings == {"": "apps.sites.urls"}


def test_files_globs_match_payload():
    m = _manifest()
    assert m.files, "manifest declares no files"
    matched = set()
    for pattern in m.files:
        hits = [p for p in FILES_ROOT.glob(pattern) if p.is_file()]
        assert hits, f"glob {pattern!r} matched no payload files"
        matched.update(hits)
    # Every .py and template file in the payload is covered by some declared glob.
    on_disk = {p for p in FILES_ROOT.rglob("*") if p.is_file()}
    assert on_disk == matched
    # Spot-check a couple of key payload files exist.
    assert (FILES_ROOT / "apps/sites/middleware/multi_domain.py").is_file()
    assert (FILES_ROOT / "templates/sites/includes/head_scripts.html").is_file()


# --- 2. apps.api decoupling / self-containment -------------------------------


def test_apps_api_imports_are_guarded():
    """Any payload file that mentions apps.api must guard it with except ImportError."""
    offenders = []
    for py in (FILES_ROOT / "apps/sites").rglob("*.py"):
        src = py.read_text(encoding="utf-8")
        if "apps.api" in src and "except ImportError" not in src:
            offenders.append(str(py.relative_to(FILES_ROOT)))
    assert offenders == [], f"unguarded apps.api usage in: {offenders}"


def test_payload_is_self_contained():
    """Only apps.sites.*, BaseModel, and guarded apps.api imports are allowed."""
    bad = []
    for py in (FILES_ROOT / "apps/sites").rglob("*.py"):
        for i, line in enumerate(py.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not (stripped.startswith("from apps.") or stripped.startswith("import apps.")):
                continue
            ok = (
                stripped.startswith("from apps.sites")
                or stripped.startswith("import apps.sites")
                or "apps.utils.models import BaseModel" in stripped
                or "apps.api" in stripped  # guarded elsewhere (see test above)
            )
            if not ok:
                bad.append(f"{py.relative_to(FILES_ROOT)}:{i}: {stripped}")
    assert bad == [], f"non-self-contained imports: {bad}"


def test_no_threading_local_in_request_state():
    """middleware/multi_domain.py and template_loader.py use asgiref Local, not threading.local."""
    for rel in ("apps/sites/middleware/multi_domain.py", "apps/sites/template_loader.py"):
        src = (FILES_ROOT / rel).read_text(encoding="utf-8")
        assert "threading.local()" not in src, f"{rel} still uses threading.local()"
        assert "from asgiref.local import Local" in src, f"{rel} missing asgiref Local import"


# --- 3. settings_append wiring ----------------------------------------------


def test_settings_middleware_ordering():
    ns = _exec_settings_block(_DEBUG_LOADERS)
    mw = ns["MIDDLEWARE"]

    # DynamicAllowedHostsMiddleware inserted before SecurityMiddleware.
    assert mw.index("apps.sites.middleware.DynamicAllowedHostsMiddleware") < mw.index(
        "django.middleware.security.SecurityMiddleware"
    )
    # CsrfViewMiddleware replaced by DynamicCsrfMiddleware.
    assert "django.middleware.csrf.CsrfViewMiddleware" not in mw
    assert "apps.sites.middleware.DynamicCsrfMiddleware" in mw
    # The four middleware sit right after AuthenticationMiddleware, in order.
    auth_i = mw.index("django.contrib.auth.middleware.AuthenticationMiddleware")
    assert mw[auth_i + 1 : auth_i + 5] == [
        "apps.sites.middleware.MultiDomainMiddleware",
        "apps.sites.middleware.ThreadLocalMiddleware",
        "apps.sites.middleware.DynamicCorsMiddleware",
        "apps.sites.middleware.AuthCallbackMiddleware",
    ]
    # AuthDomainMiddleware right after allauth's AccountMiddleware.
    account_i = mw.index("allauth.account.middleware.AccountMiddleware")
    assert mw[account_i + 1] == "apps.sites.middleware.AuthDomainMiddleware"


def test_settings_scalars_and_context_processor():
    ns = _exec_settings_block(_DEBUG_LOADERS)
    assert ns["SITE_CACHE_TIMEOUT"] == 300
    assert ns["AUTH_TOKEN_EXPIRY_MINUTES"] == 5
    assert "apps.sites.context_processors.site_config" in ns["TEMPLATES"][0]["OPTIONS"]["context_processors"]


def test_settings_loader_debug_shape():
    """DEBUG shape: list of loader strings -> SiteTemplateLoader first, no cached wrapper."""
    ns = _exec_settings_block(_DEBUG_LOADERS)
    loaders = ns["TEMPLATES"][0]["OPTIONS"]["loaders"]
    assert loaders[0] == "apps.sites.template_loader.SiteTemplateLoader"
    assert loaders[1:] == _DEBUG_LOADERS


def test_settings_loader_prod_shape():
    """PROD shape: [(cached.Loader, [...])] -> SiteAwareCachedLoader wrapping SiteTemplateLoader first."""
    ns = _exec_settings_block(_PROD_LOADERS)
    loaders = ns["TEMPLATES"][0]["OPTIONS"]["loaders"]
    assert len(loaders) == 1
    outer, inner = loaders[0]
    assert outer == "apps.sites.template_loader.SiteAwareCachedLoader"
    assert inner[0] == "apps.sites.template_loader.SiteTemplateLoader"
    # The original cached inner loaders are preserved after the site loader.
    assert inner[1:] == _DEBUG_LOADERS


# --- 4. Site-aware cached template loader ------------------------------------


def test_site_aware_cached_loader_implements_cache_key():
    """SiteAwareCachedLoader has a real, site-aware cache_key (placeholder is gone)."""
    src = (FILES_ROOT / "apps/sites/template_loader.py").read_text(encoding="utf-8")
    assert "class SiteAwareCachedLoader" in src
    # Real implementation: a cache_key override that keys on template_dir.
    key_i = src.index("class SiteAwareCachedLoader")
    body = src[key_i:]
    assert "def cache_key" in body, "cache_key override missing"
    assert "template_dir" in body, "cache_key does not reference template_dir"
    # Placeholder comment must be gone.
    assert "Task 2" not in src
    assert "Placeholder for now" not in src


def test_site_specific_hit_logged_at_debug_level():
    """The site-specific template hit log is debug, not info (hot-path noise removed)."""
    src = (FILES_ROOT / "apps/sites/template_loader.py").read_text(encoding="utf-8")
    hit_i = src.index("loaded site-specific template")
    # Walk back to the logger call opening this statement.
    call_start = src.rindex("logger.", 0, hit_i)
    assert src[call_start:hit_i].startswith("logger.debug("), (
        "site-specific template hit must be logged at debug level"
    )
    assert "logger.info(" not in src


# --- 5. Dependencies ---------------------------------------------------------


def test_python_dependencies_include_pyjwt():
    deps = _manifest().python_dependencies
    assert any(d.lower().startswith("pyjwt") for d in deps), deps
