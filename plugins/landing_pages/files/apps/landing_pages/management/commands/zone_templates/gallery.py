"""
Gallery zone templates.
"""

from ._base import ZoneType

GALLERY_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Gallery - Default Grid",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Simple responsive image grid gallery with optional lightbox.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

IMAGES
  images[]      Array of image objects:
    url           Image URL (required)
                  - Full URL: "https://example.com/img.jpg"
                  - Relative: "/media/gallery/photo.jpg"
    alt           Alt text for accessibility
    caption       Caption text below image (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style             "grid" (default for this template)
  columns           Grid columns on desktop: 2|3|4|5 (default: 3)
                - "2" - two column grid
                - "3" - three column grid (default)
                - "4" - four column grid
                - "5" - five column grid
  gap               Gap between images: 2|4|6|8 (default: 4)
                - "2" - 0.5rem (8px) - tight
                - "4" - 1rem (16px) - default
                - "6" - 1.5rem (24px) - spacious
                - "8" - 2rem (32px) - very spacious
  max_width         Container max-width: lg|xl|2xl|6xl|7xl
                - "xl"  - 1280px max width
                - "6xl" - 1152px max width
                - "7xl" - 1280px max width

APPEARANCE
  border_radius     Image corners: none|sm|md|lg|xl|2xl (default: lg)
                - "none" - square corners
                - "sm"   - slight rounding
                - "lg"   - default rounded
                - "xl"   - more rounded
                - "2xl"  - very rounded
  aspect_ratio      Force aspect ratio: square|video|auto
                - "square" - 1:1 aspect ratio
                - "video"  - 16:9 aspect ratio
                - omit for auto/natural aspect
  hover_effect      Enable scale on hover (default: false)
                - true  - images scale up on hover
                - false - no hover effect
  enable_lightbox   Click to open fullscreen modal (default: false)
                - true  - enable lightbox with navigation
                - false - no lightbox
  caption_align     Caption text alignment: left|center|right (default: center)
                - "left"   - left-aligned captions
                - "center" - centered captions (default)
                - "right"  - right-aligned captions

SPACING
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "8"  - 2rem (32px) - compact
                - "12" - 3rem (48px)
                - "16" - 4rem (64px) - default
                - "20" - 5rem (80px) - spacious
  background_color  Section background color (default: base-100)
                - "base-100" - lightest background (default)
                - "base-200" - light gray
                - "base-300" - darker gray
                - "neutral"  - dark background

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple 3-column gallery:
{
  "title": "Our Work",
  "subtitle": "Recent projects from our portfolio",
  "images": [
    {"url": "/media/project1.jpg", "alt": "Project 1"},
    {"url": "/media/project2.jpg", "alt": "Project 2"},
    {"url": "/media/project3.jpg", "alt": "Project 3"}
  ]
}
config: {"style": "grid", "columns": 3, "hover_effect": true}

Gallery with lightbox and captions:
{
  "title": "Photo Gallery",
  "images": [
    {"url": "/media/photo1.jpg", "alt": "Beach sunset", "caption": "Summer 2024"},
    {"url": "/media/photo2.jpg", "alt": "Mountain view", "caption": "Alpine trip"}
  ]
}
config: {"style": "grid", "enable_lightbox": true, "caption_align": "center"}

Square grid with tight spacing:
config: {
  "style": "grid",
  "columns": 4,
  "gap": "2",
  "aspect_ratio": "square",
  "border_radius": "none"
}

Dark theme gallery:
config: {
  "style": "grid",
  "background_color": "neutral",
  "border_radius": "xl",
  "hover_effect": true
}
""",
        "default_content": {
            "title": "Our Gallery",
            "subtitle": "Browse our collection",
            "images": [
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg", "alt": "Image 1"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg", "alt": "Image 2"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg", "alt": "Image 3"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-4.jpg", "alt": "Image 4"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-5.jpg", "alt": "Image 5"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-6.jpg", "alt": "Image 6"},
            ],
        },
        "default_config": {
            "style": "grid",
            "columns": 3,
            "gap": "4",
            "border_radius": "lg",
            "hover_effect": True,
            "enable_lightbox": True,
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    {
        "name": "Gallery - Masonry Grid",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Pinterest-style masonry layout with 4 columns of varying height images.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

COLUMNS (masonry-specific structure)
  columns[]     Array of 4 column objects, each containing:
    images[]      Array of images for this column:
      url           Image URL (required)
      alt           Alt text for accessibility

NOTE: Distribute images across 4 columns for best masonry effect.
      Vary image heights within columns for visual interest.

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style             "masonry" (REQUIRED for this template)
  max_width         Container max-width: lg|xl|2xl|6xl|7xl
                - "xl"  - 1280px max width
                - "6xl" - 1152px max width (default)
                - "7xl" - 1280px max width

APPEARANCE
  border_radius     Image corners: none|sm|md|lg|xl|2xl (default: lg)
                - "none" - square corners
                - "sm"   - slight rounding
                - "lg"   - default rounded
                - "xl"   - more rounded
  hover_effect      Enable scale on hover (default: false)
                - true  - images scale up on hover
                - false - no hover effect
  enable_lightbox   Click to open fullscreen modal (default: false)
                - true  - enable lightbox
                - false - no lightbox

SPACING
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "8"  - 2rem (32px) - compact
                - "12" - 3rem (48px)
                - "16" - 4rem (64px) - default
                - "20" - 5rem (80px) - spacious
  background_color  Section background color (default: base-100)
                - "base-100" - lightest (default)
                - "base-200" - light gray
                - "neutral"  - dark background

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic masonry layout:
{
  "title": "Photo Gallery",
  "columns": [
    {"images": [{"url": "/img/tall1.jpg"}, {"url": "/img/short1.jpg"}]},
    {"images": [{"url": "/img/short2.jpg"}, {"url": "/img/tall2.jpg"}]},
    {"images": [{"url": "/img/tall3.jpg"}, {"url": "/img/short3.jpg"}]},
    {"images": [{"url": "/img/short4.jpg"}, {"url": "/img/tall4.jpg"}]}
  ]
}
config: {"style": "masonry", "hover_effect": true}

Masonry with rounded corners:
config: {
  "style": "masonry",
  "border_radius": "xl",
  "hover_effect": true,
  "enable_lightbox": true
}

Compact masonry on dark background:
config: {
  "style": "masonry",
  "background_color": "neutral",
  "padding_y": "8",
  "border_radius": "lg"
}
""",
        "default_content": {
            "title": "Photo Gallery",
            "subtitle": "",
            "columns": [
                {
                    "images": [
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image.jpg", "alt": "Image"},
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-1.jpg", "alt": "Image"},
                    ]
                },
                {
                    "images": [
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-2.jpg", "alt": "Image"},
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-3.jpg", "alt": "Image"},
                    ]
                },
                {
                    "images": [
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-4.jpg", "alt": "Image"},
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-5.jpg", "alt": "Image"},
                    ]
                },
                {
                    "images": [
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-6.jpg", "alt": "Image"},
                        {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/masonry/image-7.jpg", "alt": "Image"},
                    ]
                },
            ],
        },
        "default_config": {
            "style": "masonry",
            "border_radius": "lg",
            "hover_effect": True,
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    {
        "name": "Gallery - Featured Image",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Large featured image with smaller grid of images below.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

FEATURED IMAGE
  featured        Featured image object:
    url             Large image URL (required)
    alt             Alt text for accessibility

GRID IMAGES
  images[]        Array of smaller images below:
    url             Image URL (required)
    alt             Alt text for accessibility

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style             "featured" (REQUIRED for this template)
  featured_height   Featured image height in pixels
                - 300 - compact featured image
                - 400 - default height
                - 500 - taller featured image
                - 600 - large hero-style
                - omit for auto height
  columns           Grid columns for smaller images: 3|4|5 (default: 5)
                - "3" - three column grid
                - "4" - four column grid
                - "5" - five column grid (default)
  max_width         Container max-width: lg|xl|2xl|6xl|7xl
                - "xl"  - 1280px max width
                - "6xl" - 1152px max width

APPEARANCE
  border_radius     Image corners: none|sm|md|lg|xl|2xl (default: lg)
                - "none" - square corners
                - "lg"   - default rounded
                - "xl"   - more rounded
  hover_effect      Enable scale on hover for grid images (default: false)
                - true  - images scale up on hover
                - false - no hover effect

SPACING
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "8"  - 2rem (32px) - compact
                - "12" - 3rem (48px)
                - "16" - 4rem (64px) - default
                - "20" - 5rem (80px)
  background_color  Section background color (default: base-100)
                - "base-100" - lightest (default)
                - "base-200" - light gray

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Product showcase:
{
  "title": "Featured Product",
  "featured": {"url": "/media/hero-product.jpg", "alt": "Main product"},
  "images": [
    {"url": "/media/detail1.jpg", "alt": "Detail 1"},
    {"url": "/media/detail2.jpg", "alt": "Detail 2"},
    {"url": "/media/detail3.jpg", "alt": "Detail 3"},
    {"url": "/media/detail4.jpg", "alt": "Detail 4"},
    {"url": "/media/detail5.jpg", "alt": "Detail 5"}
  ]
}
config: {"style": "featured", "featured_height": 500, "columns": 5}

Compact featured layout:
config: {
  "style": "featured",
  "featured_height": 300,
  "columns": 4,
  "border_radius": "xl"
}

Full-width featured with hover:
config: {
  "style": "featured",
  "featured_height": 600,
  "columns": 5,
  "hover_effect": true,
  "padding_y": "20"
}
""",
        "default_content": {
            "title": "Featured Gallery",
            "subtitle": "",
            "featured": {
                "url": "https://flowbite.s3.amazonaws.com/docs/gallery/featured/image.jpg",
                "alt": "Featured image",
            },
            "images": [
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg", "alt": "Image 1"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg", "alt": "Image 2"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg", "alt": "Image 3"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-4.jpg", "alt": "Image 4"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-5.jpg", "alt": "Image 5"},
            ],
        },
        "default_config": {
            "style": "featured",
            "columns": 5,
            "featured_height": 400,
            "border_radius": "lg",
            "hover_effect": True,
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    {
        "name": "Gallery - Quad Layout",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Simple 2x2 grid showing exactly 4 square images.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

IMAGES
  images[]      Exactly 4 images (extras are ignored):
    url           Image URL (required)
    alt           Alt text for accessibility

NOTE: Images are displayed as squares with object-cover.
      Only the first 4 images are shown.

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style             "quad" (REQUIRED for this template)
  gap               Space between images: 2|4|6|8 (default: 2)
                - "2" - 0.5rem (8px) - tight (default)
                - "4" - 1rem (16px) - standard
                - "6" - 1.5rem (24px) - spacious
  max_width         Container max-width: lg|xl|2xl|6xl|7xl
                - "2xl" - constrained width (default)
                - "xl"  - narrower

APPEARANCE
  border_radius     Image corners: none|sm|md|lg|xl|2xl (default: lg)
                - "none" - square corners
                - "lg"   - default rounded
                - "xl"   - more rounded
                - "2xl"  - very rounded
  hover_effect      Enable scale on hover (default: false)
                - true  - images scale up on hover
                - false - no hover effect

SPACING
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "8"  - 2rem (32px) - compact
                - "12" - 3rem (48px)
                - "16" - 4rem (64px) - default
  background_color  Section background color (default: base-100)
                - "base-100" - lightest (default)
                - "base-200" - light gray
                - "base-300" - darker gray

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Team photos quad:
{
  "title": "Our Team",
  "images": [
    {"url": "/media/team1.jpg", "alt": "Team member 1"},
    {"url": "/media/team2.jpg", "alt": "Team member 2"},
    {"url": "/media/team3.jpg", "alt": "Team member 3"},
    {"url": "/media/team4.jpg", "alt": "Team member 4"}
  ]
}
config: {"style": "quad", "gap": "4", "hover_effect": true}

Tight grid with square corners:
config: {
  "style": "quad",
  "gap": "2",
  "border_radius": "none"
}

Spacious rounded quad:
config: {
  "style": "quad",
  "gap": "6",
  "border_radius": "2xl",
  "hover_effect": true,
  "background_color": "base-200"
}
""",
        "default_content": {
            "title": "Gallery",
            "subtitle": "",
            "images": [
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg", "alt": "Image 1"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg", "alt": "Image 2"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg", "alt": "Image 3"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-4.jpg", "alt": "Image 4"},
            ],
        },
        "default_config": {
            "style": "quad",
            "gap": "2",
            "border_radius": "lg",
            "hover_effect": True,
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    {
        "name": "Gallery - Slider",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Carousel/slider gallery with overlay navigation arrows. Supports auto-advance.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

IMAGES
  images[]      Array of images for the slider:
    url           Image URL (required)
    alt           Alt text for accessibility

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style               "slider" (REQUIRED for this template)
  height              Slider height in pixels (default: 400)
                  - 300 - compact slider
                  - 400 - default height
                  - 500 - taller slider
                  - 600 - large slider
  max_width           Container max-width: lg|xl|2xl|6xl|7xl
                  - "xl"  - 1280px max width
                  - "6xl" - 1152px max width

APPEARANCE
  border_radius       Image corners: none|sm|md|lg|xl|2xl (default: lg)
                  - "none" - square corners
                  - "lg"   - default rounded
                  - "xl"   - more rounded

AUTO-SLIDE
  auto_slide          Enable automatic slide advance (default: true)
                  - true  - slides auto-advance
                  - false - manual navigation only
  auto_slide_interval Milliseconds between slides (default: 5000)
                  - 3000 - 3 seconds (fast)
                  - 5000 - 5 seconds (default)
                  - 7000 - 7 seconds (slow)
                  - 10000 - 10 seconds (very slow)

SPACING
  padding_y           Vertical padding in Tailwind units (default: 16)
                  - "8"  - 2rem (32px) - compact
                  - "12" - 3rem (48px)
                  - "16" - 4rem (64px) - default
  background_color    Section background color (default: base-100)
                  - "base-100" - lightest (default)
                  - "base-200" - light gray
                  - "neutral"  - dark background

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic slider with auto-advance:
{
  "title": "Image Slider",
  "images": [
    {"url": "/media/slide1.jpg", "alt": "Slide 1"},
    {"url": "/media/slide2.jpg", "alt": "Slide 2"},
    {"url": "/media/slide3.jpg", "alt": "Slide 3"}
  ]
}
config: {"style": "slider", "auto_slide": true, "auto_slide_interval": 5000}

Tall slider with slow transitions:
config: {
  "style": "slider",
  "height": 600,
  "auto_slide": true,
  "auto_slide_interval": 8000,
  "border_radius": "xl"
}

Manual navigation only:
config: {
  "style": "slider",
  "height": 400,
  "auto_slide": false,
  "border_radius": "lg"
}

Compact slider on dark background:
config: {
  "style": "slider",
  "height": 300,
  "background_color": "neutral",
  "border_radius": "none"
}
""",
        "default_content": {
            "title": "Image Slider",
            "subtitle": "",
            "images": [
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg", "alt": "Image 1"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg", "alt": "Image 2"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg", "alt": "Image 3"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-4.jpg", "alt": "Image 4"},
            ],
        },
        "default_config": {
            "style": "slider",
            "height": 400,
            "border_radius": "lg",
            "auto_slide": True,
            "auto_slide_interval": 5000,
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    {
        "name": "Gallery - Slider with Bottom Controls",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Slider with navigation controls positioned below, including slide counter.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

IMAGES
  images[]      Array of images for the slider:
    url           Image URL (required)
    alt           Alt text for accessibility

NOTE: Displays slide counter (e.g., "1 / 5") between prev/next buttons.

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style             "slider-bottom-controls" (REQUIRED for this template)
  height            Slider height in pixels (default: 400)
                - 300 - compact slider
                - 400 - default height
                - 500 - taller slider
                - 600 - large slider
  max_width         Container max-width: lg|xl|2xl|6xl|7xl
                - "xl"  - 1280px max width
                - "6xl" - 1152px max width

APPEARANCE
  border_radius     Image corners: none|sm|md|lg|xl|2xl (default: lg)
                - "none" - square corners
                - "lg"   - default rounded
                - "xl"   - more rounded

SPACING
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "8"  - 2rem (32px) - compact
                - "12" - 3rem (48px)
                - "16" - 4rem (64px) - default
  background_color  Section background color (default: base-100)
                - "base-100" - lightest (default)
                - "base-200" - light gray
                - "neutral"  - dark background

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic slider with bottom controls:
{
  "title": "Photo Slider",
  "images": [
    {"url": "/media/photo1.jpg", "alt": "Photo 1"},
    {"url": "/media/photo2.jpg", "alt": "Photo 2"},
    {"url": "/media/photo3.jpg", "alt": "Photo 3"}
  ]
}
config: {"style": "slider-bottom-controls", "height": 400}

Tall slider with rounded corners:
config: {
  "style": "slider-bottom-controls",
  "height": 500,
  "border_radius": "xl"
}

Compact slider:
config: {
  "style": "slider-bottom-controls",
  "height": 300,
  "padding_y": "8",
  "border_radius": "lg"
}

On gray background:
config: {
  "style": "slider-bottom-controls",
  "height": 400,
  "background_color": "base-200"
}
""",
        "default_content": {
            "title": "Photo Slider",
            "subtitle": "",
            "images": [
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg", "alt": "Image 1"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg", "alt": "Image 2"},
                {"url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg", "alt": "Image 3"},
            ],
        },
        "default_config": {
            "style": "slider-bottom-controls",
            "height": 400,
            "border_radius": "lg",
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    {
        "name": "Gallery - Filterable by Category",
        "zone_type": ZoneType.GALLERY,
        "template_file": "landing_pages/zones/gallery.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/gallery.html

Gallery with category filter buttons for interactive filtering.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)

CATEGORIES
  categories[]    Array of filter categories:
    name            Display name (e.g., "Shoes")
    slug            Filter value (e.g., "shoes")
                    - Must match image category values

IMAGES
  images[]        Array of images with category:
    url             Image URL (required)
    alt             Alt text for accessibility
    category        Category slug to match filter (required)
                    - Must match a category slug
    caption         Optional caption text below image

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style             "filterable" (REQUIRED for this template)
  columns           Grid columns on desktop: 2|3|4|5 (default: 3)
                - "2" - two column grid
                - "3" - three column grid (default)
                - "4" - four column grid
                - "5" - five column grid
  max_width         Container max-width: lg|xl|2xl|6xl|7xl
                - "xl"  - 1280px max width
                - "6xl" - 1152px max width

APPEARANCE
  border_radius     Image corners: none|sm|md|lg|xl|2xl (default: lg)
                - "none" - square corners
                - "lg"   - default rounded
                - "xl"   - more rounded
  hover_effect      Enable scale on hover (default: false)
                - true  - images scale up on hover
                - false - no hover effect

FILTER BUTTONS
  active_color      Active filter button background color (default: primary)
                - "primary"   - brand color (default)
                - "secondary" - secondary brand color
                - "accent"    - accent color
                - "success"   - green
                - "info"      - blue
  active_text       Active filter button text color (default: primary-content)
                - "primary-content"   - contrast text for primary bg
                - "secondary-content" - contrast text for secondary bg
                - "white"             - white text

SPACING
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "8"  - 2rem (32px) - compact
                - "12" - 3rem (48px)
                - "16" - 4rem (64px) - default
  background_color  Section background color (default: base-100)
                - "base-100" - lightest (default)
                - "base-200" - light gray

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Product gallery by category:
{
  "title": "Product Gallery",
  "categories": [
    {"name": "Shoes", "slug": "shoes"},
    {"name": "Bags", "slug": "bags"},
    {"name": "Accessories", "slug": "accessories"}
  ],
  "images": [
    {"url": "/media/shoe1.jpg", "category": "shoes", "alt": "Running shoe"},
    {"url": "/media/bag1.jpg", "category": "bags", "alt": "Leather bag"},
    {"url": "/media/acc1.jpg", "category": "accessories", "alt": "Watch"}
  ]
}
config: {"style": "filterable", "columns": 3, "hover_effect": true}

Portfolio with accent filter buttons:
config: {
  "style": "filterable",
  "columns": 4,
  "active_color": "accent",
  "active_text": "accent-content",
  "border_radius": "xl"
}

Compact filterable gallery:
config: {
  "style": "filterable",
  "columns": 2,
  "active_color": "secondary",
  "padding_y": "8"
}

With captions and hover:
{
  "images": [
    {"url": "/img.jpg", "category": "design", "caption": "Logo design project"}
  ]
}
config: {"style": "filterable", "hover_effect": true}
""",
        "default_content": {
            "title": "Product Gallery",
            "subtitle": "",
            "categories": [
                {"name": "Shoes", "slug": "shoes"},
                {"name": "Bags", "slug": "bags"},
                {"name": "Accessories", "slug": "accessories"},
            ],
            "images": [
                {
                    "url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg",
                    "alt": "Product",
                    "category": "shoes",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg",
                    "alt": "Product",
                    "category": "bags",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-3.jpg",
                    "alt": "Product",
                    "category": "shoes",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-4.jpg",
                    "alt": "Product",
                    "category": "accessories",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-5.jpg",
                    "alt": "Product",
                    "category": "bags",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-6.jpg",
                    "alt": "Product",
                    "category": "accessories",
                },
            ],
        },
        "default_config": {
            "style": "filterable",
            "columns": 3,
            "active_color": "primary",
            "active_text": "primary-content",
            "border_radius": "lg",
            "hover_effect": True,
            "padding_y": "16",
            "background_color": "base-100",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
