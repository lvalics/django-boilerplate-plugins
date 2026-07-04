"""
Template tags for the landing pages plugin.

Tailwind 4 note: Tailwind's JIT compiler only emits classes it sees as string
literals at build time, so these helpers never interpolate arbitrary values
into class names. Color-ish config values are constrained to the DaisyUI
semantic enum (ALLOWED_COLORS, all covered by templates/landing_pages/
tailwind-safelist.html); unknown values fall back to a safe default. Arbitrary
hex colors always take the inline-style path (CSS custom properties /
color-mix), never a class.
"""

import json
import logging

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

logger = logging.getLogger(__name__)

# DaisyUI semantic color enum. Every class these helpers can produce from this
# enum is listed literally in templates/landing_pages/tailwind-safelist.html.
ALLOWED_COLORS = {
    "primary",
    "secondary",
    "accent",
    "neutral",
    "info",
    "success",
    "warning",
    "error",
    "base-100",
    "base-200",
    "base-300",
    # content counterparts (valid for bg-/text-/border- utilities)
    "primary-content",
    "secondary-content",
    "accent-content",
    "neutral-content",
    "info-content",
    "success-content",
    "warning-content",
    "error-content",
    "base-content",
}

_warned_colors: set[str] = set()


def _validated_color(value, default):
    """
    Constrain a color-ish config value to the DaisyUI enum.

    Unknown values fall back to ``default`` (logged once per value) so an
    editor typo can never inject an un-emitted Tailwind class.
    """
    if not value or not isinstance(value, str):
        return default
    if value in ALLOWED_COLORS:
        return value
    if value not in _warned_colors:
        _warned_colors.add(value)
        logger.warning("landing_pages: unknown color %r, falling back to %r", value, default)
    return default


def _color_mix(color, opacity_pct):
    """CSS value for a DaisyUI color at an opacity, via color-mix (Tailwind 4 / DaisyUI 5 variables)."""
    return f"color-mix(in oklab, var(--color-{color}) {opacity_pct}%, transparent)"


@register.simple_tag
def zone_template(zone):
    """Get the template name for a zone."""
    return zone.get_template_name()


@register.filter
def json_pretty(value):
    """Pretty print JSON content."""
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    try:
        return mark_safe(json.dumps(value, indent=2, ensure_ascii=False))
    except (TypeError, ValueError):
        return value


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def get_nested(dictionary, path):
    """
    Get a nested value from a dictionary using dot notation.
    Example: {{ content|get_nested:'author.name' }}
    """
    if not isinstance(dictionary, dict):
        return None

    keys = path.split(".")
    value = dictionary
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


@register.inclusion_tag("landing_pages/components/zone_wrapper.html")
def render_zone(zone):
    """Render a zone with its wrapper."""
    return {"zone": zone}


@register.filter
def star_rating(value, max_stars=5):
    """
    Generate star rating HTML.
    Usage: {{ testimonial.rating|star_rating }}
    """
    try:
        rating = int(value)
    except (TypeError, ValueError):
        rating = 0

    stars = []
    for i in range(1, max_stars + 1):
        if i <= rating:
            stars.append('<span class="text-warning">★</span>')
        else:
            stars.append('<span class="text-base-300">☆</span>')

    return mark_safe("".join(stars))


@register.filter
def split_lines(value):
    """Split text by newlines for iteration."""
    if not value:
        return []
    return value.split("\n")


@register.filter
def is_hex_color(value):
    """Check if a value is a hex color code."""
    if not value or not isinstance(value, str):
        return False
    return value.startswith("#") and len(value) in (4, 7, 9)


@register.filter
def is_video_url(value):
    """
    Check if a URL points to a video file.
    Returns True for .mp4, .webm, .ogg, .mov video extensions.
    """
    if not value or not isinstance(value, str):
        return False
    # Remove query string for extension check
    url_path = value.split("?")[0].lower()
    video_extensions = (".mp4", ".webm", ".ogg", ".mov", ".m4v")
    return url_path.endswith(video_extensions)


@register.simple_tag
def color_style(color_value, property_name="color"):
    """
    Generate inline style for hex colors, or empty string for DaisyUI colors.
    Usage: {% color_style config.badge_text_color 'color' %}
    """
    if not color_value:
        return ""
    if isinstance(color_value, str) and color_value.startswith("#"):
        return f"{property_name}: {color_value};"
    return ""


