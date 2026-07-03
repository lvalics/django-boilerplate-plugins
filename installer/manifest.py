from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

_REQUIRED = ("id", "name", "version")
_EDITIONS = ("free", "pro")


@dataclass
class Manifest:
    id: str
    name: str
    version: str
    description: str = ""
    target: str = "django-boilerplate"
    edition: str = "free"
    python_dependencies: list[str] = field(default_factory=list)
    installed_apps: list[str] = field(default_factory=list)
    middleware: list[str] = field(default_factory=list)
    url_mappings: dict[str, str] = field(default_factory=dict)
    celery_beat_schedule: dict = field(default_factory=dict)
    files: list[str] = field(default_factory=list)
    env_vars: list[dict] = field(default_factory=list)
    post_install_notes: str = ""
    requires: dict | None = None


def load(path: Path) -> Manifest:
    path = Path(path)
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    for key in _REQUIRED:
        if key not in data:
            raise ValueError(f"{path}: missing required field: {key}")
    edition = data.get("edition", "free")
    if edition not in _EDITIONS:
        raise ValueError(f"{path}: edition must be one of {_EDITIONS}, got {edition!r}")
    known = {f for f in Manifest.__dataclass_fields__}
    kwargs = {k: v for k, v in data.items() if k in known}
    return Manifest(**kwargs)
