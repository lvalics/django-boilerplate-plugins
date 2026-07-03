import ast
from installer.manifest import Manifest
from installer.patcher import (build_settings_block, build_urls_block,
                               upsert_block, remove_block)

def _m():
    return Manifest(
        id="web_security", name="Web Security", version="1",
        installed_apps=["apps.web_security"],
        middleware=["apps.web_security.middleware.ip_block.IPBlockMiddleware"],
        url_mappings={"web-security/": "apps.web_security.urls"},
        celery_beat_schedule={"auto-block": {"task": "apps.web_security.tasks.t", "schedule": 60.0}},
    )

def test_settings_block_is_valid_python(tmp_path):
    block = build_settings_block(_m())
    assert "# >>> plugin: web_security >>>" in block
    assert 'INSTALLED_APPS += ["apps.web_security"]' in block
    ast.parse(block)   # must be syntactically valid

def test_upsert_appends_then_replaces_idempotently():
    base = "INSTALLED_APPS = []\nMIDDLEWARE = []\n"
    block1 = build_settings_block(_m())
    once = upsert_block(base, "web_security", block1)
    twice = upsert_block(once, "web_security", block1)
    assert once == twice                      # idempotent
    assert once.count("# >>> plugin: web_security >>>") == 1
    ast.parse(once)

def test_remove_block_restores():
    base = "INSTALLED_APPS = []\n"
    patched = upsert_block(base, "web_security", build_settings_block(_m()))
    restored = remove_block(patched, "web_security")
    assert restored.strip() == base.strip()

def test_urls_block_valid():
    block = build_urls_block(_m())
    assert 'include("apps.web_security.urls")' in block
    ast.parse(block)
