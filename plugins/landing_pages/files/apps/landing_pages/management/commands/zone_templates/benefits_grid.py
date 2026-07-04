"""
Benefits Grid zone templates.
"""

from ._base import ZoneType

BENEFITS_GRID_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Benefits Grid - Card Style",
        "zone_type": ZoneType.BENEFITS_GRID,
        "template_file": "landing_pages/zones/benefits_grid.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/benefits_grid.html

Feature/benefits grid with card-style items and scroll animations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title (optional)
  title            Section heading
  subtitle         Description text

ITEMS
  items[]          Array of benefit items:
    icon           Emoji, SVG, or image URL
    title          Item heading
    description    Item description
    link           Optional link object:
      url          Link URL
      text         Link text (default: "Learn more")

CTA
  primary_cta.text   Button text
  primary_cta.url    Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style            Display style (default: card)
             • "minimal"    - clean, no cards - just icon, title, description
             • "card"       - cards with background and shadow (default)
             • "bordered"   - outline cards with borders
             • "icon-left"  - horizontal layout, icon on left
  columns          Grid columns (default: 3)
             • "2" - two column grid
             • "3" - three column grid (default)
             • "4" - four column grid
             • "5" - five column grid
             • "6" - six column grid
  gap              Gap between items in Tailwind units (default: 6)
             • "4"  - 1rem (16px) - compact
             • "6"  - 1.5rem (24px) - default
             • "8"  - 2rem (32px) - spacious
  gap_md           Gap on medium+ screens (default: 8)
             • "6"  - 1.5rem (24px)
             • "8"  - 2rem (32px) - default
             • "10" - 2.5rem (40px)
  max_width        Container max width constraint
             • "4xl" - 896px
             • "5xl" - 1024px
             • "6xl" - 1152px
             • "7xl" - 1280px
  padding_y        Vertical padding (default: 16)
             • "12" - 3rem (48px)
             • "16" - 4rem (64px) - default
             • "20" - 5rem (80px)
             • "24" - 6rem (96px)
  background_color Section background (default: base-100)
             • "base-100" - lightest (default)
             • "base-200" - light gray
             • "base-300" - darker gray
             • "neutral"  - dark background
  animate          Enable scroll animations (default: true)
             • true  - items animate on scroll (default)
             • "false" - disable animations (string "false")

HEADER STYLING
  header_margin    Space below header (default: 12)
             • "8"  - 2rem (32px)
             • "12" - 3rem (48px) - default
             • "16" - 4rem (64px)
  title_size       Title font size (default: 3xl)
             • "2xl" - smaller title
             • "3xl" - default
             • "4xl" - larger title
  title_size_md    Title size on md+ screens (default: 4xl)
             • "3xl" - moderate
             • "4xl" - default
             • "5xl" - large
  title_weight     Title font weight (default: bold)
             • "semibold" - slightly lighter
             • "bold"     - default
             • "extrabold"- heavier
  title_color      Title text color (default: base-content)
             • "base-content" - default text color
             • "primary"      - brand color
             • "white"        - for dark backgrounds
  subtitle_size    Subtitle font size (default: lg)
             • "base" - smaller
             • "lg"   - default
             • "xl"   - larger
  subtitle_color   Subtitle text color (default: base-content/70)
             • "base-content/70" - 70% opacity (default)
             • "base-content/60" - lighter
             • "base-content"    - full opacity
  subtitle_max_width  Subtitle max width (default: 2xl)
             • "xl"  - 576px - narrower
             • "2xl" - 672px - default
             • "3xl" - 768px - wider
  badge_color      Badge color (default: primary)
             • "primary"   - brand color (default)
             • "secondary" - secondary brand
             • "accent"    - accent color
             • "info"      - blue

CARD/ITEM STYLING
  card_bg          Card background color (default: base-200)
             • "base-200"    - light gray (default)
             • "base-100"    - white/lightest
             • "base-300"    - darker gray
             • "transparent" - no background
  rounded          Border radius (default: xl)
             • "lg"  - 0.5rem (8px)
             • "xl"  - 0.75rem (12px) - default
             • "2xl" - 1rem (16px)
             • "3xl" - 1.5rem (24px)
  shadow           Card shadow (no default - cards have no shadow unless set)
             • "sm"  - subtle shadow
             • "md"  - medium shadow
             • "lg"  - larger shadow
             • "xl"  - prominent shadow
  border           Show border (default: false)
             • true  - show border
             • false - no border (default)
  border_color     Border color (default: base-300)
             • "base-300" - default gray
             • "base-200" - lighter
             • "primary"  - brand color
  border_width     Border width for bordered style (default: 2)
             • "1" - thin border
             • "2" - default
             • "4" - thick border
  item_padding     Card/item padding (default: 6 for card, 4 for minimal)
             • "4"  - 1rem (16px) - compact
             • "6"  - 1.5rem (24px) - default for cards
             • "8"  - 2rem (32px) - spacious
  align            Text alignment (default: center)
             • "center" - centered text (default)
             • "left"   - left-aligned text

