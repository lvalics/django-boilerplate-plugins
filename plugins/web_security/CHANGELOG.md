# Changelog

## 1.4.0 - security hardening (pass 1)

Fixes four actively-exploitable issues found in a security review. Each has a
regression test under `apps/web_security/tests/`.

- **RCE fix (critical):** the nginx `reload_command` (stored in a FirewallConfig
  credential) is now checked against an allowlist of exact argument vectors before
  running. Previously any stored string was executed via `subprocess`, so write
  access to one config row meant code execution. (`services/firewall.py`)
- **nginx injection / arbitrary-file overwrite fix:** `config_path` is confined to
  an allowed directory (`WEB_SECURITY_NGINX_CONFIG_DIR`, default `/etc/nginx`),
  writes are atomic (temp + rename), and every IP is re-validated before being
  written as a `deny` directive so a newline-injected value cannot add nginx
  directives. (`services/firewall.py`)
- **IP-spoofing fix:** `CF-Connecting-IP` and `X-Real-IP` are no longer trusted by
  default (a client could spoof them to evade blocks, frame an IP, or bypass rate
  limits). They are honored only when explicitly opted in via
  `WEB_SECURITY_BEHIND_CLOUDFLARE` / `WEB_SECURITY_TRUST_X_REAL_IP`. The
  right-to-left X-Forwarded-For walk remains the default trusted mechanism.
  (`utils.py`)
- **ReDoS fix:** regex matching now uses the `regex` engine's real per-match
  timeout, which works in every deployment. The previous SIGALRM timeout silently
  did nothing off the main thread (gunicorn gthread, uWSGI threads, ASGI), leaving
  admin-defined patterns unbounded. Adds a `regex` dependency; compiled patterns
  are no longer cached as objects in Redis. (`models/threat_pattern.py`)

New optional settings: `WEB_SECURITY_BEHIND_CLOUDFLARE`,
`WEB_SECURITY_TRUST_X_REAL_IP`, `WEB_SECURITY_NGINX_CONFIG_DIR`. New dependency:
`regex`. No database migrations.

Remaining review findings (validation on Cloudflare/AWS paths, SSRF on the custom
reputation provider, API-key-in-logs, lock-TTL sizing, encryption-key rotation,
unencrypted `IPReputationConfig.api_key`, admin secret masking, perf hot-path
work) are scheduled for pass 2.

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
