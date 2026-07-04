"""
Site-aware template loader.

Looks for templates in site-specific directories before falling back
to default templates. Enables per-site template customization.

Template resolution order:
1. templates/{template_dir}/{template_name}
2. templates/{domain_prefix}/{template_name}
3. templates/{template_name} (default)
"""

import logging

from asgiref.local import Local
from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.cached import Loader as CachedLoader
from django.template.loaders.filesystem import Loader as FilesystemLoader

from apps.sites.middleware.multi_domain import get_current_site_config

logger = logging.getLogger(__name__)

# Async-safe task/thread-local storage to track templates currently being loaded.
# This prevents infinite recursion when site templates extend base templates.
_loading_stack = Local()


def get_loading_stack():
    """Get the current thread's template loading stack."""
    if not hasattr(_loading_stack, "stack"):
        _loading_stack.stack = set()
    return _loading_stack.stack


class SiteTemplateLoader(FilesystemLoader):
    """
    Custom template loader that checks site-specific directories first.

    Configuration via SiteProfile:
    - template_dir: Explicit template subdirectory name
    - Falls back to domain prefix (first part of domain)

    Example for site 'shop.example.com' with template_dir='shop':
    - First looks in: templates/shop/base.html
    - Then falls back to: templates/base.html
    """

    def get_template_sources(self, template_name):
        """
        Yield template sources, checking site-specific paths first.
        """
        # Get current site configuration from thread-local
        site_config = get_current_site_config()
        loading_stack = get_loading_stack()

        if site_config:
            template_dir = site_config.get("template_dir", "")

            if template_dir:
                # Try site-specific template first
                site_template = f"{template_dir}/{template_name}"

                # Skip if this template is already being loaded (prevents recursion)
                if site_template not in loading_stack:
                    for template_dir_path in self.get_dirs():
                        try:
                            # Check if site-specific template exists
                            name = str(template_dir_path / site_template)
                            yield Origin(
                                name=name,
                                template_name=site_template,
                                loader=self,
                            )
                        except Exception:
                            pass

        # Fall back to default template resolution
        yield from super().get_template_sources(template_name)

    def get_template(self, template_name, skip=None):
        """
        Get template, trying site-specific version first.
        """
        tried = []
        site_config = get_current_site_config()
        loading_stack = get_loading_stack()

        logger.debug(
            "SiteTemplateLoader.get_template: template=%s, site_config=%s, loading_stack=%s",
            template_name,
            site_config,
            loading_stack,
        )

        if site_config:
            template_dir = site_config.get("template_dir", "")

            if template_dir:
                site_template = f"{template_dir}/{template_name}"

                # Skip if this template is already being loaded (prevents recursion)
                # This handles the case where mysite/web/base.html
                # extends web/base.html - without this check, we'd try to load
                # mysite/web/base.html again, causing infinite recursion
                if site_template not in loading_stack:
                    try:
                        loading_stack.add(site_template)
                        logger.debug(
                            "SiteTemplateLoader: trying site-specific template: %s",
                            site_template,
                        )
                        result = super().get_template(site_template, skip=skip)
                        loading_stack.discard(site_template)
                        logger.info(
                            "SiteTemplateLoader: loaded site-specific template: %s",
                            site_template,
                        )
                        return result
                    except TemplateDoesNotExist:
                        loading_stack.discard(site_template)
                        logger.debug(
                            "SiteTemplateLoader: site-specific template not found: %s, falling back to default",
                            site_template,
                        )
                        # Site-specific template not found, fall through to default
                        tried.append(site_template)
                else:
                    logger.debug(
                        "SiteTemplateLoader: skipping %s (already in loading stack, preventing recursion)",
                        site_template,
                    )

        # Fall back to default
        try:
            result = super().get_template(template_name, skip=skip)
            logger.debug(
                "SiteTemplateLoader: loaded default template: %s",
                template_name,
            )
            return result
        except TemplateDoesNotExist as e:
            logger.warning(
                "SiteTemplateLoader: template not found: %s (tried: %s)",
                template_name,
                tried,
            )
            e.tried = tried + (e.tried or [])
            raise


class SiteAwareCachedLoader(CachedLoader):
    """Cached template loader for the production loader stack.

    Placeholder for now: it behaves exactly like Django's cached loader. Task 2 makes
    its cache key site-aware so per-site template overrides are cached independently.
    """

    pass
