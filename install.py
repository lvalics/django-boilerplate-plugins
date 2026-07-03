#!/usr/bin/env python3
"""CLI entry point for the django-boilerplate plugin installer."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from installer import runner

PLUGINS_ROOT = Path(__file__).resolve().parent / "plugins"

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Install a django-boilerplate plugin.")
    parser.add_argument("plugin", nargs="?", help="plugin id (see --list)")
    parser.add_argument("target", nargs="?", help="path to the target project")
    parser.add_argument("--apply", action="store_true", help="apply changes (default: dry run)")
    parser.add_argument("--force", action="store_true", help="override edition gate + overwrite files")
    parser.add_argument("--uninstall", action="store_true", help="remove the plugin")
    parser.add_argument("--list", action="store_true", help="list available plugins")
    args = parser.parse_args(argv)

    if args.list:
        for m in runner.list_plugins(PLUGINS_ROOT):
            print(f"{m.id:20} {m.version:8} edition={m.edition:5} {m.description}")
        return 0
    if not args.plugin or not args.target:
        parser.error("plugin and target are required (or use --list)")
    if not (PLUGINS_ROOT / args.plugin / "plugin.toml").is_file():
        print(f"error: unknown plugin '{args.plugin}' (see --list)", file=sys.stderr)
        return 1
    try:
        if args.uninstall:
            runner.uninstall(PLUGINS_ROOT, args.plugin, Path(args.target), apply=args.apply)
        else:
            runner.install(PLUGINS_ROOT, args.plugin, Path(args.target),
                           apply=args.apply, force=args.force)
    except (ValueError, FileExistsError, FileNotFoundError, runner.EditionBlocked) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