@register.simple_tag
def color_class(color_value, prefix="text"):
    """
    Generate a Tailwind class for DaisyUI enum colors, or empty string for hex colors.
    Unknown color names produce no class (safe default).
    Usage: {% color_class config.badge_text_color 'text' %}
    """
    if not color_value:
        return ""
    if isinstance(color_value, str) and color_value.startswith("#"):
        return ""
    color = _validated_color(color_value, "")
    if not color:
        return ""
    return f"{prefix}-{color}"


@register.simple_tag
def badge_styles(text_color, bg_color, default_text="primary", default_bg="primary", opacity="10"):
    """
    Generate combined class and style attributes for a badge.
    Hex colors use inline styles; DaisyUI enum colors use safelisted classes
    (text) and a color-mix inline background (so no dynamic opacity classes).
    Usage: {% badge_styles config.badge_text_color config.badge_bg 'primary' 'primary' '10' %}
    Returns: class="..." style="..."
    """
    text_color = text_color or default_text
    bg_color = bg_color or default_bg

    classes = []
    styles = []

    # Handle text color
    if isinstance(text_color, str) and text_color.startswith("#"):
        styles.append(f"color: {text_color}")
    else:
        classes.append(f"text-{_validated_color(text_color, default_text)}")

    try:
        opacity_pct = max(0, min(100, int(opacity)))
    except (TypeError, ValueError):
        opacity_pct = 10

    # Handle background color
    if isinstance(bg_color, str) and bg_color.startswith("#"):
        # Convert hex to rgba with opacity
        hex_color = bg_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join([c * 2 for c in hex_color])
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            styles.append(f"background-color: rgba({r}, {g}, {b}, {opacity_pct / 100})")
        except ValueError:
            pass
    else:
        color = _validated_color(bg_color, default_bg)
        styles.append(f"background-color: {_color_mix(color, opacity_pct)}")

    result = ""
    if classes:
        result += f'class="{" ".join(classes)}"'
    if styles:
        if result:
            result += " "
        result += f'style="{"; ".join(styles)}"'

    return mark_safe(result)


@register.simple_tag
def section_bg(color_value, default="base-200"):
    """
    Generate background class and/or style for a section.
    Hex colors -> inline style; DaisyUI enum colors -> safelisted class.
    Usage: <section {% section_bg config.background_color 'base-200' %}>
    """
    color = color_value or default
    if not color:
        return ""

    if isinstance(color, str) and color.startswith("#"):
        return mark_safe(f'style="background-color: {color}"')
    return mark_safe(f'class="bg-{_validated_color(color, default)}"')


@register.simple_tag
def overlay_styles(overlay_color, default="neutral"):
    """
    Generate overlay class and/or style for background-image sections.
    Used with bg-blend-multiply for a semi-transparent overlay effect.
    Hex colors -> inline style; DaisyUI enum colors -> safelisted class.
    Usage: <section {% overlay_styles config.overlay_color 'neutral' %} class="bg-blend-multiply">
    """
    color = overlay_color or default
    if not color:
        return ""

    if isinstance(color, str) and color.startswith("#"):
        return mark_safe(f'style="background-color: {color}"')
    return mark_safe(f'class="bg-{_validated_color(color, default)}"')


@register.simple_tag
def btn_styles(btn_color, btn_style="solid", default_color="primary"):
    """
    Generate button class with support for hex colors.
    Hex colors -> inline style; DaisyUI enum colors -> safelisted btn-* class.
    Usage: <a class="btn" {% btn_styles config.primary_btn_color config.primary_btn_style 'primary' %}>
    """
    color = btn_color or default_color
    style = btn_style or "solid"

    if isinstance(color, str) and color.startswith("#"):
        # Hex color - use inline style
        if style == "outline":
            return mark_safe(f'style="border-color: {color}; color: {color}; background: transparent"')
        elif style == "ghost":
            return mark_safe(f'style="color: {color}; background: transparent"')
        else:  # solid
            return mark_safe(f'style="background-color: {color}; border-color: {color}; color: white"')
    else:
        color = _validated_color(color, default_color)
        if style == "outline":
            return mark_safe(f'class="btn-outline btn-{color}"')
        elif style == "ghost":
            return mark_safe('class="btn-ghost"')
        else:
            return mark_safe(f'class="btn-{color}"')


@register.simple_tag
def zone_css_class(zone, extra_classes=""):
    """
    Generate CSS classes for a zone.
    Usage: {% zone_css_class zone 'my-extra-class' %}
    """
    classes = [
        "landing-zone",
        f"zone-{zone.zone_type}",
        f"zone-order-{zone.order}",
    ]

    if not zone.is_active:
        classes.append("zone-inactive")

    if extra_classes:
        classes.append(extra_classes)

    return " ".join(classes)


