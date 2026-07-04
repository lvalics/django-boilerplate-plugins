"""
Testimonials Grid zone templates.
"""

from ._base import ZoneType

TESTIMONIALS_GRID_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Testimonials Grid - Cards",
        "zone_type": ZoneType.TESTIMONIALS_GRID,
        "template_file": "cms/zones/testimonials_grid.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/testimonials_grid.html

Grid of testimonial cards with ratings, avatars, and scroll animations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  badge              Badge text above title
  title              Main heading text
  subtitle           Description below title

TESTIMONIALS ARRAY
  testimonials       Array of testimonial objects:
    text             Testimonial quote (required)
    name             Author name (required)
    title            Job title
    company          Company name
    avatar           Avatar image URL
    logo             Company logo URL
    rating           Star rating 1-5
    verified         Show verified badge (true/false)
    image            Featured image (masonry style only)

CTA SECTION
  cta.text           Button text
  cta.url            Button URL
  cta.subtext        Optional text below button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE VARIANT
  style              Display style for testimonials (default: card)
                 * "card" - DaisyUI card layout with shadows
                 * "minimal" - Clean, no card backgrounds
                 * "masonry" - Pinterest-style varying heights
                 * "quote-large" - Large decorative quote marks
                 * "avatar-focus" - Centered large avatars

LAYOUT
  columns            Grid columns: 2|3|4 (default: 3)
                 * "2" - two column grid
                 * "3" - three column grid (default)
                 * "4" - four column grid
  gap                Gap between items (default: 6)
                 * "4" - 1rem (16px) - compact
                 * "6" - 1.5rem (24px) - default
                 * "8" - 2rem (32px) - spacious
  max_width          Container max-width (default: 7xl)
                 * "6xl" - 1152px max width
                 * "7xl" - 1280px max width (default)
  padding_y          Section vertical padding (default: 16)
                 * "12" - 3rem (48px) - compact
                 * "16" - 4rem (64px) - default
                 * "20" - 5rem (80px) - spacious
                 * "24" - 6rem (96px) - very spacious

SECTION COLORS
  background_color   Section background color (default: base-100)
                 * "base-100" - lightest background (default)
                 * "base-200" - light gray
                 * "base-300" - darker gray
                 * "neutral" - dark theme

HEADER STYLING
  header_align       Header text alignment (default: center)
                 * "left" - left-aligned header
                 * "center" - centered header (default)
  header_margin      Space below header (default: 12)
                 * "8" - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
  badge_color        Badge color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
  title_size         Title text size mobile (default: 3xl)
                 * "2xl" - smaller title
                 * "3xl" - default size
                 * "4xl" - larger title
  title_size_md      Title text size desktop (default: 4xl)
                 * "3xl" - smaller title
                 * "4xl" - default size
                 * "5xl" - larger title
  title_weight       Title font weight (default: bold)
                 * "semibold" - slightly lighter
                 * "bold" - default weight
                 * "extrabold" - heavier
  title_color        Title text color (default: base-content)
                 * "base-content" - default text color
                 * "primary" - brand color
  subtitle_size      Subtitle text size (default: lg)
                 * "base" - smaller subtitle
                 * "lg" - default size
                 * "xl" - larger subtitle
  subtitle_color     Subtitle text color (default: base-content/70)
                 * "base-content/70" - 70% opacity (default)
                 * "base-content/60" - lighter
  subtitle_max_width Subtitle max width (default: 2xl)
                 * "xl" - narrower subtitle
                 * "2xl" - default width
                 * "3xl" - wider subtitle

CARD STYLING
  card_bg            Card background color (default: base-200)
                 * "base-100" - lightest
                 * "base-200" - default light gray
                 * "base-300" - darker
                 * "white" - pure white
  shadow             Card shadow size (default: lg)
                 * "sm" - subtle shadow
                 * "md" - medium shadow
                 * "lg" - default shadow
                 * "xl" - prominent shadow
  border             Show card border (default: false)
                 * false - no border (default)
                 * true - show border
  border_color       Border color when border enabled (default: base-300)
                 * "base-300" - subtle border (default)
                 * "base-content/10" - very subtle
  rounded            Border radius for masonry/quote-large (default: 2xl)
                 * "xl" - medium rounding
                 * "2xl" - default rounding
                 * "3xl" - more rounding
  padding            Card padding for masonry/quote-large (default: 6)
                 * "4" - 1rem (16px) - compact
                 * "6" - 1.5rem (24px) - default
                 * "8" - 2rem (32px) - spacious
  hover_effect       Enable hover animation (default: false)
                 * false - no hover effect (default)
                 * true - shadow and lift on hover

