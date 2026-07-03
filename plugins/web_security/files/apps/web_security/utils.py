import ipaddress
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def get_trusted_proxies():
    """
    Get set of trusted proxy IPs/networks from settings.

    Configure WEB_SECURITY_TRUSTED_PROXIES in settings as a list of IPs or CIDR ranges.
    Example: ["10.0.0.0/8", "172.16.0.1", "192.168.1.0/24"]

    Returns:
        list: List of ipaddress network objects
    """
    trusted = getattr(settings, "WEB_SECURITY_TRUSTED_PROXIES", [])
    if isinstance(trusted, str):
        trusted = [t.strip() for t in trusted.split(",") if t.strip()]

    networks = []
    for proxy in trusted:
        try:
            # Try as network first (handles both single IPs and CIDR)
            if "/" in proxy:
                networks.append(ipaddress.ip_network(proxy, strict=False))
            else:
                # Single IP - convert to /32 or /128 network
                ip = ipaddress.ip_address(proxy)
                prefix = 32 if ip.version == 4 else 128
                networks.append(ipaddress.ip_network(f"{proxy}/{prefix}"))
        except ValueError:
            logger.warning("Invalid trusted proxy IP/network: %s", proxy)
    return networks


def is_trusted_proxy(ip_string):
    """
    Check if an IP is a trusted proxy.

    Args:
        ip_string: IP address string to check

    Returns:
        bool: True if IP is in trusted proxy list
    """
    if not ip_string:
        return False

    try:
        ip = ipaddress.ip_address(ip_string)
    except ValueError:
        return False

    trusted_networks = get_trusted_proxies()
    return any(ip in network for network in trusted_networks)


def validate_ip(ip_string):
    """
    Validate and normalize an IP address string.

    Args:
        ip_string: IP address string to validate

    Returns:
        str or None: Normalized IP string if valid, None otherwise
    """
    if not ip_string:
        return None

    ip_string = ip_string.strip()
    try:
        # Parse and normalize the IP
        ip = ipaddress.ip_address(ip_string)
        return str(ip)
    except ValueError:
        return None


def is_private_ip(ip_address):
    """
    Check if an IP address is a private/internal IP.

    Private IP ranges (RFC 1918 and others):
    - 10.0.0.0/8
    - 172.16.0.0/12
    - 192.168.0.0/16
    - 127.0.0.0/8 (loopback)
    - 0.0.0.0/8 (unspecified)
    - 169.254.0.0/16 (link-local)
    - ::1/128 (IPv6 loopback)
    - fc00::/7 (IPv6 private)

    Args:
        ip_address: IP address string to check

    Returns:
        bool: True if IP is private/internal
    """
    if not ip_address:
        return False

    try:
        ip = ipaddress.ip_address(ip_address)
        # is_private covers: 10.x, 172.16-31.x, 192.168.x, fc00::/7
        # is_loopback covers: 127.x, ::1
        # is_link_local covers: 169.254.x, fe80::/10
        # is_unspecified covers: 0.0.0.0, ::
        return ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_unspecified
    except ValueError:
        # Invalid IP address format
        return False


def get_client_ip(request):
    """
    Extract the client IP address from the request securely.

    Security considerations:
    - X-Forwarded-For can be spoofed by clients, so we only trust it when
      the request comes from a configured trusted proxy
    - We walk the X-Forwarded-For chain from RIGHT to LEFT, finding the first
      IP that is not a trusted proxy (the actual client)
    - All IPs are validated to prevent injection attacks

    Configure WEB_SECURITY_TRUSTED_PROXIES in settings to enable proxy trust.
    Without trusted proxies configured, only REMOTE_ADDR is used.
    """
    remote_addr = request.META.get("REMOTE_ADDR", "")
    validated_remote = validate_ip(remote_addr)

    # If no trusted proxies configured, use REMOTE_ADDR directly
    # This is the safest default - no header spoofing possible
    trusted_proxies = get_trusted_proxies()
    if not trusted_proxies:
        return validated_remote or ""

    # Only process forwarded headers if request comes from trusted proxy
    if not is_trusted_proxy(remote_addr):
        return validated_remote or ""

    # CF-Connecting-IP is trusted ONLY when the deployment explicitly declares it
    # sits behind Cloudflare. Otherwise a client can send this header to control the
    # derived IP (evade blocks, frame another IP, bypass rate limits), even though the
    # immediate peer is a trusted proxy that may not strip it. Opt in with
    # WEB_SECURITY_BEHIND_CLOUDFLARE = True.
    if getattr(settings, "WEB_SECURITY_BEHIND_CLOUDFLARE", False):
        cf_connecting_ip = request.META.get("HTTP_CF_CONNECTING_IP")
        if cf_connecting_ip:
            validated_cf = validate_ip(cf_connecting_ip)
            if validated_cf:
                return validated_cf

    # X-Real-IP is trusted ONLY when a setting affirms the trusted proxy sets AND
    # strips it (WEB_SECURITY_TRUST_X_REAL_IP = True). Otherwise it is client-spoofable.
    if getattr(settings, "WEB_SECURITY_TRUST_X_REAL_IP", False):
        x_real_ip = request.META.get("HTTP_X_REAL_IP")
        if x_real_ip:
            validated_real = validate_ip(x_real_ip)
            if validated_real:
                return validated_real

    # Process X-Forwarded-For header
    # Format: X-Forwarded-For: client, proxy1, proxy2
    # We walk from RIGHT to LEFT, finding the first non-trusted IP
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Split and reverse to walk from rightmost (closest proxy) to leftmost (client)
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]

        # Walk from right to left
        for ip in reversed(ips):
            validated = validate_ip(ip)
            if not validated:
                # Skip invalid IPs
                continue

            # If this IP is not a trusted proxy, it's our client
            if not is_trusted_proxy(validated):
                return validated

        # All IPs in chain are trusted proxies, use leftmost (original client claim)
        # This handles the case where the chain only contains valid IPs
        for ip in ips:
            validated = validate_ip(ip)
            if validated:
                return validated

    # Fall back to REMOTE_ADDR
    return validated_remote or ""


def get_exempt_ips():
    """
    Get list of exempt IPs from settings.

    Returns:
        set: Set of IP addresses that should never be blocked
    """
    exempt_ips = getattr(settings, "EXEMPT_IPS", "")
    if isinstance(exempt_ips, str):
        return {ip.strip() for ip in exempt_ips.split(",") if ip.strip()}
    return set(exempt_ips) if exempt_ips else set()
