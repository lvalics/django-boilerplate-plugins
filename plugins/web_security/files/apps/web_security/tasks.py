import logging

from celery import shared_task
from django.utils import timezone

from apps.utils.locks import task_lock

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
@task_lock(timeout=300)
def auto_block_high_threats(self):
    """
    Automatically block IPs that exceed the threat threshold.

    Runs periodically to check for high-threat IPs and block them.
    Uses distributed lock to prevent concurrent execution.
    """
    try:
        from apps.web_security.models import (
            IPThreatSummary,
            SecuritySettings,
            SuspiciousRequest,
        )
        from apps.web_security.services.notifications import notify_auto_block

        settings = SecuritySettings.get_settings()

        # Check if auto-blocking is enabled
        if not settings.security_enabled or not settings.auto_block_enabled:
            logger.info("Auto-blocking is disabled, skipping")
            return {"status": "skipped", "reason": "disabled"}

        threshold = settings.auto_block_threshold
        duration = settings.block_duration_minutes
        whitelist = settings.get_whitelist_ips()

        # Get high-threat IPs that aren't blocked
        high_threat_ips = IPThreatSummary.get_high_threat_ips(threshold=threshold)

        blocked_count = 0
        for summary in high_threat_ips:
            # Skip whitelisted IPs
            if summary.ip_address in whitelist:
                logger.info(f"Skipping whitelisted IP: {summary.ip_address}")
                continue

            # Block the IP
            IPThreatSummary.block_ip(
                ip_address=summary.ip_address,
                reason=f"Auto-blocked: threat score {summary.total_threat_score} >= {threshold}",
                duration_minutes=duration,
            )

            # Get recent suspicious requests for notification
            recent_requests = list(
                SuspiciousRequest.get_recent_by_ip(summary.ip_address, hours=24).values(
                    "created_at", "method", "path", "pattern_name"
                )[:10]
            )

            # Send notification
            notify_auto_block(
                settings_obj=settings,
                ip_address=summary.ip_address,
                threat_score=summary.total_threat_score,
                suspicious_requests=recent_requests,
            )

            blocked_count += 1
            logger.info(f"Auto-blocked IP {summary.ip_address} (score: {summary.total_threat_score})")

        # Clean up expired blocks
        expired_count = IPThreatSummary.cleanup_expired_blocks()

        return {
            "status": "success",
            "blocked": blocked_count,
            "expired_unblocked": expired_count,
        }

    except Exception as e:
        logger.error(f"Error in auto_block_high_threats: {e}")
        raise self.retry(exc=e, countdown=60) from e


@shared_task(bind=True, max_retries=3)
@task_lock(timeout=300)
def check_ip_reputation_batch(self):
    """
    Check IP reputation for queued IPs.

    Processes IPs marked for reputation checking in batches.
    Uses distributed lock to prevent concurrent API calls.
    """
    try:
        from apps.web_security.models import (
            IPReputationCache,
            IPThreatSummary,
            SecuritySettings,
        )
        from apps.web_security.services.ip_reputation import IPReputationServiceFactory

        settings = SecuritySettings.get_settings()

        # Check if IP reputation is enabled
        if not settings.security_enabled or not settings.ip_reputation_enabled:
            logger.info("IP reputation checking is disabled, skipping")
            return {"status": "skipped", "reason": "disabled"}

        # Get service
        service = IPReputationServiceFactory.get_default_service()
        if service is None:
            logger.warning("No IP reputation service configured")
            return {"status": "skipped", "reason": "no_service"}

        # Get pending IPs (limit to avoid API rate limits)
        pending_ips = IPReputationCache.objects.filter(check_pending=True)[:50]

        checked_count = 0
        error_count = 0
        threat_added = 0

        for cache_entry in pending_ips:
            try:
                result = service.check_ip(cache_entry.ip_address)

                if "error" not in result:
                    checked_count += 1

                    # Add threat score if IP has bad reputation
                    score = cache_entry.calculate_threat_score()
                    if score > 0:
                        IPThreatSummary.add_threat(
                            ip_address=cache_entry.ip_address,
                            threat_score=score,
                            category="reputation",
                        )
                        threat_added += 1
                else:
                    error_count += 1

            except Exception as e:
                logger.error(f"Error checking IP {cache_entry.ip_address}: {e}")
                error_count += 1

        return {
            "status": "success",
            "checked": checked_count,
            "errors": error_count,
            "threats_added": threat_added,
        }

    except Exception as e:
        logger.error(f"Error in check_ip_reputation_batch: {e}")
        raise self.retry(exc=e, countdown=60) from e


