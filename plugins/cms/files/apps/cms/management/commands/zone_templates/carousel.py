"""
Carousel zone templates.
"""

from ._base import ZoneType

CAROUSEL_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Carousel - Image Gallery",
        "zone_type": ZoneType.CAROUSEL,
        "template_file": "cms/zones/carousel.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/carousel.html

Multi-column scrollable image gallery with optional lightbox modal.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading above carousel (optional)
subtitle        Section subheading text (optional)

SLIDES ARRAY
  slides[]      Array of slide objects:
    image         Image URL (required for image slides)
                  - "https://example.com/photo.jpg"
                  - "/media/gallery/image.jpg"
    alt           Accessibility alt text for image
                  - "Product photo on white background"
                  - "Team members at conference"
    title         Overlay title text (optional)
                  - "Summer Collection"
                  - "Behind the Scenes"
    description   Overlay description text (optional)
                  - "Our latest product line"
                  - "A look at how we work"

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  columns           Number of visible columns (1-4)
                    - 1 = single-slide Flowbite carousel (fullwidth)
                    - 2 = two-column scrollable (default)
                    - 3 = three-column scrollable
                    - 4 = four-column scrollable (compact)
  height            Slide height in pixels
                    - 250 = compact gallery
                    - 350 = default height
                    - 450 = large slides
                    - 550 = extra large (hero-like)
  padding_y         Vertical section padding in Tailwind units
                    - "8"  = 2rem (32px) compact
                    - "16" = 4rem (64px) default
                    - "24" = 6rem (96px) spacious
  background_color  Section background color
                    - "base-100" = white/light (default)
                    - "base-200" = light gray
                    - "base-300" = darker gray
                    - "neutral" = dark background
                    - "primary" = brand color

APPEARANCE
  border_radius     Slide corner rounding
                    - "none" = sharp corners
                    - "sm" = small radius
                    - "md" = medium radius
                    - "lg" = default rounded
                    - "xl" = large radius
                    - "2xl" = extra large radius
  object_fit        How images fill the slide
                    - "cover" = fill and crop (default)
                    - "contain" = fit entire image
                    - "fill" = stretch to fill
                    - "none" = natural size
  overlay_opacity   Text overlay darkness (0-100)
                    - "0" = no overlay
                    - "30" = light overlay
                    - "40" = default overlay
                    - "60" = darker overlay
                    - "80" = very dark overlay

CONTROLS
  show_controls     Show prev/next navigation arrows
                    - true = show arrows (default)
                    - false = hide arrows

AUTO-SLIDE
  auto_slide        Enable automatic sliding
                    - true = auto-advance slides (default)
                    - false = manual navigation only
  auto_slide_interval  Milliseconds between slides
                    - 3000 = fast (3 seconds)
                    - 4000 = default (4 seconds)
                    - 5000 = slow (5 seconds)
                    - 7000 = very slow (7 seconds)

MODAL/LIGHTBOX
  enable_modal      Click slides to open fullscreen modal
                    - true = enable lightbox view
                    - false = no modal (default)
                    Note: Enables keyboard nav (arrow keys, Esc)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple image gallery (2 columns):
{
  "title": "Our Gallery",
  "slides": [
    {"image": "/img/photo1.jpg", "alt": "Photo 1"},
    {"image": "/img/photo2.jpg", "alt": "Photo 2"},
    {"image": "/img/photo3.jpg", "alt": "Photo 3"}
  ]
}
config: {"columns": 2, "height": 350, "enable_modal": true}

Three-column portfolio:
{
  "title": "Recent Projects",
  "subtitle": "Click to view full size",
  "slides": [
    {"image": "/img/project1.jpg", "title": "Project Alpha"},
    {"image": "/img/project2.jpg", "title": "Project Beta"},
    {"image": "/img/project3.jpg", "title": "Project Gamma"}
  ]
}
config: {"columns": 3, "height": 300, "enable_modal": true, "auto_slide": false}

