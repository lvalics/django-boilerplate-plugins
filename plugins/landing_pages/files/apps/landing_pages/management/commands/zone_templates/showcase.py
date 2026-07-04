"""
Showcase zone templates.
"""

from ._base import ZoneType

SHOWCASE_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Showcase - Product Specs",
        "zone_type": ZoneType.SHOWCASE,
        "template_file": "landing_pages/zones/showcase.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/showcase.html

Full-width product showcase with background image, title, and specification stats.
Includes scroll-based animations for image scale and text fade-in effects.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

IMAGE
  image            Background image URL (required)
             • Full URL: "https://example.com/product-hero.jpg"
             • Relative: "/media/images/product.jpg"
  image_alt        Alt text for accessibility (default: uses title)

TITLE
  title            Main heading text (supports HTML like <br>)
             • "Optimized for Your <br> Desk Setup"
             • "The Future of <br> Professional Displays"
  subtitle         Optional description text below title

SPECS
  specs[]          Array of specification items:
├─ value         The stat value (e.g., "27\"", "4K", "144Hz")
└─ label         The stat label (e.g., "Screen Size", "Resolution")

CTA
  cta.text         Button text
  cta.url          Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  min_height         Section minimum height
             • "600px" - fixed pixel height (default)
             • "100vh" - full viewport height
             • "80vh" - 80% viewport height
             • "500px" - compact height
  padding_y          Vertical padding in Tailwind units (default: 20)
             • "12" - 3rem (48px) - compact
             • "16" - 4rem (64px) - moderate
             • "20" - 5rem (80px) - default
             • "24" - 6rem (96px) - spacious
  background_color   Fallback background color (default: black)
             • "black" - pure black (default)
             • "neutral" - dark neutral
             • "gray-900" - dark gray
             • "slate-900" - dark slate
             • "zinc-900" - dark zinc
  content_position   Flex justify content (default: center)
             • "start" - content at top
             • "center" - content centered (default)
             • "end" - content at bottom
  animate            Enable scroll animations (default: true)
             • true - enable image scale and text animations
             • "false" - disable animations (use string "false")

IMAGE
  object_fit         Image fit mode (default: cover)
             • "cover" - fill area, crop if needed (default)
             • "contain" - fit entire image, may letterbox
  object_position    Image focal point (default: center)
             • "center" - center the image (default)
             • "top" - align to top edge
             • "bottom" - align to bottom edge
             • "left" - align to left edge
             • "right" - align to right edge
  initial_scale      Initial transform scale for animation (default: 0.9)
             • "0.9" - slightly zoomed out, scales up on scroll
             • "1" - no initial scale
             • "0.8" - more zoomed out start
             • "1.1" - slightly zoomed in start

VIGNETTE
  vignette           Enable radial gradient vignette (default: true)
             • true - add vignette effect (default)
             • false - no vignette
  vignette_size      Transparent area percentage (default: 70)
             • "60" - smaller transparent area, more vignette
             • "70" - balanced vignette (default)
             • "80" - larger transparent area, subtle vignette
             • "50" - strong vignette effect
  vignette_color     Edge color for vignette (default: rgb(0, 0, 0))
             • "rgb(0, 0, 0)" - black vignette (default)
             • "rgba(0, 0, 0, 0.8)" - semi-transparent black
             • "rgb(23, 23, 23)" - dark gray vignette

OVERLAY
  overlay            Enable flat color overlay (default: false)
             • false - no overlay (default)
             • true - add overlay for text readability
  overlay_color      Overlay color (default: black)
             • "black" - black overlay (default)
             • "gray-900" - dark gray overlay
             • "neutral" - neutral overlay
  overlay_opacity    Overlay opacity 0-100 (default: 30)
             • "20" - subtle overlay
             • "30" - light overlay (default)
             • "50" - medium overlay
             • "70" - heavy overlay

