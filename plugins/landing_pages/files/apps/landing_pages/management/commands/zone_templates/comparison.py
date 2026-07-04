"""
Comparison zone templates.
"""

from ._base import ZoneType

COMPARISON_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Comparison - Before/After Slider",
        "zone_type": ZoneType.COMPARISON,
        "template_file": "landing_pages/zones/comparison.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/comparison.html

Interactive before/after image comparison slider with drag functionality.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION TEXT
  title            Main heading text (optional)
  subtitle         Supporting paragraph below title (optional)
  caption          Text caption below slider (optional)

IMAGES
  before_image     URL to "before" image (left/hidden side)
               • Full URL: "https://example.com/before.jpg"
               • Relative: "/media/images/before.jpg"
               • Static: "{% static 'images/before.jpg' %}"
  after_image      URL to "after" image (right/visible side)
               • Full URL: "https://example.com/after.jpg"
               • Relative: "/media/images/after.jpg"
               • Static: "{% static 'images/after.jpg' %}"

LABELS
  before_label     Label for before image (default: "Before")
               • "Before" - default label
               • "Original" - alternative
               • "2023" - date-based
               • "Without Filter" - descriptive
               • "" - hide label
  after_label      Label for after image (default: "After")
               • "After" - default label
               • "Enhanced" - alternative
               • "2024" - date-based
               • "With Filter" - descriptive
               • "" - hide label

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  padding_y          Vertical padding in Tailwind units (default: 12)
               • "8"  - 2rem (32px) - compact
               • "12" - 3rem (48px) - default
               • "16" - 4rem (64px) - spacious
               • "20" - 5rem (80px) - very spacious
               • "24" - 6rem (96px) - maximum
  max_width          Container width constraint (default: 4xl)
               • "2xl" - 672px max width (narrow)
               • "3xl" - 768px max width
               • "4xl" - 896px max width (default)
               • "5xl" - 1024px max width
               • "6xl" - 1152px max width (wide)
  slider_max_width   Slider component max width (default: 800px)
               • "600px" - compact slider
               • "700px" - medium slider
               • "800px" - default
               • "900px" - wide slider
               • "100%" - full container width

COLORS
  background_color   Section background color (default: base-100)
               • "base-100" - lightest background (default)
               • "base-200" - light gray background
               • "base-300" - medium gray background
               • "neutral" - dark background
               • "primary" - brand color background

SLIDER STYLING
  rounded            Border radius for slider container (default: lg)
               • "none" - no rounded corners
               • "md" - medium radius
               • "lg" - large radius (default)
               • "xl" - extra large radius
               • "2xl" - maximum radius
  shadow             Shadow depth for slider container (default: xl)
               • "none" - no shadow
               • "md" - medium shadow
               • "lg" - large shadow
               • "xl" - extra large shadow (default)
               • "2xl" - maximum shadow

HANDLE STYLING
  handle_color       Slider handle and bar color (default: white)
               • "white" - white handle (default)
               • "primary" - brand color handle
               • "base-100" - light handle
               • "neutral" - dark handle
               • "accent" - accent color handle
  handle_icon_color  Handle arrow icon color (default: base-content)
               • "base-content" - default text color
               • "primary" - brand color
               • "neutral" - neutral dark
               • "white" - white icon
               • "gray-600" - medium gray

BEHAVIOR
  initial_position   Starting slider position 0-100 (default: 50)
               • "0" - fully show after image
               • "25" - mostly after visible
               • "50" - centered split (default)
               • "75" - mostly before visible
               • "100" - fully show before image

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic before/after comparison:
{
  "before_image": "https://example.com/old-design.jpg",
  "after_image": "https://example.com/new-design.jpg",
  "before_label": "Before",
  "after_label": "After",
  "title": "See the Difference",
  "subtitle": "Drag to compare old vs new"
}

Photo editing showcase:
{
  "before_image": "/media/photos/original.jpg",
  "after_image": "/media/photos/edited.jpg",
  "before_label": "Original",
  "after_label": "Enhanced",
  "title": "Professional Photo Editing",
  "subtitle": "See how we transform your images",
  "caption": "Move the slider to compare the original and edited versions"
}
config: {"initial_position": 30, "slider_max_width": "900px"}

Renovation/remodel project:
{
  "before_image": "/media/projects/kitchen-before.jpg",
  "after_image": "/media/projects/kitchen-after.jpg",
  "before_label": "2022",
  "after_label": "2024",
  "title": "Kitchen Renovation",
  "caption": "Complete transformation in just 6 weeks"
}
config: {"rounded": "2xl", "shadow": "2xl"}

Minimal without labels:
{
  "before_image": "/img/v1.jpg",
  "after_image": "/img/v2.jpg",
  "before_label": "",
  "after_label": "",
  "title": "Product Evolution"
}
config: {"padding_y": "16", "background_color": "base-200"}

Dark theme comparison:
config: {
  "background_color": "neutral",
  "handle_color": "primary",
  "handle_icon_color": "white",
  "rounded": "xl",
  "shadow": "xl"
}

Full-width immersive slider:
config: {
  "slider_max_width": "100%",
  "max_width": "6xl",
  "padding_y": "8",
  "initial_position": 50
}

═══════════════════════════════════════════════════════════════
INTERACTION NOTES
═══════════════════════════════════════════════════════════════

• Click anywhere on slider to move handle to that position
• Drag handle left/right to reveal/hide before image
• Touch support for mobile devices
• Hidden range input for accessibility (screen readers)
• Keyboard navigation via range input (left/right arrows)
• Labels only shown when before_label or after_label is provided
""",
        "default_content": {
            "title": "See the Difference",
            "subtitle": "Drag the slider to compare before and after",
            "caption": "",
            "before_image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg",
            "after_image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-2.jpg",
            "before_label": "Before",
            "after_label": "After",
        },
        "default_config": {
            "style": "slider",
            "padding_y": "12",
            "max_width": "4xl",
            "slider_max_width": "800px",
            "background_color": "base-100",
            "rounded": "lg",
            "shadow": "xl",
            "handle_color": "white",
            "handle_icon_color": "base-content",
            "initial_position": 50,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