@shared_task(bind=True, max_retries=3)
@task_lock(timeout=600)
def sync_firewall_blocks(self):
    """
    Sync blocked IPs to configured firewall.

    Syncs IPs that are blocked but not yet synced to the firewall.
    Uses distributed lock to prevent concurrent firewall updates.
    """
    try:
        from apps.web_security.models import IPThreatSummary, SecuritySettings
        from apps.web_security.services.firewall import FirewallServiceFactory

        settings = SecuritySettings.get_settings()

        # Check if security is enabled
        if not settings.security_enabled or not settings.ip_blocking_enabled:
            logger.info("IP blocking is disabled, skipping firewall sync")
            return {"status": "skipped", "reason": "disabled"}

        # Get firewall service
        service = FirewallServiceFactory.get_default_service()
        if service is None:
            logger.info("No firewall service configured, skipping sync")
            return {"status": "skipped", "reason": "no_service"}

        # Get blocked IPs not synced
        not_synced = IPThreatSummary.get_blocked_not_synced()
        ip_addresses = list(not_synced.values_list("ip_address", flat=True))

        if not ip_addresses:
            logger.info("No blocked IPs to sync")
            return {"status": "success", "synced": 0}

        # Sync to firewall
        result = service.sync_blocks(ip_addresses)

        # Mark as synced
        if result.get("added", 0) > 0 or result.get("already_blocked", 0) > 0:
            not_synced.update(firewall_synced=True)

        logger.info(f"Firewall sync complete: {result}")

        return {
            "status": "success",
            "synced": result.get("added", 0),
            "already_blocked": result.get("already_blocked", 0),
            "failed": result.get("failed", 0),
        }

    except Exception as e:
        logger.error(f"Error in sync_firewall_blocks: {e}")
        raise self.retry(exc=e, countdown=300) from e


@shared_task
def cleanup_expired_reputation_cache():
    """
    Clean up expired IP reputation cache entries.

    Runs daily to remove stale cache entries.
    """
    try:
        from apps.web_security.models import IPReputationCache

        deleted = IPReputationCache.cleanup_expired()
        logger.info(f"Cleaned up {deleted} expired reputation cache entries")

        return {"status": "success", "deleted": deleted}

    except Exception as e:
        logger.error(f"Error in cleanup_expired_reputation_cache: {e}")
        return {"status": "error", "error": str(e)}


@shared_task
def cleanup_old_suspicious_requests(days: int = 30):
    """
    Clean up old suspicious request logs.

    Args:
        days: Delete requests older than this many days
    """
    try:
        from apps.web_security.models import SuspiciousRequest

        cutoff = timezone.now() - timezone.timedelta(days=days)
        deleted, _ = SuspiciousRequest.objects.filter(created_at__lt=cutoff).delete()

        logger.info(f"Cleaned up {deleted} suspicious requests older than {days} days")

        return {"status": "success", "deleted": deleted}

    except Exception as e:
        logger.error(f"Error in cleanup_old_suspicious_requests: {e}")
        return {"status": "error", "error": str(e)}


@shared_task
def generate_threat_report(hours: int = 24):
    """
    Generate a threat report for the specified time period.

    Args:
        hours: Report period in hours

    Returns:
        dict: Report data
    """
    try:
        from django.db.models import Count, Sum

        from apps.web_security.models import IPThreatSummary, SuspiciousRequest

        cutoff = timezone.now() - timezone.timedelta(hours=hours)

        # Suspicious request stats
        requests = SuspiciousRequest.objects.filter(created_at__gte=cutoff)
        request_stats = requests.aggregate(
            total=Count("id"),
            total_score=Sum("threat_score"),
        )

        # Category breakdown
        by_category = dict(requests.values("category").annotate(count=Count("id")).values_list("category", "count"))

        # Threat level breakdown
        by_level = dict(
            requests.values("threat_level").annotate(count=Count("id")).values_list("threat_level", "count")
        )

        # Top IPs
        top_ips = list(
            requests.values("ip_address").annotate(count=Count("id"), score=Sum("threat_score")).order_by("-score")[:10]
        )

        # Blocked IPs
        blocked = IPThreatSummary.objects.filter(is_blocked=True, blocked_at__gte=cutoff).count()

        report = {
            "period_hours": hours,
            "generated_at": timezone.now().isoformat(),
            "total_suspicious_requests": request_stats["total"] or 0,
            "total_threat_score": request_stats["total_score"] or 0,
            "unique_ips": requests.values("ip_address").distinct().count(),
            "ips_blocked": blocked,
            "by_category": by_category,
            "by_threat_level": by_level,
            "top_ips": top_ips,
        }

        logger.info(f"Generated threat report for last {hours} hours")

        return report

    except Exception as e:
        logger.error(f"Error generating threat report: {e}")
        return {"status": "error", "error": str(e)}
