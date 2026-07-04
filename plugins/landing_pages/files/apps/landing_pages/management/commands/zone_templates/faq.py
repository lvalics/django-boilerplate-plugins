"""
Faq zone templates.
"""

from ._base import ZoneType

FAQ_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "FAQ - Accordion (Default)",
        "zone_type": ZoneType.FAQ,
        "template_file": "landing_pages/zones/faq.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/faq.html

FAQ section with collapsible accordion items. Supports multiple display styles.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge           Optional badge/label above title
  title           Section heading text
  subtitle        Section description text

QUESTIONS
  questions[]     Array of Q&A items:
    question      Question text (required)
    answer        Answer text (supports HTML for formatting)

CONTACT CTA
  contact_text    Text above contact button
  contact_cta     {text, url} for contact button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              Display style (default: accordion)
                 • "accordion" - collapsible items (default)
                 • "cards" - grid of cards
                 • "two-column" - two column layout
                 • "simple" - minimal with dividers
                 • "boxed" - bordered boxes
  max_width          Container width (default: 4xl)
                 • "2xl" - 672px max width (narrow)
                 • "3xl" - 768px max width
                 • "4xl" - 896px max width (default)
                 • "5xl" - 1024px max width
                 • "6xl" - 1152px max width (wide)
  padding_y          Vertical padding in Tailwind units (default: 16)
                 • "8"  - 2rem (32px) - compact
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px) - spacious
                 • "24" - 6rem (96px) - very spacious
  gap                Space between items (default: 4)
                 • "2" - 0.5rem (8px) - tight
                 • "4" - 1rem (16px) - default
                 • "6" - 1.5rem (24px) - spacious
                 • "8" - 2rem (32px) - very spacious

SECTION HEADER
  header_align       Header text alignment (default: center)
                 • "left" - left aligned
                 • "center" - centered (default)
                 • "right" - right aligned
  header_margin      Margin below header (default: 12)
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px)

COLORS
  background_color   Section background (default: base-100)
                 • "base-100" - lightest background (default)
                 • "base-200" - light gray
                 • "base-300" - darker gray
                 • "primary" - brand color background
                 • "neutral" - dark neutral
  item_bg            FAQ item background (default: base-200)
                 • "base-100" - white/lightest
                 • "base-200" - light gray (default)
                 • "base-300" - darker gray
                 • "transparent" - no background

TYPOGRAPHY - TITLE
  title_size         Title size mobile (default: 3xl)
                 • "2xl" - 1.5rem (24px)
                 • "3xl" - 1.875rem (30px) - default
                 • "4xl" - 2.25rem (36px)
  title_size_md      Title size desktop (default: 4xl)
                 • "3xl" - 1.875rem (30px)
                 • "4xl" - 2.25rem (36px) - default
                 • "5xl" - 3rem (48px)
  title_weight       Title font weight (default: bold)
                 • "semibold" - 600 weight
                 • "bold" - 700 weight (default)
                 • "extrabold" - 800 weight
  title_color        Title text color (default: base-content)
                 • "base-content" - default text color
                 • "primary" - brand color
                 • "white" - for dark backgrounds

TYPOGRAPHY - SUBTITLE
  subtitle_size      Subtitle text size (default: lg)
                 • "base" - 1rem (16px)
                 • "lg" - 1.125rem (18px) - default
                 • "xl" - 1.25rem (20px)
  subtitle_color     Subtitle text color (default: base-content/70)
                 • "base-content/70" - 70% opacity (default)
                 • "base-content/60" - 60% opacity
                 • "base-content" - full opacity
  subtitle_max_width Subtitle max width (default: 2xl)
                 • "xl" - 576px
                 • "2xl" - 672px (default)
                 • "3xl" - 768px

TYPOGRAPHY - QUESTIONS
  question_size      Question text size (default: lg)
                 • "base" - 1rem (16px)
                 • "lg" - 1.125rem (18px) - default
                 • "xl" - 1.25rem (20px)
  question_weight    Question font weight (default: medium/semibold)
                 • "medium" - 500 weight (accordion default)
                 • "semibold" - 600 weight (other styles default)
                 • "bold" - 700 weight
  answer_color       Answer text color (default: base-content/80)
                 • "base-content/80" - 80% opacity (default)
                 • "base-content/70" - 70% opacity
                 • "base-content" - full opacity

