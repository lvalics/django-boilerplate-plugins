"""
Pricing zone templates.
"""

from ._base import ZoneType

PRICING_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Pricing - Cards (Default)",
        "zone_type": ZoneType.PRICING,
        "template_file": "landing_pages/zones/pricing.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/pricing.html

Card-based pricing table with featured plan highlighting and scroll animations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  title             Main section heading
  subtitle          Supporting description text
  badge             Small badge/label above title

BILLING TOGGLE
  show_toggle       Show monthly/yearly toggle switch (boolean)
  toggle_monthly    Monthly label text (default: "Monthly")
  toggle_annual     Annual label text (default: "Annual")
  toggle_discount   Discount badge text (e.g., "Save 20%")

PLANS ARRAY
  plans[]           Array of pricing plan objects:
    name              Plan name (e.g., "Starter", "Professional")
    description       Short plan description
    icon              Optional emoji/icon before plan name
    currency          Currency symbol (default: "$")
    price             Display price (number or string)
    original_price    Strikethrough price for discounts (optional)
    period            Billing period text (e.g., "month", "year")
    featured          Boolean - highlight this plan with border/scale
    featured_text     Badge text for featured plan (e.g., "Most Popular")
    note              Small note below CTA button

    features[]        Array of feature items:
                      Simple: ["Feature 1", "Feature 2"]
                      With included flag: [{"text": "Feature", "included": true}]
                      Excluded features show strikethrough

    cta_text          Call-to-action button text
    cta_url           CTA button URL

FOOTER
  guarantee_text    Money-back guarantee or footer note

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             Pricing table style (default: cards)
              * "cards" - elevated card with shadows and borders (default)
              * "minimal" - flat cards with subtle backgrounds
              * "gradient" - gradient background on featured plans
              * "single" - single prominent plan display

LAYOUT
  max_width         Container width: 4xl|5xl|6xl|7xl (default: 6xl)
              * "4xl" - 896px max width (compact)
              * "5xl" - 1024px max width
              * "6xl" - 1152px max width (default)
              * "7xl" - 1280px max width (wide)
  padding_y         Vertical padding in Tailwind units (default: 16)
              * "12" - 3rem (48px) - compact
              * "16" - 4rem (64px) - default
              * "20" - 5rem (80px) - spacious
              * "24" - 6rem (96px) - very spacious
  gap               Gap between pricing cards (default: 8)
              * "4"  - 1rem (16px) - tight
              * "6"  - 1.5rem (24px)
              * "8"  - 2rem (32px) - default
              * "10" - 2.5rem (40px) - wide

HEADER OPTIONS
  header_align      Header text alignment (default: center)
              * "center" - centered text (default)
              * "left" - left-aligned text
              * "right" - right-aligned text
  header_margin     Header bottom margin (default: 12)
              * "8"  - 2rem (32px) - compact
              * "12" - 3rem (48px) - default
              * "16" - 4rem (64px) - spacious

COLORS
  background_color  Section background color (default: base-100)
              * "base-100" - lightest background (default)
              * "base-200" - light gray
              * "base-300" - darker gray
              * "neutral" - dark neutral
  card_bg           Card background color (default: base-100)
              * "base-100" - white/light (default)
              * "base-200" - light gray
              * "white" - pure white
  title_color       Heading text color (default: base-content)
              * "base-content" - default text color
              * "primary" - brand color
              * "white" - for dark backgrounds
  subtitle_color    Subtitle text color (default: base-content/70)
              * "base-content/70" - 70% opacity (default)
              * "base-content/60" - lighter text

BADGE OPTIONS
  badge_color       Header badge color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
              * "info" - blue
              * "success" - green

TYPOGRAPHY
  title_size        Title size on mobile (default: 3xl)
              * "2xl" - smaller title
              * "3xl" - default
              * "4xl" - larger title
  title_size_md     Title size on medium+ screens (default: 4xl)
              * "3xl" - smaller
              * "4xl" - default
              * "5xl" - larger
  title_weight      Title font weight (default: bold)
              * "semibold" - semi-bold
              * "bold" - bold (default)
              * "extrabold" - extra bold
  subtitle_size     Subtitle text size (default: lg)
              * "base" - normal size
              * "lg" - large (default)
              * "xl" - extra large
  subtitle_max_width  Subtitle max width (default: 2xl)
              * "xl" - 576px
              * "2xl" - 672px (default)
              * "3xl" - 768px

