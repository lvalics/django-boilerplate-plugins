"""
Site configuration caching layer using Redis.

Cache structure:
- site:domain:{domain} -> Full serialized SiteConfig dict
- site:id:{id} -> Same config, by ID
- site:all_domains -> List of all active site domains (for ALLOWED_HOSTS)

Features:
- Cache stampede protection with locking
- Graceful fallback on cache failure
- Automatic DB fallback when cache is unavailable
"""

import logging
import time
from typing import Any, TypeVar

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Track cache availability
_cache_available = True
_cache_check_interval = 30  # seconds between availability checks
_last_cache_check = 0

T = TypeVar("T")

# Cache keys
SITE_DOMAIN_KEY = "site:domain:{domain}"
SITE_ID_KEY = "site:id:{site_id}"
ALL_DOMAINS_KEY = "site:all_domains"
CACHE_LOCK_KEY = "site:lock:{key}"

# Default cache timeout (5 minutes)
SITE_CACHE_TIMEOUT = getattr(settings, "SITE_CACHE_TIMEOUT", 300)

# Lock settings for stampede protection
CACHE_LOCK_TIMEOUT = 10  # seconds to hold lock
CACHE_LOCK_WAIT = 0.1  # seconds between lock checks
CACHE_LOCK_MAX_WAIT = 5  # max seconds to wait for lock


def _is_cache_available() -> bool:
    """
    Check if cache is available, with periodic health checks.

    Uses a simple ping to detect Redis connection issues.
    Caches the result to avoid hammering a down cache.
    """
    global _cache_available, _last_cache_check

    current_time = time.time()

    # Skip check if we recently verified
    if current_time - _last_cache_check < _cache_check_interval:
        return _cache_available

    _last_cache_check = current_time

    try:
        # Simple ping - set and get a test key
        cache.set("_health_check", "1", timeout=5)
        result = cache.get("_health_check")
        now_available = result == "1"

        # Log recovery when the cache was previously marked down and is now reachable.
        if now_available and not _cache_available:
            logger.info("Cache connection restored")
        _cache_available = now_available
    except Exception as e:
        if _cache_available:
            logger.warning(f"Cache unavailable, falling back to DB: {e}")
        _cache_available = False

    return _cache_available


def _safe_cache_get(key: str, default: Any = None) -> Any:
    """
    Safely get from cache with fallback on connection error.

    Args:
        key: Cache key to retrieve
        default: Default value if not found or cache unavailable

    Returns:
        Cached value or default
    """
    if not _is_cache_available():
        return default

    try:
        return cache.get(key, default)
    except Exception as e:
        logger.debug(f"Cache get failed for {key}: {e}")
        return default


def _safe_cache_set(key: str, value: Any, timeout: int = None) -> bool:
    """
    Safely set cache value with fallback on connection error.

    Args:
        key: Cache key
        value: Value to cache
        timeout: Cache timeout in seconds

    Returns:
        True if cached successfully, False otherwise
    """
    if not _is_cache_available():
        return False

    try:
        cache.set(key, value, timeout=timeout or SITE_CACHE_TIMEOUT)
        return True
    except Exception as e:
        logger.debug(f"Cache set failed for {key}: {e}")
        return False