Compact four-column grid:
config: {
  "columns": 4,
  "height": 250,
  "border_radius": "xl",
  "overlay_opacity": "50"
}

Dark theme gallery:
config: {
  "columns": 2,
  "height": 400,
  "background_color": "neutral",
  "padding_y": "24"
}
""",
        "default_content": {
            "title": "Gallery",
            "subtitle": "Browse our collection",
            "slides": [
                {
                    "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg",
                    "title": "Slide Title",
                    "description": "Slide description",
                    "alt": "Gallery image 1",
                },
                {
                    "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg",
                    "title": "",
                    "description": "",
                    "alt": "Gallery image 2",
                },
                {
                    "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg",
                    "title": "",
                    "description": "",
                    "alt": "Gallery image 3",
                },
            ],
        },
        "default_config": {
            "style": "slide",
            "columns": 2,
            "height": 350,
            "padding_y": "16",
            "background_color": "base-100",
            "border_radius": "lg",
            "object_fit": "cover",
            "overlay_opacity": "40",
            "show_controls": True,
            "auto_slide": True,
            "auto_slide_interval": 4000,
            "enable_modal": True,
        },
    },
    {
        "name": "Carousel - Video Gallery",
        "zone_type": ZoneType.CAROUSEL,
        "template_file": "cms/zones/carousel.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/carousel.html

Video and image carousel with lightbox modal for playback.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading above carousel (optional)
subtitle        Section subheading text (optional)

SLIDES ARRAY
  slides[]      Array of slide objects (can mix video and image):

  FOR VIDEO SLIDES:
    video         Video URL (mp4 format required)
                  - "https://cdn.example.com/demo.mp4"
                  - "/media/videos/intro.mp4"
    poster        Thumbnail image shown before play
                  - "https://cdn.example.com/demo-thumb.jpg"
                  - "/media/videos/intro-poster.jpg"
    title         Overlay/caption title (optional)
    description   Overlay/caption text (optional)

  FOR IMAGE SLIDES:
    image         Image URL
    title         Overlay/caption title (optional)
    description   Overlay/caption text (optional)
    alt           Accessibility alt text

NOTE: You can mix video and image slides in the same carousel.

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

VIDEO SETTINGS
  video_autoplay    Auto-play videos in carousel
                    - false = user clicks to play (default, recommended)
                    - true = auto-play (will be muted per browser policy)
  video_muted       Mute video audio
                    - true = muted (default, required for autoplay)
                    - false = audio enabled
  video_loop        Loop video continuously
                    - true = loop video (default)
                    - false = play once

LAYOUT
  columns           Number of visible columns (1-4)
                    - 2 = two-column (default, recommended for video)
                    - 3 = three-column
                    - 4 = four-column (compact)
  height            Slide height in pixels
                    - 300 = compact
                    - 400 = default for video
                    - 500 = large video display
  padding_y         Vertical section padding
                    - "8"  = 2rem (32px) compact
                    - "16" = 4rem (64px) default
                    - "24" = 6rem (96px) spacious
  background_color  Section background color
                    - "base-100" = white/light (default)
                    - "base-200" = light gray
                    - "neutral" = dark background

APPEARANCE
  border_radius     Slide corner rounding
                    - "lg" = default rounded
                    - "xl" = large radius
                    - "2xl" = extra large radius
  object_fit        How video/image fills the slide
                    - "cover" = fill and crop (default)
                    - "contain" = fit entire video
  overlay_opacity   Text overlay darkness (0-100)
                    - "40" = default overlay
                    - "50" = recommended for video
                    - "60" = darker overlay

CONTROLS
  show_controls     Show prev/next navigation arrows
                    - true = show arrows (default)
                    - false = hide arrows

AUTO-SLIDE
  auto_slide        Enable automatic sliding
                    - false = manual only (recommended for video)
                    - true = auto-advance slides
  auto_slide_interval  Milliseconds between slides
                    - 4000 = default (4 seconds)
                    - 6000 = slow (6 seconds)

MODAL/LIGHTBOX
  enable_modal      Click to open fullscreen modal
                    - true = enable lightbox (recommended for video)
                    - false = no modal
                    Note: Video plays with controls in modal

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Video showcase with modal:
{
  "title": "Video Gallery",
  "subtitle": "Click to watch",
  "slides": [
    {
      "video": "https://cdn.example.com/demo1.mp4",
      "poster": "https://cdn.example.com/demo1-thumb.jpg",
      "title": "Product Demo"
    },
    {
      "video": "https://cdn.example.com/demo2.mp4",
      "poster": "https://cdn.example.com/demo2-thumb.jpg",
      "title": "Tutorial"
    }
  ]
}
config: {"columns": 2, "height": 400, "enable_modal": true, "auto_slide": false}

Mixed video and images:
{
  "title": "Media Gallery",
  "slides": [
    {"video": "/media/intro.mp4", "poster": "/media/intro-thumb.jpg"},
    {"image": "/media/photo1.jpg", "alt": "Photo 1"},
    {"video": "/media/demo.mp4", "poster": "/media/demo-thumb.jpg"}
  ]
}
config: {"columns": 3, "enable_modal": true}

Auto-playing background videos (muted):
config: {
  "columns": 2,
  "video_autoplay": true,
  "video_muted": true,
  "video_loop": true,
  "auto_slide": false,
  "enable_modal": true
}

Dark theme video gallery:
config: {
  "columns": 2,
  "height": 450,
  "background_color": "neutral",
  "border_radius": "xl",
  "overlay_opacity": "50"
}
""",
        "default_content": {
            "title": "Video Gallery",
            "subtitle": "Click to play videos",
            "slides": [
                {
                    "video": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "poster": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-5.jpg",
                    "title": "Video Title",
                    "description": "Video description",
                },
                {
                    "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-6.jpg",
                    "title": "Image Title",
                    "description": "Mix images with videos",
                    "alt": "Gallery image",
                },
            ],
        },
        "default_config": {
            "style": "slide",
            "columns": 2,
            "height": 400,
            "padding_y": "16",
            "background_color": "base-100",
            "border_radius": "xl",
            "object_fit": "cover",
            "overlay_opacity": "50",
            "show_controls": True,
            "auto_slide": False,
            "auto_slide_interval": 4000,
            "enable_modal": True,
            "video_autoplay": False,
            "video_muted": True,
            "video_loop": True,
        },
    },
    {
        "name": "Carousel - Hero Slider",
        "zone_type": ZoneType.CAROUSEL,
        "template_file": "cms/zones/carousel.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/carousel.html

Full-width single-slide carousel with overlay content and CTA buttons.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading above carousel (optional)
subtitle        Section subheading text (optional)

SLIDES ARRAY
  slides[]      Array of slide objects:
    image         Background image URL (required)
                  - "https://example.com/hero.jpg"
                  - "/media/banners/slide1.jpg"
    alt           Accessibility alt text
                  - "Hero banner image"
    title         Large overlay heading
                  - "Welcome to Our Platform"
                  - "Summer Sale Now On"
    description   Overlay paragraph text
                  - "Start your journey today"
                  - "Up to 50% off selected items"
    cta_text      Call-to-action button text (optional)
                  - "Get Started"
                  - "Shop Now"
    cta_url       Call-to-action button URL
                  - "/signup"
                  - "/shop/sale"

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  columns           Must be 1 for hero slider mode
                    - 1 = single-slide fullwidth (required)
  height            Slide height in pixels
                    - 400 = compact hero
                    - 500 = default hero height
                    - 600 = large hero
                    - 700 = extra large hero
  max_width         Container max-width constraint
                    - "4xl" = 896px max
                    - "5xl" = 1024px max
                    - "6xl" = 1152px max
                    - "7xl" = 1280px max (default)
                    - "full" = no constraint
  padding_y         Vertical section padding
                    - "8"  = 2rem (32px) compact
                    - "16" = 4rem (64px) default
                    - "24" = 6rem (96px) spacious
  background_color  Section background color
                    - "base-100" = white/light
                    - "base-200" = light gray
                    - "neutral" = dark background

APPEARANCE
  border_radius     Slide corner rounding
                    - "none" = sharp corners
                    - "lg" = default rounded
                    - "xl" = large radius
                    - "2xl" = extra large radius
  object_fit        How images fill the slide
                    - "cover" = fill and crop (default)
                    - "contain" = fit entire image
  overlay_opacity   Text overlay darkness (0-100)
                    - "40" = light overlay
                    - "50" = default
                    - "60" = darker overlay
                    - "70" = dark overlay

CONTENT ALIGNMENT
  content_align_v   Vertical content alignment
                    - "start" = top
                    - "center" = middle (default)
                    - "end" = bottom
  content_align_h   Horizontal content alignment
                    - "start" = left
                    - "center" = center (default)
                    - "end" = right

CONTROLS
  show_controls     Show prev/next navigation arrows
                    - true = show arrows (default)
                    - false = hide arrows
  show_indicators   Show dot indicators at bottom
                    - true = show dots (default)
                    - false = hide dots

ANIMATION
  style             Slide transition type
                    - "slide" = sliding animation (default)
                    - "static" = instant switch
  transition_duration  Transition speed in milliseconds
                    - "500" = fast
                    - "700" = default
                    - "1000" = slow
                    - "1500" = very slow

AUTO-SLIDE
  auto_slide        Enable automatic sliding
                    - true = auto-advance (default)
                    - false = manual only
  auto_slide_interval  Milliseconds between slides
                    - 4000 = fast (4 seconds)
                    - 5000 = default (5 seconds)
                    - 7000 = slow (7 seconds)

BUTTON STYLE
  cta_style         CTA button style
                    - "primary" = brand color (default)
                    - "secondary" = secondary brand
                    - "accent" = accent color
                    - "neutral" = neutral button
                    - "ghost" = transparent button

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Standard hero slider:
{
  "slides": [
    {
      "image": "/img/hero1.jpg",
      "title": "Welcome to Our Platform",
      "description": "Build something amazing today",
      "cta_text": "Get Started",
      "cta_url": "/signup"
    },
    {
      "image": "/img/hero2.jpg",
      "title": "Powerful Features",
      "description": "Everything you need in one place",
      "cta_text": "Learn More",
      "cta_url": "/features"
    }
  ]
}
config: {"columns": 1, "height": 500, "overlay_opacity": "50"}

Tall hero with bottom-aligned content:
config: {
  "columns": 1,
  "height": 600,
  "content_align_v": "end",
  "content_align_h": "start",
  "overlay_opacity": "60"
}

Slow-transitioning promotional slider:
config: {
  "columns": 1,
  "height": 450,
  "transition_duration": "1000",
  "auto_slide_interval": 7000,
  "cta_style": "accent"
}

Minimal hero without controls:
config: {
  "columns": 1,
  "height": 500,
  "show_controls": false,
  "show_indicators": true,
  "border_radius": "none"
}
""",
        "default_content": {
            "title": "",
            "subtitle": "",
            "slides": [
                {
                    "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg",
                    "title": "Welcome to Our Platform",
                    "description": "Start your journey with us today",
                    "cta_text": "Get Started",
                    "cta_url": "#",
                    "alt": "Hero slide 1",
                },
                {
                    "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg",
                    "title": "Powerful Features",
                    "description": "Everything you need in one place",
                    "cta_text": "Learn More",
                    "cta_url": "#",
                    "alt": "Hero slide 2",
                },
            ],
        },
        "default_config": {
            "columns": 1,
            "height": 500,
            "max_width": "7xl",
            "padding_y": "16",
            "background_color": "base-100",
            "border_radius": "lg",
            "object_fit": "cover",
            "overlay_opacity": "50",
            "content_align_v": "center",
            "content_align_h": "center",
            "show_controls": True,
            "show_indicators": True,
            "style": "slide",
            "transition_duration": "700",
            "auto_slide": True,
            "auto_slide_interval": 5000,
            "cta_style": "primary",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