RATINGS
  show_ratings       Display star ratings (default: false)
                 * false - hide ratings (default)
                 * true - show star ratings
  rating_size        Rating stars size (default: sm)
                 * "xs" - extra small
                 * "sm" - small (default)
                 * "md" - medium
                 * "lg" - large
  star_color         Star color (default: warning)
                 * "warning" - yellow/gold (default)
                 * "primary" - brand color
                 * "accent" - accent color

QUOTE STYLING
  quote_size         Quote text size (default: base)
                 * "sm" - smaller text
                 * "base" - default size
                 * "lg" - larger text
                 * "xl" - extra large (quote-large style)
  quote_color        Quote text color (default: base-content/80)
                 * "base-content" - full opacity
                 * "base-content/80" - 80% opacity (default)
                 * "base-content/70" - lighter
  quote_italic       Italic quote text (default: true for card style)
                 * true - italic text (default)
                 * "false" - normal text
  quote_weight       Quote font weight for quote-large (default: medium)
                 * "normal" - regular weight
                 * "medium" - default weight
                 * "semibold" - heavier
  show_quote_marks   Show decorative quote marks (default: false)
                 * false - no quote marks (default)
                 * true - show quote marks in card style
  quote_mark_color   Quote mark color (default: primary/30)
                 * "primary/30" - translucent brand (default)
                 * "primary/20" - more translucent
                 * "base-content/20" - neutral
  quote_mark_size    Large quote mark size for quote-large (default: 6xl)
                 * "5xl" - smaller decorative quote
                 * "6xl" - default size
                 * "7xl" - larger decorative quote
  quote_mark_top     Quote mark top position (default: 4)
                 * "2" - closer to top
                 * "4" - default position
                 * "6" - lower position
  quote_mark_left    Quote mark left position (default: 6)
                 * "4" - closer to edge
                 * "6" - default position
                 * "8" - more inset

AVATAR STYLING
  avatar_size        Avatar size in Tailwind units (default: 12)
                 * "10" - 2.5rem (40px) - small
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - medium
                 * "20" - 5rem (80px) - large (avatar-focus)
                 * "24" - 6rem (96px) - extra large
  avatar_shape       Avatar border radius (default: full)
                 * "full" - fully rounded (default)
                 * "xl" - slightly squared
                 * "lg" - more squared
  avatar_ring        Ring color around avatar (default: primary)
                 * "primary" - brand color (default)
                 * "primary/20" - translucent brand
                 * "secondary" - secondary color
  avatar_ring_hover  Ring color on hover (default: primary)
                 * "primary" - solid brand on hover (default)
                 * "secondary" - secondary on hover

AUTHOR INFO
  author_gap         Gap between avatar and text (default: 4)
                 * "3" - tighter spacing
                 * "4" - default spacing
  author_border      Show border above author section (default: false)
                 * false - no border (default)
                 * true - show top border
  author_border_color Border color (default: base-300)
                 * "base-300" - subtle border (default)
  name_weight        Author name font weight (default: bold)
                 * "semibold" - slightly lighter
                 * "bold" - default weight
  name_color         Author name color (default: base-content)
                 * "base-content" - default text color
  name_size          Author name size for avatar-focus (default: lg)
                 * "base" - smaller name
                 * "lg" - default size
  title_text_size    Job title text size (default: sm)
                 * "xs" - extra small
                 * "sm" - default size
  title_text_color   Job title/company color (default: base-content/70)
                 * "base-content/70" - 70% opacity (default)
                 * "base-content/60" - lighter

