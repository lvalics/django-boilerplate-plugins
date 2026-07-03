from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TargetProject:
    root: Path
    settings_path: Path
    urls_path: Path


def detect(path: Path) -> TargetProject:
    root = Path(path).resolve()
    if not (root / "manage.py").is_file() or not (root / "apps").is_dir():
        raise ValueError(
            f"{root} is not a django-boilerplate project (missing manage.py or apps/)"
        )
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        settings = child / "settings.py"
        urls = child / "urls.py"
        if settings.is_file() and urls.is_file() and (child / "wsgi.py").is_file():
            return TargetProject(root=root, settings_path=settings, urls_path=urls)
    raise ValueError(
        f"{root} is not a django-boilerplate project (no settings package found)"
    )
