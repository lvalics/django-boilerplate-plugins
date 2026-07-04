"""
Social Proof CTA zone templates.
"""

from ._base import ZoneType

SOCIAL_PROOF_CTA_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Social Proof CTA - Stats & Logos",
        "zone_type": ZoneType.SOCIAL_PROOF_CTA,
        "template_file": "landing_pages/zones/social_proof_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/social_proof_cta.html

Social proof section with stats, logos, testimonial quote, and CTA buttons.
Builds trust through social validation with scroll animations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge              Badge text above headline (optional)
  headline           Main heading text
  subheadline        Supporting paragraph text

STATS
  stats[]            Array of statistics:
    value            The number/value (e.g., "10K+", "99%", "24/7")
    label            Description text (e.g., "Happy Customers")

TESTIMONIAL
  quote.text         Testimonial quote text
  quote.author       Author name
  quote.role         Author title/company
  quote.avatar       Author image URL

LOGOS
  logos_title        Text above logos (e.g., "Trusted by leading companies")
  logos[]            Array of logo objects:
    url              Logo image URL
    alt              Alt text for accessibility

CTA BUTTONS
  cta_text           Primary button text
  cta_url            Primary button URL
  secondary_cta_text Secondary button text
  secondary_cta_url  Secondary button URL

TRUST BADGES
  trust_badges[]     Array of trust indicators:
    icon             Emoji or icon character
    text             Badge text

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE PRESETS
  style              Section style preset (default: default)
               - "default" - solid background color
               - "dark" - dark theme with neutral background
               - "gradient" - gradient background
               - "minimal" - no special text color styling

LAYOUT
  padding_y          Vertical padding in Tailwind units (default: 16)
               - "12" - 3rem (48px) - compact
               - "16" - 4rem (64px) - default
               - "20" - 5rem (80px) - spacious
               - "24" - 6rem (96px) - very spacious
  max_width          Container max width (optional)
               - "4xl" - 896px
               - "5xl" - 1024px
               - "6xl" - 1152px
               - "7xl" - 1280px

COLORS
  background_color   Section background color (default: primary)
               - "primary" - brand color (default for default style)
               - "secondary" - secondary brand
               - "neutral" - dark neutral (default for dark style)
               - "base-100" - lightest background
               - "base-200" - light gray
  text_color         Text color (default: primary-content)
               - "primary-content" - contrasts with primary bg (default)
               - "secondary-content" - contrasts with secondary bg
               - "neutral-content" - contrasts with neutral bg
               - "base-content" - standard text color
               - "white" - pure white

GRADIENT (when style="gradient")
  gradient_direction Gradient direction (default: r)
               - "r" - left to right (default)
               - "l" - right to left
               - "t" - bottom to top
               - "b" - top to bottom
               - "br" - top-left to bottom-right
               - "bl" - top-right to bottom-left
  gradient_from      Gradient start color (default: primary)
               - "primary" - brand color
               - "secondary" - secondary brand
               - "accent" - accent color
  gradient_to        Gradient end color (default: secondary)
               - "secondary" - secondary brand
               - "accent" - accent color
               - "primary" - brand color

BADGE
  badge_style        Badge DaisyUI style (default: secondary)
               - "primary" - brand color badge
               - "secondary" - secondary brand badge
               - "accent" - accent color badge
               - "ghost" - subtle badge
               - "outline" - outlined badge

HEADLINE STYLING
  headline_size      Headline text size (default: 3xl)
               - "2xl" - 1.5rem
               - "3xl" - 1.875rem (default)
               - "4xl" - 2.25rem
  headline_size_md   Headline size on medium screens (default: 4xl)
               - "3xl" - 1.875rem
               - "4xl" - 2.25rem (default)
               - "5xl" - 3rem
  headline_size_lg   Headline size on large screens (default: 5xl)
               - "4xl" - 2.25rem
               - "5xl" - 3rem (default)
               - "6xl" - 3.75rem
  headline_weight    Headline font weight (default: bold)
               - "semibold" - semi-bold
               - "bold" - bold (default)
               - "extrabold" - extra bold
  headline_margin    Headline bottom margin (default: 4)
               - "2" - 0.5rem
               - "4" - 1rem (default)
               - "6" - 1.5rem

SUBHEADLINE STYLING
  subheadline_size   Subheadline text size (default: xl)
               - "lg" - 1.125rem
               - "xl" - 1.25rem (default)
               - "2xl" - 1.5rem
  subheadline_opacity  Subheadline opacity (default: 90)
               - "70" - 70% opacity
               - "80" - 80% opacity
               - "90" - 90% opacity (default)
  subheadline_max_width  Subheadline max width (default: 2xl)
               - "xl" - 576px
               - "2xl" - 672px (default)
               - "3xl" - 768px
  subheadline_margin Subheadline bottom margin (default: 8)
               - "6" - 1.5rem
               - "8" - 2rem (default)
               - "10" - 2.5rem

