"""
Hero zone templates.
"""

from ._base import ZoneType

HERO_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Hero - Visual Split",
        "zone_type": ZoneType.HERO_VIDEO,
        "template_file": "landing_pages/zones/hero_visual.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/hero_visual.html

Two-column hero: content on left, image or video on right.
Great for SaaS products and feature showcases.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADLINE
  headline          Main headline text (required)
  subheadline       Supporting paragraph text

PRIMARY CTA
  primary_cta_text  Primary button text
  primary_cta_url   Primary button URL

SECONDARY CTA
  secondary_cta_text  Secondary button text
  secondary_cta_url   Secondary button URL

VISUAL (choose one)
  image_url         Hero image URL
  image_alt         Alt text for image
  video_url         YouTube/Vimeo embed URL (alternative to image)

TRUST BADGES
  trust_badges      Array of badge objects:
                    • icon: Emoji or symbol (e.g., "✓")
                    • text: Badge text

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

COLORS
  background_color    Section background (default: base-100)
                  • "base-100" - white/light (default)
                  • "base-200" - light gray
                  • "base-300" - darker gray
                  • "neutral" - dark background
                  • "primary" - brand color

BUTTONS
  primary_cta_style   Primary button style (default: primary)
                  • "primary" - brand color (default)
                  • "secondary" - secondary brand
                  • "accent" - accent color
                  • "success" - green
  secondary_cta_style Secondary button style (default: ghost)
                  • "ghost" - transparent (default)
                  • "outline" - outlined
                  • "secondary" - filled secondary

IMAGE
  image_class         CSS classes for image (default: rounded-lg shadow-2xl)
                  • "rounded-lg shadow-2xl" - rounded with shadow (default)
                  • "rounded-xl shadow-xl" - more rounded
                  • "rounded-2xl shadow-lg" - extra rounded
                  • "rounded-none" - no rounding
                  • "rounded-full" - circle
  image_container_bg  Background color for image container
                  • "" - transparent (default)
                  • "#667eea" - hex color
                  • "primary" - DaisyUI color class

STYLE
  style               Template style variant name (for display)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

SaaS product hero:
{
  "headline": "Payments tool for software companies",
  "subheadline": "Simplify your payment stack with our platform.",
  "image_url": "https://example.com/product-mockup.png",
  "image_alt": "Product dashboard screenshot",
  "primary_cta_text": "Get started",
  "primary_cta_url": "/signup",
  "secondary_cta_text": "Speak to Sales",
  "secondary_cta_url": "/contact",
  "trust_badges": [
    {"icon": "✓", "text": "Free 14-day trial"},
    {"icon": "✓", "text": "No credit card required"}
  ]
}

With video instead of image:
{
  "headline": "See it in action",
  "video_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
  "primary_cta_text": "Try it Free",
  "primary_cta_url": "/trial"
}

