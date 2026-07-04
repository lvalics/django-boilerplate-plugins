"""
Video zone templates.
"""

from ._base import ZoneType

VIDEO_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Video - Self Hosted",
        "zone_type": ZoneType.VIDEO,
        "template_file": "landing_pages/zones/video.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/video.html

Self-hosted video player with full control options.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title              Section heading text (optional)
subtitle           Description text below title (optional)
caption            Text displayed below the video (optional)

VIDEO SOURCE
  source           "self" for self-hosted video (default)
  video_url        Video file URL (required, MP4 recommended)
               • "/media/videos/demo.mp4"
               • "https://example.com/video.mp4"
  video_url_webm   Optional WebM fallback URL for browser compatibility
               • "/media/videos/demo.webm"
  video_type       MIME type of primary video (default: video/mp4)
               • "video/mp4" - most common format
               • "video/webm" - WebM format
               • "video/ogg" - Ogg format
  poster           Poster image URL shown before playback
               • "/media/images/video-poster.jpg"
               • "https://example.com/poster.jpg"

CTA BUTTON
  cta.text         Button text displayed below video
  cta.url          Button link URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  padding_y        Vertical padding in Tailwind units (default: 12)
               • "8"  - 2rem (32px) - compact
               • "12" - 3rem (48px) - default
               • "16" - 4rem (64px) - spacious
               • "20" - 5rem (80px) - very spacious
               • "24" - 6rem (96px) - maximum
  background_color Section background color (default: base-100)
               • "base-100" - lightest background (default)
               • "base-200" - light gray
               • "base-300" - darker gray
               • "neutral" - dark theme
               • "primary" - brand color background
  max_width        Section container max width
               • "4xl" - 56rem (896px)
               • "5xl" - 64rem (1024px)
               • "6xl" - 72rem (1152px)
               • "7xl" - 80rem (1280px)
  centered         Center video horizontally (default: true)
               • true - center within container (default)
               • false - left-aligned
  video_max_width  Maximum width of video container
               • "2xl" - 42rem (672px) - compact
               • "3xl" - 48rem (768px) - medium
               • "4xl" - 56rem (896px) - default
               • "5xl" - 64rem (1024px) - wide
               • "full" - full width

ASPECT RATIO
  aspect_ratio     Video aspect ratio (default: 16:9)
               • "16:9" - widescreen (default)
               • "4:3" - traditional
               • "1:1" - square
               • "21:9" - ultrawide/cinematic

VIDEO PLAYBACK
  autoplay         Auto-start video (default: false)
               • false - user must click to play (default)
               • true - auto-play (requires muted for most browsers)
  muted            Mute audio (default: false)
               • false - audio enabled (default)
               • true - muted (required for autoplay in most browsers)
  loop             Loop video continuously (default: false)
               • false - play once (default)
               • true - loop continuously
  controls         Show video player controls (default: true)
               • true - show play/pause/volume (default)
               • false - hide controls (use for background videos)
  playsinline      Play inline on mobile devices (default: false)
               • false - may go fullscreen on mobile
               • true - stay inline (good for background videos)
  preload          Video preload strategy (default: metadata)
               • "none" - don't preload
               • "metadata" - preload metadata only (default)
               • "auto" - preload entire video
  object_fit       How video fills container (default: cover)
               • "cover" - fill container, may crop (default)
               • "contain" - fit within container, may letterbox
               • "fill" - stretch to fill exactly

STYLING
  rounded          Border radius (default: none)
               • "lg" - 0.5rem (8px)
               • "xl" - 0.75rem (12px)
               • "2xl" - 1rem (16px)
               • "3xl" - 1.5rem (24px)
               • "full" - fully rounded
  shadow           Box shadow (default: none)
               • "sm" - subtle shadow
               • "md" - medium shadow
               • "lg" - larger shadow
               • "xl" - prominent shadow (default for styled)
               • "2xl" - dramatic shadow
  border           Show border around video (default: false)
               • false - no border (default)
               • true - show border
  border_color     Border color when border is enabled (default: base-300)
               • "base-300" - subtle gray (default)
               • "base-200" - lighter gray
               • "primary" - brand color border
  ring             Ring highlight width (default: none)
               • "1" - thin ring
               • "2" - medium ring
               • "4" - thick ring
  ring_color       Ring color (default: primary)
               • "primary" - brand color (default)
               • "secondary" - secondary brand
               • "accent" - accent color
  ring_offset      Ring offset spacing (default: 2)
               • "1" - 1px offset
               • "2" - 2px offset (default)
               • "4" - 4px offset

