"""
Scheduled security report - runs periodically via Celery beat.

Summarizes blocked IPs, recent suspicious requests, and active rate-limit rules from the
last N hours and emails it to the configured recipients. The email is sent with Django's
EmailMessage, so it uses whatever EMAIL_BACKEND the project configures (SMTP, Amazon SES,
an ESP via django-anymail, console, etc.) - nothing here is provider-specific.

Optional settings:
- SECURITY_REPORT_RECIPIENTS: list of addresses (defaults to [DEFAULT_FROM_EMAIL]).
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
def send_security_report(self, hours=12):
    """
    Compile and email a security summary for the last `hours` hours.

    Sections: IP blocking, recent suspicious requests, active rate-limit rules.
    Sent via the project's configured email backend.
    """
    since = timezone.now() - timedelta(hours=hours)

    report_lines = [f"<h2>Security Report - Last {hours} hours</h2>"]
    report_lines.append(f"<p>Generated: {timezone.now().strftime('%Y-%m-%d %H:%M UTC')}</p>")

    # 1. Blocked IPs
    try:
        from apps.web_security.models import IPThreatSummary

        total_blocked = IPThreatSummary.objects.filter(is_blocked=True).count()
        recently_blocked = IPThreatSummary.objects.filter(is_blocked=True, blocked_at__gte=since).count()
        top_threats = IPThreatSummary.objects.filter(is_blocked=True).order_by("-total_threat_score")[:5]

        report_lines.append("<h3>IP Blocking</h3>")
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

    # 2. Recent suspicious requests
    try:
        from apps.web_security.models import SuspiciousRequest

        recent_count = SuspiciousRequest.objects.filter(created_at__gte=since).count()
        report_lines.append("<h3>Suspicious Requests</h3>")
        report_lines.append(f"<p>Logged (last {hours}h): <strong>{recent_count}</strong></p>")
    except Exception as e:
        logger.error("Error checking suspicious requests: %s", e)
        report_lines.append("<p>Error checking suspicious requests (see server logs).</p>")

    # 3. Rate limit summary
    try:
        from apps.web_security.models import RateLimitRule

        report_lines.append("<h3>Rate Limiting</h3>")
        report_lines.append(f"<p>Active rules: {RateLimitRule.objects.filter(is_active=True).count()}</p>")
    except Exception as e:
        logger.error("Error checking rate limits: %s", e)
        report_lines.append("<p>Error checking rate limits (see server logs).</p>")

    # Build and send the email via the project's configured backend.
    html_body = "\n".join(report_lines)
    html_body += "<hr><p style='font-size:11px;color:#999;'>Automated security report</p>"

    recipients = getattr(settings, "SECURITY_REPORT_RECIPIENTS", None) or [settings.DEFAULT_FROM_EMAIL]

    email = EmailMessage(
        subject=f"Security Report - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
        body=html_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=recipients,
    )
    email.content_subtype = "html"

    success = safe_send_email(email)
    if success:
        logger.info("Security report sent to %s", recipients)
    else:
        logger.error("Failed to send security report")

    return {"sent": success, "recipients": recipients}