BILLING TOGGLE
  toggle_color      Toggle switch color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
  toggle_text_color Toggle label text color (default: base-content/70)
              * "base-content/70" - 70% opacity (default)
              * "base-content" - full opacity
  discount_badge_color  Discount badge color (default: success)
              * "success" - green (default)
              * "primary" - brand color
              * "warning" - yellow/orange

CARD STYLING
  shadow            Card shadow level (default: xl)
              * "lg" - large shadow
              * "xl" - extra large shadow (default)
              * "2xl" - double extra large
              * "" - no shadow
  hover_effect      Enable hover animations (default: false)
              * false - no hover effect (default)
              * true - lift and shadow on hover
  featured_border   Featured plan border color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
  featured_badge_color  Featured plan badge color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color

PLAN CONTENT
  plan_name_size    Plan name text size (default: 2xl)
              * "xl" - smaller
              * "2xl" - default
              * "3xl" - larger
  plan_desc_color   Plan description color (default: base-content/70)
              * "base-content/70" - 70% opacity (default)
              * "base-content/60" - lighter

PRICING
  price_size        Price text size (default: 4xl)
              * "3xl" - smaller
              * "4xl" - default
              * "5xl" - larger
  price_color       Price text color (default: base-content)
              * "base-content" - default text color
              * "primary" - brand color
  price_margin      Price vertical margin (default: 6)
              * "4" - 1rem (16px) - compact
              * "6" - 1.5rem (24px) - default
              * "8" - 2rem (32px) - spacious
  period_color      Billing period text color (default: base-content/70)
              * "base-content/70" - 70% opacity (default)
              * "base-content/60" - lighter

FEATURES LIST
  feature_gap       Gap between feature items (default: 3)
              * "2" - 0.5rem (8px) - tight
              * "3" - 0.75rem (12px) - default
              * "4" - 1rem (16px) - spacious
  check_color       Checkmark icon color (default: success)
              * "success" - green (default)
              * "primary" - brand color
              * "info" - blue
  excluded_icon_color  Excluded feature X icon color (default: base-content/30)
              * "base-content/30" - 30% opacity (default)
              * "error" - red

BUTTONS
  btn_style         Regular plan button style (default: outline)
              * "outline" - outlined button (default)
              * "ghost" - transparent background
              * "primary" - filled primary
              * "secondary" - filled secondary
  featured_btn_style  Featured plan button style (default: primary)
              * "primary" - filled primary (default)
              * "secondary" - filled secondary
              * "accent" - filled accent

FOOTER
  guarantee_margin  Guarantee note top margin (default: 8)
              * "6" - 1.5rem (24px) - compact
              * "8" - 2rem (32px) - default
              * "12" - 3rem (48px) - spacious
  guarantee_color   Guarantee text color (default: base-content/70)
              * "base-content/70" - 70% opacity (default)
              * "base-content/60" - lighter

ANIMATION
  animate           Enable scroll animations (default: true)
              * true - animate on scroll (default)
              * false - no animations (set as string "false")

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic three-tier pricing:
{
  "title": "Choose Your Plan",
  "subtitle": "Start free, upgrade when you need.",
  "plans": [
    {"name": "Free", "price": "0", "period": "month", "features": ["5 projects", "Basic support"], "cta_text": "Get Started", "cta_url": "/signup"},
    {"name": "Pro", "price": "29", "period": "month", "features": ["Unlimited projects", "Priority support"], "cta_text": "Upgrade", "cta_url": "/upgrade", "featured": true, "featured_text": "Popular"},
    {"name": "Team", "price": "99", "period": "month", "features": ["Everything in Pro", "Team features"], "cta_text": "Contact Us", "cta_url": "/contact"}
  ]
}
config: {"style": "cards"}

With billing toggle and discount:
{
  "badge": "Pricing",
  "title": "Simple, Transparent Pricing",
  "show_toggle": true,
  "toggle_discount": "Save 20%",
  "plans": [...],
  "guarantee_text": "30-day money-back guarantee"
}
config: {"style": "cards", "hover_effect": true}

Dark theme pricing:
config: {
  "style": "cards",
  "background_color": "neutral",
  "card_bg": "base-200",
  "title_color": "white",
  "subtitle_color": "white/70"
}

