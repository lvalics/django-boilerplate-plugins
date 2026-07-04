# Kamal Deploy

Shows the deployed application version in the Django admin footer and ships an
interactive [Kamal](https://kamal-deploy.org/) wrapper for versioned deploys.

## What it does

- **`apps/web/version.py`** - resolves the app version from the `KAMAL_VERSION`
  environment variable (set by Kamal during a deploy) or, for local development, from
  the git tag / short commit hash. Also detects the environment (local / staging /
  production). Exposes an `app_version` template context processor.
- **`templates/admin/base_site.html`** - overrides the Django admin base template to
  show `{{ app_version }}` in the footer. The optional Pegasus theme toggle include uses
  `ignore missing`, so it works whether or not that template is present.
- **`kamal.sh`** - an interactive wrapper around Kamal: pick or auto-generate a version,
  guards against deploying uncommitted / unpushed changes, and passes everything else
  through to `kamal`. Runs the official `ghcr.io/basecamp/kamal` image.

## Edition

`edition = "pro"`: the installer only installs this plugin into a project that is already
set up for Kamal, detected by the presence of a **`.kamal/secrets`** file. A project
without it is refused (use `--force` to override).

## Install

```bash
python install.py kamal_deploy /path/to/your/project          # dry-run
python install.py kamal_deploy /path/to/your/project --apply  # apply
```

After applying:

1. Ensure the wrapper is executable: `chmod +x kamal.sh`.
2. The installer registers the `apps.web.version.app_version` context processor in
   `TEMPLATES`; no manual settings edit is needed.
3. Deploy with `./kamal.sh deploy` (interactive), `./kamal.sh deploy --auto`
   (auto-generate a version), or `./kamal.sh <any kamal command>`.

`KAMAL_VERSION` is optional; when unset the version falls back to git.

## Uninstall

```bash
python install.py kamal_deploy /path/to/your/project --uninstall --apply
```

This removes the copied files and the settings block. If `base_site.html` replaced an
existing admin template, restore your backup (`base_site.html.bak`).