Dark theme:
config: {
  "background_color": "neutral",
  "primary_cta_style": "primary",
  "secondary_cta_style": "outline"
}
""",
        "default_content": {
            "headline": "Payments tool for software companies",
            "subheadline": "From checkout to global sales tax compliance, companies around the world use our platform to simplify their payment stack.",
            "image_url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/hero/phone-mockup.png",
            "image_alt": "Product mockup",
            "video_url": "",
            "primary_cta_text": "Get started",
            "primary_cta_url": "#signup",
            "secondary_cta_text": "Speak to Sales",
            "secondary_cta_url": "#contact",
            "trust_badges": [
                {"icon": "✓", "text": "Free 14-day trial"},
                {"icon": "✓", "text": "No credit card required"},
                {"icon": "✓", "text": "Cancel anytime"},
            ],
        },
        "default_config": {
            "style": "Visual Split",
            "background_color": "base-100",
            "primary_cta_style": "primary",
            "secondary_cta_style": "ghost",
            "image_class": "rounded-lg shadow-2xl",
            "image_container_bg": "",
        },
    },
    {
        "name": "Hero - Fullscreen Video/Image",
        "zone_type": ZoneType.HERO_VIDEO,
        "template_file": "landing_pages/zones/hero_fullscreen.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/hero_fullscreen.html

Fullscreen hero with video or image background, overlay, and animations.
Maximum visual impact for landing pages and product launches.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADLINE
  headline          Main headline text (required)
  subheadline       Supporting paragraph text

BACKGROUND (choose one)
  background_image  Background image URL
  background_alt    Alt text for background image
  background_video  MP4 video URL (takes precedence over image)
  video_poster      Poster image shown while video loads

BADGE
  badge_text        Announcement badge above headline (optional)

PRIMARY CTA
  primary_cta_text  Primary button text
  primary_cta_url   Primary button URL

SECONDARY CTA
  secondary_cta_text  Secondary button text
  secondary_cta_url   Secondary button URL

SCROLL INDICATOR
  scroll_indicator  Show bouncing scroll arrow (true/false)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

OVERLAY
  overlay_color       Overlay color (default: black)
                  • "black" - black overlay (default)
                  • "gray-900" - dark gray
                  • "primary" - brand color
  overlay_opacity     Opacity 0-100 (default: 50)
                  • "30" - light overlay
                  • "50" - medium (default)
                  • "70" - dark overlay

COLORS
  text_color          Headline color (default: white)
                  • "white" - white (default)
                  • "primary-content" - for colored overlays
  subtext_color       Subheadline color (default: white/80)
                  • "white/80" - 80% white (default)
                  • "white" - full white
                  • "gray-200" - light gray

BADGE STYLING
  badge_bg            Badge background (default: primary)
                  • "primary" - brand color (default)
                  • "secondary" - secondary brand
                  • "accent" - accent color
  badge_text_color    Badge text color (default: primary-content)
  badge_border        Badge border color (default: primary)

BUTTONS
  primary_cta_style   Primary button style (default: primary)
                  • "primary" - brand color (default)
                  • "secondary" - secondary brand
                  • "accent" - accent color
  primary_cta_icon    Show arrow icon on primary CTA (default: false)
  secondary_cta_style Secondary button style (default: ghost)
                  • "ghost" - transparent (default)
                  • "outline" - outlined

BACKGROUND
  background_position Image position (default: center)
                  • "center" - centered (default)
                  • "top" - aligned to top
                  • "bottom" - aligned to bottom

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Product launch with video:
{
  "badge_text": "New Release",
  "headline": "For the Greatest",
  "subheadline": "The ultimate professional platform.",
  "background_video": "/media/hero-video.mp4",
  "video_poster": "/media/hero-poster.jpg",
  "primary_cta_text": "Learn More",
  "primary_cta_url": "/features",
  "scroll_indicator": true
}

Image with dark overlay:
{
  "headline": "Transform Your Business",
  "background_image": "/media/hero-bg.jpg",
  "primary_cta_text": "Get Started",
  "primary_cta_url": "/signup"
}
config: {
  "overlay_color": "black",
  "overlay_opacity": "70"
}

Minimal with brand overlay:
config: {
  "overlay_color": "primary",
  "overlay_opacity": "60",
  "badge_bg": "white",
  "badge_text_color": "primary",
  "primary_cta_style": "white"
}
""",
        "default_content": {
            "headline": "For the Greatest",
            "subheadline": "The ultimate professional platform for creative excellence",
            "badge_text": "New Release",
            "background_image": "https://www.huion.com/statics/hw/site/img/kamvas-pro27144hz/images/kamvas-pro27144hz-head-pic.jpg",
            "background_alt": "Hero background",
            "background_video": "",
            "video_poster": "",
            "primary_cta_text": "Learn More",
            "primary_cta_url": "#features",
            "secondary_cta_text": "Watch Demo",
            "secondary_cta_url": "#demo",
            "scroll_indicator": True,
        },
        "default_config": {
            "style": "Fullscreen",
            "overlay_color": "black",
            "overlay_opacity": "50",
            "text_color": "white",
            "subtext_color": "white/80",
            "badge_bg": "primary",
            "badge_text_color": "primary-content",
            "badge_border": "primary",
            "primary_cta_style": "primary",
            "primary_cta_icon": True,
            "secondary_cta_style": "ghost",
            "background_position": "center",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
