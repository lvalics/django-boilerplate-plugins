"""
Banner zone templates.
"""

from ._base import ZoneType

BANNER_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════
    {
        "name": "Banner - Default Sticky",
        "zone_type": ZoneType.BANNER,
        "template_file": "landing_pages/zones/banner.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/banner.html

Simple sticky banner for announcements and notifications.
Can be positioned at top or bottom of page.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

message        Banner text message (required)
icon           Icon: info, megaphone, warning, home, or emoji
primary_cta    Object: {url, text, target} for inline link

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             "default", "marketing", or "informational"
  position          "top" or "bottom" (default: "top")

DISPLAY TIMING
  display_mode      "immediate", "after_seconds", or "after_scroll"
  show_after_seconds  Delay in seconds (default: 3)
  show_after_scroll_px  Scroll distance in pixels (default: 300)

APPEARANCE
  background_color  Banner background (default: "base-100")
  text_color        Text color (default: "base-content")
  border_color      Border color (default: "base-300")
  icon_bg           Icon background color (default: "primary")
  icon_color        Icon color (default: "primary")

BEHAVIOR
  dismissible       Allow user to close banner (default: true)
""",
        "default_content": {
            "icon": "megaphone",
            "message": "New feature announcement!",
            "primary_cta": {
                "url": "#",
                "text": "Learn more",
            },
        },
        "default_config": {
            "style": "default",
            "position": "top",
            "display_mode": "immediate",
            "dismissible": True,
            "background_color": "base-100",
            "text_color": "base-content",
            "border_color": "base-300",
        },
    },
    {
        "name": "Banner - Marketing CTA",
        "zone_type": ZoneType.BANNER,
        "template_file": "landing_pages/zones/banner.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/banner.html

Marketing-style banner with logo/icon, message, and CTA buttons.
Floating centered design with shadow.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

message          Banner text message (required)
icon             Emoji icon (optional)
logo             Logo image URL (optional)
logo_link        Logo click URL (default: "/")
logo_alt         Logo alt text
primary_cta      Object: {url, text} for primary button
secondary_cta    Object: {url, text} for secondary button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             Set to "marketing"
  position          "top" or "bottom" (default: "top")

DISPLAY TIMING
  display_mode      "immediate", "after_seconds", or "after_scroll"
  show_after_seconds  Delay in seconds (default: 3)
  show_after_scroll_px  Scroll distance in pixels (default: 300)

APPEARANCE
  background_color    Banner background (default: "base-100")
  primary_btn_color   Primary button color (default: "primary")
  text_color          Text color (default: "base-content")
""",
        "default_content": {
            "icon": "🚀",
            "message": "Get 20% off your first purchase with code WELCOME20",
            "primary_cta": {
                "url": "#signup",
                "text": "Sign Up",
            },
            "secondary_cta": {
                "url": "#learn-more",
                "text": "Learn more",
            },
        },
        "default_config": {
            "style": "marketing",
            "position": "top",
            "display_mode": "immediate",
            "dismissible": True,
            "background_color": "base-100",
            "primary_btn_color": "primary",
        },
    },
    {
        "name": "Banner - Informational",
        "zone_type": ZoneType.BANNER,
        "template_file": "landing_pages/zones/banner.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/banner.html

Full-width informational banner with title, message, and action buttons.
Ideal for important announcements or system notifications.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title            Banner heading (optional)
message          Banner text message (required)
primary_cta      Object: {url, text} for primary button
secondary_cta    Object: {url, text} for secondary button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             Set to "informational"
  position          "top" or "bottom" (default: "top")

APPEARANCE
  background_color    Banner background (default: "info/10")
  title_color         Title color (default: "base-content")
  text_color          Text color (default: "base-content/70")
  primary_btn_color   Primary button color (default: "primary")
""",
        "default_content": {
            "title": "Important Update",
            "message": "We've updated our terms of service. Please review the changes.",
            "primary_cta": {
                "url": "#review",
                "text": "Review Changes",
            },
            "secondary_cta": {
                "url": "#dismiss",
                "text": "Dismiss",
            },
        },
        "default_config": {
            "style": "informational",
            "position": "top",
            "display_mode": "immediate",
            "dismissible": True,
            "background_color": "base-200",
            "title_color": "base-content",
            "text_color": "base-content/70",
            "primary_btn_color": "primary",
        },
    },
    {
        "name": "Banner - Bottom Navigation Helper",
        "zone_type": ZoneType.BANNER,
        "template_file": "landing_pages/zones/banner.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/banner.html

Bottom banner to help users navigate back to homepage.
Useful for standalone landing pages without site template.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

message          Navigation hint message
icon             Icon: "home" shows house icon
primary_cta      Object: {url, text, target} for homepage link

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

DISPLAY TIMING
  display_mode         "after_scroll" recommended
  show_after_scroll_px Pixels to scroll before showing (default: 300)
""",
        "default_content": {
            "icon": "home",
            "message": "Looking for more?",
            "primary_cta": {
                "url": "/",
                "text": "Return to homepage",
            },
        },
        "default_config": {
            "style": "default",
            "position": "bottom",
            "display_mode": "after_scroll",
            "show_after_scroll_px": 500,
            "dismissible": True,
            "background_color": "base-200",
            "icon_bg": "primary",
            "icon_color": "primary",
        },
    },
    {
        "name": "Banner - Delayed Popup",
        "zone_type": ZoneType.BANNER,
        "template_file": "landing_pages/zones/banner.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/banner.html

Marketing banner that appears after a delay.
Great for non-intrusive promotions.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

message          Promotional message
icon             Emoji or icon name
primary_cta      Object: {url, text} for CTA button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

DISPLAY TIMING
  display_mode        "after_seconds"
  show_after_seconds  Delay in seconds (default: 5)
""",
        "default_content": {
            "icon": "🎁",
            "message": "Don't miss our special offer!",
            "primary_cta": {
                "url": "#offer",
                "text": "Claim Now",
            },
        },
        "default_config": {
            "style": "marketing",
            "position": "bottom",
            "display_mode": "after_seconds",
            "show_after_seconds": 5,
            "dismissible": True,
            "background_color": "primary",
            "text_color": "primary-content",
            "primary_btn_color": "secondary",
        },
    },
    # ═══════════════════════════════════════════════════════════════
]
