import logging
import re

from apps.web_security.models import SecuritySettings
from apps.web_security.utils import get_client_ip

logger = logging.getLogger(__name__)

# Common bot user-agent patterns
BOT_PATTERNS = re.compile(
    r"(bot|crawl|spider|scrape|scan|curl|wget|python-requests|httpx|go-http|"
    r"headless|phantom|selenium|playwright|scrapy|nutch|java/|libwww|"
    r"masscan|nmap|nikto|sqlmap|zgrab|censys|shodan|semrush|ahrefs|"
    r"dotbot|bytespider|gptbot|claudebot|petalbot|yandexbot|baiduspider)",
    re.IGNORECASE,
)


def _classify_agent(user_agent: str) -> str:
    """Classify a user-agent as bot, empty, or browser."""
    if not user_agent:
        return "NO-UA"
    if BOT_PATTERNS.search(user_agent):
        return "BOT"
    return ""


class RequestIPLoggingMiddleware:
    """
    Middleware to log request IPs for analysis.

    Provides detailed logging of requests when enabled,
    useful for debugging and security analysis.

    Logs 4xx/5xx responses at WARNING level with IP and user-agent
    so scanning bots are visible in console output.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get security settings
        settings = SecuritySettings.get_settings()

        # Check if security and logging are enabled
        if not settings.security_enabled or not settings.logging_enabled:
            return self.get_response(request)

        # Get client IP
        ip_address = get_client_ip(request)

        # Store IP on request for other middleware/views
        request.client_ip = ip_address

        # Log request details at debug level
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:200]
        logger.debug("Request: %s %s from %s (UA: %s)", request.method, request.path, ip_address, user_agent)

        response = self.get_response(request)

        # Log 4xx/5xx at WARNING with IP + bot classification
        if response.status_code >= 400:
            bot_tag = _classify_agent(user_agent)
            tag = f" [{bot_tag}]" if bot_tag else ""
            logger.warning(
                "%s %d %s %s%s (UA: %s)",
                request.method,
                response.status_code,
                request.path,
                ip_address,
                tag,
                user_agent[:100],
            )
        else:
            logger.debug(
                "Response: %d for %s %s from %s", response.status_code, request.method, request.path, ip_address
            )

        return response
