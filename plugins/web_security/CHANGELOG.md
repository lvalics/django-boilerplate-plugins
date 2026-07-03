# Changelog

## 1.3.0 - ported to django-boilerplate-plugins

- Ported `apps/web_security` from the legacy `saas_pegasus_plugin` repo
  (branch `feature/web-security`) via `git archive`, unchanged.
- Added `plugin.toml` manifest: installed app, 5-stage middleware pipeline,
  admin-only URL mapping, 4 Celery Beat scheduled tasks, `cryptography` and
  `requests` as Python dependencies, and 3 optional environment variables
  (`EXEMPT_IPS`, `WHAT_IS_MY_IP`, `ABUSEIPDB_API_KEY`).
- Added integration test verifying the plugin installs cleanly into a fresh
  django-boilerplate project and uninstalls without leaving files or settings
  behind.

Prior history (threat detection with dynamic patterns, rate limiting, IP
reputation via AbuseIPDB, firewall integration for Cloudflare/AWS
WAF/Nginx/iptables, admin interface, global enable/disable) predates this
repo; see the legacy `plugin_examples/web_security/plugin.yml` changelog in
`saas_pegasus_plugin` for the 1.0.0-1.2.x history.
