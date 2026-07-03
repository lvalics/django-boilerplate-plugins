# Web Security

Threat detection, rate limiting, IP reputation checking, and firewall integration
for [django-boilerplate](https://github.com/saaspegasus/django-boilerplate).

## What it does

- **Middleware pipeline** (`apps.web_security.middleware`): blocks known-bad IPs,
  enforces rate limits, logs request IPs, monitors for suspicious/threat patterns,
  and adds security response headers.
- **IP reputation** checking against pluggable providers (AbuseIPDB out of the box),
  with a local cache to avoid re-querying the same address.
- **Firewall sync**: pushes IP blocks out to an external firewall (Cloudflare, AWS
  WAF, Nginx, or iptables) via `apps.web_security.services.firewall`.
- **Admin interface** under Django admin for security settings, firewall configs,
  threat patterns, rate limit rules, IP reputation configs/cache, suspicious
  requests, and per-IP threat summaries.
- **Celery Beat tasks** that auto-block high-threat IPs, batch-check IP reputation,
  sync firewall blocks, and clean up expired reputation cache entries.
- An admin-only IP geolocation lookup endpoint at `web-security/ip-lookup/<ip>/`.

## Requirements

This plugin needs Celery and Redis, both already part of django-boilerplate.

Python dependencies (added automatically to the manual install steps):

- `cryptography>=42` (encrypts firewall credentials at rest)
- `requests>=2.31` (outbound calls to reputation/firewall/geolocation APIs)

## Environment variables

All are optional; the plugin works with sane defaults if left unset.

| Variable | Purpose |
| --- | --- |
| `EXEMPT_IPS` | Comma-separated list of IPs that are never blocked or rate limited. |
| `WHAT_IS_MY_IP` | WhatIsMyIP.com API key for the admin IP-lookup endpoint; falls back to the free `ip-api.com` service when unset. |
| `ABUSEIPDB_API_KEY` | Convenience place to keep your AbuseIPDB key before pasting it into Admin > Web Security > IP Reputation Configs (the key itself is stored per-provider on that model, not read from settings). |

## Install

```bash
python install.py web_security /path/to/your/project          # dry-run
python install.py web_security /path/to/your/project --apply  # apply
```

After applying:

1. Run `make migrations && make migrate` (or `python manage.py migrate web_security`)
   to create the plugin's tables.
2. Register the `CELERY_BEAT_SCHEDULE` entries the installer prints (auto-block,
   IP reputation batch check, firewall sync, reputation cache cleanup) with your
   Celery Beat worker.
3. Optionally seed the built-in threat patterns:
   `python manage.py seed_patterns`.
4. Configure at least one `IPReputationConfig` and/or `FirewallConfig` in the
   Django admin if you want reputation checking or firewall sync active.

## Uninstall

```bash
python install.py web_security /path/to/your/project --uninstall --apply
```
