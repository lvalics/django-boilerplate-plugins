"""
Jumbotron zone templates.

All color fields support both DaisyUI colors (e.g., "primary", "base-200")
and hex colors (e.g., "#FF6C0E", "#0A0EA0").

All CTA buttons support:
- text: Button text
- url: Button URL
- target: "_blank" to open in new tab (optional)
"""

from ._base import ZoneType

JUMBOTRON_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Jumbotron - Default",
        "zone_type": ZoneType.JUMBOTRON,
        "template_file": "landing_pages/zones/jumbotron.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/jumbotron.html

Centered content section with solid background - not full-screen like hero.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Main heading text (required)
description     Supporting paragraph text
badge           Optional badge/label above title

PRIMARY CTA
  primary_cta.text    Button text
  primary_cta.url     Button link URL
  primary_cta.target  "_blank" to open in new tab (optional)

SECONDARY CTA
  secondary_cta.text    Button text
  secondary_cta.url     Button link URL
  secondary_cta.target  "_blank" to open in new tab (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "default" (centered solid background)
  max_width          Container width: sm|md|lg|xl|2xl (default: xl)
                 • "sm"  - 640px max width (narrow content)
                 • "md"  - 768px max width
                 • "lg"  - 1024px max width
                 • "xl"  - 1280px max width (default)
                 • "2xl" - 1536px max width (wide content)
  padding_y          Vertical padding in Tailwind units (default: 8)
                 • "4"  - 1rem (16px) - compact
                 • "8"  - 2rem (32px) - default
                 • "12" - 3rem (48px) - spacious
                 • "16" - 4rem (64px) - very spacious
  padding_y_lg       Large screen vertical padding (default: 16)
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
                 • "24" - 6rem (96px)

COLORS (DaisyUI names OR hex codes like "#0A0EA0")
  background_color   Section background color (default: base-200)
                 • "base-100" - lightest background
                 • "base-200" - default light gray
                 • "base-300" - darker gray
                 • "primary" - brand color background
                 • "neutral" - dark neutral
                 • "#0A0EA0" - custom hex color
  title_color        Heading text color (default: base-content)
                 • "base-content" - default text color
                 • "primary" - brand color
                 • "white" - for dark backgrounds
  text_color         Description text color (default: base-content/70)
                 • "base-content/70" - 70% opacity (default)
                 • "base-content/60" - lighter text
                 • "base-content" - full opacity
  badge_text_color   Badge text color (default: primary)
                 • DaisyUI color or hex code
  badge_bg           Badge background color (default: primary)
                 • Uses opacity: bg-{color}/10 automatically
                 • DaisyUI color or hex code

BUTTONS (colors can be DaisyUI names OR hex codes)
  primary_btn_color    Primary CTA button color (default: primary)
                   • "primary" - brand color
                   • "secondary" - secondary brand
                   • "accent" - accent color
                   • "#FF6C0E" - custom hex color
  primary_btn_style    Primary CTA button style (default: solid)
                   • "solid" - filled button (default)
                   • "outline" - outlined button
                   • "ghost" - transparent background
  secondary_btn_color  Secondary CTA button color (default: neutral)
  secondary_btn_style  Secondary CTA button style (default: outline)
                   • "outline" - outlined button (default)
                   • "ghost" - transparent background
                   • "solid" - filled button
  show_arrow           Show arrow icon on primary CTA (default: false)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple announcement:
{
  "title": "Welcome to Our Platform",
  "description": "Get started with our powerful tools today.",
  "primary_cta": {"text": "Get Started", "url": "/signup", "target": ""}
}

With badge and dual CTAs (secondary opens in new tab):
{
  "badge": "New Feature",
  "title": "Introducing AI Assistant",
  "description": "Let AI help you work smarter, not harder.",
  "primary_cta": {"text": "Try it Free", "url": "/trial", "target": ""},
  "secondary_cta": {"text": "Learn More", "url": "/features", "target": "_blank"}
}

Custom hex colors:
config: {
  "style": "default",
  "background_color": "#0A0EA0",
  "primary_btn_color": "#FF6C0E",
  "secondary_btn_color": "#3C8DDE",
  "show_arrow": true
}
""",
        "default_content": {
            "badge": "",
            "title": "We invest in the world's potential",
            "description": "Here we focus on markets where technology, innovation, and capital can unlock long-term value and drive economic growth.",
            "primary_cta": {"text": "Get started", "url": "#", "target": ""},
            "secondary_cta": {"text": "Learn more", "url": "#", "target": ""},
        },
        "default_config": {
            "style": "default",
            "max_width": "xl",
            "padding_y": "8",
            "padding_y_lg": "16",
            "background_color": "base-200",
            "title_color": "base-content",
            "text_color": "base-content/70",
            "badge_text_color": "primary",
            "badge_bg": "primary",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
            "secondary_btn_color": "neutral",
            "secondary_btn_style": "outline",
            "show_arrow": False,
        },
    },
    {
        "name": "Jumbotron - Background Image",
        "zone_type": ZoneType.JUMBOTRON,
        "template_file": "landing_pages/zones/jumbotron.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/jumbotron.html

Content section with background image and overlay for readability.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title              Main heading text (required)
description        Supporting paragraph text
badge              Optional badge above title
background_image   Background image URL (required)

PRIMARY CTA
  primary_cta.text    Button text
  primary_cta.url     Button link URL
  primary_cta.target  "_blank" to open in new tab (optional)

SECONDARY CTA
  secondary_cta.text    Button text
  secondary_cta.url     Button link URL
  secondary_cta.target  "_blank" to open in new tab (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "background-image" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl (default: xl)
                 • "lg"  - 1024px max width (focused)
                 • "xl"  - 1280px max width (default)
                 • "2xl" - 1536px max width (wide)
  padding_y          Vertical padding (default: 24)
                 • "16" - 4rem (64px) - compact
                 • "24" - 6rem (96px) - default
                 • "32" - 8rem (128px) - spacious
  padding_y_lg       Large screen padding (default: 32)
                 • "24" - 6rem (96px)
                 • "32" - 8rem (128px) - default
                 • "40" - 10rem (160px)

COLORS (DaisyUI names OR hex codes like "#404040")
  overlay_color      Overlay blend color for readability (default: gray-700)
                 • "gray-700" - medium dark overlay (default)
                 • "gray-800" - darker overlay
                 • "gray-900" - very dark overlay
                 • "black" - maximum darkness
                 • "primary" - brand color overlay
                 • "#404040" - custom hex color (dark gray)
                 • "#0A0EA0" - custom hex color (brand blue)
  text_color         Description text color (default: gray-300)
                 • "gray-300" - light gray (default)
                 • "gray-200" - lighter
                 • "white" - maximum contrast
  badge_text_color   Badge text color (default: white)
  badge_bg           Badge background color (default: primary)
                 • Uses opacity: bg-{color}/20 automatically

BUTTONS (colors can be DaisyUI names OR hex codes)
  primary_btn_color    Primary CTA button color (default: primary)
                   • "primary" - brand color
                   • "white" - white button
                   • "accent" - accent color
                   • "#FF6C0E" - custom hex color
  primary_btn_style    Primary CTA button style (default: solid)
                   • "solid" - filled button (default)
                   • "outline" - outlined button
                   • "ghost" - transparent background
  secondary_btn_color  Secondary CTA button color (default: white)
  secondary_btn_style  Secondary CTA button style (default: outline)
                   • "outline" - outlined (default)
                   • "ghost" - transparent
                   • "solid" - filled
  show_arrow           Show arrow icon on primary CTA (default: false)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Event promotion:
{
  "background_image": "https://example.com/conference.jpg",
  "badge": "June 2024",
  "title": "Annual Developer Conference",
  "description": "Join 5,000+ developers for 3 days of learning.",
  "primary_cta": {"text": "Register Now", "url": "/register", "target": ""},
  "secondary_cta": {"text": "View Schedule", "url": "/schedule", "target": "_blank"}
}
config: {"style": "background-image", "overlay_color": "gray-900"}

Product launch with hex overlay color:
{
  "background_image": "https://example.com/product.jpg",
  "title": "Introducing Our New Product",
  "primary_cta": {"text": "Pre-order Now", "url": "/preorder", "target": ""}
}
config: {
  "style": "background-image",
  "overlay_color": "#0A0EA0",
  "primary_btn_color": "#FF6C0E",
  "show_arrow": true
}
""",
        "default_content": {
            "badge": "",
            "background_image": "https://flowbite.s3.amazonaws.com/docs/jumbotron/conference.jpg",
            "title": "We didn't reinvent the wheel",
            "description": "We are strategists, designers and developers. Innovators and problem solvers. Small enough to be simple and quick, but big enough to deliver.",
            "primary_cta": {"text": "Get started", "url": "#", "target": ""},
            "secondary_cta": {"text": "Learn more", "url": "#", "target": ""},
        },
        "default_config": {
            "style": "background-image",
            "max_width": "xl",
            "padding_y": "24",
            "padding_y_lg": "32",
            "overlay_color": "gray-700",
            "text_color": "gray-300",
            "badge_text_color": "white",
            "badge_bg": "primary",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
            "secondary_btn_color": "white",
            "secondary_btn_style": "outline",
            "show_arrow": False,
        },
    },
    {
        "name": "Jumbotron - Video",
        "zone_type": ZoneType.JUMBOTRON,
        "template_file": "landing_pages/zones/jumbotron.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/jumbotron.html

Two-column layout with content and embedded video.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Main heading text (required)
description     Supporting paragraph text
badge           Optional badge above title

VIDEO SOURCE (choose one)
  video_type       "youtube", "vimeo", or "self" (self-hosted)
               • "youtube" - Embed YouTube video
               • "vimeo" - Embed Vimeo video
               • "self" - Self-hosted video file
  video_id         YouTube/Vimeo video ID (for youtube/vimeo types)
               • YouTube: the part after "v=" in URL
               • Vimeo: the numeric ID from URL
  video_url        Direct video URL (for self-hosted only)
  poster           Poster image URL (for self-hosted only)

PRIMARY CTA
  primary_cta.text    Button text
  primary_cta.url     Button link URL
  primary_cta.target  "_blank" to open in new tab (optional)

SECONDARY CTA
  secondary_cta.text    Button text
  secondary_cta.url     Button link URL
  secondary_cta.target  "_blank" to open in new tab (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "video" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl (default: xl)
                 • "lg"  - 1024px (compact)
                 • "xl"  - 1280px (default)
                 • "2xl" - 1536px (wide)
  video_first        Put video on left side (default: false)
                 • false - text left, video right (default)
                 • true or "left" - video left, text right
  padding_y          Vertical padding (default: 8)
                 • "4"  - 1rem (16px) - compact
                 • "8"  - 2rem (32px) - default
                 • "12" - 3rem (48px) - spacious
  padding_y_lg       Large screen padding (default: 16)
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)

COLORS (DaisyUI names OR hex codes like "#0A0EA0")
  background_color   Section background color (default: base-200)
                 • "base-100" - lightest
                 • "base-200" - default
                 • "base-300" - darker
                 • "neutral" - dark theme
                 • "#0A0EA0" - custom hex color
  title_color        Heading text color (default: base-content)
                 • "base-content" - default
                 • "primary" - brand color
                 • "white" - for dark backgrounds
  text_color         Description text color (default: base-content/70)
                 • "base-content/70" - 70% opacity (default)
                 • "base-content/60" - lighter
  badge_text_color   Badge text color (default: primary)
  badge_bg           Badge background color (default: primary)

BUTTONS (colors can be DaisyUI names OR hex codes)
  primary_btn_color    Primary CTA button color (default: primary)
  primary_btn_style    Primary CTA button style (default: solid)
                   • "solid" - filled button (default)
                   • "outline" - outlined button
                   • "ghost" - transparent background
  secondary_btn_color  Secondary CTA button color (default: neutral)
  secondary_btn_style  Secondary CTA button style (default: ghost)
                   • "ghost" - transparent (default for video)
                   • "outline" - outlined
                   • "solid" - filled

VIDEO OPTIONS (work for YouTube, Vimeo, and self-hosted)
  autoplay           Auto-play video (default: false)
                 • false - user must click to play (default)
                 • true - auto-play (will be muted for browser policy)
  loop               Loop video continuously (default: false)
                 • Works for YouTube, Vimeo, and self-hosted
  controls           Show video controls (default: true)
                 • true - show play/pause/volume (default)
                 • false - hide controls (use with autoplay)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

YouTube video:
{
  "title": "See Our Platform in Action",
  "description": "Watch how teams use our tools to collaborate.",
  "video_type": "youtube",
  "video_id": "dQw4w9WgXcQ",
  "primary_cta": {"text": "Start Free Trial", "url": "/trial", "target": ""},
  "secondary_cta": {"text": "Watch More", "url": "/videos", "target": "_blank"}
}
config: {"style": "video"}

Vimeo video with video first (CTA opens in new tab):
{
  "title": "Customer Success Stories",
  "description": "Hear from teams who transformed their workflow.",
  "video_type": "vimeo",
  "video_id": "123456789",
  "primary_cta": {"text": "Read Case Studies", "url": "/cases", "target": "_blank"}
}
config: {"style": "video", "video_first": true}

Self-hosted looping background:
{
  "title": "Product Demo",
  "video_type": "self",
  "video_url": "/media/demo.mp4",
  "poster": "/media/demo-poster.jpg"
}
config: {"style": "video", "autoplay": true, "loop": true, "controls": false}

Custom colors:
config: {
  "style": "video",
  "background_color": "#0A0EA0",
  "primary_btn_color": "#FF6C0E",
  "secondary_btn_color": "#3C8DDE"
}
""",
        "default_content": {
            "badge": "",
            "title": "We invest in the world's potential",
            "description": "Here at Flowbite we focus on markets where technology, innovation, and capital can unlock long-term value.",
            "video_type": "youtube",
            "video_id": "KaLxCiilHns",
            "video_url": "",
            "poster": "",
            "primary_cta": {"text": "Get started", "url": "#", "target": ""},
            "secondary_cta": {"text": "Learn more", "url": "#", "target": ""},
        },
        "default_config": {
            "style": "video",
            "max_width": "xl",
            "padding_y": "8",
            "padding_y_lg": "16",
            "video_first": False,
            "background_color": "base-200",
            "title_color": "base-content",
            "text_color": "base-content/70",
            "badge_text_color": "primary",
            "badge_bg": "primary",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
            "secondary_btn_color": "neutral",
            "secondary_btn_style": "ghost",
            "autoplay": False,
            "loop": False,
            "controls": True,
        },
    },
    # NOTE: "Jumbotron - Contact Form" and "Jumbotron - Gradient with Newsletter"
    # templates have been removed. See docs/landing.md for archived documentation.
    {
        "name": "Jumbotron - Cards Grid",
        "zone_type": ZoneType.JUMBOTRON,
        "template_file": "landing_pages/zones/jumbotron.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/jumbotron.html

Featured content card with grid of smaller cards below.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

FEATURED SECTION
  badge              Section badge above title (optional)
  title              Main heading (required)
  description        Supporting text
  featured_badge     Badge on featured card (e.g., "Featured", "New")
  featured_image     Featured card image URL (optional)
                     • Full URL: "https://example.com/img.jpg"
                     • Relative: "/media/images/featured.jpg"

  primary_cta.text   CTA button text
  primary_cta.url    CTA button URL
  primary_cta.target "_blank" to open in new tab (optional)

CARDS GRID
  cards              Array of card objects:
title            Card title (required)
description      Card description text
image            Card image URL (optional)
                 • Full URL: "https://example.com/img.jpg"
                 • Relative: "/media/images/card.jpg"
badge            Optional badge text on card
badge_color      Badge color - DaisyUI name OR hex code (default: ghost)
                 • "ghost" - subtle gray
                 • "primary" - brand color
                 • "#FF6C0E" - custom hex color

link.text        Link text (default: "Read more")
link.url         Link URL
link.target      "_blank" to open in new tab (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "cards" (REQUIRED for this template)
  title_tag          HTML tag for title: h1|h2|h3|h4|h5|h6 (default: h1)
  max_width          Container width: sm|md|lg|xl|2xl (default: xl)
                 • "lg"  - 1024px (compact)
                 • "xl"  - 1280px (default)
                 • "2xl" - 1536px (wide)
  padding_y          Vertical padding (default: 8)
                 • "4"  - 1rem (16px)
                 • "8"  - 2rem (32px) - default
                 • "12" - 3rem (48px)
  padding_y_lg       Large screen padding (default: 16)
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
  columns            Grid columns for cards (default: 2)
                 • "2" - two column grid (default)
                 • "3" - three column grid
                 • "4" - four column grid
  featured_centered  Center featured card content (default: false)
                 • false - left-aligned (default)
                 • true - centered text and button
  featured_image_height  Height for featured image (default: 64)
                 • "48" - 12rem (192px)
                 • "64" - 16rem (256px) - default
                 • "80" - 20rem (320px)
                 • "96" - 24rem (384px)

COLORS (DaisyUI names OR hex codes like "#0A0EA0")
  background_color   Section background color (default: base-200)
                 • "base-100" - lightest
                 • "base-200" - default light gray
                 • "base-300" - darker gray
                 • "#0A0EA0" - custom hex color
  text_color         Description text color (default: base-content/70)
                 • "#666666" - custom hex color
  badge_text_color   Section badge text color (default: primary)
  badge_bg           Section badge background color (default: primary)
  featured_bg        Featured card background (default: base-100)
                 • "base-100" - white/light (default)
                 • "#FFFFFF" - custom hex color
  card_bg            Grid cards background (default: base-100)
                 • "base-100" - white/light (default)
                 • "#F5F5F5" - custom hex color
  link_color         Card link color (default: primary)
                 • "primary" - brand color
                 • "#0A0EA0" - custom hex color
  featured_badge_color  Featured badge color (default: primary)
                    • DaisyUI badge colors OR hex codes

BUTTONS (colors can be DaisyUI names OR hex codes)
  primary_btn_color  Featured CTA button color (default: primary)
                 • "primary" - brand color
                 • "#FF6C0E" - custom hex color
  primary_btn_style  Featured CTA button style (default: solid)
                 • "solid" - filled button (default)
                 • "outline" - outlined button
                 • "ghost" - transparent background

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Blog/resource hub with featured image:
{
  "badge": "Resources",
  "featured_badge": "Featured",
  "featured_image": "https://example.com/blog-header.jpg",
  "title": "Latest from Our Blog",
  "description": "Insights, tutorials, and updates from our team.",
  "primary_cta": {"text": "View All Posts", "url": "/blog", "target": ""},
  "cards": [
{
  "image": "https://example.com/guide.jpg",
  "badge": "Tutorial",
  "title": "Getting Started Guide",
  "description": "Learn the basics in 10 minutes.",
  "link": {"text": "Read more", "url": "/docs/start", "target": "_blank"}
},
{
  "image": "https://example.com/tips.jpg",
  "badge": "Guide",
  "title": "Best Practices",
  "description": "Tips from power users.",
  "link": {"text": "Read more", "url": "/docs/tips"}
}
  ]
}
config: {"style": "cards", "featured_centered": true, "featured_image_height": "64", "primary_btn_color": "#FF6C0E"}

Four-column grid with custom colors:
{
  "title": "Our Services",
  "cards": [
{"image": "/media/dev.jpg", "title": "Development", "link": {"url": "/dev"}},
{"image": "/media/design.jpg", "title": "Design", "link": {"url": "/design"}},
{"image": "/media/marketing.jpg", "title": "Marketing", "link": {"url": "/marketing"}},
{"image": "/media/support.jpg", "title": "Support", "link": {"url": "/support"}}
  ]
}
config: {
  "style": "cards",
  "columns": "4",
  "featured_image_height": "48",
  "background_color": "#0A0EA0",
  "featured_bg": "#FFFFFF",
  "card_bg": "#F8F8F8",
  "link_color": "#3C8DDE"
}
""",
        "default_content": {
            "badge": "",
            "featured_badge": "Tutorial",
            "featured_image": "",
            "title": "How to quickly deploy a static website",
            "description": "Learn how to deploy your static website in minutes using our platform. This step-by-step guide covers everything you need to know.",
            "primary_cta": {"text": "Read more", "url": "#", "target": ""},
            "cards": [
                {
                    "image": "",
                    "badge": "Article",
                    "badge_color": "ghost",
                    "title": "Our first project with React",
                    "description": "A deep dive into building scalable applications with React and modern tooling.",
                    "link": {"text": "Read more", "url": "#", "target": ""},
                },
                {
                    "image": "",
                    "badge": "Guide",
                    "badge_color": "ghost",
                    "title": "Enterprise design systems",
                    "description": "How to create and maintain design systems at scale for large organizations.",
                    "link": {"text": "Read more", "url": "#", "target": ""},
                },
            ],
        },
        "default_config": {
            "style": "cards",
            "title_tag": "h1",
            "max_width": "xl",
            "padding_y": "8",
            "padding_y_lg": "16",
            "columns": "2",
            "featured_centered": True,
            "featured_image_height": "64",
            "background_color": "base-200",
            "text_color": "base-content/70",
            "badge_text_color": "primary",
            "badge_bg": "primary",
            "featured_bg": "base-100",
            "card_bg": "base-100",
            "link_color": "primary",
            "featured_badge_color": "primary",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
