"""
Testimonial zone templates.
"""

from ._base import ZoneType

TESTIMONIAL_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Testimonial - Centered Card",
        "zone_type": ZoneType.TESTIMONIAL_SINGLE,
        "template_file": "landing_pages/zones/testimonial_single.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/testimonial_single.html

Single testimonial in centered card layout with avatar and rating.

═══════════════════════════════════════════════════════════════
DATA SOURCE
═══════════════════════════════════════════════════════════════

Option 1: Link to Testimonial model (recommended)
  - Select testimonial from dropdown in zone admin
  - Pulls text, author, photo, rating, verified status
  - Changes to testimonial auto-update on page

Option 2: Inline content JSON
  - Define testimonial directly in content field
  - Useful for one-off or custom testimonials

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON) - for inline testimonials
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)
text            Testimonial quote text (required)
author_name     Name of person (required)
author_title    Title/company (optional)
image           Author photo URL (optional)
rating          Star rating 1-5 (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             Layout style (default: "centered")
                - "centered" - Card with centered content and avatar
                - "quote" - Large quote marks, minimal styling
                - "card-horizontal" - Image on left, text right

LAYOUT
  max_width         Container width (default: 4xl)
                - "3xl" - 768px max width (narrow)
                - "4xl" - 896px max width (default)
                - "5xl" - 1024px max width (wider)
                - "6xl" - 1152px max width (wide)
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "12" - 3rem (48px) - compact
                - "16" - 4rem (64px) - default
                - "20" - 5rem (80px) - spacious
                - "24" - 6rem (96px) - very spacious

COLORS
  background_color  Section background color (default: base-100)
                - "base-100" - lightest background (default)
                - "base-200" - light gray
                - "base-300" - darker gray
                - "primary" - brand color background
                - "neutral" - dark neutral
  card_bg           Card background color (default: base-200)
                - "base-100" - white/light
                - "base-200" - light gray (default)
                - "base-300" - darker gray
                - "white" - pure white
  ring_color        Avatar ring color - centered style (default: primary)
                - "primary" - brand color ring (default)
                - "secondary" - secondary brand
                - "accent" - accent color
                - "neutral" - neutral gray
  quote_color       Large quote mark color - quote style (default: primary)
                - "primary" - brand color (default)
                - "secondary" - secondary brand
                - "accent" - accent color
  text_color        Quote text color - quote style (default: base-content)
                - "base-content" - default text color
                - "primary" - brand color
                - "white" - for dark backgrounds

DISPLAY
  show_rating       Show star rating (default: true)
                - true - display 5-star rating (default)
                - false - hide rating stars

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple centered testimonial:
{
  "title": "What Our Customers Say",
  "text": "This product exceeded all my expectations!",
  "author_name": "Jane Doe",
  "author_title": "CEO, Example Company",
  "rating": 5
}
config: {"style": "centered"}

Centered with avatar:
{
  "text": "Exceptional quality and outstanding support.",
  "author_name": "John Smith",
  "author_title": "Marketing Director",
  "image": "https://example.com/photo.jpg",
  "rating": 5
}
config: {"style": "centered", "ring_color": "secondary"}

Dark theme section:
{
  "text": "A game-changer for our business.",
  "author_name": "Sarah Johnson",
  "author_title": "Founder"
}
config: {
  "style": "centered",
  "background_color": "neutral",
  "card_bg": "base-200"
}

With header text:
{
  "title": "Customer Testimonial",
  "subtitle": "Hear what our clients have to say",
  "text": "We've seen incredible results since switching.",
  "author_name": "Mike Chen",
  "rating": 5
}
config: {"style": "centered", "max_width": "3xl"}
""",
        "default_content": {
            "title": "What Our Customers Say",
            "subtitle": "",
            "text": "This product exceeded all my expectations. The quality is outstanding and the customer service was exceptional.",
            "author_name": "Jane Doe",
            "author_title": "CEO, Example Company",
            "image": "",
            "rating": 5,
        },
        "default_config": {
            "style": "centered",
            "max_width": "4xl",
            "padding_y": "16",
            "background_color": "base-100",
            "card_bg": "base-200",
            "ring_color": "primary",
            "show_rating": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Testimonial - Quote Style",
        "zone_type": ZoneType.TESTIMONIAL_SINGLE,
        "template_file": "landing_pages/zones/testimonial_single.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/testimonial_single.html

Elegant quote-style testimonial with large decorative quotation marks.

═══════════════════════════════════════════════════════════════
DATA SOURCE
═══════════════════════════════════════════════════════════════

Option 1: Link to Testimonial model (recommended)
  - Select testimonial from dropdown in zone admin

Option 2: Inline content JSON
  - Define testimonial directly in content field

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)
text            Testimonial quote text (required)
author_name     Name of person (required)
author_title    Title/company (optional)
image           Author photo URL (optional)
rating          Star rating 1-5 (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             Must be "quote" for this template

LAYOUT
  max_width         Container width (default: 3xl)
                - "2xl" - 672px max width (narrow)
                - "3xl" - 768px max width (default)
                - "4xl" - 896px max width (wider)
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "12" - 3rem (48px) - compact
                - "16" - 4rem (64px) - default
                - "20" - 5rem (80px) - spacious

COLORS
  background_color  Section background color (default: base-100)
                - "base-100" - lightest background (default)
                - "base-200" - light gray
                - "base-300" - darker gray
                - "primary" - brand color background
                - "neutral" - dark neutral
  quote_color       Large quote mark color (default: primary)
                - "primary" - brand color (default)
                - "secondary" - secondary brand
                - "accent" - accent color
                - "warning" - yellow/orange
                - "success" - green
  text_color        Quote text color (default: base-content)
                - "base-content" - default text color (default)
                - "primary" - brand color text
                - "white" - for dark backgrounds
                - "base-content/80" - slightly muted

DISPLAY
  show_rating       Show star rating (default: true)
                - true - display 5-star rating (default)
                - false - hide rating stars

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Classic quote style:
{
  "text": "Working with this team was an absolute pleasure.",
  "author_name": "John Smith",
  "author_title": "Marketing Director",
  "rating": 5
}
config: {"style": "quote"}

With author photo:
{
  "text": "This solution transformed our workflow completely.",
  "author_name": "Sarah Chen",
  "author_title": "VP of Operations",
  "image": "https://example.com/sarah.jpg",
  "rating": 5
}
config: {"style": "quote", "quote_color": "accent"}

Dark background:
{
  "text": "Exceptional product with incredible support.",
  "author_name": "Mike Johnson",
  "author_title": "CTO"
}
config: {
  "style": "quote",
  "background_color": "neutral",
  "text_color": "white",
  "quote_color": "primary"
}

With section header:
{
  "title": "Featured Testimonial",
  "text": "A truly innovative platform.",
  "author_name": "Lisa Park",
  "rating": 5
}
config: {"style": "quote", "max_width": "4xl"}

No rating display:
{
  "text": "The best investment we made this year.",
  "author_name": "David Lee",
  "author_title": "Founder"
}
config: {"style": "quote", "show_rating": false}
""",
        "default_content": {
            "title": "",
            "subtitle": "",
            "text": "Working with this team was an absolute pleasure. They delivered beyond our expectations and on time.",
            "author_name": "John Smith",
            "author_title": "Marketing Director",
            "image": "",
            "rating": 5,
        },
        "default_config": {
            "style": "quote",
            "max_width": "3xl",
            "padding_y": "16",
            "background_color": "base-100",
            "quote_color": "primary",
            "text_color": "base-content",
            "show_rating": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Testimonial - Horizontal Card",
        "zone_type": ZoneType.TESTIMONIAL_SINGLE,
        "template_file": "landing_pages/zones/testimonial_single.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/testimonial_single.html

Horizontal card layout with large author image on left side.

═══════════════════════════════════════════════════════════════
DATA SOURCE
═══════════════════════════════════════════════════════════════

Option 1: Link to Testimonial model (recommended)
  - Select testimonial from dropdown in zone admin
  - Photo displays on left 1/3 of card

Option 2: Inline content JSON
  - Define testimonial directly in content field
  - Use image field for author photo

NOTE: This style works best with an author photo/image.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Section heading (optional)
subtitle        Section subheading (optional)
text            Testimonial quote text (required)
author_name     Name of person (required)
author_title    Title/company (optional)
image           Author photo URL (recommended for this style)
rating          Star rating 1-5 (optional)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             Must be "card-horizontal" for this template

LAYOUT
  max_width         Container width (default: 4xl)
                - "3xl" - 768px max width (compact)
                - "4xl" - 896px max width (default)
                - "5xl" - 1024px max width (wider)
                - "6xl" - 1152px max width (wide)
  padding_y         Vertical padding in Tailwind units (default: 16)
                - "12" - 3rem (48px) - compact
                - "16" - 4rem (64px) - default
                - "20" - 5rem (80px) - spacious

COLORS
  background_color  Section background color (default: base-100)
                - "base-100" - lightest background (default)
                - "base-200" - light gray
                - "base-300" - darker gray
                - "neutral" - dark neutral
  card_bg           Card background color (default: base-200)
                - "base-100" - white/light
                - "base-200" - light gray (default)
                - "base-300" - darker gray
                - "white" - pure white

DISPLAY
  show_rating       Show star rating (default: true)
                - true - display 5-star rating (default)
                - false - hide rating stars

NOTE: Linked testimonials with is_verified=true will display
      a "Verified" badge automatically.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Featured testimonial with photo:
{
  "text": "The results speak for themselves. Our conversion rate increased by 150%.",
  "author_name": "Sarah Johnson",
  "author_title": "Founder & CEO, TechStart",
  "image": "https://example.com/sarah.jpg",
  "rating": 5
}
config: {"style": "card-horizontal"}

Wider layout:
{
  "text": "An exceptional tool that has become essential to our operations.",
  "author_name": "Michael Chen",
  "author_title": "VP Engineering",
  "image": "https://example.com/michael.jpg",
  "rating": 5
}
config: {"style": "card-horizontal", "max_width": "5xl"}

Light card on gray background:
{
  "text": "Customer support is outstanding. Always responsive.",
  "author_name": "Emily Davis",
  "author_title": "Operations Manager",
  "image": "https://example.com/emily.jpg"
}
config: {
  "style": "card-horizontal",
  "background_color": "base-200",
  "card_bg": "base-100"
}

Compact without rating:
{
  "text": "Highly recommended for any growing business.",
  "author_name": "Alex Kim",
  "author_title": "Startup Founder",
  "image": "https://example.com/alex.jpg"
}
config: {
  "style": "card-horizontal",
  "show_rating": false,
  "padding_y": "12"
}

With section header:
{
  "title": "Customer Success Story",
  "subtitle": "See how TechStart transformed their business",
  "text": "This platform changed everything for us.",
  "author_name": "Lisa Park",
  "author_title": "CEO",
  "image": "https://example.com/lisa.jpg",
  "rating": 5
}
config: {"style": "card-horizontal", "max_width": "4xl"}
""",
        "default_content": {
            "title": "",
            "subtitle": "",
            "text": "The results speak for themselves. Our conversion rate increased by 150% after implementing their recommendations.",
            "author_name": "Sarah Johnson",
            "author_title": "Founder & CEO, TechStart",
            "image": "https://flowbite.s3.amazonaws.com/docs/gallery/square/image-1.jpg",
            "rating": 5,
        },
        "default_config": {
            "style": "card-horizontal",
            "max_width": "4xl",
            "padding_y": "16",
            "background_color": "base-100",
            "card_bg": "base-200",
            "show_rating": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
