from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from installer import manifest as manifest_mod
from installer import target as target_mod
from installer import edition as edition_mod
from installer import copier, patcher

class EditionBlocked(Exception):
    pass

@dataclass
class Plan:
    copies: list
    settings_block: str
    urls_block: str
    notes: str

def _load(plugins_root: Path, plugin_id: str) -> manifest_mod.Manifest:
    return manifest_mod.load(Path(plugins_root) / plugin_id / "plugin.toml")

def list_plugins(plugins_root: Path) -> list[manifest_mod.Manifest]:
    out = []
    for child in sorted(Path(plugins_root).iterdir()):
        toml = child / "plugin.toml"
        if toml.is_file():
            out.append(manifest_mod.load(toml))
    return out

def build_plan(plugins_root: Path, plugin_id: str, target_path: Path):
    m = _load(plugins_root, plugin_id)
    tgt = target_mod.detect(target_path)
    decision = edition_mod.evaluate(m, tgt)
    plugin_dir = Path(plugins_root) / plugin_id
    plan = Plan(
        copies=copier.plan_copies(plugin_dir, tgt, m.files),
        settings_block=patcher.build_settings_block(m),
        urls_block=patcher.build_urls_block(m) if m.url_mappings else "",
        notes=m.post_install_notes,
    )
    return plan, decision, m, tgt

def install(plugins_root, plugin_id, target_path, apply: bool, force: bool) -> None:
    plan, decision, m, tgt = build_plan(plugins_root, plugin_id, target_path)
    _print_plan(m, plan, decision)
    if not decision.allowed and not force:
        raise EditionBlocked(
            f"{plugin_id} requires the PRO edition. Unmet: {decision.reasons}. Use --force to override."
        )
    if not apply:
        print("\nDry run: nothing written. Re-run with --apply.")
        return
    copier.apply_copies(plan.copies, force=force)
    _patch_file(tgt.settings_path, m.id, plan.settings_block)
    if plan.urls_block:
        _patch_file(tgt.urls_path, m.id, plan.urls_block)
    _print_post_install(m)

def uninstall(plugins_root, plugin_id, target_path, apply: bool) -> None:
    m = _load(plugins_root, plugin_id)
    tgt = target_mod.detect(target_path)
    plugin_dir = Path(plugins_root) / plugin_id
    ops = copier.plan_copies(plugin_dir, tgt, m.files)
    print(f"Uninstall {plugin_id}: remove {len(ops)} files + marker blocks")
    if not apply:
        print("Dry run: nothing changed. Re-run with --apply.")
        return
    for op in ops:
        if op.dest.exists():
            op.dest.unlink()
    _unpatch_file(tgt.settings_path, m.id)
    _unpatch_file(tgt.urls_path, m.id)

def _patch_file(path: Path, plugin_id: str, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(patcher.upsert_block(text, plugin_id, block), encoding="utf-8")

def _unpatch_file(path: Path, plugin_id: str) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
        path.write_text(patcher.remove_block(text, plugin_id), encoding="utf-8")

def _print_plan(m, plan, decision) -> None:
    print(f"Plugin: {m.name} ({m.id}) v{m.version}  edition={m.edition}")
    if m.edition == "pro":
        print(f"  PRO gate: {'PASS' if decision.allowed else 'BLOCKED'}"
              + (" (DB check unknown)" if decision.unknown else ""))
    print(f"  Files to copy: {len(plan.copies)}")
    for op in plan.copies:
        print(f"    {'overwrite' if op.exists else 'new'}: {op.dest}")
    print("  Settings patch:\n" + "\n".join("    " + l for l in plan.settings_block.splitlines()))
    if plan.urls_block:
        print("  URLs patch:\n" + "\n".join("    " + l for l in plan.urls_block.splitlines()))

def _print_post_install(m) -> None:
    print("\nInstalled. Manual steps:")
    for ev in m.env_vars:
        req = "required" if ev.get("required") else "optional"
        print(f"  .env  {ev['name']}=  ({req}, default {ev.get('default', '')!r})")
    for dep in m.python_dependencies:
        print(f"  uv add '{dep}'")
    if m.post_install_notes:
        print(m.post_install_notes)
    print("  Run: make migrations && make migrate")
