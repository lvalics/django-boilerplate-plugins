"""
Final CTA zone templates.
"""

from ._base import ZoneType

FINAL_CTA_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Final CTA - Centered (Default)",
        "zone_type": ZoneType.FINAL_CTA,
        "template_file": "landing_pages/zones/final_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/final_cta.html

Centered final call-to-action section with urgency elements and multiple style options.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text (required)
subheadline        Supporting paragraph text
urgency_text       Urgency badge text (e.g., "Limited Offer", "Last Chance")

PRIMARY CTA
  cta_text         Primary button text
  cta_url          Primary button URL

SECONDARY CTA
  secondary_cta_text   Secondary button text
  secondary_cta_url    Secondary button URL

ADDITIONAL CONTENT
  reassurance      Small reassurance text below CTAs
                   Example: "30-day money-back guarantee"

  features[]       Array of feature/benefit strings shown with checkmarks
                   Example: ["No credit card required", "14-day trial", "Cancel anytime"]

  social_proof     Social proof section with avatars and text
                   Example: {
                     "avatars": ["url1.jpg", "url2.jpg", "url3.jpg"],
                     "text": "Join 10,000+ happy customers"
                   }

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "centered" (REQUIRED for this template)
  max_width          Container max width (default: 5xl)
                 * "3xl" - 768px max width (narrow)
                 * "4xl" - 896px max width
                 * "5xl" - 1024px max width (default)
                 * "6xl" - 1152px max width
                 * "7xl" - 1280px max width (wide)
  padding_y          Vertical padding in Tailwind units (default: 20)
                 * "12" - 3rem (48px) - compact
                 * "16" - 4rem (64px)
                 * "20" - 5rem (80px) - default
                 * "24" - 6rem (96px) - spacious

