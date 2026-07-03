from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class SuspiciousRequest(BaseModel):
    """
    Log of detected suspicious requests.

    Stores details about requests that matched threat patterns
    for analysis and reporting.
    """

    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP Address"),
        help_text=_("Client IP address"),
    )
    path = models.TextField(
        verbose_name=_("Path"),
        help_text=_("Requested URL path"),
    )
    method = models.CharField(
        max_length=10,
        verbose_name=_("Method"),
        help_text=_("HTTP method"),
    )
    user_agent = models.TextField(
        blank=True,
        default="",
        verbose_name=_("User Agent"),
        help_text=_("Client user agent string"),
    )
    headers = models.JSONField(
        default=dict,
        verbose_name=_("Headers"),
        help_text=_("Request headers"),
    )
    body_preview = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Body Preview"),
        help_text=_("First 1000 chars of request body"),
    )
    pattern_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Pattern ID"),
        help_text=_("ID of the matched threat pattern"),
    )
    pattern_name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Pattern Name"),
        help_text=_("Name of the matched pattern"),
    )
    category = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name=_("Category"),
        help_text=_("Threat category"),
    )
    threat_level = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name=_("Threat Level"),
        help_text=_("Threat severity level"),
        db_index=True,
    )
    threat_score = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Threat Score"),
        help_text=_("Score assigned to this request"),
    )
    matched_value = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Matched Value"),
        help_text=_("The value that matched the pattern"),
    )
    response_code = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Response Code"),
        help_text=_("HTTP response status code"),
    )
    action_taken = models.CharField(
        max_length=50,
        blank=True,
        default="",
        verbose_name=_("Action Taken"),
        help_text=_("Action taken in response (logged, blocked, etc.)"),
    )

    class Meta:
        verbose_name = _("Suspicious Request")
        verbose_name_plural = _("Suspicious Requests")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ip_address", "-created_at"]),
            models.Index(fields=["category", "-created_at"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.ip_address} - {self.path[:50]} ({self.threat_level})"

    @classmethod
    def log_suspicious_request(
        cls,
        request,
        ip_address,
        match_info,
        response_code=None,
        action_taken="logged",
    ):
        """
        Log a suspicious request.

        Args:
            request: Django HttpRequest
            ip_address: Client IP address
            match_info: Dict with pattern match info
            response_code: HTTP response code (optional)
            action_taken: Action taken (logged, blocked, etc.)

        Returns:
            SuspiciousRequest: Created log entry
        """
        # Extract headers (filter sensitive ones)
        headers = {}
        sensitive_headers = {"Authorization", "Cookie", "X-CSRFToken"}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                header_name = key[5:].replace("_", "-").title()
                if header_name not in sensitive_headers:
                    headers[header_name] = value[:500]  # Truncate long values

        # Get body preview (if applicable)
        body_preview = ""
        if request.method in ("POST", "PUT", "PATCH"):
            try:
                body = request.body.decode("utf-8", errors="replace")
                body_preview = body[:1000]
            except Exception:
                pass

        return cls.objects.create(
            ip_address=ip_address,
            path=request.path[:2000],
            method=request.method,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            headers=headers,
            body_preview=body_preview,
            pattern_id=match_info.get("pattern_id"),
            pattern_name=match_info.get("pattern_name", "")[:100],
            category=match_info.get("category", "")[:20],
            threat_level=match_info.get("threat_level", "")[:20],
            threat_score=match_info.get("threat_score", 0),
            matched_value=match_info.get("matched_value", "")[:200],
            response_code=response_code,
            action_taken=action_taken[:50],
        )

    @classmethod
    def get_recent_by_ip(cls, ip_address, hours=24):
        """
        Get recent suspicious requests from an IP.

        Args:
            ip_address: IP address to look up
            hours: How many hours back to look

        Returns:
            QuerySet: Recent suspicious requests
        """
        from django.utils import timezone

        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        return cls.objects.filter(ip_address=ip_address, created_at__gte=cutoff)

    @classmethod
    def get_stats(cls, hours=24):
        """
        Get statistics about recent suspicious requests.

        Args:
            hours: How many hours back to analyze

        Returns:
            dict: Statistics about suspicious requests
        """
        from django.db.models import Count, Sum
        from django.utils import timezone

        cutoff = timezone.now() - timezone.timedelta(hours=hours)
        requests = cls.objects.filter(created_at__gte=cutoff)

        return {
            "total_requests": requests.count(),
            "unique_ips": requests.values("ip_address").distinct().count(),
            "by_category": dict(
                requests.values("category").annotate(count=Count("id")).values_list("category", "count")
            ),
            "by_threat_level": dict(
                requests.values("threat_level").annotate(count=Count("id")).values_list("threat_level", "count")
            ),
            "total_threat_score": requests.aggregate(total=Sum("threat_score"))["total"] or 0,
        }