Compact layout with tight spacing:
config: {
  "style": "cards",
  "padding_y": "12",
  "gap": "4",
  "header_margin": "8",
  "price_margin": "4"
}
""",
        "default_content": {
            "badge": "Pricing",
            "title": "Simple, Transparent Pricing",
            "subtitle": "Choose the plan that's right for you. All plans include a 14-day free trial.",
            "show_toggle": False,
            "toggle_monthly": "",
            "toggle_annual": "",
            "toggle_discount": "",
            "plans": [
                {
                    "name": "Starter",
                    "description": "Perfect for individuals and small projects",
                    "icon": "",
                    "currency": "$",
                    "monthly_price": "9",
                    "monthly_original_price": "",
                    "annual_price": "90",
                    "annual_original_price": "108",
                    "features": [
                        "Up to 5 projects",
                        "Basic reporting",
                        "Email support",
                        "1GB storage",
                    ],
                    "cta_text": "Get Started",
                    "cta_url": "#signup-starter",
                    "featured": False,
                    "featured_text": "",
                    "note": "",
                },
                {
                    "name": "Professional",
                    "description": "Best for growing teams and businesses",
                    "icon": "",
                    "currency": "$",
                    "monthly_price": "29",
                    "monthly_original_price": "49",
                    "annual_price": "290",
                    "annual_original_price": "348",
                    "features": [
                        "Unlimited projects",
                        "Advanced reporting",
                        "Priority support",
                        "10GB storage",
                        "Team collaboration",
                        "API access",
                    ],
                    "cta_text": "Start Free Trial",
                    "cta_url": "#signup-pro",
                    "featured": True,
                    "featured_text": "Most Popular",
                    "note": "",
                },
                {
                    "name": "Enterprise",
                    "description": "For large organizations with custom needs",
                    "icon": "",
                    "currency": "$",
                    "monthly_price": "99",
                    "monthly_original_price": "",
                    "annual_price": "990",
                    "annual_original_price": "1188",
                    "features": [
                        "Everything in Pro",
                        "Custom integrations",
                        "Dedicated support",
                        "Unlimited storage",
                        "SLA guarantee",
                        "Custom training",
                    ],
                    "cta_text": "Contact Sales",
                    "cta_url": "#contact",
                    "featured": False,
                    "featured_text": "",
                    "note": "",
                },
            ],
            "guarantee_text": "30-day money-back guarantee. No questions asked.",
        },
        "default_config": {
            "style": "cards",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "8",
            "header_align": "center",
            "header_margin": "12",
            "background_color": "base-100",
            "card_bg": "base-100",
            "title_color": "base-content",
            "subtitle_color": "base-content/70",
            "badge_color": "primary",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_weight": "bold",
            "subtitle_size": "lg",
            "subtitle_max_width": "2xl",
            "shadow": "xl",
            "hover_effect": False,
            "featured_border": "primary",
            "featured_badge_color": "primary",
            "plan_name_size": "2xl",
            "plan_desc_color": "base-content/70",
            "price_size": "4xl",
            "price_color": "base-content",
            "price_margin": "6",
            "period_color": "base-content/70",
            "feature_gap": "3",
            "check_color": "success",
            "excluded_icon_color": "base-content/30",
            "btn_style": "outline",
            "featured_btn_style": "primary",
            "guarantee_margin": "8",
            "guarantee_color": "base-content/70",
            "animate": True,
        },
    },
    {
        "name": "Pricing - Minimal",
        "zone_type": ZoneType.PRICING,
        "template_file": "landing_pages/zones/pricing.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/pricing.html

Clean minimal pricing cards with flat styling and subtle backgrounds.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

See "Pricing - Cards" for full content field documentation.

Key differences:
- Featured plans use inverted colors (solid background)
- Simpler visual hierarchy with flat design

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             "minimal" (REQUIRED for this template)

LAYOUT OPTIONS
  padding           Card inner padding (default: 8)
              * "6"  - 1.5rem (24px) - compact
              * "8"  - 2rem (32px) - default
              * "10" - 2.5rem (40px) - spacious
  rounded           Card border radius (default: 2xl)
              * "xl" - 0.75rem (12px)
              * "2xl" - 1rem (16px) - default
              * "3xl" - 1.5rem (24px)
  gap               Gap between cards (default: 6)
              * "4"  - 1rem (16px)
              * "6"  - 1.5rem (24px) - default
              * "8"  - 2rem (32px)

COLORS
  card_bg           Regular card background (default: base-200)
              * "base-200" - light gray (default)
              * "base-100" - white
              * "base-300" - darker gray
  featured_bg       Featured plan background (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
              * "neutral" - dark neutral
  featured_text     Featured plan text color (default: primary-content)
              * "primary-content" - contrasting text (default)
              * "white" - white text

All other config options from "Pricing - Cards" are also available.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Two-column minimal:
{
  "title": "Choose Your Plan",
  "plans": [
    {"name": "Basic", "price": "0", "period": "month", "features": ["5 projects"], "cta_text": "Start Free", "cta_url": "#"},
    {"name": "Pro", "price": "19", "period": "month", "features": ["Unlimited"], "cta_text": "Get Pro", "cta_url": "#", "featured": true}
  ]
}
config: {"style": "minimal"}

Rounded corners with spacious padding:
config: {
  "style": "minimal",
  "padding": "10",
  "rounded": "3xl",
  "gap": "8"
}

Custom featured color:
config: {
  "style": "minimal",
  "featured_bg": "secondary",
  "featured_text": "secondary-content"
}
""",
        "default_content": {
            "title": "Choose Your Plan",
            "subtitle": "",
            "badge": "",
            "plans": [
                {
                    "name": "Basic",
                    "description": "For hobbyists",
                    "currency": "$",
                    "price": "0",
                    "period": "month",
                    "features": [
                        "5 projects",
                        "Community support",
                        "Basic features",
                    ],
                    "cta_text": "Start Free",
                    "cta_url": "#",
                    "featured": False,
                },
                {
                    "name": "Pro",
                    "description": "For professionals",
                    "currency": "$",
                    "price": "19",
                    "period": "month",
                    "features": [
                        "Unlimited projects",
                        "Priority support",
                        "All features",
                        "Reporting",
                    ],
                    "cta_text": "Get Pro",
                    "cta_url": "#",
                    "featured": True,
                },
            ],
            "guarantee_text": "",
        },
        "default_config": {
            "style": "minimal",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "6",
            "padding": "8",
            "rounded": "2xl",
            "background_color": "base-100",
            "card_bg": "base-200",
            "featured_bg": "primary",
            "featured_text": "primary-content",
            "animate": True,
        },
    },
    {
        "name": "Pricing - Gradient",
        "zone_type": ZoneType.PRICING,
        "template_file": "landing_pages/zones/pricing.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/pricing.html

Gradient background pricing cards with vibrant featured plan styling.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

See "Pricing - Cards" for full content field documentation.

Key differences:
- Featured plans display gradient backgrounds
- Badges work on both featured and regular plans
- High visual impact design

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             "gradient" (REQUIRED for this template)

GRADIENT OPTIONS
  gradient_from     Gradient start color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
              * "info" - blue
  gradient_to       Gradient end color (default: secondary)
              * "secondary" - secondary brand (default)
              * "primary" - brand color
              * "accent" - accent color
              * "purple-600" - custom purple

CARD OPTIONS
  card_bg           Regular card background (default: base-200)
              * "base-100" - white
              * "base-200" - light gray (default)
              * "base-300" - darker gray
  shadow            Card shadow level (default: none specified)
              * "lg" - large shadow
              * "xl" - extra large shadow
              * "2xl" - double extra large
              * "" - no shadow
  gap               Gap between cards (default: 6)
              * "4"  - 1rem (16px)
              * "6"  - 1.5rem (24px) - default
              * "8"  - 2rem (32px)

All other config options from "Pricing - Cards" are also available.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Monthly/Annual comparison:
{
  "badge": "Limited Offer",
  "title": "Invest in Your Future",
  "subtitle": "Join thousands of satisfied customers",
  "plans": [
    {"name": "Monthly", "price": "49", "period": "month", "features": ["Full access", "Cancel anytime"], "cta_text": "Start Monthly", "cta_url": "#"},
    {"name": "Annual", "price": "399", "original_price": "588", "period": "year", "features": ["Full access", "Save 32%"], "cta_text": "Get Annual Deal", "cta_url": "#", "featured": true, "featured_text": "Best Value"}
  ],
  "guarantee_text": "100% satisfaction guaranteed"
}
config: {"style": "gradient"}

Custom gradient colors:
config: {
  "style": "gradient",
  "gradient_from": "purple-500",
  "gradient_to": "pink-500"
}

With shadows:
config: {
  "style": "gradient",
  "shadow": "xl",
  "gap": "8"
}
""",
        "default_content": {
            "badge": "Limited Offer",
            "title": "Invest in Your Future",
            "subtitle": "Join thousands of satisfied customers",
            "plans": [
                {
                    "name": "Monthly",
                    "currency": "$",
                    "price": "49",
                    "period": "month",
                    "features": [
                        "Full access",
                        "Cancel anytime",
                        "24/7 support",
                    ],
                    "cta_text": "Start Monthly",
                    "cta_url": "#",
                    "featured": False,
                },
                {
                    "name": "Annual",
                    "currency": "$",
                    "price": "399",
                    "original_price": "588",
                    "period": "year",
                    "features": [
                        "Full access",
                        "Save 32%",
                        "Priority support",
                        "Exclusive content",
                    ],
                    "cta_text": "Get Annual Deal",
                    "cta_url": "#",
                    "featured": True,
                    "featured_text": "Best Value",
                },
            ],
            "guarantee_text": "100% satisfaction guaranteed",
        },
        "default_config": {
            "style": "gradient",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "6",
            "background_color": "base-100",
            "card_bg": "base-200",
            "gradient_from": "primary",
            "gradient_to": "secondary",
            "animate": True,
        },
    },
    {
        "name": "Pricing - Single Plan",
        "zone_type": ZoneType.PRICING,
        "template_file": "landing_pages/zones/pricing.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/pricing.html

Single prominent plan display for simple pricing or featured offerings.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  title             Main section heading
  subtitle          Supporting description text

SINGLE PLAN (first item in plans array)
  plans[0]          Single plan object:
    name              Plan name
    description       Plan description
    badge             Badge text on plan card
    currency          Currency symbol (default: "$")
    price             Display price
    original_price    Strikethrough price (optional)
    period            Billing period text
    guarantee         Guarantee text with shield icon

    features[]        Array of feature strings

    cta_text          CTA button text
    cta_url           CTA button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style             "single" (REQUIRED for this template)

LAYOUT
  max_width         Container width (plan card max-width is always lg)
  padding_y         Vertical padding (default: 16)

COLORS
  card_bg           Plan card background (default: base-100)
              * "base-100" - white/light (default)
              * "base-200" - light gray
  background_color  Section background (default: base-100)
              * "base-100" - lightest (default)
              * "base-200" - light gray
              * "neutral" - dark

BADGE
  badge_style       Plan badge color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
              * "success" - green

ANIMATION
  animate           Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple single plan:
{
  "title": "One Simple Price",
  "subtitle": "Everything you need, nothing you don't",
  "plans": [{
    "name": "Complete Access",
    "price": "79",
    "period": "month",
    "description": "Get everything with one subscription",
    "features": ["Unlimited projects", "All features", "Priority support"],
    "cta_text": "Start Free Trial",
    "cta_url": "#"
  }]
}
config: {"style": "single"}

With badge and guarantee:
{
  "title": "Premium Plan",
  "plans": [{
    "name": "Pro",
    "badge": "Best Value",
    "price": "99",
    "original_price": "149",
    "period": "month",
    "features": ["Everything included"],
    "cta_text": "Get Started",
    "cta_url": "#",
    "guarantee": "14-day free trial. Cancel anytime."
  }]
}
config: {"style": "single", "badge_style": "success"}

Dark background:
config: {
  "style": "single",
  "background_color": "base-200",
  "card_bg": "base-100"
}
""",
        "default_content": {
            "title": "One Simple Price",
            "subtitle": "Everything you need, nothing you don't",
            "plans": [
                {
                    "name": "Complete Access",
                    "description": "Get everything with one simple subscription",
                    "badge": "",
                    "currency": "$",
                    "price": "79",
                    "original_price": "",
                    "period": "month",
                    "features": [
                        "Unlimited projects & users",
                        "All premium features",
                        "Priority 24/7 support",
                        "Custom integrations",
                        "Advanced reporting",
                        "Dedicated account manager",
                    ],
                    "cta_text": "Start Your Free Trial",
                    "cta_url": "#",
                    "guarantee": "14-day free trial. Cancel anytime.",
                },
            ],
            "guarantee_text": "",
        },
        "default_config": {
            "style": "single",
            "max_width": "6xl",
            "padding_y": "16",
            "background_color": "base-100",
            "card_bg": "base-100",
            "badge_style": "primary",
            "animate": True,
        },
    },
    {
        "name": "Pricing - With Billing Toggle",
        "zone_type": ZoneType.PRICING,
        "template_file": "landing_pages/zones/pricing.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/pricing.html

Card-based pricing with monthly/annual billing toggle switch.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

See "Pricing - Cards" for full content field documentation.

BILLING TOGGLE (specific to this template)
  show_toggle       true (REQUIRED to show toggle)
  toggle_monthly    Monthly label (default: "Monthly")
  toggle_annual     Annual label (default: "Annual")
  toggle_discount   Discount badge text (e.g., "Save 20%")

Note: The toggle is visual only. JavaScript is required to switch prices.
Use data attributes on price elements for dynamic price switching.

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

TOGGLE OPTIONS
  toggle_color      Toggle switch color (default: primary)
              * "primary" - brand color (default)
              * "secondary" - secondary brand
              * "accent" - accent color
  toggle_text_color Toggle label text color (default: base-content/70)
              * "base-content/70" - 70% opacity (default)
              * "base-content" - full opacity
  discount_badge_color  Discount badge color (default: success)
              * "success" - green (default)
              * "primary" - brand color
              * "warning" - yellow/orange
              * "info" - blue

All other config options from "Pricing - Cards" are also available.

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

With discount badge:
{
  "badge": "Pricing",
  "title": "Choose Your Plan",
  "show_toggle": true,
  "toggle_discount": "Save 20%",
  "plans": [...]
}
config: {"style": "cards", "toggle_color": "primary"}

Custom toggle colors:
config: {
  "style": "cards",
  "toggle_color": "accent",
  "toggle_text_color": "base-content",
  "discount_badge_color": "info"
}

Annual savings emphasis:
{
  "show_toggle": true,
  "toggle_monthly": "Pay Monthly",
  "toggle_annual": "Pay Yearly",
  "toggle_discount": "2 Months Free!"
}
config: {"style": "cards", "discount_badge_color": "success"}
""",
        "default_content": {
            "badge": "Pricing",
            "title": "Flexible Plans for Every Need",
            "subtitle": "Switch between monthly and annual billing. Save more when you commit annually.",
            "show_toggle": True,
            "toggle_monthly": "Monthly",
            "toggle_annual": "Annual",
            "toggle_discount": "Save 20%",
            "plans": [
                {
                    "name": "Starter",
                    "description": "For individuals",
                    "currency": "$",
                    "monthly_price": "9",
                    "monthly_original_price": "",
                    "annual_price": "86",
                    "annual_original_price": "108",
                    "features": [
                        "5 projects",
                        "Basic support",
                        "1GB storage",
                    ],
                    "cta_text": "Get Started",
                    "cta_url": "#",
                },
                {
                    "name": "Professional",
                    "description": "For teams",
                    "currency": "$",
                    "monthly_price": "29",
                    "monthly_original_price": "",
                    "annual_price": "278",
                    "annual_original_price": "348",
                    "features": [
                        "Unlimited projects",
                        "Priority support",
                        "10GB storage",
                        "Team features",
                    ],
                    "cta_text": "Start Trial",
                    "cta_url": "#",
                    "featured": True,
                    "featured_text": "Most Popular",
                },
                {
                    "name": "Enterprise",
                    "description": "For organizations",
                    "currency": "$",
                    "monthly_price": "99",
                    "monthly_original_price": "",
                    "annual_price": "950",
                    "annual_original_price": "1188",
                    "features": [
                        "Everything in Pro",
                        "Custom integrations",
                        "Dedicated support",
                        "Unlimited storage",
                    ],
                    "cta_text": "Contact Sales",
                    "cta_url": "#",
                },
            ],
            "guarantee_text": "30-day money-back guarantee",
        },
        "default_config": {
            "style": "cards",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "8",
            "background_color": "base-100",
            "toggle_color": "primary",
            "toggle_text_color": "base-content/70",
            "discount_badge_color": "success",
            "hover_effect": True,
            "animate": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