BADGE
  badge_color        Badge color (default: primary)
                 • "primary" - brand color (default)
                 • "secondary" - secondary brand
                 • "accent" - accent color
                 • "neutral" - neutral color

ACCORDION OPTIONS (style: accordion)
  collapse_style     Collapse indicator style (default: plus)
                 • "plus" - plus/minus icon (default)
                 • "arrow" - chevron arrow
  allow_multiple     Allow multiple items open (default: false)
                 • false - only one open at a time (default)
                 • true - multiple can be open
  first_open         Open first item by default (default: false)
                 • false - all closed initially (default)
                 • true - first item open

CARDS OPTIONS (style: cards)
  columns            Grid columns (default: 2)
                 • "1" - single column
                 • "2" - two columns (default)
                 • "3" - three columns
  show_icon          Show question mark icon (default: false)
                 • false - no icon (default)
                 • true - show question mark icon
  icon_color         Icon color (default: primary)
                 • "primary" - brand color (default)
                 • "secondary" - secondary brand
                 • "accent" - accent color
  hover_effect       Enable hover shadow effect (default: false)
                 • false - no hover effect (default)
                 • true - shadow on hover

TWO-COLUMN OPTIONS (style: two-column)
  gap_x              Horizontal gap between columns (default: 12)
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px)
  gap_y              Vertical gap between items (default: 8)
                 • "6" - 1.5rem (24px)
                 • "8" - 2rem (32px) - default
                 • "10" - 2.5rem (40px)

SIMPLE OPTIONS (style: simple)
  divider_color      Divider line color (default: base-300)
                 • "base-200" - light divider
                 • "base-300" - default divider
                 • "base-content/20" - subtle divider
  item_padding       Vertical padding per item (default: 6)
                 • "4" - 1rem (16px)
                 • "6" - 1.5rem (24px) - default
                 • "8" - 2rem (32px)

BOXED OPTIONS (style: boxed)
  border_width       Border thickness (default: 2)
                 • "1" - 1px border
                 • "2" - 2px border (default)
  border_color       Border color (default: base-300)
                 • "base-200" - light border
                 • "base-300" - default border
                 • "base-content/20" - subtle border
  rounded            Border radius (default: xl)
                 • "lg" - 0.5rem (8px)
                 • "xl" - 0.75rem (12px) - default
                 • "2xl" - 1rem (16px)
  padding            Inner padding (default: 6)
                 • "4" - 1rem (16px)
                 • "6" - 1.5rem (24px) - default
                 • "8" - 2rem (32px)
  hover_effect       Enable hover border color change (default: false)
  hover_border       Hover border color (default: primary)
                 • "primary" - brand color (default)
                 • "secondary" - secondary brand
                 • "accent" - accent color

NUMBERING (all styles)
  numbered           Show question numbers (default: false)
                 • false - no numbers (default)
                 • true - show numbers
  number_color       Number badge color (default: primary)
                 • "primary" - brand color (default)
                 • "secondary" - secondary brand
                 • "accent" - accent color
  number_bg          Number circle background - boxed style (default: primary)
  number_text        Number circle text color - boxed style (default: primary-content)

BORDERS & SHADOWS (accordion, cards, boxed)
  rounded            Border radius (default: xl)
                 • "lg" - 0.5rem (8px)
                 • "xl" - 0.75rem (12px) - default
                 • "2xl" - 1rem (16px)
  shadow             Box shadow (default: none)
                 • "sm" - small shadow
                 • "md" - medium shadow
                 • "lg" - large shadow
  border             Enable border (default: false)
  border_color       Border color (default: base-300)

ANIMATION
  animate            Enable scroll animations (default: true)
                 • true - animate on scroll (default)
                 • "false" - disable animations

CONTACT CTA
  contact_margin     Margin above contact section (default: 12)
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px)
  contact_color      Contact text color (default: base-content/70)
  contact_btn_style  Contact button style (default: primary)
                 • "primary" - primary button (default)
                 • "secondary" - secondary button
                 • "outline" - outlined button
                 • "ghost" - ghost button

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic accordion with first item open:
{
  "title": "Frequently Asked Questions",
  "subtitle": "Everything you need to know about our product.",
  "questions": [
    {"question": "What is included?", "answer": "Full access to all features."},
    {"question": "Can I cancel?", "answer": "Yes, cancel anytime."}
  ]
}
config: {"style": "accordion", "first_open": true}

Accordion with multiple items open and numbering:
config: {
  "style": "accordion",
  "allow_multiple": true,
  "numbered": true,
  "collapse_style": "arrow"
}

