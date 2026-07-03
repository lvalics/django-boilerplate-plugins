# django-boilerplate-plugins

Zero-dependency installer + plugins for the free
[django-boilerplate](https://github.com/saaspegasus/django-boilerplate).

## Usage

```bash
python install.py <plugin> /path/to/your/project          # dry-run
python install.py <plugin> /path/to/your/project --apply  # apply
python install.py <plugin> /path/to/your/project --uninstall
python install.py --list
```

See `docs/specs/` for the design and `docs/authoring-a-plugin.md` to add a plugin.
