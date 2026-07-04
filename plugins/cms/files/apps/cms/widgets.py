"""Admin form widgets for the CMS plugin."""

from django import forms


class JSONEditorWidget(forms.Textarea):
    """A textarea enhanced with a small, self-contained JSON editor.

    Progressive enhancement only: the field is a normal ``<textarea>`` holding raw
    JSON text, so it works (and Django's ``JSONField`` still validates server-side)
    with JavaScript disabled. The bundled admin asset adds pretty-printing, a
    format/minify toolbar, and live syntax validation. No external/CDN dependency.
    """

    def __init__(self, attrs=None):
        defaults = {
            "class": "cms-json-editor vLargeTextField",
            "rows": 20,
            "cols": 100,
            "spellcheck": "false",
        }
        if attrs:
            defaults.update(attrs)
        super().__init__(defaults)

    class Media:
        css = {"all": ["cms/admin/json-editor.css"]}
        js = ["cms/admin/json-editor.js"]
