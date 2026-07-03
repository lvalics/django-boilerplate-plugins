import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_security_notification(
    to_email: str,
    subject: str,
    message: str,
    html_message: str | None = None,
) -> bool:
    """
    Send a security notification email.

    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message

    Returns:
        bool: True if email was sent successfully
    """
    try:
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

        send_mail(
            subject=f"[Security Alert] {subject}",
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent security notification to {to_email}: {subject}")
        return True

    except Exception as e:
        logger.error(f"Failed to send security notification: {e}")
        return False


def notify_auto_block(settings_obj, ip_address: str, threat_score: int, suspicious_requests: list):
    """
    Send notification when an IP is auto-blocked.

    Args:
        settings_obj: SecuritySettings instance
        ip_address: Blocked IP address
        threat_score: Total threat score
        suspicious_requests: List of recent suspicious requests
    """
    if not settings_obj.notify_on_block or not settings_obj.notification_email:
        return

    subject = f"IP Auto-Blocked: {ip_address}"

    # Build request details
    request_details = []
    for req in suspicious_requests[:10]:  # Limit to 10
        request_details.append(
            f"- {req.get('created_at', 'N/A')}: {req.get('method', 'GET')} {req.get('path', '/')} "
            f"({req.get('pattern_name', 'Unknown')})"
        )

    message = f"""
Security Alert: IP Address Auto-Blocked

IP Address: {ip_address}
Threat Score: {threat_score}
Blocked At: {timezone.now().isoformat()}
Block Duration: {settings_obj.block_duration_minutes} minutes

Recent Suspicious Activity:
{chr(10).join(request_details) if request_details else "No details available"}

This IP was automatically blocked because its threat score ({threat_score})
exceeded the threshold ({settings_obj.auto_block_threshold}).

To manage blocked IPs, visit the Web Security admin panel.
"""

    send_security_notification(
        to_email=settings_obj.notification_email,
        subject=subject,
        message=message,
    )


def notify_critical_threat(settings_obj, ip_address: str, threat_info: dict):
    """
    Send notification for critical threats.

    Args:
        settings_obj: SecuritySettings instance
        ip_address: Source IP address
        threat_info: Threat details
    """
    if not settings_obj.notify_on_critical or not settings_obj.notification_email:
        return

    subject = f"Critical Threat Detected: {threat_info.get('pattern_name', 'Unknown')}"

    message = f"""
Security Alert: Critical Threat Detected

IP Address: {ip_address}
Threat Level: {threat_info.get("threat_level", "Unknown")}
Category: {threat_info.get("category", "Unknown")}
Pattern: {threat_info.get("pattern_name", "Unknown")}
Detected At: {timezone.now().isoformat()}

Request Details:
- Path: {threat_info.get("path", "N/A")}
- Method: {threat_info.get("method", "N/A")}
- Matched Value: {(threat_info.get("matched_value") or "N/A")[:200]}

Immediate action may be required. Review this activity in the Web Security admin panel.
"""

    send_security_notification(
        to_email=settings_obj.notification_email,
        subject=subject,
        message=message,
    )


def notify_high_volume_attack(settings_obj, ip_address: str, request_count: int, time_window_minutes: int):
    """
    Send notification for high-volume attacks.

    Args:
        settings_obj: SecuritySettings instance
        ip_address: Source IP address
        request_count: Number of suspicious requests
        time_window_minutes: Time window for the count
    """
    if not settings_obj.notify_on_critical or not settings_obj.notification_email:
        return

    subject = f"High Volume Attack: {request_count} requests from {ip_address}"

    message = f"""
Security Alert: High Volume Attack Detected

IP Address: {ip_address}
Request Count: {request_count} suspicious requests
Time Window: Last {time_window_minutes} minutes
Detected At: {timezone.now().isoformat()}

This may indicate an automated attack or scanning attempt.
The IP may be auto-blocked if it exceeds the threat threshold.

Review this activity in the Web Security admin panel.
"""

    send_security_notification(
        to_email=settings_obj.notification_email,
        subject=subject,
        message=message,
    )