ICON STYLING
  icon_type        Icon source type (default: emoji)
             • "emoji" - emoji characters (default)
             • "svg"   - inline SVG markup
             • "image" - image URL
  icon_size        Icon size (varies by style)
             • "2xl" - for icon-left (default: 2xl)
             • "3xl" - for card/bordered (default: 3xl)
             • "4xl" - for minimal (default: 4xl)
             • For image/svg: "6", "8", "10", "12" (Tailwind w-/h- units)
  icon_color       SVG icon color (default: primary)
             • "primary"   - brand color (default)
             • "secondary" - secondary brand
             • "accent"    - accent color
             • "info"      - blue
  icon_bg          Icon container background (optional)
             • "primary/10"   - light brand tint
             • "secondary/10" - light secondary tint
             • "base-200"     - light gray
  icon_container_size  Icon container size (default: 14)
             • "12" - 3rem (48px)
             • "14" - 3.5rem (56px) - default
             • "16" - 4rem (64px)
  icon_rounded     Icon container border radius (default: full)
             • "lg"   - rounded corners
             • "xl"   - more rounded
             • "full" - circular (default)
  icon_margin      Space below icon (default: 4)
             • "2" - 0.5rem (8px)
             • "4" - 1rem (16px) - default
             • "6" - 1.5rem (24px)
  icon_gap         Gap between icon and content for icon-left (default: 4)
             • "3" - 0.75rem (12px)
             • "4" - 1rem (16px) - default
             • "6" - 1.5rem (24px)
  show_icon        Show/hide icons (default: true)
             • true  - show icons (default)
             • false - hide icons

ITEM TEXT STYLING
  item_title_size  Item title font size (default: lg)
             • "base" - smaller
             • "lg"   - default
             • "xl"   - larger
  item_title_weight  Item title font weight (default: semibold)
             • "medium"   - lighter
             • "semibold" - default
             • "bold"     - heavier
  item_title_color Item title color (default: base-content)
             • "base-content" - default text
             • "primary"      - brand color
             • "white"        - for dark backgrounds
  title_margin     Space below item title (default: 2)
             • "1" - 0.25rem (4px) - tight
             • "2" - 0.5rem (8px) - default
             • "3" - 0.75rem (12px) - spacious
  item_desc_size   Item description font size (default: sm)
             • "xs"   - extra small
             • "sm"   - default
             • "base" - larger
  item_desc_color  Item description color (default: base-content/70)
             • "base-content/70" - 70% opacity (default)
             • "base-content/60" - lighter
             • "base-content"    - full opacity
  show_description Show item descriptions (default: true)
             • true  - show descriptions (default)
             • false - hide descriptions

HOVER EFFECTS
  hover_effect     Enable hover animations (default: false)
             • true  - enable hover effects
             • false - no hover effects (default)
  hover_shadow     Shadow on hover for card style (default: lg)
             • "md" - medium shadow
             • "lg" - default
             • "xl" - larger shadow
  hover_bg         Background color on hover
             • "base-200"    - light gray
             • "base-200/50" - semi-transparent
             • "base-100"    - white
  hover_border     Border color on hover for bordered style (default: primary)
             • "primary"   - brand color (default)
             • "secondary" - secondary brand
             • "accent"    - accent color

LINK STYLING (for card style with item links)
  link_color       Link text color (default: primary)
             • "primary"   - brand color (default)
             • "secondary" - secondary brand
             • "accent"    - accent color

