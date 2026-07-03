import ast
from pathlib import Path

from installer import runner

PLUGINS = Path(__file__).resolve().parents[1] / "plugins"


def _fake_boilerplate(tmp_path: Path) -> Path:
    root = tmp_path / "bp"
    (root / "apps").mkdir(parents=True)
    (root / "manage.py").write_text("#\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='bp'\n", encoding="utf-8")
    pkg = root / "project"
    pkg.mkdir()
    (pkg / "settings.py").write_text("INSTALLED_APPS = []\nMIDDLEWARE = []\n", encoding="utf-8")
    (pkg / "urls.py").write_text("from django.urls import path\nurlpatterns = []\n", encoding="utf-8")
    (pkg / "wsgi.py").write_text("application=None\n", encoding="utf-8")
    return root


def test_web_security_installs_and_settings_stay_valid(tmp_path):
    target = _fake_boilerplate(tmp_path)
    runner.install(PLUGINS, "web_security", target, apply=True, force=False)
    settings = (target / "project" / "settings.py").read_text()
    urls = (target / "project" / "urls.py").read_text()
    ast.parse(settings)  # settings.py still parses after patching
    ast.parse(urls)
    assert 'INSTALLED_APPS += ["apps.web_security"]' in settings
    assert 'include("apps.web_security.urls")' in urls
    assert (target / "apps" / "web_security" / "__init__.py").exists()


def test_web_security_uninstall_is_clean(tmp_path):
    target = _fake_boilerplate(tmp_path)
    runner.install(PLUGINS, "web_security", target, apply=True, force=False)
    runner.uninstall(PLUGINS, "web_security", target, apply=True)
    settings = (target / "project" / "settings.py").read_text()
    assert "web_security" not in settings
    assert not (target / "apps" / "web_security").exists()