Dark background with light items:
config: {
  "style": "accordion",
  "background_color": "neutral",
  "title_color": "white",
  "subtitle_color": "white/70",
  "item_bg": "base-100"
}

Minimal styling with shadows:
config: {
  "style": "accordion",
  "item_bg": "base-100",
  "shadow": "md",
  "border": true,
  "border_color": "base-200"
}
""",
        "default_content": {
            "badge": "FAQ",
            "title": "Frequently Asked Questions",
            "subtitle": "Everything you need to know about our product and service.",
            "questions": [
                {
                    "question": "What is included in my subscription?",
                    "answer": "Your subscription includes full access to all features, unlimited projects, priority support, and regular updates. You also get access to our exclusive community and resources.",
                },
                {
                    "question": "Can I cancel my subscription anytime?",
                    "answer": "Yes! You can cancel your subscription at any time with no penalties. Your access will continue until the end of your billing period.",
                },
                {
                    "question": "Do you offer refunds?",
                    "answer": "We offer a 30-day money-back guarantee. If you're not satisfied within the first 30 days, contact us for a full refund.",
                },
                {
                    "question": "How do I get support?",
                    "answer": "You can reach our support team via email, live chat, or through our help center. Pro and Enterprise customers get priority support with faster response times.",
                },
                {
                    "question": "Can I upgrade or downgrade my plan?",
                    "answer": "Absolutely! You can change your plan at any time. Upgrades take effect immediately, and downgrades take effect at the start of your next billing cycle.",
                },
            ],
            "contact_text": "Still have questions?",
            "contact_cta": {"text": "Contact Support", "url": "#contact"},
        },
        "default_config": {
            "style": "accordion",
            "max_width": "4xl",
            "padding_y": "16",
            "gap": "4",
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
            "collapse_style": "plus",
            "item_bg": "base-200",
            "rounded": "xl",
            "question_size": "lg",
            "question_weight": "medium",
            "answer_color": "base-content/80",
            "first_open": True,
            "allow_multiple": False,
            "animate": True,
            "contact_margin": "12",
            "contact_color": "base-content/70",
            "contact_btn_style": "primary",
        },
    },
    {
        "name": "FAQ - Cards",
        "zone_type": ZoneType.FAQ,
        "template_file": "landing_pages/zones/faq.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/faq.html

Grid of FAQ cards with optional icons.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge           Optional badge/label above title
  title           Section heading text
  subtitle        Section description text

QUESTIONS
  questions[]     Array of Q&A items:
    question      Question text (required)
    answer        Answer text

CONTACT CTA
  contact_text    Text above contact button
  contact_cta     {text, url} for contact button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

See "FAQ - Accordion (Default)" for full documentation.

KEY OPTIONS FOR CARDS STYLE:
  style              Must be "cards"
  columns            Grid columns: 1|2|3 (default: 2)
  show_icon          Show question mark icon (default: false)
  icon_color         Icon color (default: primary)
  hover_effect       Enable hover shadow (default: false)
  gap                Space between cards (default: 6)
  item_bg            Card background (default: base-200)
  shadow             Card shadow: sm|md|lg
  question_size      Question text size (default: lg)
  answer_color       Answer text color (default: base-content/70)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Two-column with icons and hover:
config: {
  "style": "cards",
  "columns": "2",
  "show_icon": true,
  "hover_effect": true
}

Three-column compact:
config: {
  "style": "cards",
  "columns": "3",
  "gap": "4",
  "question_size": "base"
}

Cards with shadows:
config: {
  "style": "cards",
  "shadow": "md",
  "item_bg": "base-100",
  "hover_effect": true
}

Dark theme cards:
config: {
  "style": "cards",
  "background_color": "neutral",
  "item_bg": "base-100",
  "title_color": "white",
  "subtitle_color": "white/70"
}
""",
        "default_content": {
            "title": "Common Questions",
            "questions": [
                {
                    "question": "How does billing work?",
                    "answer": "We bill monthly or annually depending on your plan. You can switch between billing cycles at any time.",
                },
                {
                    "question": "Is there a free trial?",
                    "answer": "Yes! All plans include a 14-day free trial. No credit card required to start.",
                },
                {
                    "question": "What payment methods do you accept?",
                    "answer": "We accept all major credit cards, PayPal, and bank transfers for Enterprise plans.",
                },
                {
                    "question": "How secure is my data?",
                    "answer": "We use bank-level encryption and are SOC 2 compliant. Your data is safe with us.",
                },
            ],
        },
        "default_config": {
            "style": "cards",
            "max_width": "4xl",
            "padding_y": "16",
            "gap": "6",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_weight": "bold",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "columns": "2",
            "item_bg": "base-200",
            "question_size": "lg",
            "answer_color": "base-content/70",
            "show_icon": True,
            "icon_color": "primary",
            "hover_effect": True,
            "animate": True,
        },
    },
    {
        "name": "FAQ - Two Column",
        "zone_type": ZoneType.FAQ,
        "template_file": "landing_pages/zones/faq.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/faq.html

Two-column Q&A layout with optional numbering or icons.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge           Optional badge/label above title
  title           Section heading text
  subtitle        Section description text

QUESTIONS
  questions[]     Array of Q&A items:
    question      Question text (required)
    answer        Answer text

CONTACT CTA
  contact_text    Text above contact button
  contact_cta     {text, url} for contact button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

See "FAQ - Accordion (Default)" for full documentation.

KEY OPTIONS FOR TWO-COLUMN STYLE:
  style              Must be "two-column"
  gap_x              Horizontal gap between columns (default: 12)
  gap_y              Vertical gap between items (default: 8)
  numbered           Show question numbers (default: false)
  number_color       Number badge color (default: primary)
  show_icon          Show question mark icon if not numbered (default: false)
  icon_color         Icon color (default: primary)
  question_size      Question text size (default: lg)
  question_weight    Question font weight (default: semibold)
  answer_color       Answer text color (default: base-content/70)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Numbered questions:
config: {
  "style": "two-column",
  "numbered": true,
  "number_color": "primary"
}

With icons instead of numbers:
config: {
  "style": "two-column",
  "show_icon": true,
  "icon_color": "secondary"
}

Compact spacing:
config: {
  "style": "two-column",
  "gap_x": "8",
  "gap_y": "6"
}

Wide gaps:
config: {
  "style": "two-column",
  "gap_x": "16",
  "gap_y": "10",
  "numbered": true
}
""",
        "default_content": {
            "badge": "Help Center",
            "title": "Questions & Answers",
            "questions": [
                {"question": "What's the refund policy?", "answer": "30-day money-back guarantee on all plans."},
                {"question": "Can I change plans later?", "answer": "Yes, upgrade or downgrade anytime."},
                {
                    "question": "Is there a setup fee?",
                    "answer": "No setup fees. Pay only for your subscription.",
                },
                {"question": "Do you offer discounts?", "answer": "Yes, save 20% with annual billing."},
                {"question": "How long is the free trial?", "answer": "14 days, no credit card required."},
                {
                    "question": "Can I export my data?",
                    "answer": "Yes, export your data anytime in multiple formats.",
                },
            ],
        },
        "default_config": {
            "style": "two-column",
            "max_width": "4xl",
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
            "gap_x": "12",
            "gap_y": "8",
            "question_size": "lg",
            "question_weight": "semibold",
            "answer_color": "base-content/70",
            "numbered": True,
            "number_color": "primary",
            "animate": True,
        },
    },
    {
        "name": "FAQ - Simple",
        "zone_type": ZoneType.FAQ,
        "template_file": "landing_pages/zones/faq.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/faq.html

Minimal divider-separated FAQ list with clean styling.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge           Optional badge/label above title
  title           Section heading text
  subtitle        Section description text

QUESTIONS
  questions[]     Array of Q&A items:
    question      Question text (required)
    answer        Answer text

CONTACT CTA
  contact_text    Text above contact button
  contact_cta     {text, url} for contact button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

See "FAQ - Accordion (Default)" for full documentation.

KEY OPTIONS FOR SIMPLE STYLE:
  style              Must be "simple"
  divider_color      Divider line color (default: base-300)
  item_padding       Vertical padding per item (default: 6)
  question_size      Question text size (default: lg)
  question_weight    Question font weight (default: semibold)
  answer_color       Answer text color (default: base-content/70)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Default simple:
config: {
  "style": "simple"
}

Subtle dividers:
config: {
  "style": "simple",
  "divider_color": "base-200"
}

Compact items:
config: {
  "style": "simple",
  "item_padding": "4",
  "question_size": "base"
}

Spacious items:
config: {
  "style": "simple",
  "item_padding": "8",
  "question_size": "xl"
}

Dark theme:
config: {
  "style": "simple",
  "background_color": "neutral",
  "title_color": "white",
  "divider_color": "base-content/20"
}
""",
        "default_content": {
            "title": "FAQ",
            "questions": [
                {
                    "question": "How do I get started?",
                    "answer": "Sign up for a free account and follow our quick start guide. You'll be up and running in minutes.",
                },
                {
                    "question": "Is there a mobile app?",
                    "answer": "Yes! We have iOS and Android apps available for download.",
                },
                {
                    "question": "Can I invite team members?",
                    "answer": "Team plans allow unlimited team members with role-based permissions.",
                },
            ],
        },
        "default_config": {
            "style": "simple",
            "max_width": "4xl",
            "padding_y": "16",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_weight": "bold",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "divider_color": "base-300",
            "item_padding": "6",
            "question_size": "lg",
            "question_weight": "semibold",
            "answer_color": "base-content/70",
            "animate": True,
        },
    },
    {
        "name": "FAQ - Boxed",
        "zone_type": ZoneType.FAQ,
        "template_file": "landing_pages/zones/faq.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/faq.html

Bordered box style FAQ items with optional numbering and hover effects.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge           Optional badge/label above title
  title           Section heading text
  subtitle        Section description text

QUESTIONS
  questions[]     Array of Q&A items:
    question      Question text (required)
    answer        Answer text

CONTACT CTA
  contact_text    Text above contact button
  contact_cta     {text, url} for contact button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

See "FAQ - Accordion (Default)" for full documentation.

KEY OPTIONS FOR BOXED STYLE:
  style              Must be "boxed"
  gap                Space between boxes (default: 4)
  border_width       Border thickness (default: 2)
  border_color       Border color (default: base-300)
  rounded            Border radius (default: xl)
  padding            Inner padding (default: 6)
  hover_effect       Enable hover border change (default: false)
  hover_border       Hover border color (default: primary)
  numbered           Show circular number badges (default: false)
  number_bg          Number circle background (default: primary)
  number_text        Number circle text color (default: primary-content)
  question_size      Question text size (default: lg)
  question_weight    Question font weight (default: semibold)
  answer_color       Answer text color (default: base-content/70)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Numbered with hover:
config: {
  "style": "boxed",
  "numbered": true,
  "hover_effect": true
}

Thick borders:
config: {
  "style": "boxed",
  "border_width": "4",
  "border_color": "primary/30"
}

Rounded corners:
config: {
  "style": "boxed",
  "rounded": "2xl",
  "padding": "8"
}

Accent color scheme:
config: {
  "style": "boxed",
  "numbered": true,
  "number_bg": "accent",
  "number_text": "accent-content",
  "hover_border": "accent"
}

Minimal boxed:
config: {
  "style": "boxed",
  "border_width": "1",
  "border_color": "base-200",
  "rounded": "lg"
}
""",
        "default_content": {
            "title": "Got Questions?",
            "subtitle": "We've got answers",
            "questions": [
                {
                    "question": "What makes you different?",
                    "answer": "We focus on simplicity and user experience. Our tool is designed to be intuitive while still being powerful enough for professionals.",
                },
                {
                    "question": "Do you offer custom plans?",
                    "answer": "Yes! Enterprise customers can work with our team to create a custom plan that fits their specific needs.",
                },
                {
                    "question": "Is training available?",
                    "answer": "We offer free onboarding sessions and have an extensive knowledge base with video tutorials.",
                },
                {
                    "question": "What's your uptime guarantee?",
                    "answer": "We guarantee 99.9% uptime SLA for all paid plans, backed by service credits.",
                },
            ],
            "contact_text": "Can't find what you're looking for?",
            "contact_cta": {"text": "Ask Us Anything", "url": "#contact"},
        },
        "default_config": {
            "style": "boxed",
            "max_width": "4xl",
            "padding_y": "16",
            "gap": "4",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_weight": "bold",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "border_width": "2",
            "border_color": "base-300",
            "rounded": "xl",
            "padding": "6",
            "question_size": "lg",
            "question_weight": "semibold",
            "answer_color": "base-content/70",
            "numbered": True,
            "number_bg": "primary",
            "number_text": "primary-content",
            "hover_effect": True,
            "hover_border": "primary",
            "animate": True,
            "contact_margin": "12",
            "contact_color": "base-content/70",
            "contact_btn_style": "primary",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
