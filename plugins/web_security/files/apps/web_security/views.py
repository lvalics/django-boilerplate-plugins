import logging

import requests
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger("web_security")

# WhatIsMyIP API error codes
WHATISMYIP_ERRORS = {
    0: "API key was not entered",
    1: "API key is invalid",
    2: "API key is inactive",
    3: "Too many lookups (100/day limit)",
    4: "No input provided",
    5: "Invalid input",
    6: "Unknown API error",
}


def _lookup_whatismyip(ip_address, api_key):
    """Look up IP via WhatIsMyIP API (requires paid plan for ip-address-lookup).

    API docs: https://www.whatismyip.com/api/
    JSON format: {"ip_address_lookup": [{"status":"ok"}, {data}]}
    """
    response = requests.get(
        "https://api.whatismyip.com/ip-address-lookup.php",
        params={"key": api_key, "input": ip_address, "output": "json"},
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()

    # API returns a single int on error
    if isinstance(data, int):
        error_msg = WHATISMYIP_ERRORS.get(data, f"Unknown error code: {data}")
        raise ValueError(error_msg)

    lookup_list = data.get("ip_address_lookup", [])
    if len(lookup_list) < 2:
        raise ValueError("Unexpected API response format")

    if lookup_list[0].get("status") != "ok":
        raise ValueError(f"API status: {lookup_list[0].get('status', 'unknown')}")

    geo = lookup_list[1]
    return {
        "ip": geo.get("ip", ip_address),
        "country": geo.get("country", ""),
        "region": geo.get("region", ""),
        "city": geo.get("city", ""),
        "lat": geo.get("latitude", ""),
        "lon": geo.get("longitude", ""),
        "isp": geo.get("isp", ""),
    }


def _lookup_ip_api(ip_address):
    """Look up IP via ip-api.com (free, no key, 45 req/min).

    API docs: https://ip-api.com/docs/api:json
    """
    response = requests.get(
        f"http://ip-api.com/json/{ip_address}",
        params={"fields": "status,message,country,countryCode,regionName,city,lat,lon,isp,query"},
        timeout=5,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "success":
        raise ValueError(data.get("message", "IP API lookup failed"))

    return {
        "ip": data.get("query", ip_address),
        "country": data.get("country", ""),
        "country_code": data.get("countryCode", ""),
        "region": data.get("regionName", ""),
        "city": data.get("city", ""),
        "lat": str(data.get("lat", "")),
        "lon": str(data.get("lon", "")),
        "isp": data.get("isp", ""),
    }


@staff_member_required
def ip_lookup_view(request, ip_address):
    """Admin-only endpoint to look up IP geolocation.

    Tries WhatIsMyIP API first (if configured), falls back to ip-api.com.
    Results are cached for 24 hours to minimize API calls.
    """
    # Check cache first
    cache_key = f"ip_lookup:{ip_address}"
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse(cached)

    api_key = settings.WHAT_IS_MY_IP

    # Try WhatIsMyIP first if key is configured
    if api_key:
        try:
            result = _lookup_whatismyip(ip_address, api_key)
            cache.set(cache_key, result, 60 * 60 * 24)
            return JsonResponse(result)
        except Exception:
            logger.debug("WhatIsMyIP failed for %s, falling back to ip-api.com", ip_address)

    # Fallback to ip-api.com (free)
    try:
        result = _lookup_ip_api(ip_address)
        cache.set(cache_key, result, 60 * 60 * 24)
        return JsonResponse(result)
    except requests.RequestException:
        logger.exception("IP lookup request error for %s", ip_address)
        return JsonResponse({"error": "API request failed"}, status=502)
    except (ValueError, KeyError, TypeError):
        logger.exception("IP lookup invalid response for %s", ip_address)
        return JsonResponse({"error": "Invalid API response"}, status=502)