def _safe_cache_delete(keys: list[str]) -> bool:
    """
    Safely delete cache keys with fallback on connection error.

    Args:
        keys: List of cache keys to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    if not _is_cache_available():
        return False

    try:
        cache.delete_many(keys)
        return True
    except Exception as e:
        logger.debug(f"Cache delete failed: {e}")
        return False


def _safe_cache_add(key: str, value: Any, timeout: int = None) -> bool:
    """
    Safely add to cache (atomic, only if key doesn't exist).

    Args:
        key: Cache key
        value: Value to cache
        timeout: Cache timeout in seconds

    Returns:
        True only if the key was actually added (caller genuinely holds the lock). On a
        cache outage returns False: the caller does NOT hold the lock and must decide its
        own fallback (e.g. _load_with_lock loads directly from DB) rather than assuming a
        held lock, which would let every process believe it won and stampede the DB.
    """
    if not _is_cache_available():
        return False

    try:
        return cache.add(key, value, timeout=timeout)
    except Exception as e:
        logger.debug(f"Cache add failed for {key}: {e}")
        return False


def get_site_config_by_domain(domain: str) -> dict | None:
    """
    Get site configuration from cache or database by domain.

    Uses locking to prevent cache stampede on cache miss.
    Falls back to database if cache is unavailable.

    Args:
        domain: The domain to look up (e.g., 'example.com')

    Returns:
        Site configuration dict or None if not found
    """
    cache_key = SITE_DOMAIN_KEY.format(domain=domain)

    # Try cache first (with safe fallback)
    config = _safe_cache_get(cache_key)
    if config is not None:
        logger.debug(f"Cache hit for domain: {domain}")
        return config

    logger.debug(f"Cache miss for domain: {domain}")

    # Use lock to prevent stampede (or load directly if cache unavailable)
    return _load_with_lock(
        cache_key=cache_key,
        load_func=lambda: _load_site_config_from_db(domain=domain),
    )


def get_site_config_by_id(site_id: int) -> dict | None:
    """
    Get site configuration from cache or database by site ID.

    Uses locking to prevent cache stampede on cache miss.
    Falls back to database if cache is unavailable.

    Args:
        site_id: The Django Site ID

    Returns:
        Site configuration dict or None if not found
    """
    cache_key = SITE_ID_KEY.format(site_id=site_id)

    # Try cache first (with safe fallback)
    config = _safe_cache_get(cache_key)
    if config is not None:
        logger.debug(f"Cache hit for site_id: {site_id}")
        return config

    logger.debug(f"Cache miss for site_id: {site_id}")

    # Use lock to prevent stampede (or load directly if cache unavailable)
    return _load_with_lock(
        cache_key=cache_key,
        load_func=lambda: _load_site_config_from_db(site_id=site_id),
    )


def _load_with_lock(cache_key: str, load_func: callable) -> dict | None:
    """
    Load data with lock to prevent cache stampede.

    Only one process loads from DB, others wait for cache.
    If cache is unavailable, loads directly from DB.

    Args:
        cache_key: The cache key being loaded
        load_func: Function to call to load data from DB

    Returns:
        Loaded configuration or None
    """
    # If cache is unavailable, load directly from DB
    if not _is_cache_available():
        logger.debug(f"Cache unavailable, loading {cache_key} from DB")
        return load_func()

    lock_key = CACHE_LOCK_KEY.format(key=cache_key)

    # Try to acquire lock (atomic add returns True if key was created)
    lock_acquired = _safe_cache_add(lock_key, "1", timeout=CACHE_LOCK_TIMEOUT)

    if lock_acquired:
        # We got the lock - load from DB and cache
        try:
            config = load_func()
            if config:
                _cache_site_config(config)
            return config
        finally:
            # Release lock
            try:
                cache.delete(lock_key)
            except Exception:
                pass  # Ignore lock release failures
    else:
        # Another process is loading - wait for cache to be populated
        waited = 0
        while waited < CACHE_LOCK_MAX_WAIT:
            time.sleep(CACHE_LOCK_WAIT)
            waited += CACHE_LOCK_WAIT

            # Check if data is now in cache
            config = _safe_cache_get(cache_key)
            if config is not None:
                logger.debug(f"Cache populated by another process for {cache_key}")
                return config

            # Check if lock was released (loader might have failed)
            if _safe_cache_get(lock_key) is None:
                break

        # Timeout or lock released without data - try loading ourselves
        logger.warning(f"Lock wait timeout for {cache_key}, loading directly")
        config = load_func()
        if config:
            _cache_site_config(config)
        return config


def get_all_site_domains() -> list[str]:
    """
    Get all active site domains from cache or database.
    Used for dynamic ALLOWED_HOSTS.
    Falls back to database if cache is unavailable.

    Returns:
        List of domain strings
    """
    domains = _safe_cache_get(ALL_DOMAINS_KEY)

    if domains is not None:
        return domains

    domains = _load_all_domains_from_db()
    _safe_cache_set(ALL_DOMAINS_KEY, domains, timeout=SITE_CACHE_TIMEOUT)

    return domains


def invalidate_site_cache(site_id: int = None, domain: str = None) -> None:
    """
    Invalidate cache for a specific site.
    Silently ignores cache failures.

    Args:
        site_id: The site ID to invalidate
        domain: The domain to invalidate
    """
    keys_to_delete = [ALL_DOMAINS_KEY]

    if site_id:
        keys_to_delete.append(SITE_ID_KEY.format(site_id=site_id))

    if domain:
        keys_to_delete.append(SITE_DOMAIN_KEY.format(domain=domain))

    _safe_cache_delete(keys_to_delete)
    logger.info(f"Invalidated cache for site_id={site_id}, domain={domain}")


def invalidate_all_site_cache() -> None:
    """
    Invalidate all site-related cache entries.
    Use sparingly - prefer targeted invalidation.
    Silently ignores cache failures.
    """
    from apps.sites.models import SiteProfile

    # Get all domains to build cache keys
    profiles = SiteProfile.objects.select_related("site").filter(is_active=True)

    keys_to_delete = [ALL_DOMAINS_KEY]
    for profile in profiles:
        keys_to_delete.append(SITE_DOMAIN_KEY.format(domain=profile.site.domain))
        keys_to_delete.append(SITE_ID_KEY.format(site_id=profile.site_id))

    _safe_cache_delete(keys_to_delete)
    logger.info(f"Invalidated all site cache ({len(keys_to_delete)} keys)")


def warm_site_cache() -> int:
    """
    Pre-populate cache for all active sites.
    Useful for startup or after cache flush.
    Silently continues if cache is unavailable.

    Returns:
        Number of sites cached
    """
    from apps.sites.models import SiteProfile

    profiles = SiteProfile.objects.select_related("site", "auth_domain__site").filter(is_active=True)

    count = 0
    for profile in profiles:
        config = profile.to_config_dict()
        _cache_site_config(config)
        count += 1

    # Also cache all domains list
    domains = [p.site.domain for p in profiles]
    _safe_cache_set(ALL_DOMAINS_KEY, domains, timeout=SITE_CACHE_TIMEOUT)

    logger.info(f"Warmed cache for {count} sites")
    return count


def _load_site_config_from_db(domain: str = None, site_id: int = None) -> dict | None:
    """
    Load site configuration from database.

    Args:
        domain: Domain to look up
        site_id: Site ID to look up

    Returns:
        Site configuration dict or None
    """
    from apps.sites.models import SiteProfile

    try:
        queryset = SiteProfile.objects.select_related("site", "auth_domain__site")

        if domain:
            profile = queryset.get(site__domain=domain, is_active=True)
        elif site_id:
            profile = queryset.get(site_id=site_id, is_active=True)
        else:
            return None

        return profile.to_config_dict()

    except SiteProfile.DoesNotExist:
        logger.warning(f"SiteProfile not found: domain={domain}, site_id={site_id}")
        return None


def _load_all_domains_from_db() -> list[str]:
    """
    Load all active site domains from database.

    Returns:
        List of domain strings
    """
    from apps.sites.models import SiteProfile

    return list(
        SiteProfile.objects.select_related("site").filter(is_active=True).values_list("site__domain", flat=True)
    )


def _cache_site_config(config: dict) -> None:
    """
    Cache site configuration by both domain and ID.
    Silently ignores cache failures.

    Args:
        config: The site configuration dict
    """
    domain = config.get("domain")
    site_id = config.get("site_id")

    if domain:
        _safe_cache_set(SITE_DOMAIN_KEY.format(domain=domain), config, timeout=SITE_CACHE_TIMEOUT)

    if site_id:
        _safe_cache_set(SITE_ID_KEY.format(site_id=site_id), config, timeout=SITE_CACHE_TIMEOUT)
