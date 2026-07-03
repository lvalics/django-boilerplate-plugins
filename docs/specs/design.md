# django-boilerplate-plugins — Design Spec

**Date:** 2026-07-03
**Status:** Approved design, pending spec review
**Target repo:** `github.com/lvalics/django-boilerplate-plugins` — a **new, private** repo
under the owner's account, created fresh (its own clean git history; none of the
`saas_pegasus_plugin` feature-branch history is carried over). The existing
`saaspegasus/django-boilerplate` repo is **not** used and stays untouched.
**Scope of THIS spec:** the distribution mechanism (installer + unified manifest + edition gating) and the first pilot plugin (`web_security`). The remaining six plugins each get their own follow-up spec/plan.

---

## 1. Problem & Goal

Seven plugins were developed inside the **paid** SaaS Pegasus project
(`saas_pegasus_plugin`), each on a `feature/*` branch, packaged loosely under
`plugin_examples/` with two inconsistent manifest formats and `sync.sh` scripts
that only *package* files (no installer). Several plugins write into paid-only
apps (`apps/sites`, `apps/ecommerce`, `apps/landing_pages`) that the **free**
`django-boilerplate` does not have.

**Goal:** a new, dedicated monorepo that makes these plugins installable into a
free `django-boilerplate` project (and, for PRO-only plugins, into a paid
Pegasus project) via a single installer, cleanly usable by other people. Once
proven, this replaces the ad-hoc `saas_pegasus_plugin` distribution.

### Success criteria
- `python install.py web_security /path/to/target --apply` copies files, patches
  `settings.py`/`urls.py` idempotently, and prints post-install steps.
- Re-running is a no-op; `--uninstall` cleanly reverses it.
- A `pro`-marked plugin refuses to install on a free target unless `--force`.
- No untrusted plugin code is executed during install.
- `web_security` installs into a fresh free boilerplate and its admin/migrations work.

---

## 2. Security preconditions (from the pre-migration audit)

