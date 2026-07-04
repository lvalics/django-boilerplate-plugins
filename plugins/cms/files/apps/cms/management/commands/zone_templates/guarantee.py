"""
Guarantee zone templates.
"""

from ._base import ZoneType

GUARANTEE_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Guarantee - Card (Default)",
        "zone_type": ZoneType.GUARANTEE,
        "template_file": "cms/zones/guarantee.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/guarantee.html

Centered card-based guarantee/trust section with optional badge and feature list.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Main heading text (e.g., "100% Satisfaction Guarantee")
text            Description text (supports HTML, line breaks)
icon            Emoji or custom icon (e.g., "🛡️", "✓")
                • If empty, displays shield SVG icon
badge           Small badge text above title (e.g., "Risk Free")
features[]      Array of feature strings displayed with checkmarks
                • Example: ["Full refund within 30 days", "No questions asked"]
terms           Terms/conditions text below features

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "card" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl
                 • "2xl" - 672px max width (compact)
                 • "3xl" - 768px max width
                 • "4xl" - 896px max width (default)
                 • "5xl" - 1024px max width
                 • "6xl" - 1152px max width (wide)
  padding_y          Section vertical padding in Tailwind units
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
                 • "24" - 6rem (96px)
  padding            Card internal padding
                 • "6"  - 1.5rem (24px)
                 • "8"  - 2rem (32px)
                 • "10" - 2.5rem (40px) - default
                 • "12" - 3rem (48px)
  animate            Enable scroll animations
                 • true - animate on scroll (default)
                 • false - no animation

