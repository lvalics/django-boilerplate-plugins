from __future__ import annotations
import json
import re
from installer.manifest import Manifest

def _start(plugin_id: str) -> str:
    return f"# >>> plugin: {plugin_id} >>>"

def _end(plugin_id: str) -> str:
    return f"# <<< plugin: {plugin_id} <<<"

def _py_literal(value) -> str:
    """Render a value as a valid, double-quoted Python literal (stdlib-only)."""
    if isinstance(value, bool):          # must precede int — bool is a subclass of int
        return "True" if value else "False"
    if value is None:
        return "None"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value)         # double-quoted, correctly escaped, valid Python
    if isinstance(value, list):
        return "[" + ", ".join(_py_literal(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{_py_literal(k)}: {_py_literal(v)}" for k, v in value.items()) + "}"
    raise TypeError(f"unsupported manifest value type for code emission: {type(value).__name__}")

def build_settings_block(m: Manifest) -> str:
    lines = [_start(m.id)]
    if m.installed_apps:
        lines.append(f"INSTALLED_APPS += {_py_literal(m.installed_apps)}")
    if m.middleware:
        lines.append(f"MIDDLEWARE += {_py_literal(m.middleware)}")
    if m.celery_beat_schedule:
        lines.append(
            "CELERY_BEAT_SCHEDULE = {**globals().get('CELERY_BEAT_SCHEDULE', {}), "
            f"**{_py_literal(m.celery_beat_schedule)}}}"
        )
    lines.append(_end(m.id))
    return "\n".join(lines)

def build_urls_block(m: Manifest) -> str:
    lines = [_start(m.id), "from django.urls import include, path"]
    for prefix, module in m.url_mappings.items():
        lines.append(f'urlpatterns += [path({_py_literal(prefix)}, include({_py_literal(module)}))]')
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
