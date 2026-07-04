"""
Submission notification emails.

Plain Django ``EmailMessage`` helpers - no pluggable service layer. Notification
recipients are configured per ORDER_FORM zone in ``zone.config``:

- ``notification_email_enabled``: bool (default False)
- ``notification_email_to``: primary recipient (falls back to DEFAULT_FROM_EMAIL)
- ``notification_email_cc``: comma-separated CC recipients
- ``notification_email_subject``: subject, supports ``{field}`` placeholders from
  the submitted form data plus ``{page}`` and ``{date}``
"""

import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_submission_notification(zone, submission) -> bool:
    """
    Email the configured recipients about a new form submission.

    Returns True when a mail was sent, False when notifications are disabled or
    sending failed (failures are logged, never raised - a broken mail server
    must not break the visitor-facing submission flow).
    """
    config = zone.config or {}

    if not config.get("notification_email_enabled", False):
        return False

    email_to = (config.get("notification_email_to") or "").strip()
    if not email_to:
        email_to = getattr(settings, "DEFAULT_FROM_EMAIL", "")
    if not email_to:
        logger.debug("Submission notification enabled but no recipient configured")
        return False

    email_cc = (config.get("notification_email_cc") or "").strip()
    cc_list = [e.strip() for e in email_cc.split(",") if e.strip()] if email_cc else []

    form_data = submission.form_data or {}

    # Build subject with placeholders
    subject = config.get("notification_email_subject", "New form submission")
    for key, value in form_data.items():
        placeholder = "{" + key + "}"
        if placeholder in subject:
            subject = subject.replace(placeholder, str(value) if value else "")
    subject = subject.replace("{page}", zone.page.title)
    subject = subject.replace("{date}", datetime.now().strftime("%Y-%m-%d %H:%M"))

    # Plain text body
    lines = [
        f"New form submission from: {zone.page.title}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Submission ID: {submission.pk}",
        "",
        "Form Data:",
        "-" * 40,
    ]
    for key, value in form_data.items():
        lines.append(f"{key}: {value}")
    if submission.uploaded_files:
        lines += ["", "Uploaded files:", "-" * 40]
        for item in submission.uploaded_files:
            if isinstance(item, dict):
                lines.append(f"{item.get('field', 'file')}: {item.get('path', '')} ({item.get('name', '')})")
            else:
                lines.append(str(item))

    message = EmailMessage(
        subject=subject,
        body="\n".join(lines),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[email_to],
        cc=cc_list,
    )

    try:
        message.send(fail_silently=False)
    except Exception as e:
        logger.error("Failed to send submission notification email: %s", e)
        return False

    logger.info(
        "Sent submission notification email to %s%s",
        email_to,
        f" (CC: {', '.join(cc_list)})" if cc_list else "",
    )
    return True