VERIFIED & LOGOS
  show_verified      Show verified badges (default: false)
                 * false - hide badges (default)
                 * true - show verified badges
  verified_color     Verified badge color (default: success)
                 * "success" - green (default)
                 * "primary" - brand color
                 * "info" - blue
  show_logos         Show company logos (default: false)
                 * false - hide logos (default)
                 * true - show company logos
  logo_height        Logo height in Tailwind units (default: 6)
                 * "5" - 1.25rem (20px) - small
                 * "6" - 1.5rem (24px) - default
                 * "8" - 2rem (32px) - larger

CTA SECTION
  cta_margin         Space above CTA (default: 12)
                 * "8" - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
  cta_style          CTA button style (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "outline" - outlined button
                 * "ghost" - transparent button
  cta_size           CTA button size (default: unset)
                 * "sm" - small button
                 * "md" - medium button
                 * "lg" - large button

QUOTE-LARGE SPECIFIC
  divider_color      Author section border color (default: base-300)
                 * "base-300" - subtle border (default)
                 * "base-content/10" - very subtle

ANIMATION
  animate            Enable scroll animations (default: true)
                 * true - enable animations (default)
                 * "false" - disable animations

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Customer reviews with ratings:
{
  "badge": "Customer Love",
  "title": "What Our Customers Say",
  "subtitle": "Join thousands of satisfied users",
  "testimonials": [
    {"text": "Amazing product!", "name": "Jane D.", "rating": 5, "verified": true}
  ]
}
config: {"style": "card", "show_ratings": true, "show_verified": true, "hover_effect": true}

Enterprise clients with logos:
{
  "title": "Trusted by Industry Leaders",
  "testimonials": [
    {"text": "...", "name": "CEO", "company": "Acme", "logo": "/logo.png"}
  ]
}
config: {"style": "quote-large", "show_logos": true, "columns": "2"}

Minimal style with dark background:
config: {
  "style": "minimal",
  "background_color": "neutral",
  "quote_color": "white/80",
  "name_color": "white",
  "title_text_color": "white/60"
}

Avatar-focused community testimonials:
config: {
  "style": "avatar-focus",
  "columns": "4",
  "avatar_size": "20",
  "hover_effect": true
}

Masonry wall of love:
config: {
  "style": "masonry",
  "columns": "3",
  "show_ratings": true,
  "shadow": "md"
}
""",
        "default_content": {
            "badge": "Testimonials",
            "title": "What Our Customers Say",
            "subtitle": "Join thousands of satisfied customers who have transformed their business",
            "testimonials": [
                {
                    "text": "This platform has completely transformed how we manage our projects. The intuitive interface and powerful features have increased our team's productivity by 40%.",
                    "name": "Sarah Mitchell",
                    "title": "Product Manager",
                    "company": "TechFlow Inc",
                    "avatar": "https://i.pravatar.cc/150?img=1",
                    "rating": 5,
                    "verified": True,
                },
                {
                    "text": "The customer support is exceptional. Every time I had a question, the team responded within hours with helpful solutions. Truly impressive service!",
                    "name": "Michael Chen",
                    "title": "Startup Founder",
                    "company": "NexGen Labs",
                    "avatar": "https://i.pravatar.cc/150?img=3",
                    "rating": 5,
                    "verified": True,
                },
                {
                    "text": "We've tried many similar tools, but none compare to this one. The learning curve is minimal and the results are immediate. Highly recommend!",
                    "name": "Emily Rodriguez",
                    "title": "Marketing Director",
                    "company": "Growth Co",
                    "avatar": "https://i.pravatar.cc/150?img=5",
                    "rating": 5,
                },
                {
                    "text": "As a freelancer, I need tools that are reliable and efficient. This platform delivers on both fronts. It's become an essential part of my workflow.",
                    "name": "David Park",
                    "title": "Freelance Designer",
                    "avatar": "https://i.pravatar.cc/150?img=7",
                    "rating": 4,
                },
                {
                    "text": "The automation features alone have saved us countless hours each week. Our team can now focus on what really matters - serving our customers.",
                    "name": "Jessica Thompson",
                    "title": "Operations Lead",
                    "company": "ServiceFirst",
                    "avatar": "https://i.pravatar.cc/150?img=9",
                    "rating": 5,
                    "verified": True,
                },
                {
                    "text": "I was skeptical at first, but after using it for a month, I can't imagine going back. The ROI has been incredible for our small business.",
                    "name": "Robert Williams",
                    "title": "Small Business Owner",
                    "avatar": "https://i.pravatar.cc/150?img=11",
                    "rating": 5,
                },
            ],
            "cta": {
                "text": "Join Our Community",
                "url": "#signup",
                "subtext": "Start your free trial today",
            },
        },
        "default_config": {
            "style": "card",
            "columns": "3",
            "gap": "6",
            "max_width": "7xl",
            "padding_y": "16",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "badge_color": "primary",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_weight": "bold",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "subtitle_max_width": "2xl",
            "card_bg": "base-200",
            "shadow": "lg",
            "hover_effect": True,
            "show_ratings": True,
            "rating_size": "sm",
            "star_color": "warning",
            "quote_size": "base",
            "quote_color": "base-content/80",
            "avatar_size": "12",
            "avatar_shape": "full",
            "author_gap": "4",
            "name_weight": "bold",
            "name_color": "base-content",
            "title_text_size": "sm",
            "title_text_color": "base-content/70",
            "show_verified": True,
            "verified_color": "success",
            "cta_style": "primary",
            "cta_margin": "12",
            "animate": True,
        },
    },
    {
        "name": "Testimonials Grid - Minimal",
        "zone_type": ZoneType.TESTIMONIALS_GRID,
        "template_file": "cms/zones/testimonials_grid.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/testimonials_grid.html

Clean, minimal testimonials without card backgrounds.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  title              Main heading text
  subtitle           Description below title

TESTIMONIALS ARRAY
  testimonials       Array of testimonial objects:
    text             Testimonial quote (required)
    name             Author name (required)
    title            Job title
    avatar           Avatar image URL
    rating           Star rating 1-5

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style              Must be "minimal" for this template

LAYOUT
  columns            Grid columns: 2|3|4 (default: 3)
  gap                Gap between items (default: 8)
  max_width          Container max-width (default: 7xl)
  padding_y          Section vertical padding (default: 16)
  text_align         Text alignment (default: left)
                 * "left" - left-aligned text (default)
                 * "center" - centered text

COLORS
  background_color   Section background color (default: base-100)
  quote_size         Quote text size (default: lg)
  quote_color        Quote text color (default: base-content)
  name_color         Author name color (default: base-content)
  title_text_color   Job title color (default: base-content/60)

RATINGS
  show_ratings       Display star ratings (default: true)
  rating_size        Rating stars size (default: sm)
  star_color         Star color (default: warning)

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Default minimal:
config: {"style": "minimal", "columns": "3", "show_ratings": true}

Centered text:
config: {"style": "minimal", "text_align": "center"}

Dark theme:
config: {
  "style": "minimal",
  "background_color": "neutral",
  "quote_color": "white",
  "name_color": "white",
  "title_text_color": "white/60"
}
""",
        "default_content": {
            "title": "Trusted by Professionals",
            "subtitle": "See why industry leaders choose our platform",
            "testimonials": [
                {
                    "text": "The simplicity of this tool is its greatest strength. It does exactly what you need without unnecessary complexity or bloat.",
                    "name": "Anna Lee",
                    "title": "UX Designer at Figma",
                    "avatar": "https://i.pravatar.cc/150?img=10",
                    "rating": 5,
                },
                {
                    "text": "After evaluating dozens of solutions, we found the perfect fit. Integration was seamless and our team adopted it within days.",
                    "name": "Marcus Johnson",
                    "title": "CTO at Startup Hub",
                    "avatar": "https://i.pravatar.cc/150?img=12",
                    "rating": 5,
                },
                {
                    "text": "Clear documentation, responsive support, and a product that just works. What more could you ask for?",
                    "name": "Rachel Kim",
                    "title": "Engineering Manager",
                    "avatar": "https://i.pravatar.cc/150?img=16",
                    "rating": 4,
                },
            ],
        },
        "default_config": {
            "style": "minimal",
            "columns": "3",
            "gap": "8",
            "max_width": "7xl",
            "padding_y": "16",
            "background_color": "base-100",
            "text_align": "left",
            "show_ratings": True,
            "rating_size": "sm",
            "star_color": "warning",
            "quote_size": "lg",
            "quote_color": "base-content",
            "name_color": "base-content",
            "title_text_color": "base-content/60",
            "animate": True,
        },
    },
    {
        "name": "Testimonials Grid - Masonry",
        "zone_type": ZoneType.TESTIMONIALS_GRID,
        "template_file": "cms/zones/testimonials_grid.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/testimonials_grid.html

Pinterest-style masonry layout with varying heights.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  badge              Badge text above title
  title              Main heading text

TESTIMONIALS ARRAY
  testimonials       Array of testimonial objects:
    text             Testimonial quote (required)
    name             Author name (required)
    title            Job title
    company          Company name
    avatar           Avatar image URL
    rating           Star rating 1-5
    image            Featured image URL (optional, varies card height)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style              Must be "masonry" for this template

LAYOUT
  columns            Column count: 2|3|4 (default: 3)
  gap                Gap between items (default: 6)
  max_width          Container max-width (default: 7xl)
  padding_y          Section vertical padding (default: 16)

CARD STYLING
  card_bg            Card background color (default: base-200)
  shadow             Card shadow: sm|md|lg|xl (default: md)
  border             Show card border (default: false)
  border_color       Border color (default: base-300)
  rounded            Border radius (default: 2xl)
  padding            Card internal padding (default: 6)

RATINGS
  show_ratings       Display star ratings (default: true)
  rating_size        Rating stars size (default: sm)
  star_color         Star color (default: warning)

QUOTE STYLING
  quote_size         Quote text size (default: base)
  quote_color        Quote text color (default: base-content/80)

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Default masonry:
config: {"style": "masonry", "columns": "3", "show_ratings": true}

Subtle cards:
config: {"style": "masonry", "shadow": "sm", "card_bg": "base-100"}

With borders:
config: {"style": "masonry", "border": true, "shadow": ""}
""",
        "default_content": {
            "badge": "Wall of Love",
            "title": "Customer Stories",
            "testimonials": [
                {
                    "text": "Absolutely game-changing! This platform has revolutionized our entire workflow.",
                    "name": "Tom Bradley",
                    "title": "CEO",
                    "company": "InnovateTech",
                    "avatar": "https://i.pravatar.cc/150?img=13",
                    "rating": 5,
                },
                {
                    "text": "We migrated from our old system in less than a week. The import tools are fantastic, and the support team was incredibly helpful throughout the entire process. Couldn't be happier with our decision.",
                    "name": "Lisa Wang",
                    "title": "Data Manager",
                    "company": "Insights Pro",
                    "avatar": "https://i.pravatar.cc/150?img=20",
                    "rating": 5,
                },
                {
                    "text": "Fast, reliable, and beautiful. Exactly what we needed.",
                    "name": "Chris Martinez",
                    "title": "Designer",
                    "avatar": "https://i.pravatar.cc/150?img=15",
                },
                {
                    "text": "I've recommended this to every colleague I know. The value for money is unbeatable, and the constant improvements show the team really cares about their product and customers.",
                    "name": "Patricia Anderson",
                    "title": "Consultant",
                    "company": "Strategy Plus",
                    "avatar": "https://i.pravatar.cc/150?img=25",
                    "rating": 5,
                },
                {
                    "text": "The API documentation is excellent. Integration took just a few hours.",
                    "name": "Kevin O'Brien",
                    "title": "Developer",
                    "avatar": "https://i.pravatar.cc/150?img=17",
                    "rating": 4,
                },
                {
                    "text": "Best decision we made this year!",
                    "name": "Amanda Foster",
                    "title": "Project Lead",
                    "avatar": "https://i.pravatar.cc/150?img=23",
                    "rating": 5,
                },
            ],
        },
        "default_config": {
            "style": "masonry",
            "columns": "3",
            "gap": "6",
            "max_width": "7xl",
            "padding_y": "16",
            "background_color": "base-100",
            "card_bg": "base-200",
            "shadow": "md",
            "rounded": "2xl",
            "padding": "6",
            "show_ratings": True,
            "rating_size": "sm",
            "star_color": "warning",
            "quote_size": "base",
            "quote_color": "base-content/80",
            "animate": True,
        },
    },
    {
        "name": "Testimonials Grid - Quote Large",
        "zone_type": ZoneType.TESTIMONIALS_GRID,
        "template_file": "cms/zones/testimonials_grid.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/testimonials_grid.html

Featured testimonials with large decorative quote marks.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  title              Main heading text

TESTIMONIALS ARRAY
  testimonials       Array of testimonial objects:
    text             Testimonial quote (required)
    name             Author name (required)
    title            Job title
    company          Company name
    avatar           Avatar image URL
    rating           Star rating 1-5

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style              Must be "quote-large" for this template

LAYOUT
  columns            Grid columns: 2|3 (default: 2)
  gap                Gap between items (default: 8)
  max_width          Container max-width (default: 7xl)
  padding_y          Section vertical padding (default: 16)

CARD STYLING
  card_bg            Card background color (default: base-200)
  shadow             Card shadow: sm|md|lg|xl (default: lg)
  border             Show card border (default: false)
  border_color       Border color (default: base-300)
  rounded            Border radius (default: 2xl)
  padding            Card internal padding (default: 8)

QUOTE STYLING
  quote_size         Quote text size (default: xl)
  quote_color        Quote text color (default: base-content)
  quote_weight       Quote font weight (default: medium)
  quote_mark_size    Decorative quote size (default: 6xl)
  quote_mark_color   Quote mark color (default: primary/20)
  quote_mark_top     Quote mark top position (default: 4)
  quote_mark_left    Quote mark left position (default: 6)

RATINGS
  show_ratings       Display star ratings (default: true)
  rating_size        Rating stars size (default: md)
  star_color         Star color (default: warning)

AVATAR STYLING
  avatar_ring        Ring color around avatar (default: primary)

AUTHOR INFO
  name_color         Author name color (default: base-content)
  title_text_color   Job title color (default: base-content/70)
  divider_color      Border above author section (default: base-300)

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Default quote-large:
config: {"style": "quote-large", "columns": "2", "show_ratings": true}

Three columns:
config: {"style": "quote-large", "columns": "3", "padding": "6"}

Accent quote marks:
config: {"style": "quote-large", "quote_mark_color": "accent/30"}
""",
        "default_content": {
            "title": "What Industry Leaders Say",
            "testimonials": [
                {
                    "text": "This solution has transformed our enterprise operations. We've seen a 60% reduction in processing time and significant cost savings across all departments.",
                    "name": "Dr. James Wilson",
                    "title": "Chief Operating Officer",
                    "company": "Fortune 500 Corp",
                    "avatar": "https://i.pravatar.cc/150?img=60",
                    "rating": 5,
                },
                {
                    "text": "A truly innovative platform that understands the needs of modern businesses. The team's dedication to customer success is evident in every feature they release.",
                    "name": "Catherine Moore",
                    "title": "VP of Technology",
                    "company": "Global Systems Inc",
                    "avatar": "https://i.pravatar.cc/150?img=32",
                    "rating": 5,
                },
            ],
        },
        "default_config": {
            "style": "quote-large",
            "columns": "2",
            "gap": "8",
            "max_width": "7xl",
            "padding_y": "16",
            "background_color": "base-100",
            "card_bg": "base-200",
            "shadow": "lg",
            "rounded": "2xl",
            "padding": "8",
            "show_ratings": True,
            "rating_size": "md",
            "star_color": "warning",
            "quote_size": "xl",
            "quote_color": "base-content",
            "quote_weight": "medium",
            "quote_mark_size": "6xl",
            "quote_mark_color": "primary/20",
            "quote_mark_top": "4",
            "quote_mark_left": "6",
            "avatar_ring": "primary",
            "name_color": "base-content",
            "title_text_color": "base-content/70",
            "divider_color": "base-300",
            "animate": True,
        },
    },
    {
        "name": "Testimonials Grid - Avatar Focus",
        "zone_type": ZoneType.TESTIMONIALS_GRID,
        "template_file": "cms/zones/testimonials_grid.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/testimonials_grid.html

Centered layout with large prominent avatars.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  badge              Badge text above title
  title              Main heading text
  subtitle           Description below title

TESTIMONIALS ARRAY
  testimonials       Array of testimonial objects:
    text             Testimonial quote (required)
    name             Author name (required)
    title            Job title
    company          Company name
    avatar           Avatar image URL (important for this style)
    rating           Star rating 1-5
    logo             Company logo URL

CTA SECTION
  cta.text           Button text
  cta.url            Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style              Must be "avatar-focus" for this template

LAYOUT
  columns            Grid columns: 2|3|4 (default: 4)
  gap                Gap between items (default: 8)
  max_width          Container max-width (default: 7xl)
  padding_y          Section vertical padding (default: 16)

AVATAR STYLING
  avatar_size        Avatar size (default: 24)
                 * "16" - 4rem (64px) - medium
                 * "20" - 5rem (80px) - large
                 * "24" - 6rem (96px) - extra large (default)
  avatar_ring        Ring color around avatar (default: primary/20)
  avatar_ring_hover  Ring color on hover (default: primary)
  hover_effect       Enable hover animation (default: true)

RATINGS
  show_ratings       Display star ratings (default: true)
  rating_size        Rating stars size (default: sm)
  star_color         Star color (default: warning)

QUOTE STYLING
  quote_size         Quote text size (default: base)
  quote_color        Quote text color (default: base-content/80)

AUTHOR INFO
  name_size          Author name size (default: lg)
  name_color         Author name color (default: base-content)
  title_text_color   Job title color (default: base-content/60)

LOGOS
  show_logos         Show company logos (default: false)
  logo_height        Logo height (default: 6)

CTA SECTION
  cta_style          CTA button style (default: primary)
  cta_margin         Space above CTA (default: 12)

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Default avatar-focus:
config: {"style": "avatar-focus", "columns": "4", "hover_effect": true}

Three columns with larger avatars:
config: {"style": "avatar-focus", "columns": "3", "avatar_size": "28"}

With company logos:
config: {"style": "avatar-focus", "show_logos": true, "columns": "3"}
""",
        "default_content": {
            "badge": "Happy Customers",
            "title": "Meet Our Community",
            "subtitle": "Real people, real results",
            "testimonials": [
                {
                    "text": "Joining this community was the best decision for my career. The networking opportunities and resources are invaluable.",
                    "name": "Sophie Turner",
                    "title": "Entrepreneur",
                    "company": "Turner Ventures",
                    "avatar": "https://i.pravatar.cc/150?img=44",
                    "rating": 5,
                },
                {
                    "text": "The learning curve was minimal and the support has been outstanding. I feel like part of a family here.",
                    "name": "Daniel Cooper",
                    "title": "Software Engineer",
                    "company": "DevCore",
                    "avatar": "https://i.pravatar.cc/150?img=53",
                    "rating": 5,
                },
                {
                    "text": "Incredible value! The premium features are worth every penny. I've achieved more in 3 months than I did in a year.",
                    "name": "Nina Patel",
                    "title": "Growth Strategist",
                    "avatar": "https://i.pravatar.cc/150?img=47",
                    "rating": 5,
                },
                {
                    "text": "Finally, a platform that delivers on its promises. I'm continuously impressed by the quality and attention to detail.",
                    "name": "Alex Rivera",
                    "title": "Creative Director",
                    "company": "Design Labs",
                    "avatar": "https://i.pravatar.cc/150?img=51",
                    "rating": 4,
                },
            ],
            "cta": {
                "text": "Join Our Community",
                "url": "#join",
            },
        },
        "default_config": {
            "style": "avatar-focus",
            "columns": "4",
            "gap": "8",
            "max_width": "7xl",
            "padding_y": "16",
            "background_color": "base-100",
            "show_ratings": True,
            "rating_size": "sm",
            "star_color": "warning",
            "avatar_size": "24",
            "avatar_ring": "primary/20",
            "avatar_ring_hover": "primary",
            "hover_effect": True,
            "quote_size": "base",
            "quote_color": "base-content/80",
            "name_size": "lg",
            "name_color": "base-content",
            "title_text_color": "base-content/60",
            "cta_style": "primary",
            "cta_margin": "12",
            "animate": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