CTA BUTTON
  cta_color        CTA button color (default: primary)
               • "primary" - brand color (default)
               • "secondary" - secondary brand
               • "accent" - accent color
               • "neutral" - neutral gray
  cta_size         CTA button size (default: none/medium)
               • "sm" - small button
               • "md" - medium button
               • "lg" - large button

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Product demo with title and CTA:
{
  "source": "self",
  "video_url": "/media/videos/demo.mp4",
  "poster": "/media/images/demo-poster.jpg",
  "title": "See It In Action",
  "subtitle": "Watch how our platform works",
  "caption": "2 minute product demonstration",
  "cta": {"text": "Start Free Trial", "url": "/signup"}
}
config: {"controls": true, "rounded": "xl", "shadow": "lg"}

Background video (autoplay, muted, looping):
{
  "source": "self",
  "video_url": "/media/videos/background.mp4"
}
config: {
  "autoplay": true,
  "muted": true,
  "loop": true,
  "controls": false,
  "playsinline": true,
  "video_max_width": "full"
}

Minimal centered video:
{
  "source": "self",
  "video_url": "/media/videos/intro.mp4",
  "title": "Introduction"
}
config: {"centered": true, "video_max_width": "3xl", "shadow": "md"}

Dark theme with ring highlight:
config: {
  "background_color": "neutral",
  "rounded": "2xl",
  "ring": "2",
  "ring_color": "primary",
  "ring_offset": "4"
}
""",
        "default_content": {
            "source": "self",
            "video_url": "https://flowbite.com/docs/videos/flowbite.mp4",
            "video_url_webm": "",
            "video_type": "video/mp4",
            "poster": "",
            "title": "See It In Action",
            "subtitle": "Watch how our platform works",
            "caption": "Product demonstration video",
            "cta": {"text": "", "url": ""},
        },
        "default_config": {
            "padding_y": "12",
            "background_color": "base-100",
            "centered": True,
            "video_max_width": "4xl",
            "aspect_ratio": "16:9",
            "autoplay": False,
            "muted": False,
            "loop": False,
            "controls": True,
            "playsinline": False,
            "preload": "metadata",
            "object_fit": "cover",
            "rounded": "lg",
            "shadow": "xl",
        },
    },
    {
        "name": "Video - YouTube Embed",
        "zone_type": ZoneType.VIDEO,
        "template_file": "landing_pages/zones/video.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/video.html

Embedded YouTube video player with section styling.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title              Section heading text (optional)
subtitle           Description text below title (optional)
caption            Text displayed below the video (optional)

VIDEO SOURCE
  source           "youtube" (required for YouTube embed)
  video_id         YouTube video ID (required)
               • Extract from URL: youtube.com/watch?v=VIDEO_ID
               • Example: "dQw4w9WgXcQ"
               • From shortened URL: youtu.be/VIDEO_ID

CTA BUTTON
  cta.text         Button text displayed below video
  cta.url          Button link URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  padding_y        Vertical padding in Tailwind units (default: 12)
               • "8"  - 2rem (32px) - compact
               • "12" - 3rem (48px) - default
               • "16" - 4rem (64px) - spacious
               • "20" - 5rem (80px) - very spacious
               • "24" - 6rem (96px) - maximum
  background_color Section background color (default: base-100)
               • "base-100" - lightest background (default)
               • "base-200" - light gray
               • "base-300" - darker gray
               • "neutral" - dark theme
               • "primary" - brand color background
  max_width        Section container max width
               • "4xl" - 56rem (896px)
               • "5xl" - 64rem (1024px)
               • "6xl" - 72rem (1152px)
               • "7xl" - 80rem (1280px)
  centered         Center video horizontally (default: true)
               • true - center within container (default)
               • false - left-aligned
  video_max_width  Maximum width of video container
               • "2xl" - 42rem (672px) - compact
               • "3xl" - 48rem (768px) - medium
               • "4xl" - 56rem (896px) - default
               • "5xl" - 64rem (1024px) - wide
               • "full" - full width

ASPECT RATIO
  aspect_ratio     Video aspect ratio (default: 16:9)
               • "16:9" - widescreen (default)
               • "4:3" - traditional
               • "1:1" - square
               • "21:9" - ultrawide/cinematic

VIDEO PLAYBACK
  autoplay         Auto-start video (default: false)
               • false - user must click to play (default)
               • true - auto-play (will be muted automatically)
  loop             Loop video continuously (default: false)
               • false - play once (default)
               • true - loop continuously
  controls         Show YouTube player controls (default: true)
               • true - show full YouTube controls (default)
               • false - hide controls
  start            Start time in seconds (default: none)
               • 0 - start from beginning
               • 30 - start at 30 seconds
               • 120 - start at 2 minutes

STYLING
  rounded          Border radius (default: none)
               • "lg" - 0.5rem (8px)
               • "xl" - 0.75rem (12px)
               • "2xl" - 1rem (16px)
               • "3xl" - 1.5rem (24px)
  shadow           Box shadow (default: none)
               • "sm" - subtle shadow
               • "md" - medium shadow
               • "lg" - larger shadow
               • "xl" - prominent shadow (default for styled)
               • "2xl" - dramatic shadow
  border           Show border around video (default: false)
               • false - no border (default)
               • true - show border
  border_color     Border color when border is enabled (default: base-300)
               • "base-300" - subtle gray (default)
               • "base-200" - lighter gray
               • "primary" - brand color border
  ring             Ring highlight width (default: none)
               • "1" - thin ring
               • "2" - medium ring
               • "4" - thick ring
  ring_color       Ring color (default: primary)
               • "primary" - brand color (default)
               • "secondary" - secondary brand
               • "accent" - accent color
  ring_offset      Ring offset spacing (default: 2)
               • "1" - 1px offset
               • "2" - 2px offset (default)
               • "4" - 4px offset

CTA BUTTON
  cta_color        CTA button color (default: primary)
               • "primary" - brand color (default)
               • "secondary" - secondary brand
               • "accent" - accent color
               • "neutral" - neutral gray
  cta_size         CTA button size (default: none/medium)
               • "sm" - small button
               • "md" - medium button
               • "lg" - large button

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple YouTube embed:
{
  "source": "youtube",
  "video_id": "dQw4w9WgXcQ",
  "title": "Watch Our Story"
}
config: {"controls": true, "rounded": "lg", "shadow": "xl"}

Tutorial video starting at specific time:
{
  "source": "youtube",
  "video_id": "ABC123xyz",
  "title": "Quick Start Tutorial",
  "subtitle": "Learn the basics in under 5 minutes",
  "caption": "Part 1 of our getting started series"
}
config: {"start": 45, "video_max_width": "3xl"}

Looping promotional video:
{
  "source": "youtube",
  "video_id": "XYZ789abc",
  "title": "Product Highlights"
}
config: {"autoplay": true, "loop": true, "controls": false}

Video with CTA on dark background:
{
  "source": "youtube",
  "video_id": "demo123",
  "title": "See It In Action",
  "cta": {"text": "Start Free Trial", "url": "/signup"}
}
config: {
  "background_color": "neutral",
  "rounded": "xl",
  "shadow": "2xl",
  "cta_color": "primary",
  "cta_size": "lg"
}

Wide cinematic presentation:
{
  "source": "youtube",
  "video_id": "film456"
}
config: {
  "aspect_ratio": "21:9",
  "video_max_width": "5xl",
  "rounded": "2xl"
}
""",
        "default_content": {
            "source": "youtube",
            "video_id": "KaLxCiilHns",
            "title": "Watch Our Story",
            "subtitle": "Learn how we're changing the industry",
            "caption": "",
            "cta": {"text": "", "url": ""},
        },
        "default_config": {
            "padding_y": "12",
            "background_color": "base-100",
            "centered": True,
            "video_max_width": "4xl",
            "aspect_ratio": "16:9",
            "autoplay": False,
            "loop": False,
            "controls": True,
            "rounded": "lg",
            "shadow": "xl",
        },
    },
    {
        "name": "Video - Vimeo Embed",
        "zone_type": ZoneType.VIDEO,
        "template_file": "landing_pages/zones/video.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/video.html

Embedded Vimeo video player with section styling.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title              Section heading text (optional)
subtitle           Description text below title (optional)
caption            Text displayed below the video (optional)

VIDEO SOURCE
  source           "vimeo" (required for Vimeo embed)
  video_id         Vimeo video ID (required)
               • Extract from URL: vimeo.com/VIDEO_ID
               • Example: "123456789"
               • Numeric ID only

CTA BUTTON
  cta.text         Button text displayed below video
  cta.url          Button link URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  padding_y        Vertical padding in Tailwind units (default: 12)
               • "8"  - 2rem (32px) - compact
               • "12" - 3rem (48px) - default
               • "16" - 4rem (64px) - spacious
               • "20" - 5rem (80px) - very spacious
               • "24" - 6rem (96px) - maximum
  background_color Section background color (default: base-100)
               • "base-100" - lightest background (default)
               • "base-200" - light gray
               • "base-300" - darker gray
               • "neutral" - dark theme
               • "primary" - brand color background
  max_width        Section container max width
               • "4xl" - 56rem (896px)
               • "5xl" - 64rem (1024px)
               • "6xl" - 72rem (1152px)
               • "7xl" - 80rem (1280px)
  centered         Center video horizontally (default: true)
               • true - center within container (default)
               • false - left-aligned
  video_max_width  Maximum width of video container
               • "2xl" - 42rem (672px) - compact
               • "3xl" - 48rem (768px) - medium
               • "4xl" - 56rem (896px) - default
               • "5xl" - 64rem (1024px) - wide
               • "full" - full width

ASPECT RATIO
  aspect_ratio     Video aspect ratio (default: 16:9)
               • "16:9" - widescreen (default)
               • "4:3" - traditional
               • "1:1" - square
               • "21:9" - ultrawide/cinematic

VIDEO PLAYBACK
  autoplay         Auto-start video (default: false)
               • false - user must click to play (default)
               • true - auto-play (will be muted automatically)
  loop             Loop video continuously (default: false)
               • false - play once (default)
               • true - loop continuously
  controls         Show Vimeo player controls (default: true)
               • true - show full Vimeo controls (default)
               • false - hide controls

STYLING
  rounded          Border radius (default: none)
               • "lg" - 0.5rem (8px)
               • "xl" - 0.75rem (12px)
               • "2xl" - 1rem (16px)
               • "3xl" - 1.5rem (24px)
  shadow           Box shadow (default: none)
               • "sm" - subtle shadow
               • "md" - medium shadow
               • "lg" - larger shadow
               • "xl" - prominent shadow (default for styled)
               • "2xl" - dramatic shadow
  border           Show border around video (default: false)
               • false - no border (default)
               • true - show border
  border_color     Border color when border is enabled (default: base-300)
               • "base-300" - subtle gray (default)
               • "base-200" - lighter gray
               • "primary" - brand color border
  ring             Ring highlight width (default: none)
               • "1" - thin ring
               • "2" - medium ring
               • "4" - thick ring
  ring_color       Ring color (default: primary)
               • "primary" - brand color (default)
               • "secondary" - secondary brand
               • "accent" - accent color
  ring_offset      Ring offset spacing (default: 2)
               • "1" - 1px offset
               • "2" - 2px offset (default)
               • "4" - 4px offset

CTA BUTTON
  cta_color        CTA button color (default: primary)
               • "primary" - brand color (default)
               • "secondary" - secondary brand
               • "accent" - accent color
               • "neutral" - neutral gray
  cta_size         CTA button size (default: none/medium)
               • "sm" - small button
               • "md" - medium button
               • "lg" - large button

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple Vimeo embed:
{
  "source": "vimeo",
  "video_id": "123456789",
  "title": "Product Demo"
}
config: {"controls": true, "rounded": "lg", "shadow": "xl"}

Professional portfolio video:
{
  "source": "vimeo",
  "video_id": "987654321",
  "title": "Our Latest Work",
  "subtitle": "A showcase of recent projects",
  "caption": "Client: Example Corp, 2024"
}
config: {"video_max_width": "5xl", "rounded": "xl"}

Looping background video:
{
  "source": "vimeo",
  "video_id": "555666777"
}
config: {"autoplay": true, "loop": true, "controls": false}

Video with CTA:
{
  "source": "vimeo",
  "video_id": "111222333",
  "title": "Watch the Full Story",
  "cta": {"text": "Contact Us", "url": "/contact"}
}
config: {
  "rounded": "2xl",
  "shadow": "lg",
  "cta_color": "accent",
  "cta_size": "lg"
}

Centered compact video:
{
  "source": "vimeo",
  "video_id": "444555666",
  "title": "Quick Overview"
}
config: {
  "centered": true,
  "video_max_width": "2xl",
  "aspect_ratio": "4:3",
  "border": true,
  "border_color": "base-200"
}
""",
        "default_content": {
            "source": "vimeo",
            "video_id": "123456789",
            "title": "Product Demo",
            "subtitle": "See our platform in action",
            "caption": "",
            "cta": {"text": "", "url": ""},
        },
        "default_config": {
            "padding_y": "12",
            "background_color": "base-100",
            "centered": True,
            "video_max_width": "4xl",
            "aspect_ratio": "16:9",
            "autoplay": False,
            "loop": False,
            "controls": True,
            "rounded": "lg",
            "shadow": "xl",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
