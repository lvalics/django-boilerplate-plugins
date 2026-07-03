import ast
from pathlib import Path
from installer.manifest import Manifest
from installer.target import TargetProject
from installer.edition import evaluate, _build_db_probe


def _target(tmp_path: Path) -> TargetProject:
    (tmp_path / "apps").mkdir(exist_ok=True)
    pkg = tmp_path / "project"; pkg.mkdir(exist_ok=True)
    s = pkg / "settings.py"; s.write_text("PEGASUS_PRO = True\n", encoding="utf-8")
    u = pkg / "urls.py"; u.write_text("urlpatterns = []\n", encoding="utf-8")
    return TargetProject(root=tmp_path, settings_path=s, urls_path=u)


def test_free_always_allowed(tmp_path):
    m = Manifest(id="x", name="X", version="1", edition="free")
    assert evaluate(m, _target(tmp_path)).allowed is True


def test_pro_blocked_when_no_marker(tmp_path):
    m = Manifest(id="x", name="X", version="1", edition="pro",
                 requires={"any_of": [{"app": "apps.subscriptions"}]})
    d = evaluate(m, _target(tmp_path))
    assert d.allowed is False
    assert any("apps.subscriptions" in r for r in d.reasons)


def test_pro_allowed_by_app_dir(tmp_path):
    t = _target(tmp_path)
    (t.root / "apps" / "subscriptions").mkdir(parents=True)
    m = Manifest(id="x", name="X", version="1", edition="pro",
                 requires={"any_of": [{"app": "apps.subscriptions"}]})
    assert evaluate(m, t).allowed is True


def test_pro_allowed_by_setting(tmp_path):
    t = _target(tmp_path)
    m = Manifest(id="x", name="X", version="1", edition="pro",
                 requires={"any_of": [{"setting": {"name": "PEGASUS_PRO", "equals": True}}]})
    assert evaluate(m, t).allowed is True


def test_all_of_requires_every_marker(tmp_path):
    t = _target(tmp_path)
    (t.root / "apps" / "subscriptions").mkdir(parents=True)
    m = Manifest(id="x", name="X", version="1", edition="pro",
                 requires={"all_of": [{"app": "apps.subscriptions"},
                                      {"file": "apps/teams/models.py"}]})
    assert evaluate(m, t).allowed is False   # teams file missing


def test_db_probe_is_injection_safe():
    malicious = "x' in [] or __import__('os').system('id') or 'x"
    code = _build_db_probe(malicious)
    tree = ast.parse(code)                      # must be valid Python
    # the malicious payload must appear ONLY inside a string constant, never as executable code:
    assert not any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "__import__" for n in ast.walk(tree))
    consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert malicious in consts                  # embedded verbatim as a string literal


def test_db_probe_normal_table():
    code = _build_db_probe("subscriptions_subscription")
    assert '"subscriptions_subscription"' in code
    ast.parse(code)
