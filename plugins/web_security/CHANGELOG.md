# Changelog

## 1.5.0 - security hardening (pass 2)

Addresses the remaining High/Medium review findings (security + safe performance
wins). No hot-path behavioural refactors (those are deliberately left for a future
pass). 35 new tests; full app suite 50/50. Adds migrations 0006 and 0007.

Security (2a/2b):
- **SSRF:** the custom IP-reputation `api_url` is https-only, its host is resolved and
  rejected if private/loopback/link-local, and `allow_redirects=False` on all reputation
  calls. (`services/ip_reputation.py`)
- **API-key log leak:** IPQualityScore error handlers log only the IP and exception type.
- **Firewall IP validation:** base-class `_validated_ip(s)` helpers; Cloudflare and AWS now
  validate every IP before building WAF expressions / API payloads. (`services/firewall.py`)
- **Body-buffering DoS:** request-body inspection is skipped when `Content-Length` exceeds
  the cap, so large bodies are never buffered. (`middleware/threat_monitor.py`)
- **Encryption key rotation:** optional `WEB_SECURITY_ENCRYPTION_KEY` decouples encryption
  from `SECRET_KEY`; decrypt failures log loudly. (`encryption.py`)
- **API key at rest:** `IPReputationConfig.api_key` is now stored encrypted (`_api_key` +
  decrypting property); migration `0006` encrypts existing values.
- **Admin secret masking:** firewall credentials show masked values with blank-to-keep; the
  reputation API key uses a write-only field. Secrets are never rendered in the admin.
- **Migration 0004 reverse** now writes valid JSON (was corrupting on rollback).

Performance / correctness (2c):
- Reputation batch lock TTL raised to 900s and per-request timeout lowered to 10s, so a
  slow batch cannot expire its lock and be double-processed. (`tasks.py`, `services/ip_reputation.py`)
- Rate limiting logs loudly (once) on a non-atomic cache backend and flags DummyCache
  (previously it silently disabled limiting). (`models/rate_limit.py`)
- Removed 4 redundant DB indexes (2 duplicated a unique index, 2 duplicated a compound's
  leftmost column); migration `0007`.
- Admin block/unblock actions use a single bulk update instead of N writes. (`admin.py`)
- New weekly `cleanup_old_ip_threat_summaries` task so `IPThreatSummary` no longer grows
  forever (blocked IPs are always kept). (`tasks.py`)
- `views.py` validates the IP before any outbound lookup / cache key; deprecated
  `X-XSS-Protection` set to `0`; critical-threat notification no longer crashes on a `None`
  matched value.

New optional settings: `WEB_SECURITY_ENCRYPTION_KEY`. See `SECURITY_REVIEW.md` for the full
finding list and what remains (behavioural refactors + a few Low items).

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
