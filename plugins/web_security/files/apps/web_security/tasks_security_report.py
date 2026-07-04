"""
Scheduled security report — runs twice daily via Celery beat.

Checks for contact form spam, blocked IPs, and Mandrill email stats.
Sends a summary email to admins.
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

from apps.web_security.email_utils import safe_send_email

logger = logging.getLogger(__name__)


def _mask_email(addr):
    """Mask the local part of an email address for display, e.g. 'john.doe@example.com' -> '***@example.com'."""
    if not addr or "@" not in addr:
        return addr or "?"
    _, domain = addr.split("@", 1)
    return f"***@{domain}"


@shared_task(bind=True, max_retries=0)
def send_security_report(self):
    """
    Compile and send a security report covering the last 12 hours.

    Checks:
    1. Mandrill email stats (spam subjects, rejected emails)
    2. Blocked IPs from threat summary
    3. Recent suspicious requests
    4. Contact form submission attempts
    """
    hours = 12
    since = timezone.now() - timedelta(hours=hours)

    report_lines = [f"<h2>Security Report — Last {hours} hours</h2>"]
    report_lines.append(f"<p>Generated: {timezone.now().strftime('%Y-%m-%d %H:%M UTC')}</p>")

    # 1. Blocked IPs
    try:
        from apps.web_security.models import IPThreatSummary

        total_blocked = IPThreatSummary.objects.filter(is_blocked=True).count()
        recently_blocked = IPThreatSummary.objects.filter(
            is_blocked=True,
            blocked_at__gte=since,
        ).count()

        top_threats = IPThreatSummary.objects.filter(
            is_blocked=True,
        ).order_by("-total_threat_score")[:5]

        report_lines.append("<h3>🛡️ IP Blocking</h3>")
        report_lines.append(f"<p>Total blocked IPs: <strong>{total_blocked}</strong></p>")
        report_lines.append(f"<p>Newly blocked (last {hours}h): <strong>{recently_blocked}</strong></p>")

        if top_threats:
            report_lines.append("<table border='1' cellpadding='4' cellspacing='0'>")
            report_lines.append("<tr><th>IP</th><th>Score</th><th>Requests</th><th>Categories</th></tr>")
            for t in top_threats:
                report_lines.append(
                    f"<tr><td>{t.ip_address}</td><td>{t.total_threat_score}</td>"
                    f"<td>{t.request_count}</td><td>{t.categories_detected}</td></tr>"
                )
            report_lines.append("</table>")
    except Exception as e:
        logger.error("Error checking blocked IPs: %s", e)
        report_lines.append("<p>Error checking blocked IPs (see server logs).</p>")

    # 2. Mandrill email stats
    try:
        import httpx

        mandrill_key = getattr(settings, "MANDRILL_API_KEY", "")
        if mandrill_key:
            date_from = since.strftime("%Y-%m-%d")
            date_to = timezone.now().strftime("%Y-%m-%d")

            resp = httpx.post(
                "https://mandrillapp.com/api/1.0/messages/search.json",
                json={
                    "key": mandrill_key,
                    "query": "*",
                    "date_from": date_from,
                    "date_to": date_to,
                    "limit": 100,
                },
                timeout=15,
            )
            emails = resp.json() if resp.status_code == 200 else []

            total = len(emails)
            sent = sum(1 for e in emails if e.get("state") == "sent")
            rejected = sum(1 for e in emails if e.get("state") == "rejected")
            bounced = sum(1 for e in emails if e.get("state") == "bounced")
            opened = sum(1 for e in emails if e.get("opens", 0) > 0)

            # Detect spam subjects
            spam_keywords = ["bitcoin", "btc", "withdraw", "lottery", "prize", "tираж", "сюрприз"]
            spam_emails = [e for e in emails if any(kw in (e.get("subject", "") or "").lower() for kw in spam_keywords)]

            report_lines.append("<h3>📧 Mandrill Email Stats</h3>")
            report_lines.append(
                f"<p>Total: {total} | Sent: {sent} | Rejected: {rejected} | Bounced: {bounced} | Opened: {opened}</p>"
            )

            if spam_emails:
                report_lines.append(
                    f"<p style='color:red;'><strong>⚠️ {len(spam_emails)} spam emails detected!</strong></p>"
                )
                report_lines.append("<ul>")
                for se in spam_emails[:5]:
                    report_lines.append(
                        f"<li>{se.get('state')} → {_mask_email(se.get('email'))} — {(se.get('subject') or '?')[:60]}</li>"
                    )
                report_lines.append("</ul>")
            else:
                report_lines.append("<p style='color:green;'>✅ No spam emails detected.</p>")
        else:
            report_lines.append("<p>Mandrill API key not configured.</p>")
    except Exception as e:
        logger.error("Error checking Mandrill: %s", e)
        report_lines.append("<p>Error checking Mandrill (see server logs).</p>")

    # 3. Government forms submissions
    try:
        from apps.government_forms.models import FormRetrievalAttempt, FormSubmission

        recent_submissions = FormSubmission.objects.filter(created_at__gte=since).count()
        failed_retrievals = FormRetrievalAttempt.objects.filter(
            attempted_at__gte=since,
            success=False,
        ).count()

        report_lines.append("<h3>📋 Government Forms</h3>")
        report_lines.append(f"<p>New submissions: {recent_submissions}</p>")
        report_lines.append(f"<p>Failed retrieval attempts: {failed_retrievals}</p>")
    except Exception as e:
        logger.error("Error checking forms: %s", e)
        report_lines.append("<p>Error checking forms (see server logs).</p>")

    # 4. Rate limit summary
    try:
        from apps.web_security.models import RateLimitRule

        rules = RateLimitRule.objects.filter(is_active=True)
        report_lines.append("<h3>⏱️ Rate Limiting</h3>")
        report_lines.append(f"<p>Active rules: {rules.count()}</p>")
    except Exception as e:
        logger.error("Error checking rate limits: %s", e)
        report_lines.append("<p>Error checking rate limits (see server logs).</p>")

    # Build and send email
    html_body = "\n".join(report_lines)
    html_body += "<hr><p style='font-size:11px;color:#999;'>Automated security report — ghidulprimariilor.ro</p>"

    recipients = getattr(settings, "SECURITY_REPORT_RECIPIENTS", None)
    if not recipients:
        recipients = [getattr(settings, "DEFAULT_FROM_EMAIL", "contact@ghidulprimariilor.ro")]

    email = EmailMessage(
        subject=f"🛡️ Security Report — {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        body=html_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@ghidulprimariilor.ro"),
        to=recipients,
    )
    email.content_subtype = "html"

    success = safe_send_email(email)
    if success:
        logger.info("Security report sent to %s", recipients)
    else:
        logger.error("Failed to send security report")

    return {"sent": success, "recipients": recipients}
