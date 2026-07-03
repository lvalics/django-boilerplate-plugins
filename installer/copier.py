from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from installer.target import TargetProject


@dataclass
class CopyOp:
    src: Path
    dest: Path
    exists: bool


def plan_copies(
    plugin_dir: Path, target: TargetProject, globs: list[str]
) -> list[CopyOp]:
    files_root = Path(plugin_dir) / "files"
    ops: dict[Path, CopyOp] = {}
    for pattern in globs:
        for src in sorted(files_root.glob(pattern)):
            if not src.is_file():
                continue
            rel = src.relative_to(files_root)
            dest = target.root / rel
            ops[dest] = CopyOp(src=src, dest=dest, exists=dest.exists())
    return list(ops.values())


def apply_copies(ops: list[CopyOp], force: bool) -> None:
    for op in ops:
        if op.dest.exists() and not force:
            raise FileExistsError(f"refusing to overwrite {op.dest} (use --force)")
        op.dest.parent.mkdir(parents=True, exist_ok=True)
        if op.dest.exists():
            shutil.copy2(op.dest, op.dest.with_suffix(op.dest.suffix + ".bak"))
        shutil.copy2(op.src, op.dest)