STATS STYLING
  stats_gap          Gap between stats (default: 8)
               - "4" - 1rem
               - "6" - 1.5rem
               - "8" - 2rem (default)
  stats_gap_md       Gap on medium screens (default: 16)
               - "12" - 3rem
               - "16" - 4rem (default)
               - "20" - 5rem
  stats_margin       Stats section bottom margin (default: 12)
               - "8" - 2rem
               - "12" - 3rem (default)
               - "16" - 4rem
  stat_padding       Individual stat horizontal padding (default: 4)
               - "2" - 0.5rem
               - "4" - 1rem (default)
               - "6" - 1.5rem
  stat_value_size    Stat value text size (default: 4xl)
               - "3xl" - 1.875rem
               - "4xl" - 2.25rem (default)
               - "5xl" - 3rem
  stat_value_size_md Stat value size on medium screens (default: 5xl)
               - "4xl" - 2.25rem
               - "5xl" - 3rem (default)
               - "6xl" - 3.75rem
  stat_value_weight  Stat value font weight (default: bold)
               - "semibold" - semi-bold
               - "bold" - bold (default)
               - "extrabold" - extra bold
  stat_value_color   Stat value text color (optional)
               - "white" - white text
               - "primary-content" - contrasts with primary
               - "accent" - accent color
  stat_label_size    Stat label text size (default: sm)
               - "xs" - 0.75rem
               - "sm" - 0.875rem (default)
               - "base" - 1rem
  stat_label_opacity Stat label opacity (default: 80)
               - "60" - 60% opacity
               - "70" - 70% opacity
               - "80" - 80% opacity (default)

QUOTE STYLING
  quote_size         Quote text size (default: xl)
               - "lg" - 1.125rem
               - "xl" - 1.25rem (default)
               - "2xl" - 1.5rem
  quote_size_md      Quote size on medium screens (default: 2xl)
               - "xl" - 1.25rem
               - "2xl" - 1.5rem (default)
               - "3xl" - 1.875rem
  quote_max_width    Quote max width (default: 3xl)
               - "2xl" - 672px
               - "3xl" - 768px (default)
               - "4xl" - 896px
  quote_margin       Quote section bottom margin (default: 12)
               - "8" - 2rem
               - "12" - 3rem (default)
               - "16" - 4rem
  align              Quote author alignment (default: center)
               - "center" - centered (default)
               - "left" - left-aligned

LOGOS STYLING
  logos_margin       Logos section bottom margin (default: 12)
               - "8" - 2rem
               - "12" - 3rem (default)
               - "16" - 4rem
  logos_title_size   Logos title text size (default: sm)
               - "xs" - 0.75rem
               - "sm" - 0.875rem (default)
               - "base" - 1rem
  logos_gap          Gap between logos (default: 8)
               - "4" - 1rem
               - "6" - 1.5rem
               - "8" - 2rem (default)
  logos_gap_md       Logos gap on medium screens (default: 12)
               - "8" - 2rem
               - "12" - 3rem (default)
               - "16" - 4rem
  logo_height        Logo height (default: 8)
               - "6" - 1.5rem
               - "8" - 2rem (default)
               - "10" - 2.5rem
  logo_height_md     Logo height on medium screens (default: 10)
               - "8" - 2rem
               - "10" - 2.5rem (default)
               - "12" - 3rem
  logos_opacity      Logo opacity (default: 70)
               - "50" - 50% opacity
               - "70" - 70% opacity (default)
               - "80" - 80% opacity
  logo_filter        CSS filter for logos (optional)
               - "brightness(0) invert(1)" - white logos for dark bg
               - "grayscale(100%)" - grayscale logos
               - "brightness(0)" - black logos

CTA BUTTONS
  cta_style          Primary button style (default: secondary)
               - "primary" - brand color
               - "secondary" - secondary brand (default)
               - "accent" - accent color
               - "success" - green
               - "ghost" - transparent
  cta_size           Button size (default: lg)
               - "sm" - small
               - "md" - medium
               - "lg" - large (default)
  secondary_cta_style  Secondary button style (default: ghost)
               - "ghost" - transparent (default)
               - "outline" - outlined
               - "link" - link style

