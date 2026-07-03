"""
Management command to set up periodic tasks for web security.

Usage:
    python manage.py setup_web_security_tasks
    python manage.py setup_web_security_tasks --disable
    python manage.py setup_web_security_tasks --list
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Set up Celery Beat periodic tasks for web security."""

    help = "Set up periodic tasks for web security (auto-block, cleanup, firewall sync)"

    # Task configurations: (name, task_path, interval_minutes, description)
    TASKS = [
        (
            "Web Security: Auto-Block High Threats",
            "apps.web_security.tasks.auto_block_high_threats",
            1,  # Every minute
            "Automatically block IPs exceeding threat threshold",
        ),
        (
            "Web Security: Sync Firewall Blocks",
            "apps.web_security.tasks.sync_firewall_blocks",
            5,  # Every 5 minutes
            "Sync blocked IPs to configured firewall (Cloudflare, AWS WAF, etc.)",
        ),
        (
            "Web Security: Cleanup Old Requests",
            "apps.web_security.tasks.cleanup_old_suspicious_requests",
            1440,  # Daily (24 * 60)
            "Delete suspicious request logs older than 30 days",
        ),
        (
            "Web Security: Cleanup Expired Reputation Cache",
            "apps.web_security.tasks.cleanup_expired_reputation_cache",
            1440,  # Daily
            "Remove expired IP reputation cache entries",
        ),
        (
            "Web Security: Check IP Reputation Batch",
            "apps.web_security.tasks.check_ip_reputation_batch",
            5,  # Every 5 minutes
            "Process pending IP reputation checks",
        ),
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--disable",
            action="store_true",
            help="Disable all web security periodic tasks",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List current status of all tasks",
        )

    def handle(self, *args, **options):
        try:
            from django_celery_beat.models import IntervalSchedule, PeriodicTask
        except ImportError:
            self.stderr.write(
                self.style.ERROR("django-celery-beat is not installed. Run: pip install django-celery-beat")
            )
            return

        if options["list"]:
            self._list_tasks(PeriodicTask)
            return

        if options["disable"]:
            self._disable_tasks(PeriodicTask)
            return

        self._setup_tasks(IntervalSchedule, PeriodicTask)

    def _list_tasks(self, PeriodicTask):
        """List current status of web security tasks."""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Web Security Periodic Tasks Status")
        self.stdout.write("=" * 70 + "\n")

        for name, task_path, interval, description in self.TASKS:
            try:
                task = PeriodicTask.objects.get(name=name)
                status = self.style.SUCCESS("ENABLED") if task.enabled else self.style.WARNING("DISABLED")
                last_run = task.last_run_at.strftime("%Y-%m-%d %H:%M") if task.last_run_at else "Never"
                self.stdout.write(f"  [{status}] {name}")
                self.stdout.write(f"           Last run: {last_run}")
            except PeriodicTask.DoesNotExist:
                self.stdout.write(f"  [{self.style.ERROR('NOT SETUP')}] {name}")

        self.stdout.write("")

    def _disable_tasks(self, PeriodicTask):
        """Disable all web security tasks."""
        self.stdout.write("\nDisabling web security periodic tasks...\n")

        for name, _, _, _ in self.TASKS:
            try:
                task = PeriodicTask.objects.get(name=name)
                task.enabled = False
                task.save()
                self.stdout.write(self.style.WARNING(f"  Disabled: {name}"))
            except PeriodicTask.DoesNotExist:
                self.stdout.write(f"  Not found: {name}")

        self.stdout.write(self.style.SUCCESS("\nAll tasks disabled."))

    def _setup_tasks(self, IntervalSchedule, PeriodicTask):
        """Set up all web security periodic tasks."""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write("Setting up Web Security Periodic Tasks")
        self.stdout.write("=" * 70 + "\n")

        # Cache for interval schedules
        schedules = {}

        for name, task_path, interval_minutes, description in self.TASKS:
            # Get or create interval schedule
            if interval_minutes not in schedules:
                schedule, created = IntervalSchedule.objects.get_or_create(
                    every=interval_minutes,
                    period=IntervalSchedule.MINUTES,
                )
                schedules[interval_minutes] = schedule

            schedule = schedules[interval_minutes]

            # Create or update task
            task, created = PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    "task": task_path,
                    "interval": schedule,
                    "enabled": True,
                },
            )

            action = "Created" if created else "Updated"
            interval_str = f"{interval_minutes} min" if interval_minutes < 60 else f"{interval_minutes // 60} hr"

            self.stdout.write(self.style.SUCCESS(f"  {action}: {name}"))
            self.stdout.write(f"           Schedule: Every {interval_str}")
            self.stdout.write(f"           {description}\n")

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("All web security tasks configured!"))
        self.stdout.write("=" * 70)
        self.stdout.write("\nTo check status: python manage.py setup_web_security_tasks --list")
        self.stdout.write("To disable:      python manage.py setup_web_security_tasks --disable\n")