CTA BUTTON
  cta_margin       Space above CTA button (default: 12)
             • "8"  - 2rem (32px)
             • "12" - 3rem (48px) - default
             • "16" - 4rem (64px)
  cta_style        Button style/color (default: primary)
             • "primary"   - brand color (default)
             • "secondary" - secondary brand
             • "accent"    - accent color
             • "neutral"   - neutral color
  cta_size         Button size (optional)
             • "sm" - small button
             • "md" - medium button
             • "lg" - large button
  cta_outline      Outline button style (default: false)
             • true  - outlined button
             • false - filled button (default)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple features grid:
{
  "title": "Why Choose Us",
  "subtitle": "Discover the benefits that set us apart",
  "items": [
    {"icon": "🚀", "title": "Fast", "description": "Lightning quick performance"},
    {"icon": "🔒", "title": "Secure", "description": "Enterprise-grade security"},
    {"icon": "📱", "title": "Mobile", "description": "Works on any device"}
  ]
}
config: {"style": "card", "columns": "3"}

With badge and CTA:
{
  "badge": "Features",
  "title": "Everything You Need",
  "items": [...],
  "primary_cta": {"text": "Get Started", "url": "/signup"}
}
config: {"style": "card", "hover_effect": true, "shadow": "md"}

Minimal clean layout:
config: {
  "style": "minimal",
  "columns": "4",
  "hover_effect": true,
  "hover_bg": "base-200"
}

Bordered cards:
config: {
  "style": "bordered",
  "border_width": "2",
  "border_color": "base-300",
  "hover_effect": true,
  "hover_border": "primary"
}

Horizontal icon-left layout:
config: {
  "style": "icon-left",
  "columns": "2",
  "icon_bg": "primary/10",
  "icon_rounded": "lg"
}

