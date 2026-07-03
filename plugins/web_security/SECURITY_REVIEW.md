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
- ⏳ **Reputation-batch lock TTL (300s) < worst-case runtime (~1500s)** — `tasks.py`.
- ✅ **SSRF via `CustomAPIService.api_url`** — `services/ip_reputation.py`. https-only +
  resolve host + reject private/link-local + `allow_redirects=False` on all calls. (pass 2a)

## High/Medium (arch & secrets)
- ⏳ Firewall commands assume the web/worker runs as root — move to a narrow sudoers helper; document.
- ⏳ Encryption key derived from `SECRET_KEY`; rotation silently loses creds — dedicated key + surfaced failures. `encryption.py`.
- ⏳ `IPReputationConfig.api_key` stored unencrypted — `models/ip_reputation.py`.
- ⏳ Admin renders secrets in cleartext — `admin.py` (use existing `get_masked_credentials()`).
- ⏳ Reverse migration 0004 writes a repr-dict into a text column (corrupts on rollback).

## Medium (performance)
- ⏳ 5 middleware each re-load settings + re-parse client IP per request — resolve once, stash on `request`.
- ⏳ Synchronous DB writes + row lock on the request path on a match — offload to Celery.
- ⏳ `auto_block` sends SMTP synchronously in-loop under the lock — `tasks.py`.
- ⏳ Rate-limit fallback is a read-modify-write race; DummyCache silently disables limiting — `middleware/rate_limit.py`.
- ⏳ Duplicate indexes (`models/ip_threat_summary.py`, `models/ip_reputation.py`, `models/suspicious_request.py`); per-row admin block/unblock loop (`admin.py`).

## Low / polish
- ⏳ `IPThreatSummary` has no retention cleanup (grows forever).
- ⏳ Report emails embed raw exception strings + third-party PII — `tasks_security_report.py`.
- ⏳ `views.py` interpolates an unvalidated IP into an outbound path + cache key.
- ⏳ Deprecated `X-XSS-Protection: 1; mode=block`; `mask_credentials` leaks first 4 chars;
  `notifications.py` crashes on `matched_value=None`; threat-score bands ignore `min_confidence_score`.

## Refactor (oversized files, pass 3)
- ⏳ `admin.py` (1060 lines) and `services/firewall.py` (740 lines) → split into packages,
  matching the existing `models/` / `services/` / `middleware/` package style.
