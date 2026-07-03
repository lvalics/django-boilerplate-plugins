from pathlib import Path
import pytest
from installer.manifest import load, Manifest


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "plugin.toml"
    p.write_text(body, encoding="utf-8")
    return p


def test_load_minimal(tmp_path):
    m = load(_write(tmp_path, 'id = "demo"\nname = "Demo"\nversion = "1.0.0"\n'))
    assert isinstance(m, Manifest)
    assert m.id == "demo"
    assert m.edition == "free"            # default
    assert m.installed_apps == []          # default
    assert m.requires is None


def test_load_full(tmp_path):
    body = '''
id = "web_security"
name = "Web Security"
version = "1.3.0"
edition = "free"
installed_apps = ["apps.web_security"]
middleware = ["apps.web_security.middleware.ip_block.IPBlockMiddleware"]
files = ["apps/web_security/**"]
[url_mappings]
"web-security/" = "apps.web_security.urls"
[celery_beat_schedule.auto-block]
task = "apps.web_security.tasks.auto_block"
schedule = 60.0
'''
    m = load(_write(tmp_path, body))
    assert m.installed_apps == ["apps.web_security"]
    assert m.url_mappings == {"web-security/": "apps.web_security.urls"}
    assert m.celery_beat_schedule["auto-block"]["schedule"] == 60.0


def test_missing_required_field(tmp_path):
    with pytest.raises(ValueError, match="missing required field: version"):
        load(_write(tmp_path, 'id = "x"\nname = "X"\n'))


def test_bad_edition(tmp_path):
    with pytest.raises(ValueError, match="edition"):
        load(_write(tmp_path, 'id="x"\nname="X"\nversion="1"\nedition="ultra"\n'))
