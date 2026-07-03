import json

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.utils import timezone

from apps.web_security.models import IPThreatSummary, SuspiciousRequest


class Command(BaseCommand):
    """Analyze threat data and generate reports."""

    help = "Analyze threat data and generate reports in various formats"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days to analyze (default: 7)",
        )
        parser.add_argument(
            "--format",
            choices=["text", "json", "csv", "iptables", "nginx"],
            default="text",
            help="Output format (default: text)",
        )
        parser.add_argument(
            "--output-file",
            type=str,
            help="Write output to file instead of stdout",
        )
        parser.add_argument(
            "--min-score",
            type=int,
            default=50,
            help="Minimum threat score for blocklist output (default: 50)",
        )
        parser.add_argument(
            "--top",
            type=int,
            default=20,
            help="Number of top IPs to show (default: 20)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        output_format = options["format"]
        output_file = options["output_file"]
        min_score = options["min_score"]
        top_count = options["top"]

        cutoff = timezone.now() - timezone.timedelta(days=days)

        if output_format == "text":
            output = self._generate_text_report(cutoff, top_count)
        elif output_format == "json":
            output = self._generate_json_report(cutoff, top_count)
        elif output_format == "csv":
            output = self._generate_csv_report(cutoff, top_count)
        elif output_format == "iptables":
            output = self._generate_iptables_rules(min_score)
        elif output_format == "nginx":
            output = self._generate_nginx_rules(min_score)
        else:
            output = "Unknown format"

        if output_file:
            with open(output_file, "w") as f:
                f.write(output)
            self.stdout.write(self.style.SUCCESS(f"Report written to {output_file}"))
        else:
            self.stdout.write(output)

    def _generate_text_report(self, cutoff, top_count):
        """Generate a text report of threat analysis."""
        requests = SuspiciousRequest.objects.filter(created_at__gte=cutoff)
        summaries = IPThreatSummary.objects.all()

        # Statistics
        total_requests = requests.count()
        unique_ips = requests.values("ip_address").distinct().count()
        blocked_ips = summaries.filter(is_blocked=True).count()
        total_score = requests.aggregate(total=Sum("threat_score"))["total"] or 0

        # Category breakdown
        by_category = dict(
            requests.values("category").annotate(count=Count("id")).order_by("-count").values_list("category", "count")
        )

        # Threat level breakdown
        by_level = dict(
            requests.values("threat_level")
            .annotate(count=Count("id"))
            .order_by("-count")
            .values_list("threat_level", "count")
        )

        # Top IPs
        top_ips = list(
            summaries.order_by("-total_threat_score")[:top_count].values(
                "ip_address",
                "total_threat_score",
                "request_count",
                "is_blocked",
            )
        )

        # Generate report
        lines = [
            "=" * 60,
            "THREAT ANALYSIS REPORT",
            f"Period: Last {(timezone.now() - cutoff).days} days",
            f"Generated: {timezone.now().isoformat()}",
            "=" * 60,
            "",
            "SUMMARY",
            "-" * 40,
            f"Total Suspicious Requests: {total_requests:,}",
            f"Unique IP Addresses: {unique_ips:,}",
            f"Currently Blocked IPs: {blocked_ips:,}",
            f"Total Threat Score: {total_score:,}",
            "",
            "BY CATEGORY",
            "-" * 40,
        ]

        for category, count in sorted(by_category.items(), key=lambda x: -x[1]):
            lines.append(f"  {category or 'Unknown'}: {count:,}")

        lines.extend(["", "BY THREAT LEVEL", "-" * 40])

        for level, count in sorted(by_level.items(), key=lambda x: -x[1]):
            lines.append(f"  {level or 'Unknown'}: {count:,}")

        lines.extend(["", f"TOP {top_count} THREAT IPs", "-" * 40])

        for ip_data in top_ips:
            blocked = " [BLOCKED]" if ip_data["is_blocked"] else ""
            lines.append(
                f"  {ip_data['ip_address']}: "
                f"score={ip_data['total_threat_score']}, "
                f"requests={ip_data['request_count']}{blocked}"
            )

        lines.extend(["", "=" * 60])

        return "\n".join(lines)

    def _generate_json_report(self, cutoff, top_count):
        """Generate a JSON report."""
        requests = SuspiciousRequest.objects.filter(created_at__gte=cutoff)
        summaries = IPThreatSummary.objects.all()

        report = {
            "generated_at": timezone.now().isoformat(),
            "period_days": (timezone.now() - cutoff).days,
            "summary": {
                "total_requests": requests.count(),
                "unique_ips": requests.values("ip_address").distinct().count(),
                "blocked_ips": summaries.filter(is_blocked=True).count(),
                "total_threat_score": requests.aggregate(total=Sum("threat_score"))["total"] or 0,
            },
            "by_category": dict(
                requests.values("category").annotate(count=Count("id")).values_list("category", "count")
            ),
            "by_threat_level": dict(
                requests.values("threat_level").annotate(count=Count("id")).values_list("threat_level", "count")
            ),
            "top_ips": list(
                summaries.order_by("-total_threat_score")[:top_count].values(
                    "ip_address",
                    "total_threat_score",
                    "request_count",
                    "is_blocked",
                    "first_seen",
                    "last_seen",
                )
            ),
        }

        return json.dumps(report, indent=2, default=str)

    def _generate_csv_report(self, cutoff, top_count):
        """Generate a CSV report of top IPs."""
        summaries = IPThreatSummary.objects.order_by("-total_threat_score")[:top_count]

        lines = ["ip_address,threat_score,request_count,is_blocked,first_seen,last_seen"]

        for s in summaries:
            lines.append(
                f"{s.ip_address},{s.total_threat_score},{s.request_count},"
                f"{s.is_blocked},{s.first_seen.isoformat()},{s.last_seen.isoformat()}"
            )

        return "\n".join(lines)

    def _generate_iptables_rules(self, min_score):
        """Generate iptables rules for blocking high-threat IPs."""
        ips = IPThreatSummary.objects.filter(total_threat_score__gte=min_score).values_list("ip_address", flat=True)

        lines = [
            "#!/bin/bash",
            "# Auto-generated iptables rules for blocking high-threat IPs",
            f"# Generated: {timezone.now().isoformat()}",
            f"# Minimum threat score: {min_score}",
            f"# Total IPs: {len(ips)}",
            "",
        ]

        for ip in ips:
            lines.append(f"iptables -A INPUT -s {ip} -j DROP")

        return "\n".join(lines)

    def _generate_nginx_rules(self, min_score):
        """Generate nginx deny rules for blocking high-threat IPs."""
        ips = IPThreatSummary.objects.filter(total_threat_score__gte=min_score).values_list("ip_address", flat=True)

        lines = [
            "# Auto-generated nginx blocklist",
            f"# Generated: {timezone.now().isoformat()}",
            f"# Minimum threat score: {min_score}",
            f"# Total IPs: {len(ips)}",
            "",
        ]

        for ip in ips:
            lines.append(f"deny {ip};")

        return "\n".join(lines)
