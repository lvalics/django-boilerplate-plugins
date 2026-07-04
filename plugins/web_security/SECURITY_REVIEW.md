# web_security — security & architecture review

Findings from a multi-agent review (2026-07). Status tracked per item.
✅ = fixed (v1.4.0, pass 1, with regression tests) · ⏳ = scheduled (pass 2+).

## Critical
- ✅ **RCE via admin-set `reload_command`** — `services/firewall.py`. The nginx reload
  command (a DB-stored credential) was executed verbatim via `subprocess`. Now
  allowlisted to exact argv vectors.

## High (security)
- ✅ **IP spoofing via `CF-Connecting-IP` / `X-Real-IP`** — `utils.py`. Trusted by
  default once the peer was a trusted proxy. Now opt-in only
  (`WEB_SECURITY_BEHIND_CLOUDFLARE`, `WEB_SECURITY_TRUST_X_REAL_IP`).
- ✅ **ReDoS timeout was a no-op off the main thread** — `models/threat_pattern.py`.
  SIGALRM only works in the main thread. Now uses the `regex` engine's per-match
  timeout (works everywhere).
- ✅ **nginx config injection + arbitrary-file overwrite** — `services/firewall.py`.
  Unvalidated IPs and an admin-set `config_path`. Now path-confined + atomic writes +
  per-IP validation.
- ✅ **`request.body` buffers the entire body every request** — `middleware/threat_monitor.py`.
  Now skips inspection when `Content-Length` exceeds the cap; small bodies read bounded. (pass 2a)
- ✅ **Validation guard only on the iptables path** — `services/firewall.py`. Base-class
  `_validated_ip(s)` helpers added; Cloudflare + AWS + nginx now validate every IP. (pass 2a)
- ✅ **API key in URL path leaks to logs (IPQualityScore)** — `services/ip_reputation.py`.
  Error handlers log only ip + exception type; key never reaches logs. (pass 2a)
- ✅ **Reputation-batch lock TTL (300s) < worst-case runtime** — TTL raised to 900s and
  per-request timeout lowered to 10s. `tasks.py`, `services/ip_reputation.py`. (pass 2c)
- ✅ **SSRF via `CustomAPIService.api_url`** — `services/ip_reputation.py`. https-only +
  resolve host + reject private/link-local + `allow_redirects=False` on all calls. (pass 2a)

## High/Medium (arch & secrets)
- ⏳ Firewall commands assume the web/worker runs as root — move to a narrow sudoers helper; document.
- ✅ Encryption key derived from `SECRET_KEY`; rotation silently loses creds — added dedicated
  `WEB_SECURITY_ENCRYPTION_KEY` (falls back to SECRET_KEY); loud decrypt-failure logs. `encryption.py`. (pass 2b)
- ✅ `IPReputationConfig.api_key` stored unencrypted — now `_api_key` (encrypted at rest) + decrypting
  `api_key` property; migration `0006`. `models/ip_reputation.py`. (pass 2b)
- ✅ Admin renders secrets in cleartext — FirewallConfigForm shows masked values + blank-to-keep;
  IPReputationConfigForm uses a write-only PasswordInput. `admin.py`. (pass 2b)
- ✅ Reverse migration 0004 writes a repr-dict into a text column — now `json.dumps`. (pass 2b)

## Medium (performance)
- ✅ 5 middleware each re-load settings + re-parse client IP per request — now resolved once
  via `utils.get_cached_settings`/`get_cached_client_ip` and shared on the request. (pass 4)
- ✅ Synchronous DB writes + row lock on the request path on a match — moved to the
  `record_threat_matches` Celery task; the request path now only dispatches. (pass 4)
- ✅ `auto_block` SMTP in-loop under the lock — moved to `send_auto_block_notification`
  dispatched per IP, so SMTP + the recent-requests query run outside the lock. (pass 4)
- ✅ Rate-limit fallback race; DummyCache silently disabled limiting — now logs loudly (once)
  on a non-atomic backend and flags DummyCache. `models/rate_limit.py`. (pass 2c)
- ✅ Duplicate indexes removed (migration `0007`); admin block/unblock now bulk-update. (pass 2c)

## Low / polish
- ✅ `IPThreatSummary` retention — new weekly `cleanup_old_ip_threat_summaries` task (keeps
  blocked IPs). (pass 2c)
- ✅ Report emails embedded raw exception strings + third-party PII — now log server-side
  with a generic marker in the email, and correspondent addresses are masked. (pass 4)
- ✅ `views.py` now validates the IP before any outbound path / cache key. (pass 2c)
- ✅ `X-XSS-Protection` set to `0`; `mask_credentials` fully masks (2b); `notifications.py`
  no longer crashes on `matched_value=None`. (pass 2b/2c)
- ✅ Threat-score bands now scale with `min_confidence_score` (`IPReputationCache.calculate_threat_score`). (pass 4)

## Compatibility (found during pass 4)
- ✅ The plugin's Celery tasks imported `apps.utils.locks` / `apps.utils.email_utils` — helpers
  that exist in neither the free boilerplate nor the paid project (they were dev-only in the
  original repo), so `tasks.py` could not import standalone. Vendored `web_security/locks.py`
  (`task_lock`) and `web_security/email_utils.py` (`safe_send_email`); the plugin is now
  self-contained. (pass 4)
- ✅ `tasks_security_report.py` was user-specific (Mandrill API monitoring, `apps.government_forms`,
  a hardcoded domain, lazy `httpx`). Rewritten generic: IP-blocking / suspicious-requests /
  rate-limit summary, emailed via the project's configured `EMAIL_BACKEND` (no provider lock-in).
  `httpx` dependency dropped. (v1.6.1)

## Refactor (oversized files, pass 3)
- ✅ `admin.py` (1110) → `admin/` package (10 focused modules); `services/firewall.py` (842)
  → `services/firewall/` package (base/cloudflare/aws/nginx/iptables/factory). Verbatim moves,
  public API preserved, largest file now ~294 lines. (pass 3)
