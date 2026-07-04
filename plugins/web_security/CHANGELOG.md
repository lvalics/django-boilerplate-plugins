# Changelog

## 1.6.1 - make the security report project-agnostic

`tasks_security_report.py` was user-specific. Made it generic:
- Removed the Mandrill API monitoring section (provider-specific) and its lazy `httpx`
  dependency, the `apps.government_forms` section (an app that does not exist here), and the
  hardcoded `ghidulprimariilor.ro` domain / from-address.
- Added a general "Suspicious Requests" section; report now covers IP blocking, suspicious
  requests, and active rate-limit rules.
- The report email is sent with Django's `EmailMessage`, so it uses whatever `EMAIL_BACKEND`
  the project configures (SMTP, Amazon SES, an ESP via django-anymail, console, etc.) - no
  provider lock-in. `from_email` defaults to `DEFAULT_FROM_EMAIL`.
- Tests updated: the report is exercised through Django's locmem backend; Mandrill/httpx tests
  removed.

## 1.6.0 - request-path offload + self-contained tasks (pass 4)

Behaviour-changing performance refactors + a compatibility fix. Full suite 62 (2 skipped
where httpx is absent).

- **Async threat recording:** on a pattern match the ThreatMonitor middleware no longer does
  synchronous DB writes / row locks inline; it dispatches `record_threat_matches` (Celery) with
  plain serializable args. New `SuspiciousRequest.record()` creates the row from those fields.
  (`middleware/threat_monitor.py`, `models/suspicious_request.py`, `tasks.py`)
- **SMTP out of the lock:** `auto_block_high_threats` dispatches `send_auto_block_notification`
  per IP, so the (blocking) email send and the recent-requests query run outside the task's
  distributed lock. (`tasks.py`)
- **Shared per-request lookup:** `utils.get_cached_settings` / `get_cached_client_ip` resolve
  the settings and client IP once per request; all five middleware reuse them instead of each
  re-querying / re-parsing. (`utils.py`, `middleware/*`)
- **Report email hardening:** raw exception text is logged server-side with a generic marker in
  the email; correspondent addresses are masked. (`tasks_security_report.py`)
- **Threat-score bands scale with `min_confidence_score`** instead of hardcoded 75/50.
  (`models/ip_reputation.py`)
- **Self-contained tasks (compat fix):** the tasks depended on `apps.utils.locks` /
  `apps.utils.email_utils` — helpers absent from both the free boilerplate and the paid project,
  so the tasks could not import standalone. Vendored `locks.py` (`task_lock`, a cache-based
  distributed lock) and `email_utils.py` (`safe_send_email`). The plugin is now self-contained.

## 1.5.1 - refactor: split oversized modules (pass 3)

Pure structural refactor, no behaviour change (full suite 50/50):
- `admin.py` (1110 lines) -> `admin/` package: `mixins`, `forms`, and one module per
  ModelAdmin (`settings_admin`, `firewall_admin`, `threat_pattern_admin`,
  `rate_limit_admin`, `reputation_admin`, `suspicious_admin`, `threat_summary_admin`).
  `admin/__init__.py` imports every submodule so `@admin.register` still runs and re-exports
  the forms/admin classes tests import.
- `services/firewall.py` (842 lines) -> `services/firewall/` package: `base`, `cloudflare`,
  `aws`, `nginx`, `iptables`, `factory`. `__init__.py` re-exports the full public API, so
  `from apps.web_security.services.firewall import FirewallServiceFactory` is unchanged.
- Largest module is now ~294 lines (was 1110). Test mock-patch targets updated to the new
  submodule paths.

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
