"""Regression tests for ReDoS protection (safe_regex_match).

Fix #3: the timeout must bound catastrophic-backtracking regexes in ANY thread. The
old SIGALRM approach silently did nothing off the main thread (gunicorn gthread, uWSGI,
ASGI); the regex-engine timeout must actually fire.
"""

import threading
import time

import regex
from django.test import SimpleTestCase

from apps.web_security.models.threat_pattern import safe_regex_match

# Nested quantifier + non-matching suffix => exponential backtracking without a timeout.
# 2**44 steps would take far longer than any test budget, so completing fast PROVES the
# timeout fired (rather than the engine simply finishing).
_CATASTROPHIC = regex.compile(r"(a+)+$")
_TARGET = "a" * 44 + "!"


class ReDoSTests(SimpleTestCase):
    def test_catastrophic_pattern_times_out_to_none(self):
        start = time.monotonic()
        result = safe_regex_match(_CATASTROPHIC, _TARGET, timeout=0.1)
        elapsed = time.monotonic() - start
        self.assertIsNone(result)
        self.assertLess(elapsed, 5.0, "match was not bounded by the timeout")

    def test_timeout_fires_off_the_main_thread(self):
        box = {}

        def run():
            box["result"] = safe_regex_match(_CATASTROPHIC, _TARGET, timeout=0.1)

        worker = threading.Thread(target=run)
        worker.start()
        worker.join(timeout=10)
        self.assertFalse(worker.is_alive(), "regex hung in a worker thread => ReDoS unbounded")
        self.assertIsNone(box.get("result"))

    def test_normal_matching_still_works(self):
        pat = regex.compile(r"abc")
        self.assertIsNotNone(safe_regex_match(pat, "xabcy"))
        self.assertIsNone(safe_regex_match(pat, "xyz"))