A static, read-only audit of all feature branches + Pegasus baseline found **no
trojan indicators** (no reverse shells, obfuscation, exfil sinks, npm lifecycle
hooks, tampered CI, embedded blobs, committed secrets, or opaque binaries). The
reported infection lived in `node_modules` (a file hidden in a `fonts/` /
`webfonts/` dir, almost certainly FontAwesome's), which is gitignored, never
committed, and no longer on disk. The free lockfile is `lockfileVersion: 3` with
118/118 packages carrying sha512 integrity hashes and zero non-official
registries.

**Hard requirements baked into this design:**
1. Build the new repo by extracting file **blobs** from git (`git show` /
   `git archive`) — never by *running* the legacy `sync.sh` / `install.py`.
2. Never copy `node_modules`; the new repo ships none. Consumers use `npm ci`
   (integrity-enforced), not loose `npm install`.
3. Keep the clean, integrity-pinned `package-lock.json`; do not regenerate loosely.
4. `.gitignore` must cover `node_modules/`.
5. The installer executes **no untrusted plugin code**. The only code it may run
   is the *target's own* `manage.py` (for the optional `db_table` edition check),
   and only read-only.

---

## 3. Repo structure

```
django-boilerplate-plugins/
  install.py                  # thin CLI entry (argparse) → installer package
  installer/                  # stdlib-only package, focused modules
    __init__.py
    manifest.py               # load + validate plugin.toml (tomllib)
    target.py                 # validate target project, locate settings.py/urls.py
    edition.py                # edition gating (app/file/setting/db_table checks)
    copier.py                 # file copy with backup / --force
    patcher.py                # marker-block patch of settings.py / urls.py
    runner.py                 # orchestrate install / uninstall + dry-run plan
  plugins/
    web_security/
      plugin.toml             # unified manifest (stdlib tomllib)
      files/                  # payload, laid out at target-relative paths
        apps/web_security/…
        templates/…
      README.md
      CHANGELOG.md
    kamal_deploy/  …          # follow-up specs
  tests/                      # pytest, tmp_path fixtures (fake target projects)
  docs/
    manifest-spec.md
    authoring-a-plugin.md
  README.md                   # plugin catalog + quickstart
  pyproject.toml              # dev-only: pytest; the installer itself needs no deps
  .gitignore                  # node_modules/, .env, __pycache__, etc.
```

Each plugin is self-contained under `files/`, mirroring where each file lands in
the target project. No `node_modules`, `.zip`, or `.env` is ever committed.

---

## 4. Unified manifest (`plugin.toml`)

Replaces the two inconsistent legacy formats. Standardizes on a single **TOML**
schema parsed with the **stdlib `tomllib`** (Python 3.11+), keeping the installer
zero-dependency. Carries everything the `web_security`-style manifest needed;
the flat `files:`-list style is dropped.

> **Decision (2026-07-03):** TOML chosen over YAML/JSON because it is the only
> option that keeps the installer stdlib-only (no PyYAML) while remaining
> comment-friendly and human-authorable. `tomllib` is read-only, which is all the
> installer needs.

```toml
id = "web_security"
name = "Web Security"
version = "1.3.0"
description = "Threat detection, rate limiting, IP reputation, firewall integration."
target = "django-boilerplate"

edition = "free"              # free (default) = installs anywhere · pro = gated

python_dependencies = ["cryptography>=42"]   # appended to pyproject / printed as `uv add …`
installed_apps = ["apps.web_security"]
middleware = [                # appended to END of MIDDLEWARE (after auth)
  "apps.web_security.middleware.ip_block.IPBlockMiddleware",
  "apps.web_security.middleware.rate_limit.RateLimitMiddleware",
]
files = ["apps/web_security/**", "templates/**"]   # globs copied into target

post_install_notes = """
1. Add the env vars below to your .env.
2. Run: make migrations && make migrate
"""

# Evaluated ONLY when edition = "pro"; target must satisfy any_of (all_of also supported).
[requires]
any_of = [
  { app = "apps.subscriptions" },
  { file = "apps/teams/models.py" },
  { setting = { name = "PEGASUS_PRO", equals = true } },
  { db_table = "subscriptions_subscription" },   # optional live-DB check
]

[url_mappings]
"web-security/" = "apps.web_security.urls"

[celery_beat_schedule.auto-block-threats]
task = "apps.web_security.tasks.auto_block_high_threats"
schedule = 60.0

# DOCUMENTED only — never auto-written to .env
[[env_vars]]
name = "ABUSEIPDB_API_KEY"
required = false
default = ""
```

### Manifest field semantics
- `edition`: `free` → no gate. `pro` → installer evaluates `requires` first.
- `requires.any_of` / `requires.all_of`: list of marker checks. Marker types:
  - `app: <dotted>` — present in target `INSTALLED_APPS` **or** as an `apps/<name>/` dir.
  - `file: <relpath>` — path exists in target.
  - `setting: {name, equals}` — value read from target settings.
  - `db_table: <name>` — exists in target DB (optional; read-only; degrades to warning if DB unreachable).
- `files`: globs relative to `plugins/<id>/files/`, copied to the same relative path in target.
- `middleware`: appended to the end of `MIDDLEWARE` (sufficient for these plugins,
  which want to run after authentication).

---

## 5. Installer behavior — `python install.py <plugin> <target> [flags]`

**Flags:** `--apply` (write; default is dry-run), `--force` (override edition gate
and overwrite files), `--uninstall`, `--list`.

### Steps (in order)
1. **Resolve plugin** from `plugins/<name>/plugin.toml`; validate schema.
2. **Validate target** is a django-boilerplate project: require `manage.py`,
   `apps/`, `pyproject.toml`. Locate the settings module and `urls.py`.
3. **Edition gate** (only if `edition: pro`): evaluate `requires`. Static markers
   (`app`/`file`/`setting`) checked against target source. `db_table` checked via
   a read-only query through the target's own Django settings; if the DB is
   unreachable, emit a warning and treat that single check as "unknown" rather
   than crashing. On failure → refuse with a clear message unless `--force`.
4. **Plan** (always printed first): list files to copy (new vs overwrite) and
   settings/urls patches to apply. Dry-run stops here unless `--apply`.
5. **Copy** `files/**` into target. Refuse to overwrite an existing file unless
   `--force`; when overwriting with `--force`, back up to `<file>.bak`.
6. **Patch idempotently** using guarded marker blocks (avoids fragile in-place
   list edits and makes uninstall trivial):
   ```python
   # >>> plugin: web_security >>>
   INSTALLED_APPS += ["apps.web_security"]
   MIDDLEWARE += ["apps.web_security.middleware.ip_block.IPBlockMiddleware"]
   CELERY_BEAT_SCHEDULE = {**globals().get("CELERY_BEAT_SCHEDULE", {}),
                           "auto-block-threats": {…}}
   # <<< plugin: web_security <<<
   ```
   The same marker-block pattern appends to `urlpatterns` in `urls.py`.
   If a marker block for this plugin already exists, replace it (idempotent).
7. **Dependencies:** append `python_dependencies` to `pyproject.toml` (or, if that
   is ambiguous, print the exact `uv add …` commands).
8. **`.env`:** never modified — print required/optional env vars as manual steps.
9. **Migrations:** printed as a manual step, not auto-run.
10. **Summary:** print `post_install_notes`.

### `--uninstall`
Remove the plugin's marker blocks from `settings.py`/`urls.py`, delete the files
listed in `files` (restoring any `<file>.bak` if present), and print which
`python_dependencies` / env vars the user may want to remove manually.

### Idempotency & safety
- All patches live inside `# >>> plugin: <id> >>> … # <<<` markers → re-run
  replaces, uninstall removes, nothing duplicates.
- Overwrites require `--force` and always back up.
- Edition-gate `db_table` is the only path that runs target code, read-only.

---

## 6. Building the repo from the feature branches (porting workflow)

For each plugin (done in its own follow-up spec, except `web_security` here):
1. Extract the plugin's files straight out of its `feature/*` branch with
   `git show <branch>:<path>` / `git archive` (read-only; **no** `sync.sh`).
2. Refactor paid-app dependencies to stand alone: `apps/sites/*` (and, for
   landingpage, `apps/ecommerce` / `apps/landing_pages`) → a self-contained
   `apps/<plugin>/` that owns its own models/middleware.
3. Author the unified `plugin.yaml`, `README.md`, `CHANGELOG.md`.
4. Verify install into a fresh free boilerplate; run migrations.

---

## 7. Edition assignments

- `kamal_deploy` → **`pro`** (per owner decision).
- All others → default **`free`**, revisited per plugin during its port; a plugin
  becomes `pro` only if it genuinely needs a paid feature.
- The edition-gating mechanism is **built and unit-tested in this spec** using a
  synthetic `pro` manifest, so `kamal_deploy` and later pro plugins drop into it.

---

## 8. Implementation order (each = its own plan)

1. **This spec:** installer + unified manifest + edition gating + `web_security`
   pilot (self-contained → best first real target).
2. `kamal_deploy` (low effort; only touches `apps/web`; `edition: pro`).
3. Refactor-to-standalone group, ascending effort:
   `multi_domain` → `mailfixing` → `s3media` → `django_npm_dev` → `landingpage`.

---

## 9. Out of scope (for this spec)
- Porting the six non-pilot plugins (each is a follow-up spec).
- A package-registry / PyPI distribution model (chosen approach is copy+patch).
- Auto-editing `.env` or auto-running migrations.
- Full dependency-lockfile typosquat audit (npm surface already verified clean at
  the manifest level; deeper audit is a separate optional task).
