"""Email helpers (vendored so the plugin is self-contained)."""

import logging

logger = logging.getLogger(__name__)


def safe_send_email(email) -> bool:
    """
    Send a prepared Django EmailMessage, returning True on success.

    Never raises: a failed send is logged and reported as False so a broken mail server
    cannot crash the caller (e.g. a scheduled report task).
    """
    try:
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False
