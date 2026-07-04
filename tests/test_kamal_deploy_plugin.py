"""Tests for the kamal_deploy plugin: PRO gating on .kamal/secrets + settings_append."""

import ast
import os
import stat
from pathlib import Path

import pytest

from installer import runner

PLUGINS = Path(__file__).resolve().parents[1] / "plugins"


def _target(tmp_path, with_kamal_secrets):
    root = tmp_path / "proj"
    (root / "apps" / "web").mkdir(parents=True)
    (root / "manage.py").write_text("#\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname='p'\n", encoding="utf-8")
    pkg = root / "project"
    pkg.mkdir()
    pkg.joinpath("settings.py").write_text(
        "TEMPLATES = [{'BACKEND': 'x', 'OPTIONS': {'context_processors': []}}]\n", encoding="utf-8"
    )
    pkg.joinpath("urls.py").write_text("urlpatterns = []\n", encoding="utf-8")
    pkg.joinpath("wsgi.py").write_text("application = None\n", encoding="utf-8")
    if with_kamal_secrets:
        (root / ".kamal").mkdir()
        (root / ".kamal" / "secrets").write_text("SECRET=1\n", encoding="utf-8")
    return root


def test_refused_without_kamal_secrets(tmp_path):
    target = _target(tmp_path, with_kamal_secrets=False)
    with pytest.raises(runner.EditionBlocked):
        runner.install(PLUGINS, "kamal_deploy", target, apply=True, force=False)
    assert not (target / "kamal.sh").exists()  # nothing written when gated out


def test_installs_when_kamal_secrets_present(tmp_path):
    target = _target(tmp_path, with_kamal_secrets=True)
    runner.install(PLUGINS, "kamal_deploy", target, apply=True, force=False)

    assert (target / "apps" / "web" / "version.py").exists()
    assert (target / "kamal.sh").exists()
    # base_site.html is a manual step, never auto-copied over the project's admin template
    assert not (target / "templates" / "admin" / "base_site.html").exists()

    settings = (target / "project" / "settings.py").read_text()
    ast.parse(settings)  # settings.py still parses after the settings_append block
    assert 'context_processors"].append("apps.web.version.app_version")' in settings


def test_force_overrides_gate(tmp_path):
    target = _target(tmp_path, with_kamal_secrets=False)
    runner.install(PLUGINS, "kamal_deploy", target, apply=True, force=True)
    assert (target / "kamal.sh").exists()


def test_kamal_sh_executable_bit_preserved(tmp_path):
    target = _target(tmp_path, with_kamal_secrets=True)
    runner.install(PLUGINS, "kamal_deploy", target, apply=True, force=False)
    mode = os.stat(target / "kamal.sh").st_mode
    assert mode & stat.S_IXUSR  # copier preserves the source's executable bit


def test_uninstall_is_clean(tmp_path):
    target = _target(tmp_path, with_kamal_secrets=True)
    runner.install(PLUGINS, "kamal_deploy", target, apply=True, force=False)
    runner.uninstall(PLUGINS, "kamal_deploy", target, apply=True)
    assert not (target / "apps" / "web" / "version.py").exists()
    assert not (target / "kamal.sh").exists()
    assert "apps.web.version.app_version" not in (target / "project" / "settings.py").read_text()
    assert (target / "apps").is_dir()  # shared apps/ preserved