@register.filter
def currency_format(value, currency="$"):
    """
    Format a number as currency.
    Usage: {{ price|currency_format:'€' }}
    """
    try:
        number = float(value)
        if number == int(number):
            return f"{currency}{int(number)}"
        return f"{currency}{number:.2f}"
    except (TypeError, ValueError):
        return value


@register.inclusion_tag("landing_pages/components/schema_markup.html")
def schema_markup(testimonial):
    """Render Schema.org Review markup for a testimonial."""
    return {"testimonial": testimonial}


@register.simple_tag
def build_url_params(**kwargs):
    """
    Build URL query parameters.
    Usage: {% build_url_params utm_source='landing' utm_medium='cta' %}
    """
    params = []
    for key, value in kwargs.items():
        if value:
            params.append(f"{key}={value}")
    if params:
        return "?" + "&".join(params)
    return ""


@register.simple_tag
def gradient_style(direction="br", color_from="primary/10", color_to="secondary/10"):
    """
    Generate an inline CSS gradient (never classes, so no JIT dependency).
    Supports hex colors and DaisyUI enum names with opacity ('primary/10').
    DaisyUI colors resolve through the Tailwind 4 / DaisyUI 5 CSS variables
    (--color-primary etc.) via color-mix.

    Usage: <div style="{% gradient_style config.gradient_direction config.gradient_from config.gradient_to %}">
    """
    direction_map = {
        "br": "to bottom right",
        "tr": "to top right",
        "bl": "to bottom left",
        "tl": "to top left",
        "r": "to right",
        "l": "to left",
        "t": "to top",
        "b": "to bottom",
    }
    css_direction = direction_map.get(direction or "br", "to bottom right")

    def parse_color(color_str):
        """Convert color string to CSS value."""
        if not color_str or not isinstance(color_str, str):
            return _color_mix("primary", 10)

        # Hex color - use directly
        if color_str.startswith("#"):
            return color_str

        # DaisyUI color with opacity (e.g., 'primary/10')
        if "/" in color_str:
            color_name, opacity = color_str.rsplit("/", 1)
            try:
                opacity_pct = max(0, min(100, int(opacity)))
            except ValueError:
                opacity_pct = 10
        else:
            color_name = color_str
            opacity_pct = 100

        color_name = _validated_color(color_name, "primary")
        return _color_mix(color_name, opacity_pct)

    from_color = parse_color(color_from)
    to_color = parse_color(color_to)

    return mark_safe(f"background: linear-gradient({css_direction}, {from_color}, {to_color});")


@register.simple_tag
def heading(content, tag="h1", css_class="", auto_size=True):
    """
    Render a heading with a dynamic tag and automatic sizing.
    Usage: {% heading content.title tag=config.title_tag|default:'h1' css_class='font-bold' %}

    Args:
        content: The text/HTML content for the heading
        tag: The heading tag to use (h1-h6, p, div, span, small). Defaults to h1.
        css_class: CSS classes to apply to the heading
        auto_size: If True, automatically adds responsive size classes based on tag

    Returns:
        Safe HTML string with the heading wrapped in the specified tag
    """
    # Validate tag - only allow safe heading-like tags
    allowed_tags = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "span", "small"}
    tag = str(tag).lower().strip() if tag else "h1"
    if tag not in allowed_tags:
        tag = "h1"

    # Auto-size classes based on heading level (all literal, JIT-safe)
    size_classes = {
        "h1": "text-4xl md:text-5xl lg:text-6xl",
        "h2": "text-3xl md:text-4xl lg:text-5xl",
        "h3": "text-2xl md:text-3xl lg:text-4xl",
        "h4": "text-xl md:text-2xl lg:text-3xl",
        "h5": "text-lg md:text-xl lg:text-2xl",
        "h6": "text-base md:text-lg lg:text-xl",
        "p": "text-base",
        "div": "text-base",
        "span": "",
        "small": "text-sm",
    }

    # Build final class string
    final_classes = []
    if auto_size and tag in size_classes:
        final_classes.append(size_classes[tag])
    if css_class:
        final_classes.append(css_class)

    class_str = " ".join(final_classes)
    class_attr = f' class="{class_str}"' if class_str else ""

    return mark_safe(f"<{tag}{class_attr}>{content}</{tag}>")
