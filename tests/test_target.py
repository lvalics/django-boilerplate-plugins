from pathlib import Path
import pytest
from installer.target import detect, TargetProject


def _make_project(tmp_path: Path, pkg="project"):
    (tmp_path / "manage.py").write_text("# manage\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n", encoding="utf-8")
    (tmp_path / "apps").mkdir()
    p = tmp_path / pkg
    p.mkdir()
    (p / "settings.py").write_text("INSTALLED_APPS = []\n", encoding="utf-8")
    (p / "urls.py").write_text("urlpatterns = []\n", encoding="utf-8")
    (p / "wsgi.py").write_text("application = None\n", encoding="utf-8")
    return tmp_path


def test_detect_valid(tmp_path):
    root = _make_project(tmp_path)
    t = detect(root)
    assert isinstance(t, TargetProject)
    assert t.settings_path == root / "project" / "settings.py"
    assert t.urls_path == root / "project" / "urls.py"


def test_detect_custom_package_name(tmp_path):
    root = _make_project(tmp_path, pkg="mysaas")
    t = detect(root)
    assert t.settings_path.parent.name == "mysaas"


def test_detect_rejects_non_project(tmp_path):
    with pytest.raises(ValueError, match="not a django-boilerplate project"):
        detect(tmp_path)