ANIMATION
  animate            Enable scroll animations (default: true)
               - true - animations enabled (default)
               - "false" - animations disabled

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Stats with logos (default):
{
  "headline": "Join 10,000+ Happy Customers",
  "subheadline": "See why businesses choose us",
  "stats": [
    {"value": "10K+", "label": "Active Users"},
    {"value": "99%", "label": "Satisfaction"},
    {"value": "24/7", "label": "Support"}
  ],
  "logos_title": "Trusted by",
  "logos": [{"url": "/img/logo1.svg", "alt": "Company 1"}],
  "cta_text": "Start Free Trial",
  "cta_url": "/signup"
}
config: {"style": "default", "background_color": "primary"}

Gradient with testimonial:
{
  "badge": "Customer Success",
  "headline": "Loved by Teams Worldwide",
  "quote": {
    "text": "This platform transformed how we work.",
    "author": "Sarah Johnson",
    "role": "CEO at TechCorp",
    "avatar": "/img/avatar.jpg"
  },
  "cta_text": "See How It Works",
  "cta_url": "/demo"
}
config: {
  "style": "gradient",
  "gradient_from": "primary",
  "gradient_to": "secondary",
  "padding_y": "20"
}

Dark theme with inverted logos:
{
  "headline": "Trusted by Industry Leaders",
  "logos_title": "Our Partners",
  "logos": [{"url": "/img/partner.svg", "alt": "Partner"}],
  "cta_text": "Get Started",
  "cta_url": "/signup"
}
config: {
  "style": "dark",
  "background_color": "neutral",
  "logo_filter": "brightness(0) invert(1)",
  "logos_opacity": "80"
}

