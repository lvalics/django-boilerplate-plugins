from __future__ import annotations
import json
import re
from installer.manifest import Manifest

def _start(plugin_id: str) -> str:
    return f"# >>> plugin: {plugin_id} >>>"

def _end(plugin_id: str) -> str:
    return f"# <<< plugin: {plugin_id} <<<"

def build_settings_block(m: Manifest) -> str:
    lines = [_start(m.id)]
    if m.installed_apps:
        lines.append(f"INSTALLED_APPS += {json.dumps(m.installed_apps)}")
    if m.middleware:
        lines.append(f"MIDDLEWARE += {json.dumps(m.middleware)}")
    if m.celery_beat_schedule:
        lines.append(
            "CELERY_BEAT_SCHEDULE = {**globals().get('CELERY_BEAT_SCHEDULE', {}), "
            f"**{json.dumps(m.celery_beat_schedule)}}}"
        )
    lines.append(_end(m.id))
    return "\n".join(lines)

def build_urls_block(m: Manifest) -> str:
    lines = [_start(m.id), "from django.urls import include, path"]
    for prefix, module in m.url_mappings.items():
        lines.append(f'urlpatterns += [path({json.dumps(prefix)}, include({json.dumps(module)}))]')
    lines.append(_end(m.id))
    return "\n".join(lines)

def _block_re(plugin_id: str) -> re.Pattern:
    return re.compile(
        rf"\n*{re.escape(_start(plugin_id))}.*?{re.escape(_end(plugin_id))}\n*",
        re.DOTALL,
    )

def upsert_block(text: str, plugin_id: str, block: str) -> str:
    pattern = _block_re(plugin_id)
    if pattern.search(text):
        return pattern.sub("\n\n" + block + "\n", text)
    sep = "" if text.endswith("\n") else "\n"
    return f"{text}{sep}\n{block}\n"

def remove_block(text: str, plugin_id: str) -> str:
    return _block_re(plugin_id).sub("\n", text)
