"""
Template tags for site-specific functionality.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def site_feature(context, feature_name, default=False):
    """
    Check if a feature is enabled for the current site.

    Usage:
        {% site_feature "enable_blog" as has_blog %}
        {% if has_blog %}...{% endif %}

        {% if site_feature "enable_shop" %}...{% endif %}
    """
    site_config = context.get("site_config", {})
    features = site_config.get("features", {})
    return features.get(feature_name, default)


@register.simple_tag(takes_context=True)
def site_meta(context, meta_name, default=""):
    """
    Get a meta default value for the current site.

    Usage:
        {% site_meta "description" as meta_description %}
        <meta name="description" content="{{ meta_description }}">
    """
    site_config = context.get("site_config", {})
    meta_defaults = site_config.get("meta_defaults", {})
    return meta_defaults.get(meta_name, default)


@register.simple_tag(takes_context=True)
def site_setting(context, setting_path, default=None):
    """
    Get any site config value by dot-notation path.

    Usage:
        {% site_setting "email_settings.from_email" as from_email %}
        {% site_setting "features.beta_banner" as beta_banner %}

    Note: the "integrations" key is not available in template context (it may
    contain secrets); resolve integrations server-side via SiteProfile.get_integration().
    """
    site_config = context.get("site_config", {})

    # Navigate the path
    value = site_config
    for key in setting_path.split("."):
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default

    return value if value is not None else default


@register.inclusion_tag("sites/includes/head_scripts.html", takes_context=True)
def render_head_scripts(context):
    """
    Render head scripts defined in site config.

    Usage in base.html:
        {% load site_tags %}
        {% render_head_scripts %}
    """
    site_config = context.get("site_config", {})
    return {
        "scripts": site_config.get("head_scripts", []),
        "custom_css": site_config.get("custom_css", ""),
    }


@register.inclusion_tag("sites/includes/body_scripts.html", takes_context=True)
def render_body_scripts(context):
    """
    Render body scripts defined in site config.

    Usage at end of body in base.html:
        {% load site_tags %}
        {% render_body_scripts %}
    """
    site_config = context.get("site_config", {})
    return {
        "scripts": site_config.get("body_scripts", []),
    }


@register.simple_tag(takes_context=True)
def site_css_vars(context):
    """
    Output CSS custom properties for site colors.

    Usage in <head>:
        <style>:root { {% site_css_vars %} }</style>
    """
    site_config = context.get("site_config", {})
    primary = site_config.get("primary_color", "#3B82F6")
    secondary = site_config.get("secondary_color", "#1E40AF")

    css = f"--site-primary: {primary}; --site-secondary: {secondary};"
    return mark_safe(css)


@register.filter
def site_url(path, site_config):
    """
    Build a URL for a specific site.

    Usage:
        {{ "/dashboard/"|site_url:other_site_config }}
    """
    if not site_config:
        return path

    domain = site_config.get("domain", "")
    if domain:
        scheme = "https"  # Assume HTTPS in production
        return f"{scheme}://{domain}{path}"

    return path
