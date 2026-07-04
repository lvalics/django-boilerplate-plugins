"""
Footer zone templates.
"""

from ._base import ZoneType

FOOTER_TEMPLATES = [
    {
        "name": "Footer - Full with Columns",
        "zone_type": ZoneType.FOOTER,
        "template_file": "landing_pages/zones/footer.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/footer.html

Full footer with logo, link columns, copyright, and social icons.
Best for sites with multiple pages and comprehensive navigation.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

BRAND
  logo              Logo image URL
  brand_name        Company/brand name
  brand_url         Logo link URL (default: "/")
  brand_description Short tagline or description

LINK COLUMNS
  columns           Array of column objects:
    - title         Column heading (e.g., "Resources")
    - links         Array of {text, url, external?}

COPYRIGHT
  company_name      Company name for copyright
  company_url       Company website URL
  copyright_year    Year (default: current year)

SOCIAL
  social_links      Array of {platform, url}
                    Platforms: facebook, twitter, github, discord,
                               instagram, linkedin, youtube, dribbble

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             "default" (columns), "simple", "minimal", "centered"
  max_width         Container width: xl, 2xl, 7xl (default: "xl")

APPEARANCE
  background_color  Footer background (default: "base-200")
  heading_color     Column heading color (default: "base-content")
  text_color        Body text color (default: "base-content/70")
  brand_color       Brand name color (default: "base-content")
  border_color      Divider line color (default: "base-300")
  social_color      Social icon color (default: "base-content/60")
  social_hover_color Social icon hover (default: "base-content")
""",
        "default_content": {
            "logo": "https://flowbite.com/docs/images/logo.svg",
            "brand_name": "YourBrand",
            "brand_url": "/",
            "brand_description": "Making the world a better place through quality products.",
            "company_name": "YourBrand",
            "company_url": "/",
            "copyright_year": "2024",
            "columns": [
                {
                    "title": "Resources",
                    "links": [
                        {"text": "Documentation", "url": "/docs/"},
                        {"text": "Blog", "url": "/blog/"},
                        {"text": "Support", "url": "/support/"},
                    ],
                },
                {
                    "title": "Follow Us",
                    "links": [
                        {"text": "GitHub", "url": "https://github.com/", "external": True},
                        {"text": "Discord", "url": "https://discord.com/", "external": True},
                    ],
                },
                {
                    "title": "Legal",
                    "links": [
                        {"text": "Privacy Policy", "url": "/privacy/"},
                        {"text": "Terms & Conditions", "url": "/terms/"},
                    ],
                },
            ],
            "social_links": [
                {"platform": "facebook", "url": "#"},
                {"platform": "twitter", "url": "#"},
                {"platform": "github", "url": "#"},
                {"platform": "discord", "url": "#"},
            ],
        },
        "default_config": {
            "style": "default",
            "max_width": "xl",
            "background_color": "base-200",
            "heading_color": "base-content",
            "text_color": "base-content/70",
        },
    },
    {
        "name": "Footer - Simple",
        "zone_type": ZoneType.FOOTER,
        "template_file": "landing_pages/zones/footer.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/footer.html

Simple one-line footer with copyright and inline links.
Great for landing pages and minimal sites.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

company_name      Company name for copyright
company_url       Company website URL
copyright_year    Year (default: current year)
links             Array of {text, url} for inline links
""",
        "default_content": {
            "company_name": "YourBrand",
            "company_url": "/",
            "copyright_year": "2024",
            "links": [
                {"text": "About", "url": "/about/"},
                {"text": "Privacy Policy", "url": "/privacy/"},
                {"text": "Contact", "url": "/contact/"},
            ],
        },
        "default_config": {
            "style": "simple",
            "max_width": "xl",
            "background_color": "base-200",
            "text_color": "base-content/70",
        },
    },
    {
        "name": "Footer - Minimal",
        "zone_type": ZoneType.FOOTER,
        "template_file": "landing_pages/zones/footer.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/footer.html

Minimal centered copyright line only.
Perfect for single-page landing pages.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

company_name      Company name for copyright
company_url       Company website URL (optional)
copyright_year    Year (default: current year)
""",
        "default_content": {
            "company_name": "YourBrand",
            "copyright_year": "2024",
        },
        "default_config": {
            "style": "minimal",
            "max_width": "xl",
            "background_color": "base-200",
            "text_color": "base-content/70",
            "padding_y": "6",
        },
    },
    {
        "name": "Footer - Centered with Social",
        "zone_type": ZoneType.FOOTER,
        "template_file": "landing_pages/zones/footer.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/footer.html

Centered footer with logo, nav links, social icons, and copyright.
Modern, clean design for brand-focused pages.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

BRAND
  logo              Logo image URL
  brand_name        Company/brand name
  brand_url         Logo link URL (default: "/")

NAVIGATION
  nav_links         Array of {text, url} for main links

COPYRIGHT
  company_name      Company name for copyright
  copyright_year    Year (default: current year)

SOCIAL
  social_links      Array of {platform, url}
""",
        "default_content": {
            "logo": "https://flowbite.com/docs/images/logo.svg",
            "brand_name": "YourBrand",
            "brand_url": "/",
            "nav_links": [
                {"text": "About", "url": "/about/"},
                {"text": "Features", "url": "/features/"},
                {"text": "Pricing", "url": "/pricing/"},
                {"text": "Contact", "url": "/contact/"},
            ],
            "company_name": "YourBrand",
            "copyright_year": "2024",
            "social_links": [
                {"platform": "facebook", "url": "#"},
                {"platform": "instagram", "url": "#"},
                {"platform": "twitter", "url": "#"},
                {"platform": "github", "url": "#"},
            ],
        },
        "default_config": {
            "style": "centered",
            "max_width": "xl",
            "background_color": "base-200",
            "brand_color": "base-content",
            "text_color": "base-content/70",
            "social_color": "base-content/60",
            "social_hover_color": "base-content",
        },
    },
]