Full-featured section:
{
  "badge": "Trusted Platform",
  "headline": "Powering the World's Best Teams",
  "subheadline": "Join thousands of satisfied customers",
  "stats": [{"value": "50K+", "label": "Users"}],
  "quote": {"text": "Amazing product!", "author": "John Doe"},
  "logos_title": "As seen in",
  "logos": [{"url": "/img/logo.svg", "alt": "Logo"}],
  "cta_text": "Try Free",
  "cta_url": "/trial",
  "secondary_cta_text": "Learn More",
  "secondary_cta_url": "/features",
  "trust_badges": [
    {"icon": "check", "text": "No credit card required"},
    {"icon": "check", "text": "Cancel anytime"}
  ]
}
config: {
  "style": "default",
  "padding_y": "20",
  "animate": true
}
""",
        "default_content": {
            "badge": "",
            "headline": "Join 10,000+ Happy Customers",
            "subheadline": "See why businesses choose us to power their growth",
            "stats": [
                {"value": "10K+", "label": "Active Users"},
                {"value": "99%", "label": "Satisfaction"},
                {"value": "24/7", "label": "Support"},
                {"value": "150+", "label": "Countries"},
            ],
            "quote": {
                "text": "",
                "author": "",
                "role": "",
                "avatar": "",
            },
            "logos_title": "Trusted by leading companies",
            "logos": [
                {"url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google.svg", "alt": "Google"},
                {
                    "url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft.svg",
                    "alt": "Microsoft",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify.svg",
                    "alt": "Spotify",
                },
            ],
            "cta_text": "Start Free Trial",
            "cta_url": "#signup",
            "secondary_cta_text": "",
            "secondary_cta_url": "",
            "trust_badges": [
                {"icon": "check", "text": "No credit card required"},
                {"icon": "check", "text": "Cancel anytime"},
            ],
        },
        "default_config": {
            "style": "default",
            "padding_y": "16",
            "max_width": "",
            "background_color": "primary",
            "text_color": "primary-content",
            "gradient_direction": "r",
            "gradient_from": "primary",
            "gradient_to": "secondary",
            "badge_style": "secondary",
            "headline_size": "3xl",
            "headline_size_md": "4xl",
            "headline_size_lg": "5xl",
            "headline_weight": "bold",
            "headline_margin": "4",
            "subheadline_size": "xl",
            "subheadline_opacity": "90",
            "subheadline_max_width": "2xl",
            "subheadline_margin": "8",
            "stats_gap": "8",
            "stats_gap_md": "16",
            "stats_margin": "12",
            "stat_padding": "4",
            "stat_value_size": "4xl",
            "stat_value_size_md": "5xl",
            "stat_value_weight": "bold",
            "stat_value_color": "",
            "stat_label_size": "sm",
            "stat_label_opacity": "80",
            "quote_size": "xl",
            "quote_size_md": "2xl",
            "quote_max_width": "3xl",
            "quote_margin": "12",
            "align": "center",
            "logos_margin": "12",
            "logos_title_size": "sm",
            "logos_gap": "8",
            "logos_gap_md": "12",
            "logo_height": "8",
            "logo_height_md": "10",
            "logos_opacity": "70",
            "logo_filter": "",
            "cta_style": "secondary",
            "cta_size": "lg",
            "secondary_cta_style": "ghost",
            "animate": True,
        },
    },
    {
        "name": "Social Proof CTA - Dark with Logos",
        "zone_type": ZoneType.SOCIAL_PROOF_CTA,
        "template_file": "landing_pages/zones/social_proof_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/social_proof_cta.html

Dark social proof section with inverted logos for high contrast.

Uses style="dark". See "Social Proof CTA - Stats & Logos" for full documentation.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text
subheadline        Supporting paragraph text
logos_title        Text above logos
logos[]            Array of logo objects: {url, alt}
cta_text           Primary button text
cta_url            Primary button URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

style              Set to "dark" for this template
background_color   Background color (default: neutral)
logo_filter        CSS filter for logos (default: brightness(0) invert(1))
logos_opacity      Logo opacity (default: 80)
padding_y          Vertical padding (default: 16)
animate            Enable animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Dark neutral background:
config: {
  "style": "dark",
  "background_color": "neutral",
  "logo_filter": "brightness(0) invert(1)",
  "logos_opacity": "80"
}

Dark with grayscale logos:
config: {
  "style": "dark",
  "background_color": "base-300",
  "logo_filter": "grayscale(100%) brightness(2)",
  "logos_opacity": "60"
}
""",
        "default_content": {
            "badge": "",
            "headline": "Trusted by Industry Leaders",
            "subheadline": "Join the companies that rely on us every day",
            "quote": {
                "text": "",
                "author": "",
                "role": "",
                "avatar": "",
            },
            "stats": [],
            "logos_title": "Our Partners",
            "logos": [
                {"url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/google.svg", "alt": "Google"},
                {
                    "url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/microsoft.svg",
                    "alt": "Microsoft",
                },
                {
                    "url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/spotify.svg",
                    "alt": "Spotify",
                },
                {"url": "https://flowbite.s3.amazonaws.com/blocks/marketing-ui/customers/amazon.svg", "alt": "Amazon"},
            ],
            "cta_text": "Get Started",
            "cta_url": "#signup",
            "secondary_cta_text": "",
            "secondary_cta_url": "",
            "trust_badges": [],
        },
        "default_config": {
            "style": "dark",
            "padding_y": "16",
            "background_color": "neutral",
            "text_color": "neutral-content",
            "logo_filter": "brightness(0) invert(1)",
            "logos_opacity": "80",
            "animate": True,
        },
    },
    {
        "name": "Social Proof CTA - Minimal Stats",
        "zone_type": ZoneType.SOCIAL_PROOF_CTA,
        "template_file": "landing_pages/zones/social_proof_cta.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/social_proof_cta.html

Minimal social proof section focused on key statistics.

Uses style="minimal". See "Social Proof CTA - Stats & Logos" for full documentation.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

headline           Main heading text
stats[]            Array of statistics: {value, label}
cta_text           Primary button text
cta_url            Primary button URL
trust_badges[]     Array of trust indicators: {icon, text}

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

style              Set to "minimal" for this template
background_color   Background color (default: base-200)
padding_y          Vertical padding (default: 12)
stat_value_size    Stat value text size (default: 5xl)
animate            Enable animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Clean minimal:
config: {
  "style": "minimal",
  "background_color": "base-100",
  "padding_y": "16",
  "stat_value_size": "5xl"
}

Compact minimal:
config: {
  "style": "minimal",
  "background_color": "base-200",
  "padding_y": "8",
  "stat_value_size": "4xl"
}
""",
        "default_content": {
            "badge": "",
            "headline": "Proven Results",
            "subheadline": "",
            "quote": {
                "text": "",
                "author": "",
                "role": "",
                "avatar": "",
            },
            "stats": [
                {"value": "500K+", "label": "Downloads"},
                {"value": "4.9/5", "label": "Rating"},
                {"value": "100+", "label": "Integrations"},
            ],
            "logos_title": "",
            "logos": [],
            "cta_text": "Get Started Free",
            "cta_url": "#signup",
            "secondary_cta_text": "View Pricing",
            "secondary_cta_url": "#pricing",
            "trust_badges": [
                {"icon": "check", "text": "Free forever plan"},
                {"icon": "check", "text": "No setup required"},
            ],
        },
        "default_config": {
            "style": "minimal",
            "padding_y": "12",
            "background_color": "base-200",
            "stat_value_size": "5xl",
            "stat_value_size_md": "6xl",
            "cta_style": "primary",
            "animate": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
