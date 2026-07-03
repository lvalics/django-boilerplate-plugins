from pathlib import Path
import pytest
from installer.target import TargetProject
from installer.copier import plan_copies, apply_copies


def _plugin(tmp_path: Path):
    files = tmp_path / "plugin" / "files"
    (files / "apps" / "demo").mkdir(parents=True)
    (files / "apps" / "demo" / "models.py").write_text("m\n", encoding="utf-8")
    (files / "apps" / "demo" / "views.py").write_text("v\n", encoding="utf-8")
    return tmp_path / "plugin"


def _target(tmp_path: Path):
    root = tmp_path / "target"
    (root / "apps").mkdir(parents=True)
    return TargetProject(root=root, settings_path=root / "s.py", urls_path=root / "u.py")


def test_plan_and_apply(tmp_path):
    plugin, target = _plugin(tmp_path), _target(tmp_path)
    ops = plan_copies(plugin, target, ["apps/demo/**"])
    assert {o.dest.relative_to(target.root).as_posix() for o in ops} == {
        "apps/demo/models.py",
        "apps/demo/views.py",
    }
    assert all(o.exists is False for o in ops)
    apply_copies(ops, force=False)
    assert (target.root / "apps" / "demo" / "models.py").read_text() == "m\n"


def test_overwrite_requires_force(tmp_path):
    plugin, target = _plugin(tmp_path), _target(tmp_path)
    dest = target.root / "apps" / "demo" / "models.py"
    dest.parent.mkdir(parents=True)
    dest.write_text("OLD\n", encoding="utf-8")
    ops = plan_copies(plugin, target, ["apps/demo/models.py"])
    assert ops[0].exists is True
    with pytest.raises(FileExistsError):
        apply_copies(ops, force=False)
    apply_copies(ops, force=True)
    assert dest.read_text() == "m\n"
    assert (dest.parent / "models.py.bak").read_text() == "OLD\n"
