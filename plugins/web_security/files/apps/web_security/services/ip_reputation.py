import abc
import logging

import requests
from django.utils import timezone

from apps.web_security.models import IPReputationCache, IPReputationConfig

logger = logging.getLogger(__name__)


class BaseIPReputationService(abc.ABC):
    """Abstract base class for IP reputation services."""

    def __init__(self, config: IPReputationConfig):
        self.config = config
        self.api_key = config.api_key
        self.cache_duration_hours = config.cache_duration_hours

    @abc.abstractmethod
    def check_ip(self, ip_address: str) -> dict:
        """
        Check IP reputation.

        Args:
            ip_address: IP address to check

        Returns:
            dict with reputation data
        """
        pass

    def update_cache(self, ip_address: str, data: dict) -> IPReputationCache:
        """
        Update or create cache entry for IP.

        Args:
            ip_address: IP address
            data: Reputation data

        Returns:
            IPReputationCache instance
        """
        expires_at = timezone.now() + timezone.timedelta(hours=self.cache_duration_hours)

        cache_entry, created = IPReputationCache.objects.update_or_create(
            ip_address=ip_address,
            defaults={
                "abuse_confidence_score": data.get("abuse_confidence_score", 0),
                "is_tor_node": data.get("is_tor_node", False),
                "is_vpn": data.get("is_vpn", False),
                "is_datacenter": data.get("is_datacenter", False),
                "country_code": data.get("country_code", "")[:2],
                "isp": data.get("isp", "")[:255],
                "domain": data.get("domain", "")[:255],
                "total_reports": data.get("total_reports", 0),
                "last_reported_at": data.get("last_reported_at"),
                "raw_response": data.get("raw_response", {}),
                "expires_at": expires_at,
                "check_pending": False,
            },
        )
        return cache_entry


class AbuseIPDBService(BaseIPReputationService):
    """AbuseIPDB IP reputation service."""

    BASE_URL = "https://api.abuseipdb.com/api/v2"

    def check_ip(self, ip_address: str) -> dict:
        """
        Check IP reputation via AbuseIPDB API.

        Args:
            ip_address: IP address to check

        Returns:
            dict with reputation data
        """
        try:
            url = f"{self.BASE_URL}/check"
            headers = {
                "Key": self.api_key,
                "Accept": "application/json",
            }
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": 90,
                "verbose": True,
            }

            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            result = response.json()
            data = result.get("data", {})

            # Parse response
            reputation_data = {
                "abuse_confidence_score": data.get("abuseConfidenceScore", 0),
                "is_tor_node": data.get("isTor", False),
                "is_vpn": data.get("usageType", "").lower() in ("vpn", "proxy"),
                "is_datacenter": data.get("usageType", "").lower() in ("data center", "hosting"),
                "country_code": data.get("countryCode", ""),
                "isp": data.get("isp", ""),
                "domain": data.get("domain", ""),
                "total_reports": data.get("totalReports", 0),
                "last_reported_at": self._parse_date(data.get("lastReportedAt")),
                "raw_response": data,
            }

            # Update cache
            self.update_cache(ip_address, reputation_data)

            logger.info(f"Checked IP {ip_address}: score={reputation_data['abuse_confidence_score']}")

            return reputation_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking IP {ip_address} via AbuseIPDB: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error checking IP {ip_address}: {e}")
            return {"error": str(e)}

    def _parse_date(self, date_str: str | None):
        """Parse ISO date string to datetime."""
        if not date_str:
            return None
        try:
            from django.utils.dateparse import parse_datetime

            return parse_datetime(date_str)
        except Exception:
            return None


class IPQualityScoreService(BaseIPReputationService):
    """IPQualityScore IP reputation service."""

    BASE_URL = "https://ipqualityscore.com/api/json/ip"

    def check_ip(self, ip_address: str) -> dict:
        """
        Check IP reputation via IPQualityScore API.

        Args:
            ip_address: IP address to check

        Returns:
            dict with reputation data
        """
        try:
            url = f"{self.BASE_URL}/{self.api_key}/{ip_address}"
            params = {
                "strictness": 1,
                "allow_public_access_points": "true",
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                return {"error": data.get("message", "Unknown error")}

            # Parse response - IPQualityScore uses different field names
            reputation_data = {
                "abuse_confidence_score": data.get("fraud_score", 0),
                "is_tor_node": data.get("tor", False),
                "is_vpn": data.get("vpn", False) or data.get("proxy", False),
                "is_datacenter": data.get("is_crawler", False),
                "country_code": data.get("country_code", ""),
                "isp": data.get("ISP", ""),
                "domain": data.get("host", ""),
                "total_reports": data.get("recent_abuse", 0) and 1 or 0,
                "last_reported_at": None,
                "raw_response": data,
            }

            # Update cache
            self.update_cache(ip_address, reputation_data)

            logger.info(
                f"Checked IP {ip_address} via IPQualityScore: score={reputation_data['abuse_confidence_score']}"
            )

            return reputation_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error checking IP {ip_address} via IPQualityScore: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error checking IP {ip_address}: {e}")
            return {"error": str(e)}


class CustomAPIService(BaseIPReputationService):
    """Custom API IP reputation service."""

    def __init__(self, config: IPReputationConfig):
        super().__init__(config)
        self.api_url = config.api_url

    def check_ip(self, ip_address: str) -> dict:
        """
        Check IP reputation via custom API.

        Expected response format:
        {
            "abuse_confidence_score": int,
            "is_tor_node": bool,
            "is_vpn": bool,
            "is_datacenter": bool,
            "country_code": str,
            "isp": str,
            "domain": str,
            "total_reports": int
        }
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
            }

            url = self.api_url.replace("{ip}", ip_address)
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            data["raw_response"] = data.copy()

            # Update cache
            self.update_cache(ip_address, data)

            return data

        except Exception as e:
            logger.error(f"Error checking IP {ip_address} via custom API: {e}")
            return {"error": str(e)}


class IPReputationServiceFactory:
    """Factory for creating IP reputation service instances."""

    _services = {
        IPReputationConfig.Provider.ABUSEIPDB: AbuseIPDBService,
        IPReputationConfig.Provider.IPQUALITYSCORE: IPQualityScoreService,
        IPReputationConfig.Provider.CUSTOM: CustomAPIService,
    }

    @classmethod
    def create(cls, config: IPReputationConfig) -> BaseIPReputationService:
        """
        Create an IP reputation service instance.

        Args:
            config: IPReputationConfig instance

        Returns:
            IP reputation service instance

        Raises:
            ValueError: If provider is not supported
        """
        service_class = cls._services.get(config.provider)
        if service_class is None:
            raise ValueError(f"Unsupported IP reputation provider: {config.provider}")
        return service_class(config)

    @classmethod
    def get_default_service(cls) -> BaseIPReputationService | None:
        """
        Get the default IP reputation service.

        Returns:
            Default service or None if not configured
        """
        config = IPReputationConfig.get_default()
        if config is None:
            return None
        return cls.create(config)

    @classmethod
    def check_ip(cls, ip_address: str) -> dict | None:
        """
        Check IP using default service.

        Args:
            ip_address: IP address to check

        Returns:
            Reputation data or None if service not configured
        """
        service = cls.get_default_service()
        if service is None:
            logger.warning("No IP reputation service configured")
            return None
        return service.check_ip(ip_address)
