# django-boilerplate-plugins

A small, zero-dependency installer and a set of optional plugins for the free
[SaaS Pegasus django-boilerplate](https://github.com/saaspegasus/django-boilerplate).

Each plugin is a self-contained Django app plus a manifest. The installer copies the
plugin's files into your project and wires it into `settings.py` / `urls.py` for you,
so adding a feature is one command instead of a manual merge. Everything it changes
lives inside clearly marked blocks, so installing is reversible.

## Available plugins

| Plugin | Edition | Description |
| --- | --- | --- |
| `web_security` | free | Threat detection, rate limiting, IP reputation, and firewall integration (Cloudflare / AWS WAF / Nginx / iptables), with a Django-admin control panel and Celery background tasks. See `plugins/web_security/README.md`. |
| `kamal_deploy` | pro | Exposes the deployed app version (from `KAMAL_VERSION` or git) via a template context processor, and ships an interactive [Kamal](https://kamal-deploy.org/) deploy wrapper (`kamal.sh`). Showing it in the admin footer is a one-line manual snippet, so the installer never overwrites your admin template. Installs only where the project is set up for Kamal (a `.kamal/secrets` file exists). See `plugins/kamal_deploy/README.md`. |

More plugins are being ported in; run `python install.py --list` to see what a given
checkout ships.

## Usage

Run from a clone of this repository, pointing at your target project:

```bash
python install.py --list                                        # list available plugins
python install.py <plugin> /path/to/your/project                # dry-run (shows the plan)
python install.py <plugin> /path/to/your/project --apply        # apply
python install.py <plugin> /path/to/your/project --uninstall --apply  # remove
```

The installer needs only Python 3.11+ (standard library only). After an install it
prints the manual follow-up steps a plugin needs (env vars, `uv add` for any Python
dependencies, and `make migrate`).

## How it works

- **Dry-run by default.** Nothing is written until you pass `--apply`; the command
  first prints exactly which files it will copy and which settings/URL edits it will make.
- **Idempotent, reversible edits.** All `settings.py` / `urls.py` changes go inside a
  guarded block (`# >>> plugin: <id> >>>` ... `# <<< plugin: <id> <<<`). Re-running
  replaces the block; `--uninstall` removes it and the copied files.
- **Safe file handling.** It refuses to overwrite an existing file unless you pass
  `--force`, and backs up anything it replaces.
- **It never touches your `.env`** and never runs migrations for you; those are printed
  as manual steps.
- **Edition gating.** A plugin marked `edition = "pro"` only installs into a project
  detected as the paid Pegasus edition; `--force` overrides with a warning.

## Repository layout

```
install.py            # the CLI (stdlib only)
installer/            # installer package: manifest, target detection, edition gating,
                      #   file copier, marker-block patcher, runner
plugins/<name>/
  plugin.toml         # manifest: edition, deps, installed_apps, middleware, urls, files
  files/              # the payload, laid out at the paths it lands in the target project
  README.md           # per-plugin docs
tests/                # installer + plugin tests
```

## Adding a plugin

Create `plugins/<name>/` with:

1. `files/` containing the app and any templates, laid out exactly where they should
   land in the target (e.g. `files/apps/<name>/...`, `files/templates/...`).
2. `plugin.toml` describing it:

   ```toml
   id = "my_plugin"
   name = "My Plugin"
   version = "1.0.0"
   edition = "free"                       # or "pro"
   python_dependencies = ["some-pkg>=1.0"]
   installed_apps = ["apps.my_plugin"]
   middleware = ["apps.my_plugin.middleware.Something"]
   files = ["apps/my_plugin/**", "templates/**"]

   [url_mappings]
   "my-plugin/" = "apps.my_plugin.urls"
   ```
3. A `README.md` for the plugin.

Keep the plugin self-contained: it must not import project-specific helpers that only
existed in the source project (check with `grep -rn "from apps.utils" files/`), and it
should degrade gracefully when an optional integration isn't configured.