Dark theme section:
config: {
  "background_color": "neutral",
  "title_color": "white",
  "subtitle_color": "white/70",
  "card_bg": "base-100"
}
""",
        "default_content": {
            "badge": "Features",
            "title": "Why Choose Us",
            "subtitle": "Discover the benefits that set us apart from the competition",
            "items": [
                {
                    "icon": "🚀",
                    "title": "Lightning Fast",
                    "description": "Optimized for speed with cutting-edge technology",
                },
                {
                    "icon": "🔒",
                    "title": "Secure",
                    "description": "Enterprise-grade security to protect your data",
                },
                {
                    "icon": "📱",
                    "title": "Mobile First",
                    "description": "Responsive design that works on any device",
                },
                {
                    "icon": "🎨",
                    "title": "Customizable",
                    "description": "Tailor everything to match your brand",
                },
                {
                    "icon": "📊",
                    "title": "Reporting",
                    "description": "Detailed insights to track your success",
                },
                {
                    "icon": "🤝",
                    "title": "24/7 Support",
                    "description": "Expert help whenever you need it",
                },
            ],
            "primary_cta": {"text": "Get Started", "url": "#signup"},
        },
        "default_config": {
            "style": "card",
            "columns": "3",
            "gap": "6",
            "gap_md": "8",
            "padding_y": "16",
            "background_color": "base-100",
            "animate": True,
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_weight": "bold",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "subtitle_max_width": "2xl",
            "badge_color": "primary",
            "card_bg": "base-200",
            "rounded": "xl",
            "shadow": "md",
            "item_padding": "6",
            "align": "center",
            "icon_margin": "4",
            "item_title_size": "lg",
            "item_title_weight": "semibold",
            "item_title_color": "base-content",
            "title_margin": "2",
            "item_desc_size": "sm",
            "item_desc_color": "base-content/70",
            "hover_effect": True,
            "hover_shadow": "lg",
            "cta_style": "primary",
            "cta_margin": "12",
        },
    },
    {
        "name": "Benefits Grid - Minimal Style",
        "zone_type": ZoneType.BENEFITS_GRID,
        "template_file": "landing_pages/zones/benefits_grid.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/benefits_grid.html

Minimal benefits grid without cards - just icons, titles, and descriptions.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title (optional)
  title            Section heading
  subtitle         Description text

ITEMS
  items[]          Array of benefit items:
    icon           Emoji, SVG, or image URL
    title          Item heading
    description    Item description

CTA
  primary_cta.text   Button text
  primary_cta.url    Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style            "minimal" (REQUIRED for this template)
  columns          Grid columns: 2|3|4|5|6 (default: 4)
             • "3" - three columns
             • "4" - four columns (default for minimal)
             • "5" - five columns
  gap              Gap between items (default: 6)
  gap_md           Gap on medium+ screens (default: 8)
  padding_y        Vertical padding (default: 16)
  background_color Section background (default: base-100)
  animate          Enable animations (default: true)

ITEM STYLING
  item_padding     Item padding (default: 4)
             • "2" - compact
             • "4" - default
             • "6" - spacious
  align            Text alignment (default: center)
             • "center" - centered (default)
             • "left"   - left-aligned
  rounded          Border radius for hover effect (default: lg)

ICON STYLING
  icon_type        Icon type: emoji|svg|image (default: emoji)
  icon_size        Icon size (default: 4xl for emoji)
             • "3xl" - smaller
             • "4xl" - default for minimal
             • "5xl" - larger
  icon_color       SVG icon color (default: primary)
  icon_margin      Space below icon (default: 4)
  show_icon        Show/hide icons (default: true)

TEXT STYLING
  item_title_size  Title size (default: lg)
  item_title_weight  Title weight (default: semibold)
  item_title_color Title color (default: base-content)
  title_margin     Space below title (default: 2)
  item_desc_size   Description size (default: sm)
  item_desc_color  Description color (default: base-content/70)
  show_description Show descriptions (default: true)

HOVER EFFECTS
  hover_effect     Enable hover background (default: false)
  hover_bg         Background on hover (default: base-200)
             • "base-200" - light gray
             • "base-100" - white
             • "primary/5" - light brand tint

See "Benefits Grid - Card Style" for full documentation of all options.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Clean feature grid:
{
  "title": "Our Features",
  "subtitle": "Simple, powerful tools",
  "items": [
    {"icon": "✨", "title": "Simple", "description": "Easy to use"},
    {"icon": "⚡", "title": "Fast", "description": "Lightning quick"},
    {"icon": "🎯", "title": "Focused", "description": "Goal-oriented"},
    {"icon": "🔄", "title": "Sync", "description": "Always updated"}
  ]
}
config: {"style": "minimal", "columns": "4"}

With hover effect:
config: {
  "style": "minimal",
  "hover_effect": true,
  "hover_bg": "base-200"
}

Left-aligned minimal:
config: {
  "style": "minimal",
  "columns": "3",
  "align": "left"
}

Large icons:
config: {
  "style": "minimal",
  "icon_size": "5xl",
  "columns": "3"
}
""",
        "default_content": {
            "title": "Our Features",
            "subtitle": "Simple, powerful, and designed for you",
            "items": [
                {
                    "icon": "✨",
                    "title": "Simple Setup",
                    "description": "Get started in minutes, not hours",
                },
                {
                    "icon": "⚡",
                    "title": "Blazing Fast",
                    "description": "Performance you can feel",
                },
                {
                    "icon": "🎯",
                    "title": "Goal Focused",
                    "description": "Tools that help you achieve more",
                },
                {
                    "icon": "🔄",
                    "title": "Auto Sync",
                    "description": "Everything stays up to date",
                },
            ],
        },
        "default_config": {
            "style": "minimal",
            "columns": "4",
            "gap": "6",
            "gap_md": "8",
            "padding_y": "16",
            "background_color": "base-100",
            "animate": True,
            "item_padding": "4",
            "align": "center",
            "rounded": "lg",
            "icon_size": "4xl",
            "icon_margin": "4",
            "item_title_size": "lg",
            "item_title_weight": "semibold",
            "item_title_color": "base-content",
            "title_margin": "2",
            "item_desc_size": "sm",
            "item_desc_color": "base-content/70",
            "hover_effect": True,
            "hover_bg": "base-200",
        },
    },
    {
        "name": "Benefits Grid - Bordered Style",
        "zone_type": ZoneType.BENEFITS_GRID,
        "template_file": "landing_pages/zones/benefits_grid.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/benefits_grid.html

Benefits grid with bordered outline cards - clean, modern look.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title (optional)
  title            Section heading
  subtitle         Description text

ITEMS
  items[]          Array of benefit items:
    icon           Emoji, SVG, or image URL
    title          Item heading
    description    Item description

CTA
  primary_cta.text   Button text
  primary_cta.url    Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style            "bordered" (REQUIRED for this template)
  columns          Grid columns: 2|3|4|5|6 (default: 3)
  gap              Gap between items (default: 6)
  gap_md           Gap on medium+ screens (default: 8)
  padding_y        Vertical padding (default: 16)
  background_color Section background (default: base-100)
  animate          Enable animations (default: true)

BORDER STYLING
  border_width     Border thickness (default: 2)
             • "1" - thin border
             • "2" - default
             • "4" - thick border
  border_color     Border color (default: base-300)
             • "base-300" - default gray
             • "base-200" - lighter
             • "primary/20" - light brand
  rounded          Border radius (default: xl)
             • "lg"  - moderate rounding
             • "xl"  - default
             • "2xl" - more rounded

CARD STYLING
  card_bg          Card background (default: transparent)
             • "transparent" - no background (default)
             • "base-100"    - white
             • "base-200"    - light gray
  item_padding     Card padding (default: 6)
  align            Text alignment (default: center)

ICON STYLING
  icon_type        Icon type: emoji|svg|image (default: emoji)
  icon_size        Icon size (default: 3xl for emoji, 10 for svg/image)
  icon_color       SVG icon color (default: primary)
  icon_margin      Space below icon (default: 4)
  show_icon        Show/hide icons (default: true)

TEXT STYLING
  item_title_size  Title size (default: lg)
  item_title_weight  Title weight (default: semibold)
  item_title_color Title color (default: base-content)
  item_desc_size   Description size (default: sm)
  item_desc_color  Description color (default: base-content/70)
  show_description Show descriptions (default: true)

HOVER EFFECTS
  hover_effect     Enable hover animations (default: false)
  hover_border     Border color on hover (default: primary)
             • "primary"   - brand color (default)
             • "secondary" - secondary brand
             • "accent"    - accent color
  hover_bg         Background on hover (default: base-200/50)
             • "base-200/50" - semi-transparent gray
             • "base-200"    - solid gray
             • "primary/5"   - light brand tint

See "Benefits Grid - Card Style" for full documentation of all options.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic bordered grid:
{
  "title": "What You Get",
  "items": [
    {"icon": "📦", "title": "All-in-One", "description": "Complete solution"},
    {"icon": "🔧", "title": "Easy Config", "description": "No coding required"},
    {"icon": "📈", "title": "Growth Ready", "description": "Scales with you"}
  ]
}
config: {"style": "bordered", "columns": "3"}

With hover effect:
config: {
  "style": "bordered",
  "border_width": "2",
  "border_color": "base-300",
  "hover_effect": true,
  "hover_border": "primary",
  "hover_bg": "base-200/50"
}

Thicker borders:
config: {
  "style": "bordered",
  "border_width": "4",
  "border_color": "primary/20"
}

With background fill:
config: {
  "style": "bordered",
  "card_bg": "base-100",
  "border_color": "base-200"
}

Accent color scheme:
config: {
  "style": "bordered",
  "hover_border": "accent",
  "icon_color": "accent"
}
""",
        "default_content": {
            "title": "What You Get",
            "subtitle": "Everything you need to succeed",
            "items": [
                {
                    "icon": "📦",
                    "title": "All-in-One",
                    "description": "Complete solution in one package",
                },
                {
                    "icon": "🔧",
                    "title": "Easy Config",
                    "description": "No coding required",
                },
                {
                    "icon": "📈",
                    "title": "Growth Ready",
                    "description": "Scales with your business",
                },
            ],
        },
        "default_config": {
            "style": "bordered",
            "columns": "3",
            "gap": "6",
            "gap_md": "8",
            "padding_y": "16",
            "background_color": "base-100",
            "animate": True,
            "border_width": "2",
            "border_color": "base-300",
            "card_bg": "transparent",
            "rounded": "xl",
            "item_padding": "6",
            "align": "center",
            "icon_size": "3xl",
            "icon_color": "primary",
            "icon_margin": "4",
            "item_title_size": "lg",
            "item_title_weight": "semibold",
            "item_title_color": "base-content",
            "title_margin": "2",
            "item_desc_size": "sm",
            "item_desc_color": "base-content/70",
            "hover_effect": True,
            "hover_border": "primary",
            "hover_bg": "base-200/50",
        },
    },
    {
        "name": "Benefits Grid - Icon Left Style",
        "zone_type": ZoneType.BENEFITS_GRID,
        "template_file": "landing_pages/zones/benefits_grid.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/benefits_grid.html

Benefits grid with horizontal layout - icon on left, text on right.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title (optional)
  title            Section heading
  subtitle         Description text

ITEMS
  items[]          Array of benefit items:
    icon           Emoji, SVG, or image URL
    title          Item heading
    description    Item description

CTA
  primary_cta.text   Button text
  primary_cta.url    Button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style            "icon-left" (REQUIRED for this template)
  columns          Grid columns: 1|2|3 (default: 2)
             • "1" - single column (full width items)
             • "2" - two columns (default)
             • "3" - three columns
  gap              Gap between items (default: 6)
  gap_md           Gap on medium+ screens (default: 8)
  padding_y        Vertical padding (default: 16)
  background_color Section background (default: base-100)
  animate          Enable animations (default: true)

ITEM STYLING
  item_padding     Item padding (default: 4)
  card_bg          Optional item background (no default)
             • "base-100" - white
             • "base-200" - light gray
  rounded          Border radius when card_bg set (default: lg)
  icon_gap         Gap between icon and content (default: 4)
             • "3" - tighter
             • "4" - default
             • "6" - wider

ICON CONTAINER
  icon_bg          Icon background color (optional)
             • "primary/10"   - light brand (default when set)
             • "secondary/10" - secondary brand
             • "base-200"     - light gray
  icon_container_size  Container size (default: 12)
             • "10" - 2.5rem (40px)
             • "12" - 3rem (48px) - default
             • "14" - 3.5rem (56px)
  icon_rounded     Container border radius (default: lg)
             • "md"   - moderate
             • "lg"   - default
             • "xl"   - more rounded
             • "full" - circular

ICON STYLING
  icon_type        Icon type: emoji|svg|image (default: emoji)
  icon_size        Icon size (default: 2xl for emoji, 6 for svg/image)
             • "xl"  - smaller
             • "2xl" - default
             • "3xl" - larger
  icon_color       SVG icon color (default: primary)
  show_icon        Show/hide icons (default: true)

TEXT STYLING
  item_title_size  Title size (default: base)
             • "sm"   - smaller
             • "base" - default
             • "lg"   - larger
  item_title_weight  Title weight (default: semibold)
  item_title_color Title color (default: base-content)
  title_margin     Space below title (default: 1)
  item_desc_size   Description size (default: sm)
  item_desc_color  Description color (default: base-content/70)
  show_description Show descriptions (default: true)

HOVER EFFECTS
  hover_effect     Enable hover background (default: false)
  hover_bg         Background on hover (default: base-200)
             • "base-200" - light gray
             • "base-100" - white
             • "primary/5" - light brand tint

See "Benefits Grid - Card Style" for full documentation of all options.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

How it works steps:
{
  "title": "How It Works",
  "items": [
    {"icon": "1", "title": "Sign Up", "description": "Create your account"},
    {"icon": "2", "title": "Configure", "description": "Set up preferences"},
    {"icon": "3", "title": "Launch", "description": "Go live"},
    {"icon": "4", "title": "Grow", "description": "Scale your success"}
  ]
}
config: {"style": "icon-left", "columns": "2"}

With icon background:
config: {
  "style": "icon-left",
  "icon_bg": "primary/10",
  "icon_container_size": "12",
  "icon_rounded": "lg"
}

Circular icon containers:
config: {
  "style": "icon-left",
  "icon_bg": "secondary/10",
  "icon_rounded": "full"
}

Single column layout:
config: {
  "style": "icon-left",
  "columns": "1",
  "icon_gap": "6"
}

With card backgrounds:
config: {
  "style": "icon-left",
  "columns": "2",
  "card_bg": "base-100",
  "rounded": "xl",
  "hover_effect": true,
  "hover_bg": "base-200"
}
""",
        "default_content": {
            "title": "How It Works",
            "subtitle": "Simple steps to get started",
            "items": [
                {
                    "icon": "1️⃣",
                    "title": "Sign Up",
                    "description": "Create your free account in seconds",
                },
                {
                    "icon": "2️⃣",
                    "title": "Configure",
                    "description": "Set up your preferences and integrations",
                },
                {
                    "icon": "3️⃣",
                    "title": "Launch",
                    "description": "Go live and start seeing results",
                },
                {
                    "icon": "4️⃣",
                    "title": "Grow",
                    "description": "Scale your success with our tools",
                },
            ],
        },
        "default_config": {
            "style": "icon-left",
            "columns": "2",
            "gap": "6",
            "gap_md": "8",
            "padding_y": "16",
            "background_color": "base-100",
            "animate": True,
            "item_padding": "4",
            "rounded": "lg",
            "icon_gap": "4",
            "icon_bg": "primary/10",
            "icon_container_size": "12",
            "icon_rounded": "lg",
            "icon_size": "2xl",
            "icon_color": "primary",
            "item_title_size": "base",
            "item_title_weight": "semibold",
            "item_title_color": "base-content",
            "title_margin": "1",
            "item_desc_size": "sm",
            "item_desc_color": "base-content/70",
            "hover_effect": True,
            "hover_bg": "base-200",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
