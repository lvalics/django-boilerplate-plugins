from __future__ import annotations

import ast
import json
import re
import subprocess
from dataclasses import dataclass, field

from installer.manifest import Manifest
from installer.target import TargetProject


@dataclass
class EditionDecision:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    unknown: bool = False


def _check_app(target: TargetProject, dotted: str) -> bool:
    return (target.root / dotted.replace(".", "/")).is_dir()


def _check_file(target: TargetProject, rel: str) -> bool:
    return (target.root / rel).exists()


def _check_setting(target: TargetProject, name: str, equals) -> bool:
    text = target.settings_path.read_text(encoding="utf-8")
    m = re.search(rf"^{re.escape(name)}\s*=\s*(.+?)\s*$", text, re.MULTILINE)
    if not m:
        return False
    try:
        return ast.literal_eval(m.group(1)) == equals
    except (ValueError, SyntaxError):
        return False


def _build_db_probe(table: str) -> str:
    """Build a read-only introspection snippet with the table name safely embedded as a literal."""
    return (
        "from django.db import connection;"
        f"print('YES' if {json.dumps(table)} in connection.introspection.table_names() else 'NO')"
    )


def _check_db_table(target: TargetProject, table: str) -> bool | None:
    """Read-only introspection via the target's own manage.py. None = unknown."""
    code = _build_db_probe(table)
    try:
        out = subprocess.run(
            ["python", "manage.py", "shell", "-c", code],
            cwd=target.root,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip().endswith("YES")


def _eval_marker(target: TargetProject, marker: dict) -> bool | None:
    if "app" in marker:
        return _check_app(target, marker["app"])
    if "file" in marker:
        return _check_file(target, marker["file"])
    if "setting" in marker:
        s = marker["setting"]
        return _check_setting(target, s["name"], s.get("equals", True))
    if "db_table" in marker:
        return _check_db_table(target, marker["db_table"])
    return None


def evaluate(manifest: Manifest, target: TargetProject) -> EditionDecision:
    if manifest.edition == "free":
        return EditionDecision(allowed=True)
    req = manifest.requires or {}
    mode = "all_of" if "all_of" in req else "any_of"
    markers = req.get(mode, [])
    if not markers:
        return EditionDecision(
            allowed=False,
            reasons=["plugin is edition=pro but declares no requires markers"],
        )
    results = [(m, _eval_marker(target, m)) for m in markers]
    unknown = any(r is None for _, r in results)
    truthy = [r is True for _, r in results]
    allowed = all(truthy) if mode == "all_of" else any(truthy)
    reasons = (
        []
        if allowed
        else [f"unmet PRO marker: {m}" for m, r in results if r is not True]
    )
    return EditionDecision(allowed=allowed, reasons=reasons, unknown=unknown)
