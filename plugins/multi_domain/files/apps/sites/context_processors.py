"""
Context processors for site configuration.

Makes site config available in all templates.
"""


def site_config(request):
    """
    Add site configuration to template context.

    Available in templates as:
    - site_config: Full configuration dict
    - site_name: Site display name
    - site_theme: Current theme identifier
    - site_features: Feature flags dict
    """
    config = getattr(request, "site_config", None) or {}

    # Exclude integrations from template context: it may carry third-party API config
    # (and env: secret placeholders) that should never be exposed to templates. Server-side
    # code resolves secrets via SiteProfile.get_integration() / resolve_integration().
    template_config = {k: v for k, v in config.items() if k != "integrations"}

    return {
        "site_config": template_config,
        "site_name": config.get("site_name", ""),
        "site_theme": config.get("theme", "default"),
        "site_features": config.get("features", {}),
        "site_meta": config.get("meta_defaults", {}),
        "site_primary_color": config.get("primary_color", "#3B82F6"),
        "site_secondary_color": config.get("secondary_color", "#1E40AF"),
        "site_custom_css": config.get("custom_css", ""),
    }