COLORS
  background_color   Section background color (default: primary)
                 * "primary" - brand color background (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "neutral" - dark neutral
                 * "base-200" - light gray
  text_color         Text color (default: primary-content)
                 * "primary-content" - contrasts with primary bg (default)
                 * "secondary-content" - contrasts with secondary bg
                 * "base-content" - default text color
                 * "white" - white text

TYPOGRAPHY
  title_size         Mobile heading size (default: 4xl)
                 * "3xl" - smaller heading
                 * "4xl" - default mobile size
                 * "5xl" - larger heading
  title_size_md      Desktop heading size (default: 5xl)
                 * "4xl" - smaller desktop heading
                 * "5xl" - default desktop size
                 * "6xl" - larger desktop heading
  title_weight       Heading font weight (default: bold)
                 * "semibold" - slightly lighter
                 * "bold" - default
                 * "extrabold" - heavier
  subtitle_size      Mobile subheadline size (default: xl)
                 * "lg" - smaller
                 * "xl" - default mobile size
                 * "2xl" - larger
  subtitle_size_md   Desktop subheadline size (default: 2xl)
                 * "xl" - smaller desktop
                 * "2xl" - default desktop size
                 * "3xl" - larger desktop

URGENCY BADGE
  urgency_color      Urgency badge color (default: warning)
                 * "warning" - yellow/orange (default, creates urgency)
                 * "error" - red (high urgency)
                 * "info" - blue
                 * "success" - green
                 * "primary" - brand color
  urgency_pulse      Animate urgency badge with pulse (default: true)
                 * true - pulsing animation (default)
                 * "false" - no animation

BUTTONS
  cta_style          Primary CTA button color (default: secondary)
                 * "secondary" - contrasts with primary bg (default)
                 * "primary" - brand color
                 * "accent" - accent color
                 * "success" - green
  cta_size           Button size (default: lg)
                 * "md" - medium size
                 * "lg" - large size (default)
                 * "xl" - extra large

ANIMATION
  animate            Enable scroll animations (default: true)
                 * true - fade-in animations on scroll (default)
                 * "false" - no animations

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Standard centered CTA:
{
  "urgency_text": "Limited Time Offer",
  "headline": "Ready to Transform Your Business?",
  "subheadline": "Join thousands of successful customers today.",
  "cta_text": "Start Free Trial",
  "cta_url": "/signup",
  "secondary_cta_text": "Schedule Demo",
  "secondary_cta_url": "/demo",
  "reassurance": "30-day money-back guarantee"
}
config: {"style": "centered"}

With features list:
{
  "headline": "Get Started Today",
  "subheadline": "Everything you need to succeed.",
  "features": ["No credit card required", "14-day free trial", "Cancel anytime"],
  "cta_text": "Sign Up Free",
  "cta_url": "/signup"
}
config: {"style": "centered", "background_color": "secondary"}

With social proof:
{
  "headline": "Join Our Community",
  "subheadline": "Trusted by teams worldwide.",
  "cta_text": "Get Started",
  "cta_url": "/start",
  "social_proof": {
    "avatars": ["/img/user1.jpg", "/img/user2.jpg", "/img/user3.jpg"],
    "text": "Join 10,000+ happy customers"
  }
}
config: {"style": "centered", "cta_style": "accent"}

High-urgency with red badge:
config: {
  "style": "centered",
  "urgency_color": "error",
  "urgency_pulse": true,
  "background_color": "neutral",
  "text_color": "white"
}
""",
        "default_content": {
            "urgency_text": "Limited Time Offer",
            "headline": "Ready to Transform Your Business?",
            "subheadline": "Join thousands of successful customers who have already made the switch. Start your free trial today and see the difference.",
            "features": ["No credit card required", "14-day free trial", "Cancel anytime"],
            "cta_text": "Start Your Free Trial",
            "cta_url": "#signup",
            "secondary_cta_text": "Schedule a Demo",
            "secondary_cta_url": "#demo",
            "reassurance": "30-day money-back guarantee. No questions asked.",
        },
        "default_config": {
            "style": "centered",
            "max_width": "5xl",
            "padding_y": "20",
            "background_color": "primary",
            "text_color": "primary-content",
            "title_size": "4xl",
            "title_size_md": "5xl",
            "title_weight": "bold",
            "subtitle_size": "xl",
            "subtitle_size_md": "2xl",
            "urgency_color": "warning",
            "urgency_pulse": True,
            "cta_style": "secondary",
            "cta_size": "lg",
            "animate": True,
        },
    },
    {
        "name": "Final CTA - Split",
        "zone_type": ZoneType.FINAL_CTA,
        "template_file": "landing_pages/zones/final_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/final_cta.html

Two-column split layout with content on left and image on right.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text (required)
subheadline        Supporting paragraph text
urgency_text       Urgency badge text

PRIMARY CTA
  cta_text         Primary button text
  cta_url          Primary button URL

SECONDARY CTA
  secondary_cta_text   Secondary button text
  secondary_cta_url    Secondary button URL

ADDITIONAL CONTENT
  reassurance      Small reassurance text below CTAs
  features[]       Array of feature strings shown as list with checkmarks
  image            Image URL displayed on right side (recommended)
                   Example: "https://example.com/product-mockup.png"

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "split" (REQUIRED for this template)
  max_width          Container max width (default: 5xl)
                 * "4xl" - 896px (narrower)
                 * "5xl" - 1024px (default)
                 * "6xl" - 1152px
                 * "7xl" - 1280px (wider)
  padding_y          Vertical padding (default: 20)
                 * "16" - 4rem (64px) - compact
                 * "20" - 5rem (80px) - default
                 * "24" - 6rem (96px) - spacious
  image_width        Image column width (default: 2/5)
                 * "1/3" - narrower image (33%)
                 * "2/5" - default (40%)
                 * "1/2" - half width (50%)

COLORS
  background_color   Section background color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "neutral" - dark neutral
                 * "base-200" - light gray
  text_color         Text color (default: primary-content)
                 * "primary-content" - default
                 * "white" - white text

IMAGE STYLING
  image_bg           Image container background color (optional)
                 * "" - no background (default)
                 * "primary" - brand color background
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "neutral" - neutral dark
                 * "base-200" - light gray
                 * "base-300" - darker gray
                 When set, adds padding around image
  rounded            Image border radius (default: 2xl)
                 * "lg" - 8px radius
                 * "xl" - 12px radius
                 * "2xl" - 16px radius (default)
                 * "3xl" - 24px radius
  shadow             Image shadow (default: 2xl)
                 * "lg" - medium shadow
                 * "xl" - large shadow
                 * "2xl" - extra large shadow (default)

URGENCY BADGE
  urgency_color      Urgency badge color (default: warning)
                 * "warning" - yellow/orange (default)
                 * "error" - red
                 * "success" - green
                 * "primary" - brand color
  urgency_pulse      Animate badge (default: true)

BUTTONS
  cta_style          Primary CTA button color (default: secondary)

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Product showcase:
{
  "urgency_text": "Start Today",
  "headline": "Take the First Step",
  "subheadline": "Your journey to success starts here.",
  "features": ["Personalized path", "Expert mentorship", "Lifetime access"],
  "cta_text": "Get Started Now",
  "cta_url": "/start",
  "image": "https://example.com/product-mockup.png",
  "reassurance": "Join 10,000+ happy customers"
}
config: {"style": "split"}

App promotion with larger image:
{
  "headline": "Download Our App",
  "subheadline": "Available on iOS and Android.",
  "cta_text": "Download Free",
  "cta_url": "/download",
  "image": "/media/app-screenshot.png"
}
config: {"style": "split", "image_width": "1/2", "rounded": "3xl"}

Dark theme split:
config: {
  "style": "split",
  "background_color": "neutral",
  "text_color": "white",
  "shadow": "xl"
}
""",
        "default_content": {
            "urgency_text": "Start Today",
            "headline": "Take the First Step",
            "subheadline": "Your journey to success starts here. Join our community of achievers and unlock your full potential.",
            "features": ["Personalized learning path", "Expert mentorship", "Lifetime access"],
            "cta_text": "Get Started Now",
            "cta_url": "#start",
            "secondary_cta_text": "Learn More",
            "secondary_cta_url": "#learn",
            "image": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/hero/phone-mockup.png",
            "reassurance": "Join 10,000+ happy customers",
        },
        "default_config": {
            "style": "split",
            "max_width": "5xl",
            "padding_y": "20",
            "background_color": "primary",
            "text_color": "primary-content",
            "image_width": "2/5",
            "image_bg": "",
            "rounded": "2xl",
            "shadow": "2xl",
            "urgency_color": "warning",
            "urgency_pulse": True,
            "cta_style": "secondary",
            "animate": True,
        },
    },
    {
        "name": "Final CTA - Gradient",
        "zone_type": ZoneType.FINAL_CTA,
        "template_file": "landing_pages/zones/final_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/final_cta.html

Full-width gradient background with centered content and prominent styling.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text (required)
subheadline        Supporting paragraph text
urgency_text       Urgency text (displayed in frosted glass pill)
icon               Large emoji/icon displayed above content
                   Example: "fire:", "rocket:", "star:"

PRIMARY CTA
  cta_text         Primary button text
  cta_url          Primary button URL

SECONDARY CTA
  secondary_cta_text   Secondary button text
  secondary_cta_url    Secondary button URL

TRUST BADGES
  trust_badges[]   Array of trust badge objects with icon and text
                   Example: [
                     {"icon": "lock:", "text": "Secure Payment"},
                     {"icon": "zap:", "text": "Instant Access"},
                     {"icon": "check:", "text": "Money-Back Guarantee"}
                   ]

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "gradient" (REQUIRED for this template)
  max_width          Container max width (default: 5xl)
                 * "4xl" - 896px (narrower)
                 * "5xl" - 1024px (default)
                 * "6xl" - 1152px (wider)
  padding_y          Vertical padding (default: 20)
                 * "16" - 4rem (64px)
                 * "20" - 5rem (80px) - default
                 * "24" - 6rem (96px)
                 * "28" - 7rem (112px)

GRADIENT COLORS
  gradient_from_color  Gradient start color as hex (default: #0f172a)
                   * "#0f172a" - slate 900 (default, dark blue)
                   * "#1e293b" - slate 800 (lighter dark)
                   * "#0c4a6e" - sky 900 (dark blue)
                   * "#312e81" - indigo 900 (dark purple)
                   * "#14532d" - green 900 (dark green)
  gradient_to_color    Gradient end color as hex (default: #334155)
                   * "#334155" - slate 700 (default)
                   * "#475569" - slate 600 (lighter)
                   * "#0369a1" - sky 700 (blue)
                   * "#4338ca" - indigo 700 (purple)

BUTTONS
  button_text_color  Primary button text color as hex (default: #0f172a)
                 * "#0f172a" - dark text on white button (default)
                 * "#1e293b" - slightly lighter
                 * "#000000" - pure black

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Launch offer with trust badges:
{
  "icon": "rocket:",
  "urgency_text": "Launch Offer - 50% Off",
  "headline": "Don't Miss Out",
  "subheadline": "This special pricing won't last forever.",
  "cta_text": "Claim Your Discount",
  "cta_url": "/claim",
  "trust_badges": [
    {"icon": "lock:", "text": "Secure Payment"},
    {"icon": "zap:", "text": "Instant Access"},
    {"icon": "check:", "text": "Money-Back Guarantee"}
  ]
}
config: {"style": "gradient"}

Blue gradient:
config: {
  "style": "gradient",
  "gradient_from_color": "#0c4a6e",
  "gradient_to_color": "#0369a1"
}

Purple gradient:
config: {
  "style": "gradient",
  "gradient_from_color": "#312e81",
  "gradient_to_color": "#4338ca"
}

Green gradient:
config: {
  "style": "gradient",
  "gradient_from_color": "#14532d",
  "gradient_to_color": "#166534"
}

Warm gradient:
config: {
  "style": "gradient",
  "gradient_from_color": "#7c2d12",
  "gradient_to_color": "#c2410c"
}
""",
        "default_content": {
            "icon": "rocket:",
            "urgency_text": "Launch Offer - 50% Off",
            "headline": "Don't Miss Out",
            "subheadline": "This special pricing won't last forever. Lock in your discount before it's gone.",
            "cta_text": "Claim Your Discount",
            "cta_url": "#claim",
            "secondary_cta_text": "See Pricing",
            "secondary_cta_url": "#pricing",
            "trust_badges": [
                {"icon": "lock:", "text": "Secure Payment"},
                {"icon": "zap:", "text": "Instant Access"},
                {"icon": "check:", "text": "Money-Back Guarantee"},
            ],
        },
        "default_config": {
            "style": "gradient",
            "max_width": "5xl",
            "padding_y": "20",
            "gradient_from_color": "#0f172a",
            "gradient_to_color": "#334155",
            "button_text_color": "#0f172a",
            "animate": True,
        },
    },
    {
        "name": "Final CTA - Minimal",
        "zone_type": ZoneType.FINAL_CTA,
        "template_file": "landing_pages/zones/final_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/final_cta.html

Clean, minimal call-to-action with simple centered layout.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text (required)
subheadline        Supporting paragraph text

PRIMARY CTA
  cta_text         Primary button text
  cta_url          Primary button URL

SECONDARY CTA
  secondary_cta_text   Secondary button text
  secondary_cta_url    Secondary button URL

ADDITIONAL CONTENT
  reassurance      Small reassurance text below CTAs

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "minimal" (REQUIRED for this template)
  max_width          Container max width (default: 5xl)
                 * "3xl" - 768px (narrow, focused)
                 * "4xl" - 896px
                 * "5xl" - 1024px (default)
  padding_y          Vertical padding (default: 20)
                 * "12" - 3rem (48px) - compact
                 * "16" - 4rem (64px)
                 * "20" - 5rem (80px) - default

COLORS
  background_color   Section background color (default: base-200)
                 * "base-100" - white/lightest
                 * "base-200" - light gray (default)
                 * "base-300" - darker gray
                 * "transparent" - no background

BUTTONS
  cta_style          Primary CTA button color (default: primary)
                 * "primary" - brand color (default for minimal)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "neutral" - neutral dark
  cta_size           Button size (default: lg)
                 * "md" - medium
                 * "lg" - large (default)

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple signup CTA:
{
  "headline": "Ready to get started?",
  "subheadline": "Create your free account in seconds.",
  "cta_text": "Sign Up Free",
  "cta_url": "/signup",
  "secondary_cta_text": "Contact Sales",
  "secondary_cta_url": "/contact",
  "reassurance": "No credit card required"
}
config: {"style": "minimal"}

Narrow focused layout:
config: {
  "style": "minimal",
  "max_width": "3xl",
  "background_color": "base-100"
}

With accent button:
config: {
  "style": "minimal",
  "cta_style": "accent",
  "background_color": "base-200"
}

Compact spacing:
config: {
  "style": "minimal",
  "padding_y": "12",
  "max_width": "4xl"
}
""",
        "default_content": {
            "headline": "Ready to get started?",
            "subheadline": "Create your free account in seconds.",
            "cta_text": "Sign Up Free",
            "cta_url": "#signup",
            "secondary_cta_text": "Contact Sales",
            "secondary_cta_url": "#contact",
            "reassurance": "No credit card required",
        },
        "default_config": {
            "style": "minimal",
            "max_width": "5xl",
            "padding_y": "20",
            "background_color": "base-200",
            "cta_style": "primary",
            "cta_size": "lg",
            "animate": True,
        },
    },
    {
        "name": "Final CTA - Boxed",
        "zone_type": ZoneType.FINAL_CTA,
        "template_file": "landing_pages/zones/final_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/final_cta.html

Card-style boxed CTA with prominent shadow and contained styling.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text (required)
subheadline        Supporting paragraph text
urgency_text       Urgency badge text

PRIMARY CTA
  cta_text         Primary button text
  cta_url          Primary button URL

SECONDARY CTA
  secondary_cta_text   Secondary button text
  secondary_cta_url    Secondary button URL

ADDITIONAL CONTENT
  reassurance      Small reassurance text below CTAs
  features[]       Array of feature strings shown as badges with checkmarks

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "boxed" (REQUIRED for this template)
  max_width          Container max width (default: 5xl)
                 * "4xl" - 896px
                 * "5xl" - 1024px (default)
                 * "6xl" - 1152px
  padding_y          Section vertical padding (default: 20)
                 * "16" - 4rem (64px)
                 * "20" - 5rem (80px) - default
                 * "24" - 6rem (96px)
  padding            Card body padding (default: 12)
                 * "8" - 2rem (32px) - compact
                 * "10" - 2.5rem (40px)
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious

COLORS
  background_color   Section background color (default: base-200)
                 * "base-100" - white/lightest
                 * "base-200" - light gray (default)
                 * "base-300" - darker gray
  card_bg            Card background color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "neutral" - dark neutral
  card_text          Card text color (default: primary-content)
                 * "primary-content" - contrasts with primary (default)
                 * "secondary-content" - contrasts with secondary
                 * "white" - white text

CARD STYLING
  shadow             Card shadow size (default: 2xl)
                 * "lg" - medium shadow
                 * "xl" - large shadow
                 * "2xl" - extra large shadow (default)

URGENCY BADGE
  urgency_color      Urgency badge color (default: warning)
                 * "warning" - yellow/orange (default)
                 * "error" - red
                 * "success" - green
  urgency_pulse      Animate badge (default: true)

BUTTONS
  cta_style          Primary CTA button color (default: secondary)
                 * "secondary" - contrasts with card bg (default)
                 * "accent" - accent color
                 * "neutral" - neutral

ANIMATION
  animate            Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Special offer card:
{
  "urgency_text": "Special Offer",
  "headline": "Start Your Journey Today",
  "subheadline": "Everything you need to succeed. Get exclusive bonuses worth $500.",
  "features": ["Lifetime access", "Free updates", "Premium support"],
  "cta_text": "Get Instant Access",
  "cta_url": "/access",
  "reassurance": "Secure checkout. Instant delivery."
}
config: {"style": "boxed"}

Secondary brand card:
config: {
  "style": "boxed",
  "card_bg": "secondary",
  "card_text": "secondary-content",
  "background_color": "base-100"
}

Accent color card:
config: {
  "style": "boxed",
  "card_bg": "accent",
  "card_text": "accent-content",
  "cta_style": "neutral"
}

Dark neutral card:
config: {
  "style": "boxed",
  "card_bg": "neutral",
  "card_text": "neutral-content",
  "shadow": "xl"
}

Compact card with less padding:
config: {
  "style": "boxed",
  "padding": "8",
  "padding_y": "16"
}
""",
        "default_content": {
            "urgency_text": "Special Offer",
            "headline": "Start Your Journey Today",
            "subheadline": "Everything you need to succeed, all in one place. Join now and get exclusive bonuses worth $500.",
            "features": ["Lifetime access", "Free updates", "Premium support", "Exclusive community"],
            "cta_text": "Get Instant Access",
            "cta_url": "#access",
            "secondary_cta_text": "View Details",
            "secondary_cta_url": "#details",
            "reassurance": "Secure checkout. Instant delivery.",
        },
        "default_config": {
            "style": "boxed",
            "max_width": "5xl",
            "padding_y": "20",
            "padding": "12",
            "background_color": "base-200",
            "card_bg": "primary",
            "card_text": "primary-content",
            "shadow": "2xl",
            "urgency_color": "warning",
            "urgency_pulse": True,
            "cta_style": "secondary",
            "animate": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
