"""
Distributed task lock (vendored so the plugin is self-contained).

Uses the Django cache (Redis in the boilerplate) so only one instance of a periodic
Celery task runs at a time across workers. If the lock is held, the task is skipped.
"""

import functools
import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


def task_lock(timeout=300, key=None):
    """
    Decorator ensuring single concurrent execution of a task via a cache lock.

    Args:
        timeout: lock TTL in seconds. Must exceed the task's worst-case runtime, otherwise
            the lock can expire mid-run and a second instance may start.
        key: optional explicit lock key (defaults to the function's dotted path).
    """

    def decorator(func):
        lock_key = key or f"web_security:task_lock:{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # cache.add is atomic on Redis/Memcached (SET NX): True only if not already held.
            if not cache.add(lock_key, "1", timeout):
                logger.info("Task %s skipped: lock already held", func.__name__)
                return {"status": "skipped", "reason": "locked"}
            try:
                return func(*args, **kwargs)
            finally:
                cache.delete(lock_key)

        return wrapper

    return decorator