TITLE STYLING
  title_position     Vertical position of title (default: center)
             • "top" - title at top with padding
             • "center" - title vertically centered (default)
             • "bottom" - title at bottom with padding
  title_size         Base title size (default: 4xl)
             • "3xl" - smaller title
             • "4xl" - medium title (default)
             • "5xl" - large title
  title_size_md      Title size on medium screens (default: 5xl)
             • "4xl" - smaller on tablets
             • "5xl" - medium on tablets (default)
             • "6xl" - larger on tablets
  title_size_lg      Title size on large screens (default: 6xl)
             • "5xl" - moderate on desktop
             • "6xl" - large on desktop (default)
             • "7xl" - extra large on desktop
  title_weight       Font weight for title (default: bold)
             • "bold" - bold weight (default)
             • "extrabold" - extra bold
             • "semibold" - semi bold
             • "black" - heaviest weight
  title_color        Title text color (default: white)
             • "white" - white text (default)
             • "gray-100" - off-white
             • "primary" - brand color
  subtitle_size      Subtitle text size (default: xl)
             • "lg" - smaller subtitle
             • "xl" - medium subtitle (default)
             • "2xl" - larger subtitle
  subtitle_color     Subtitle text color (default: white/80)
             • "white/80" - 80% white (default)
             • "white/70" - 70% white
             • "gray-300" - light gray

SPECS STYLING
  specs_position     Position of specs row (default: inline)
             • "bottom" - push specs to bottom of container
             • omit - specs flow with content
  specs_gap          Gap between specs on mobile (default: 8)
             • "4" - tight spacing
             • "8" - default spacing
             • "12" - wider spacing
  specs_gap_md       Gap between specs on tablet/desktop (default: 16)
             • "12" - moderate spacing
             • "16" - default spacing
             • "20" - wide spacing
  value_size         Spec value size on mobile (default: 3xl)
             • "2xl" - smaller values
             • "3xl" - default values
             • "4xl" - larger values
  value_size_md      Spec value size on tablet/desktop (default: 5xl)
             • "4xl" - moderate values
             • "5xl" - default values
             • "6xl" - large values
  value_weight       Spec value font weight (default: bold)
             • "bold" - bold weight (default)
             • "extrabold" - extra bold
             • "semibold" - semi bold
  value_color        Spec value text color (default: white)
             • "white" - white text (default)
             • "gray-100" - off-white
             • "primary" - brand color
  label_size         Spec label size (default: sm)
             • "xs" - smaller labels
             • "sm" - default labels
             • "base" - larger labels
  label_color        Spec label text color (default: white/70)
             • "white/70" - 70% white (default)
             • "white/60" - 60% white
             • "gray-400" - gray labels

