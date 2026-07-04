# Changelog

## 1.1.0 - ported to django-boilerplate-plugins

- Ported the kamal-deploy plugin (admin version footer + `kamal.sh` wrapper) from the
  legacy `saas_pegasus_plugin` repo.
- Made it self-contained for the installer:
  - The `app_version` context processor now lives in `apps/web/version.py` (a plain file
    copy) instead of modifying an existing `context_processors.py`.
  - Registration uses the manifest's `settings_append` to add the context processor to
    `TEMPLATES`, so no manual settings edit is required.
  - The admin footer template is NOT auto-installed (overwriting a project's
    `base_site.html` would clobber its customisations). The one-line footer snippet is a
    documented post-install step; a ready-to-use example ships in `files/`. The example
    includes the optional Pegasus theme toggle with `ignore missing`.
- `kamal.sh` is the latest wrapper, shipped with its executable bit; no project-specific
  values (uses the official `ghcr.io/basecamp/kamal` image and `$HOME/.ssh`).
- `edition = "pro"`, gated on the presence of a `.kamal/secrets` file in the target.