COLORS
  background_color   Section background color
                 • "base-100" - lightest background
                 • "base-200" - light gray (default)
                 • "base-300" - darker gray
                 • "neutral" - dark neutral
                 • "primary" - brand color background
  card_bg            Card background color
                 • "base-100" - white/light (default)
                 • "base-200" - slightly darker
                 • "white" - pure white
  shadow             Card shadow intensity
                 • "md" - medium shadow
                 • "lg" - large shadow
                 • "xl" - extra large (default)
                 • "2xl" - maximum shadow
  icon_color         Icon SVG color (when no emoji icon)
                 • "success" - green (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "info" - blue
                 • "warning" - yellow
  icon_size          Icon size (for SVG: w-/h- value, for emoji: text-size)
                 • "16" - 4rem (64px)
                 • "20" - 5rem (80px) - default for SVG
                 • "24" - 6rem (96px)
                 • "6xl" - default for emoji
  badge_color        Badge color
                 • "success" - green (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "accent" - accent color
                 • "info" - blue
  title_size         Title text size
                 • "2xl" - smaller title
                 • "3xl" - default
                 • "4xl" - larger title
  text_color         Description text color
                 • "base-content/80" - 80% opacity (default)
                 • "base-content/70" - lighter text
                 • "base-content" - full opacity
  feature_color      Feature list text color
                 • "base-content/70" - 70% opacity (default)
                 • "base-content/80" - slightly darker
                 • "base-content" - full opacity
  check_color        Checkmark icon color for features
                 • "success" - green (default)
                 • "primary" - brand color
                 • "info" - blue

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Standard money-back guarantee:
{
  "badge": "Risk Free",
  "title": "100% Satisfaction Guarantee",
  "text": "If you're not completely satisfied within 30 days, we'll give you a full refund.",
  "features": ["Full refund within 30 days", "No questions asked", "Keep all bonus materials"],
  "terms": "Refund requests must be submitted within 30 days of purchase."
}
config: {"style": "card"}

Emoji icon with larger padding:
{
  "icon": "🛡️",
  "title": "Your Purchase is Protected",
  "text": "We stand behind our product with an industry-leading guarantee."
}
config: {"style": "card", "padding": "12", "padding_y": "20"}

Primary themed card:
{
  "badge": "Guaranteed",
  "title": "Risk-Free Trial",
  "text": "Try for 14 days. If it's not right for you, cancel anytime."
}
config: {
  "style": "card",
  "icon_color": "primary",
  "badge_color": "primary",
  "check_color": "primary"
}

Dark section background:
config: {
  "style": "card",
  "background_color": "neutral",
  "card_bg": "base-100",
  "shadow": "2xl"
}
""",
        "default_content": {
            "icon": "",
            "badge": "Risk Free",
            "title": "100% Satisfaction Guarantee",
            "text": "We're confident you'll love our product. If for any reason you're not completely satisfied within the first 30 days, we'll give you a full refund. No questions asked.\n\nYour success is our priority, and we stand behind everything we create.",
            "features": ["Full refund within 30 days", "No questions asked", "Keep all bonus materials"],
            "terms": "Refund requests must be submitted within 30 days of purchase.",
        },
        "default_config": {
            "style": "card",
            "max_width": "4xl",
            "padding_y": "16",
            "padding": "10",
            "animate": True,
            "background_color": "base-200",
            "card_bg": "base-100",
            "shadow": "xl",
            "icon_color": "success",
            "icon_size": "20",
            "badge_color": "success",
            "title_size": "3xl",
            "text_color": "base-content/80",
            "feature_color": "base-content/70",
            "check_color": "success",
        },
    },
    {
        "name": "Guarantee - Banner",
        "zone_type": ZoneType.GUARANTEE,
        "template_file": "cms/zones/guarantee.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/guarantee.html

Full-width gradient banner with icon, text, and optional CTA button.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Main heading text (required)
text            Short description text
icon            Emoji or custom icon (e.g., "🛡️")
                • If empty, displays shield SVG icon

CTA BUTTON
  cta.text      Button text
  cta.url       Button link URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "banner" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl
                 • "4xl" - 896px max width (default)
                 • "5xl" - 1024px max width
                 • "6xl" - 1152px max width
                 • "7xl" - 1280px max width (wide)
  padding_y          Section vertical padding
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
  padding            Banner internal padding
                 • "6"  - 1.5rem (24px)
                 • "8"  - 2rem (32px) - default
                 • "10" - 2.5rem (40px)
                 • "12" - 3rem (48px)
  rounded            Border radius
                 • "xl" - 0.75rem
                 • "2xl" - 1rem (default)
                 • "3xl" - 1.5rem
  animate            Enable scroll animations
                 • true - animate on scroll (default)
                 • false - no animation

COLORS
  background_color   Section background color
                 • "base-100" - lightest
                 • "base-200" - light gray (default)
                 • "base-300" - darker gray
                 • "transparent" - no background
  gradient_from_color  Gradient start color (CSS color)
                   • "#059669" - emerald green (default)
                   • "#0284c7" - sky blue
                   • "#7c3aed" - violet
                   • "#dc2626" - red
                   • Any valid CSS color value
  gradient_to_color    Gradient end color (CSS color)
                   • "#0284c7" - sky blue (default)
                   • "#059669" - emerald green
                   • "#a855f7" - purple
                   • Any valid CSS color value
  cta_style          CTA button style
                 • "secondary" - secondary style (default)
                 • "primary" - primary color
                 • "accent" - accent color
                 • "ghost" - transparent
                 • "outline" - outlined

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Standard money-back banner:
{
  "icon": "🛡️",
  "title": "30-Day Money-Back Guarantee",
  "text": "Try risk-free. If you're not satisfied, get a full refund within 30 days.",
  "cta": {"text": "Start Free Trial", "url": "#trial"}
}
config: {"style": "banner"}

Blue gradient without CTA:
{
  "icon": "✓",
  "title": "Satisfaction Guaranteed",
  "text": "We stand behind every product we sell."
}
config: {
  "style": "banner",
  "gradient_from_color": "#0284c7",
  "gradient_to_color": "#06b6d4"
}

Purple/pink gradient with rounded corners:
{
  "icon": "💎",
  "title": "Premium Quality Guaranteed",
  "text": "Experience excellence or your money back.",
  "cta": {"text": "Learn More", "url": "#guarantee"}
}
config: {
  "style": "banner",
  "gradient_from_color": "#7c3aed",
  "gradient_to_color": "#ec4899",
  "rounded": "3xl",
  "cta_style": "ghost"
}

Wide banner with extra padding:
config: {
  "style": "banner",
  "max_width": "6xl",
  "padding": "12",
  "padding_y": "20"
}
""",
        "default_content": {
            "icon": "🛡️",
            "title": "30-Day Money-Back Guarantee",
            "text": "Try risk-free. If you're not satisfied, get a full refund within 30 days.",
            "cta": {"text": "Start Free Trial", "url": "#trial"},
        },
        "default_config": {
            "style": "banner",
            "max_width": "4xl",
            "padding_y": "16",
            "padding": "8",
            "rounded": "2xl",
            "animate": True,
            "background_color": "base-200",
            "gradient_from_color": "#059669",
            "gradient_to_color": "#0284c7",
            "cta_style": "secondary",
        },
    },
    {
        "name": "Guarantee - Minimal",
        "zone_type": ZoneType.GUARANTEE,
        "template_file": "cms/zones/guarantee.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/guarantee.html

Simple inline guarantee with icon and text, minimal visual weight.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

title           Main heading text (required)
text            Short description text
icon            Emoji or custom icon (e.g., "✓", "🛡️")
                • If empty, displays shield SVG icon

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "minimal" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl
                 • "2xl" - 672px max width (compact)
                 • "3xl" - 768px max width
                 • "4xl" - 896px max width (default)
                 • "5xl" - 1024px max width
  padding_y          Section vertical padding
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
  animate            Enable scroll animations
                 • true - animate on scroll (default)
                 • false - no animation

COLORS
  background_color   Section background color
                 • "base-100" - lightest
                 • "base-200" - light gray (default)
                 • "base-300" - darker gray
                 • "transparent" - no background
  icon_color         Icon color (for SVG when no emoji)
                 • "success" - green (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "info" - blue
  text_color         Description text color
                 • "base-content/70" - 70% opacity (default)
                 • "base-content/80" - slightly darker
                 • "base-content" - full opacity

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple checkmark guarantee:
{
  "icon": "✓",
  "title": "30-Day Money-Back Guarantee",
  "text": "Not satisfied? Get a full refund within 30 days. No questions asked."
}
config: {"style": "minimal"}

Shield emoji with primary colors:
{
  "icon": "🛡️",
  "title": "Satisfaction Guaranteed",
  "text": "We stand behind our product 100%."
}
config: {
  "style": "minimal",
  "icon_color": "primary",
  "text_color": "base-content/80"
}

Minimal on transparent background:
{
  "icon": "✓",
  "title": "Risk-Free Purchase",
  "text": "Try it free for 14 days."
}
config: {
  "style": "minimal",
  "background_color": "transparent",
  "padding_y": "8"
}

Compact minimal:
config: {
  "style": "minimal",
  "max_width": "2xl",
  "padding_y": "12"
}
""",
        "default_content": {
            "icon": "✓",
            "title": "30-Day Money-Back Guarantee",
            "text": "Not satisfied? Get a full refund within 30 days. No questions asked.",
        },
        "default_config": {
            "style": "minimal",
            "max_width": "4xl",
            "padding_y": "16",
            "animate": True,
            "background_color": "base-200",
            "icon_color": "success",
            "text_color": "base-content/70",
        },
    },
    {
        "name": "Guarantee - Badge",
        "zone_type": ZoneType.GUARANTEE,
        "template_file": "cms/zones/guarantee.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/guarantee.html

Large centered badge/seal style guarantee with number display.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

BADGE SEAL
  badge_number      Large number in seal (e.g., "30", "60", "100")
  badge_label       Text below number (e.g., "Day", "Days", "%")
  badge_subtitle    Small text at bottom (e.g., "Guarantee", "Refund")

CONTENT
  title             Main heading below badge (required)
  text              Description text
  features[]        Array of feature strings with checkmarks

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "badge" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl
                 • "2xl" - 672px max width (compact)
                 • "3xl" - 768px max width
                 • "4xl" - 896px max width (default)
                 • "5xl" - 1024px max width
  padding_y          Section vertical padding
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
                 • "24" - 6rem (96px)
  animate            Enable scroll animations
                 • true - animate on scroll (default)
                 • false - no animation

COLORS
  background_color   Section background color
                 • "base-100" - lightest
                 • "base-200" - light gray (default)
                 • "base-300" - darker gray
  badge_bg           Badge outer ring background (with opacity)
                 • "success/10" - light green (default)
                 • "primary/10" - light brand color
                 • "secondary/10" - light secondary
                 • "info/10" - light blue
  badge_color        Badge circle background color
                 • "success" - green (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "info" - blue
  badge_text         Badge text/number color
                 • "success-content" - contrast for success (default)
                 • "primary-content" - contrast for primary
                 • "white" - white text
  text_color         Description text color
                 • "base-content/70" - 70% opacity (default)
                 • "base-content/80" - slightly darker
                 • "base-content" - full opacity
  check_color        Checkmark color for features
                 • "success" - green (default)
                 • "primary" - brand color
                 • "info" - blue

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

30-day guarantee seal:
{
  "badge_number": "30",
  "badge_label": "Day",
  "badge_subtitle": "Guarantee",
  "title": "Your Purchase is Protected",
  "text": "We offer a 30-day, no-questions-asked money-back guarantee.",
  "features": ["Instant refund processing", "Keep all downloaded materials", "No restocking fees"]
}
config: {"style": "badge"}

60-day extended guarantee:
{
  "badge_number": "60",
  "badge_label": "Days",
  "badge_subtitle": "Money Back",
  "title": "Extended Guarantee",
  "text": "Take your time to evaluate - 60 full days to decide."
}
config: {
  "style": "badge",
  "badge_color": "primary",
  "badge_bg": "primary/10",
  "badge_text": "primary-content"
}

100% satisfaction style:
{
  "badge_number": "100",
  "badge_label": "%",
  "badge_subtitle": "Satisfaction",
  "title": "Complete Satisfaction Guaranteed",
  "text": "If you're not 100% satisfied, we'll make it right."
}
config: {"style": "badge", "padding_y": "20"}

Premium blue theme:
config: {
  "style": "badge",
  "badge_color": "info",
  "badge_bg": "info/10",
  "badge_text": "info-content",
  "check_color": "info"
}
""",
        "default_content": {
            "badge_number": "30",
            "badge_label": "Day",
            "badge_subtitle": "Guarantee",
            "title": "Your Purchase is Protected",
            "text": "We believe in our product so much that we offer a 30-day, no-questions-asked money-back guarantee. If you're not completely satisfied, simply let us know and we'll refund your purchase in full.",
            "features": ["Instant refund processing", "Keep all downloaded materials", "No restocking fees"],
        },
        "default_config": {
            "style": "badge",
            "max_width": "4xl",
            "padding_y": "16",
            "animate": True,
            "background_color": "base-200",
            "badge_bg": "success/10",
            "badge_color": "success",
            "badge_text": "success-content",
            "text_color": "base-content/70",
            "check_color": "success",
        },
    },
    {
        "name": "Guarantee - Split",
        "zone_type": ZoneType.GUARANTEE,
        "template_file": "cms/zones/guarantee.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/guarantee.html

Two-column layout with icon/badge on left, content on right.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

LEFT COLUMN
  icon              Emoji or custom icon (e.g., "🏆", "🛡️")
                    • If empty, displays shield SVG in circle
  badge             Small badge text below icon (e.g., "100% Guaranteed")

RIGHT COLUMN
  title             Main heading (required)
  text              Description text (supports HTML, line breaks)
  features[]        Array of feature strings with checkmarks

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "split" (REQUIRED for this template)
  max_width          Container width: sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl
                 • "3xl" - 768px max width (compact)
                 • "4xl" - 896px max width (default)
                 • "5xl" - 1024px max width
                 • "6xl" - 1152px max width (wide)
  padding_y          Section vertical padding
                 • "12" - 3rem (48px)
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px)
                 • "24" - 6rem (96px)
  animate            Enable scroll animations
                 • true - animate on scroll (default)
                 • false - no animation
  header_align       Feature list alignment on mobile
                 • "center" - center on mobile, left on desktop (default)
                 • "left" - always left aligned

COLORS
  background_color   Section background color
                 • "base-100" - lightest
                 • "base-200" - light gray (default)
                 • "base-300" - darker gray
                 • "neutral" - dark neutral
  icon_bg            Icon circle background (when no emoji)
                 • "success/10" - light green (default)
                 • "primary/10" - light brand color
                 • "secondary/10" - light secondary
                 • "info/10" - light blue
  icon_color         Icon SVG color (when no emoji)
                 • "success" - green (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "info" - blue
  badge_color        Badge color below icon
                 • "success" - green (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "accent" - accent color
  text_color         Description text color
                 • "base-content/80" - 80% opacity (default)
                 • "base-content/70" - lighter
                 • "base-content" - full opacity
  check_color        Checkmark color for features
                 • "success" - green (default)
                 • "primary" - brand color
                 • "info" - blue

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Trophy icon with features:
{
  "icon": "🏆",
  "badge": "100% Guaranteed",
  "title": "Our Promise to You",
  "text": "We're so confident in the quality of our product that we back it with an industry-leading guarantee.",
  "features": ["Full money-back guarantee", "Priority customer support", "Free updates for life", "No hidden fees ever"]
}
config: {"style": "split"}

Shield icon with primary theme:
{
  "badge": "Protected",
  "title": "Secure Purchase Guarantee",
  "text": "Your transaction is protected by our comprehensive guarantee policy."
}
config: {
  "style": "split",
  "icon_color": "primary",
  "icon_bg": "primary/10",
  "badge_color": "primary",
  "check_color": "primary"
}

Wide layout without badge:
{
  "icon": "🛡️",
  "title": "Risk-Free Experience",
  "text": "Try our product for 30 days. If you're not completely satisfied, we'll refund every penny.",
  "features": ["No risk trial", "Instant refunds", "Keep your data"]
}
config: {
  "style": "split",
  "max_width": "5xl",
  "padding_y": "20"
}

Dark background theme:
config: {
  "style": "split",
  "background_color": "neutral",
  "text_color": "base-content/80",
  "header_align": "left"
}
""",
        "default_content": {
            "icon": "🏆",
            "badge": "100% Guaranteed",
            "title": "Our Promise to You",
            "text": "We're so confident in the quality of our product that we back it with an industry-leading guarantee. Your satisfaction is our top priority.\n\nIf you're not happy for any reason, we'll make it right.",
            "features": [
                "Full money-back guarantee",
                "Priority customer support",
                "Free updates for life",
                "No hidden fees ever",
            ],
        },
        "default_config": {
            "style": "split",
            "max_width": "4xl",
            "padding_y": "16",
            "animate": True,
            "header_align": "center",
            "background_color": "base-200",
            "icon_bg": "success/10",
            "icon_color": "success",
            "badge_color": "success",
            "text_color": "base-content/80",
            "check_color": "success",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