CTA BUTTON
  cta_style          Button style (default: primary)
             • "primary" - primary brand button (default)
             • "secondary" - secondary brand button
             • "accent" - accent color button
             • "neutral" - neutral button
             • "ghost" - ghost/transparent button
  cta_size           Button size
             • "sm" - small button
             • "md" - medium button
             • "lg" - large button
             • omit - default button size
  cta_outline        Use outline style (default: false)
             • false - solid button (default)
             • true - outline button

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Product specs showcase (default):
{
  "image": "https://example.com/product-hero.jpg",
  "title": "Optimized for Your <br> Desk Setup",
  "specs": [
    {"value": "27\\"", "label": "Screen Size"},
    {"value": "4K", "label": "Resolution"},
    {"value": "144Hz", "label": "Refresh Rate"}
  ]
}
config: {"min_height": "600px", "vignette": true, "specs_position": "bottom"}

Full-screen hero with CTA:
{
  "image": "/media/hero-background.jpg",
  "title": "The Future of <br> Professional Displays",
  "subtitle": "Experience color like never before",
  "cta": {"text": "Learn More", "url": "/products"}
}
config: {"min_height": "100vh", "title_position": "center", "overlay": true}

Minimal with overlay:
{
  "image": "/media/product-shot.jpg",
  "title": "Studio Pro X",
  "specs": [
    {"value": "32\\"", "label": "Display"},
    {"value": "HDR", "label": "Technology"}
  ]
}
config: {
  "min_height": "80vh",
  "vignette": false,
  "overlay": true,
  "overlay_opacity": "40",
  "specs_position": "bottom"
}

Compact showcase without animation:
{
  "image": "/media/product-compact.jpg",
  "title": "Performance Redefined"
}
config: {
  "min_height": "500px",
  "animate": "false",
  "title_position": "top",
  "vignette": true
}

Dark theme with strong vignette:
config: {
  "min_height": "600px",
  "background_color": "black",
  "vignette": true,
  "vignette_size": "50",
  "title_color": "white",
  "value_color": "white",
  "label_color": "white/60"
}
""",
        "default_content": {
            "image": "https://www.huion.com/statics/hw/site/img/kamvas-pro27144hz/images/kamvas-pro27144hz-setup-pic.jpg",
            "image_alt": "Product Showcase",
            "title": "Optimized for Your <br> Desk Setup",
            "subtitle": "",
            "specs": [
                {"value": '27"', "label": "Screen Size"},
                {"value": "4K", "label": "Resolution"},
                {"value": "144Hz", "label": "Refresh Rate"},
                {"value": "1B", "label": "Colors"},
            ],
            "cta": {"text": "", "url": ""},
        },
        "default_config": {
            "min_height": "600px",
            "padding_y": "20",
            "background_color": "black",
            "content_position": "center",
            "animate": True,
            "object_fit": "cover",
            "object_position": "center",
            "initial_scale": "0.9",
            "vignette": True,
            "vignette_size": "70",
            "vignette_color": "rgb(0, 0, 0)",
            "overlay": False,
            "overlay_color": "black",
            "overlay_opacity": "30",
            "title_position": "center",
            "title_size": "4xl",
            "title_size_md": "5xl",
            "title_size_lg": "6xl",
            "title_weight": "bold",
            "title_color": "white",
            "subtitle_size": "xl",
            "subtitle_color": "white/80",
            "specs_position": "bottom",
            "specs_gap": "8",
            "specs_gap_md": "16",
            "value_size": "3xl",
            "value_size_md": "5xl",
            "value_weight": "bold",
            "value_color": "white",
            "label_size": "sm",
            "label_color": "white/70",
            "cta_style": "primary",
            "cta_size": "",
            "cta_outline": False,
        },
    },
    {
        "name": "Showcase - Full Screen Hero",
        "zone_type": ZoneType.SHOWCASE,
        "template_file": "landing_pages/zones/showcase.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/showcase.html

Full viewport height showcase with centered content and CTA button.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

IMAGE
  image            Background image URL (required)
  image_alt        Alt text for accessibility

TITLE
  title            Main heading text (supports HTML like <br>)
  subtitle         Description text below title

CTA
  cta.text         Button text
  cta.url          Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

See "Showcase - Product Specs" for full config option documentation.

Key differences from default:
  min_height       Set to "100vh" for full viewport
  overlay          Enabled for better text readability
  cta_style        Primary button for prominent CTA

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Landing page hero:
{
  "image": "/media/hero-bg.jpg",
  "title": "Transform Your Workflow",
  "subtitle": "The all-in-one platform for creative professionals",
  "cta": {"text": "Get Started Free", "url": "/signup"}
}

Event announcement:
{
  "image": "/media/conference-bg.jpg",
  "title": "DevCon 2025",
  "subtitle": "Join thousands of developers for 3 days of innovation",
  "cta": {"text": "Register Now", "url": "/register"}
}
config: {"overlay_opacity": "50", "cta_style": "accent"}

Product launch with specs:
{
  "image": "/media/product-launch.jpg",
  "title": "Introducing <br> Studio Pro Max",
  "subtitle": "Our most powerful display yet",
  "specs": [
    {"value": "8K", "label": "Resolution"},
    {"value": "120Hz", "label": "Refresh Rate"}
  ],
  "cta": {"text": "Pre-order Now", "url": "/pre-order"}
}
""",
        "default_content": {
            "image": "https://images.unsplash.com/photo-1517134191118-9d595e4c8c2b?w=1920",
            "image_alt": "Full Screen Hero",
            "title": "Transform Your <br> Creative Workflow",
            "subtitle": "The all-in-one platform for designers and developers",
            "specs": [],
            "cta": {"text": "Get Started", "url": "#"},
        },
        "default_config": {
            "min_height": "100vh",
            "padding_y": "24",
            "background_color": "black",
            "content_position": "center",
            "animate": True,
            "object_fit": "cover",
            "object_position": "center",
            "initial_scale": "0.9",
            "vignette": True,
            "vignette_size": "60",
            "vignette_color": "rgb(0, 0, 0)",
            "overlay": True,
            "overlay_color": "black",
            "overlay_opacity": "40",
            "title_position": "center",
            "title_size": "4xl",
            "title_size_md": "6xl",
            "title_size_lg": "7xl",
            "title_weight": "bold",
            "title_color": "white",
            "subtitle_size": "xl",
            "subtitle_color": "white/80",
            "specs_position": "bottom",
            "specs_gap": "8",
            "specs_gap_md": "16",
            "value_size": "3xl",
            "value_size_md": "5xl",
            "value_weight": "bold",
            "value_color": "white",
            "label_size": "sm",
            "label_color": "white/70",
            "cta_style": "primary",
            "cta_size": "lg",
            "cta_outline": False,
        },
    },
    {
        "name": "Showcase - Minimal",
        "zone_type": ZoneType.SHOWCASE,
        "template_file": "landing_pages/zones/showcase.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/showcase.html

Clean, minimal showcase with title positioned at top. No specs or animations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

IMAGE
  image            Background image URL (required)
  image_alt        Alt text for accessibility

TITLE
  title            Main heading text
  subtitle         Optional description text

CTA
  cta.text         Button text (optional)
  cta.url          Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

See "Showcase - Product Specs" for full config option documentation.

Key differences from default:
  animate          Disabled for static presentation
  title_position   Set to "top" for header-style layout
  vignette         Disabled for clean look
  overlay          Optional light overlay

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Brand showcase:
{
  "image": "/media/brand-hero.jpg",
  "title": "Premium Quality",
  "subtitle": "Crafted with care"
}

Portfolio piece:
{
  "image": "/media/project-hero.jpg",
  "title": "Project Nebula"
}
config: {"overlay": true, "overlay_opacity": "20"}

Product category:
{
  "image": "/media/category-bg.jpg",
  "title": "Professional Series",
  "cta": {"text": "View Collection", "url": "/products/pro"}
}
config: {"cta_outline": true, "cta_style": "neutral"}
""",
        "default_content": {
            "image": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920",
            "image_alt": "Minimal Showcase",
            "title": "Premium Quality",
            "subtitle": "",
            "specs": [],
            "cta": {"text": "", "url": ""},
        },
        "default_config": {
            "min_height": "500px",
            "padding_y": "16",
            "background_color": "black",
            "content_position": "start",
            "animate": False,
            "object_fit": "cover",
            "object_position": "center",
            "initial_scale": "1",
            "vignette": False,
            "vignette_size": "70",
            "vignette_color": "rgb(0, 0, 0)",
            "overlay": True,
            "overlay_color": "black",
            "overlay_opacity": "20",
            "title_position": "top",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_size_lg": "5xl",
            "title_weight": "bold",
            "title_color": "white",
            "subtitle_size": "lg",
            "subtitle_color": "white/70",
            "specs_position": "",
            "specs_gap": "8",
            "specs_gap_md": "16",
            "value_size": "3xl",
            "value_size_md": "5xl",
            "value_weight": "bold",
            "value_color": "white",
            "label_size": "sm",
            "label_color": "white/70",
            "cta_style": "ghost",
            "cta_size": "",
            "cta_outline": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
