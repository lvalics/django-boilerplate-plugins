# tests/test_runner.py
from pathlib import Path
import pytest
from installer import runner

def _plugin(plugins_root: Path):
    d = plugins_root / "demo"; (d / "files" / "apps" / "demo").mkdir(parents=True)
    (d / "files" / "apps" / "demo" / "__init__.py").write_text("", encoding="utf-8")
    (d / "files" / "apps" / "demo" / "models.py").write_text("# demo\n", encoding="utf-8")
    (d / "plugin.toml").write_text(
        'id="demo"\nname="Demo"\nversion="1"\n'
        'installed_apps=["apps.demo"]\nfiles=["apps/demo/**"]\n'
        '[url_mappings]\n"demo/"="apps.demo.urls"\n',
        encoding="utf-8")
    return d

def _target(tmp_path: Path):
    root = tmp_path / "target"; (root / "apps").mkdir(parents=True)
    (root / "manage.py").write_text("#\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
    pkg = root / "project"; pkg.mkdir()
    (pkg / "settings.py").write_text("INSTALLED_APPS = []\n", encoding="utf-8")
    (pkg / "urls.py").write_text("urlpatterns = []\n", encoding="utf-8")
    (pkg / "wsgi.py").write_text("application=None\n", encoding="utf-8")
    return root

def test_dry_run_does_not_write(tmp_path):
    plugins = tmp_path / "plugins"; plugins.mkdir(); _plugin(plugins)
    target = _target(tmp_path)
    runner.install(plugins, "demo", target, apply=False, force=False)
    assert not (target / "apps" / "demo" / "models.py").exists()
    assert "apps.demo" not in (target / "project" / "settings.py").read_text()

def test_apply_then_uninstall_roundtrip(tmp_path):
    plugins = tmp_path / "plugins"; plugins.mkdir(); _plugin(plugins)
    target = _target(tmp_path)
    runner.install(plugins, "demo", target, apply=True, force=False)
    settings = (target / "project" / "settings.py").read_text()
    urls = (target / "project" / "urls.py").read_text()
    assert 'INSTALLED_APPS += ["apps.demo"]' in settings
    assert 'include("apps.demo.urls")' in urls
    assert (target / "apps" / "demo" / "models.py").exists()
    # idempotent re-apply
    runner.install(plugins, "demo", target, apply=True, force=True)
    assert (target / "project" / "settings.py").read_text().count("# >>> plugin: demo >>>") == 1
    # uninstall
    runner.uninstall(plugins, "demo", target, apply=True)
    assert "apps.demo" not in (target / "project" / "settings.py").read_text()
    assert not (target / "apps" / "demo" / "models.py").exists()

def test_pro_plugin_blocked_on_free_target(tmp_path):
    plugins = tmp_path / "plugins"; plugins.mkdir()
    d = plugins / "prod"; (d / "files").mkdir(parents=True)
    (d / "plugin.toml").write_text(
        'id="prod"\nname="Pro"\nversion="1"\nedition="pro"\n'
        '[requires]\nany_of=[{app="apps.subscriptions"}]\n', encoding="utf-8")
    target = _target(tmp_path)
    with pytest.raises(runner.EditionBlocked):
        runner.install(plugins, "prod", target, apply=True, force=False)
