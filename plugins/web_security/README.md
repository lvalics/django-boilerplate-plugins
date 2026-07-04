# Web Security

Threat detection, rate limiting, IP reputation checking, and firewall integration
for [django-boilerplate](https://github.com/saaspegasus/django-boilerplate).

Self-contained: it bundles its own task-lock and email helpers, so it does not depend
on any project-specific utilities.

## What it does

- **Middleware pipeline** (`apps.web_security.middleware`): blocks known-bad IPs,
  enforces rate limits, logs request IPs, monitors for suspicious/threat patterns,
  and adds security response headers. The five middleware share a single per-request
  settings + client-IP lookup.
- **IP reputation** checking against pluggable providers (AbuseIPDB out of the box),
  with a local cache. Outbound calls are timeout-bounded and, for custom providers,
  SSRF-guarded (https only, private/link-local hosts refused, no redirects).
- **Firewall sync**: pushes IP blocks out to an external firewall (Cloudflare, AWS
  WAF, Nginx, or iptables) via `apps.web_security.services.firewall`. Every IP is
  validated before use; the Nginx reload command is allowlisted and its config path
  is confined to an allowed directory.
- **Admin interface** for security settings, firewall configs, threat patterns, rate
  limit rules, IP reputation configs/cache, suspicious requests, and per-IP threat
  summaries. Secrets (firewall credentials, reputation API keys) are stored encrypted
  at rest and never rendered in the admin.
- **Celery Beat tasks**: auto-block high-threat IPs, batch-check IP reputation, sync
  firewall blocks, clean up expired reputation cache, and prune stale IP threat
  summaries. Threat records and auto-block notifications are written off the request
  path / outside the auto-block lock.
- **Optional security report** (`send_security_report`): a summary email (blocked IPs,
  suspicious requests, rate-limit rules) sent through the project's own email backend.
- An admin-only IP geolocation lookup endpoint at `web-security/ip-lookup/<ip>/`.

## Requirements

Celery and Redis (both already part of django-boilerplate).

Python dependencies (the installer prints `uv add` commands for these):

- `cryptography>=42` - encrypts firewall/reputation credentials at rest.
- `requests>=2.31` - outbound calls to reputation/firewall/geolocation APIs.
- `regex>=2024` - regex engine with a real per-match timeout (reliable ReDoS
  protection in threaded/ASGI deployments, unlike a SIGALRM-based timeout).

## Configuration

All settings are optional; the plugin works with safe defaults. Add them to your
Django settings (wire from environment variables as you prefer).

### Client-IP trust (important behind a proxy/CDN)

| Setting | Default | Purpose |
| --- | --- | --- |
| `WEB_SECURITY_TRUSTED_PROXIES` | `[]` | List of proxy IPs/CIDRs. Only when the request arrives from one of these is `X-Forwarded-For` parsed (rightmost non-proxy = client). With none set, only `REMOTE_ADDR` is trusted. |
| `WEB_SECURITY_BEHIND_CLOUDFLARE` | `False` | Trust the `CF-Connecting-IP` header. Leave off unless you are actually behind Cloudflare (otherwise it is client-spoofable). |
| `WEB_SECURITY_TRUST_X_REAL_IP` | `False` | Trust the `X-Real-IP` header. Enable only if your trusted proxy sets AND strips it. |

### Secrets & firewall

| Setting | Default | Purpose |
| --- | --- | --- |
| `WEB_SECURITY_ENCRYPTION_KEY` | derived from `SECRET_KEY` | Dedicated Fernet key for encrypting stored credentials. Set it so rotating `SECRET_KEY` does not make stored secrets undecryptable. Generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. |
| `WEB_SECURITY_NGINX_CONFIG_DIR` | `/etc/nginx` | Directory the Nginx firewall blocklist file must stay within. |

### Reporting & misc

| Setting | Default | Purpose |
| --- | --- | --- |
| `SECURITY_REPORT_RECIPIENTS` | `[DEFAULT_FROM_EMAIL]` | Recipients of the optional `send_security_report` email (sent via your configured `EMAIL_BACKEND`). |
| `EXEMPT_IPS` | `""` | Comma-separated IPs that are never blocked or rate limited. |
| `WHAT_IS_MY_IP` | unset | WhatIsMyIP.com API key for the admin IP-lookup endpoint; falls back to the free `ip-api.com` service when unset. |
| `ABUSEIPDB_API_KEY` | unset | Convenience place to keep your AbuseIPDB key; the key is actually stored per-provider on `IPReputationConfig` in the admin, not read from settings. |

Advanced tuning (rarely needed): `WEB_SECURITY_REGEX_TIMEOUT` (default `0.1`s),
`WEB_SECURITY_MAX_PATTERN_LENGTH` (`500`), `WEB_SECURITY_MAX_BODY_SIZE` (`65536` bytes).

## Install

```bash
python install.py web_security /path/to/your/project          # dry-run
python install.py web_security /path/to/your/project --apply  # apply
```

After applying:

1. Run `make migrations && make migrate` (or `python manage.py migrate web_security`)
   to create the plugin's tables.
2. Register the `CELERY_BEAT_SCHEDULE` entries the installer prints (auto-block,
   IP reputation batch check, firewall sync, reputation cache cleanup, IP threat
   summary cleanup) with your Celery Beat worker. Optionally schedule
   `apps.web_security.tasks_security_report.send_security_report` for the summary email.
3. Optionally seed the built-in threat patterns: `python manage.py seed_patterns`.
4. Configure at least one `IPReputationConfig` and/or `FirewallConfig` in the Django
   admin if you want reputation checking or firewall sync active.
5. If you use a proxy/CDN, set `WEB_SECURITY_TRUSTED_PROXIES` (and the Cloudflare /
   X-Real-IP flags as appropriate) so client IPs are resolved correctly.

## Uninstall

```bash
python install.py web_security /path/to/your/project --uninstall --apply
```

See `CHANGELOG.md` for version history and `SECURITY_REVIEW.md` for the security
review and remediation status.
