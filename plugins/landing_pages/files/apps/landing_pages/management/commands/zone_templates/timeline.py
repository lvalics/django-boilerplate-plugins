"""
Timeline zone templates.
"""

from ._base import ZoneType

TIMELINE_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Timeline - Vertical",
        "zone_type": ZoneType.TIMELINE,
        "template_file": "landing_pages/zones/timeline.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/timeline.html

Vertical timeline with dates, titles, descriptions, and optional badges/links.
Best for company history, project milestones, or step-by-step processes.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  title              Section heading text
  subtitle           Description text below heading

TIMELINE ITEMS
  items              Array of timeline items:
    date             Date/time label (e.g., "March 2024", "Q1 2023")
    title            Item title (required)
    description      Item description text
    icon             Optional emoji/icon (e.g., "rocket", "star")
    badge            Optional badge text (e.g., "Milestone", "New")
    badge_color      Badge color (default: primary)
                     - "primary" - brand color
                     - "secondary" - secondary brand
                     - "accent" - accent color
                     - "success" - green
                     - "warning" - yellow
                     - "error" - red
                     - "info" - blue
    image            Optional image URL
    link.text        Link text (default: "Learn more")
    link.url         Link URL

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "vertical" (REQUIRED for this template)
  max_width          Container width (default: 4xl)
                     - "2xl" - 672px max width (narrow)
                     - "3xl" - 768px max width
                     - "4xl" - 896px max width (default)
                     - "5xl" - 1024px max width
                     - "6xl" - 1152px max width (wide)
  padding_y          Vertical padding in Tailwind units (default: 12)
                     - "8"  - 2rem (32px) - compact
                     - "12" - 3rem (48px) - default
                     - "16" - 4rem (64px) - spacious
                     - "20" - 5rem (80px) - very spacious
                     - "24" - 6rem (96px) - maximum
  centered           Center the timeline in container (default: false)
                     - false - left aligned (default)
                     - true - centered with max-w-2xl
  show_numbers       Show step numbers instead of icons (default: false)
                     - false - show icons or default calendar icon
                     - true - show 1, 2, 3... in dots

COLORS
  background_color   Section background color (default: base-100)
                     - "base-100" - lightest background (default)
                     - "base-200" - light gray
                     - "base-300" - darker gray
                     - "neutral" - dark neutral
                     - "primary" - brand color background
  line_color         Timeline line color (default: base-300)
                     - "base-200" - very light line
                     - "base-300" - light gray (default)
                     - "primary" - brand color line
                     - "secondary" - secondary brand
  dot_color          Timeline dot/circle color (default: primary)
                     - "primary" - brand color (default)
                     - "secondary" - secondary brand
                     - "accent" - accent color
                     - "success" - green
                     - "neutral" - dark neutral
  ring_color         Ring around dots (default: base-100)
                     - "base-100" - matches light background (default)
                     - "base-200" - for base-200 backgrounds
                     - "white" - pure white ring
  icon_text          Icon/number text color (default: primary-content)
                     - "primary-content" - contrasts primary (default)
                     - "secondary-content" - contrasts secondary
                     - "white" - white text
  title_color        Item title text color (default: base-content)
                     - "base-content" - default text color
                     - "primary" - brand color
                     - "white" - for dark backgrounds
  link_color         Link text color (default: primary)
                     - "primary" - brand color (default)
                     - "secondary" - secondary brand
                     - "accent" - accent color

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Company history:
{
  "title": "Our Journey",
  "subtitle": "Key milestones in our company history",
  "items": [
    {"date": "2020", "title": "Founded", "description": "Started in a garage", "icon": "rocket"},
    {"date": "2022", "title": "Series A", "description": "Raised $10M", "badge": "Milestone"},
    {"date": "2024", "title": "Global Launch", "description": "50 countries"}
  ]
}
config: {"style": "vertical", "centered": true}

Project roadmap with links:
{
  "title": "Product Roadmap",
  "items": [
    {"date": "Q1", "title": "Beta Launch", "description": "Initial release", "link": {"text": "View release notes", "url": "/releases/v1"}},
    {"date": "Q2", "title": "Mobile App", "description": "iOS and Android"},
    {"date": "Q3", "title": "Enterprise", "description": "Team features"}
  ]
}
config: {"style": "vertical", "show_numbers": true}

Dark theme timeline:
config: {
  "style": "vertical",
  "background_color": "neutral",
  "title_color": "white",
  "line_color": "base-300",
  "dot_color": "primary",
  "ring_color": "neutral"
}

Accent colored timeline:
config: {
  "style": "vertical",
  "dot_color": "accent",
  "line_color": "accent",
  "link_color": "accent"
}
""",
        "default_content": {
            "title": "Our Journey",
            "subtitle": "Key milestones in our company history",
            "items": [
                {
                    "date": "January 2020",
                    "title": "Company Founded",
                    "description": "We started with a simple idea: to make technology accessible to everyone.",
                    "icon": "rocket",
                },
                {
                    "date": "March 2021",
                    "title": "First Product Launch",
                    "description": "Released our flagship product to overwhelming positive response.",
                    "badge": "Milestone",
                    "badge_color": "success",
                },
                {
                    "date": "September 2022",
                    "title": "Series A Funding",
                    "description": "Raised $10M to accelerate growth and expand our team.",
                    "icon": "banknotes",
                },
                {
                    "date": "June 2024",
                    "title": "Global Expansion",
                    "description": "Now serving customers in over 50 countries worldwide.",
                    "icon": "globe-alt",
                    "link": {"text": "Read the full story", "url": "#"},
                },
            ],
        },
        "default_config": {
            "style": "vertical",
            "max_width": "4xl",
            "padding_y": "12",
            "centered": True,
            "background_color": "base-100",
            "line_color": "base-300",
            "dot_color": "primary",
            "ring_color": "base-100",
            "icon_text": "primary-content",
            "title_color": "base-content",
            "link_color": "primary",
            "show_numbers": False,
        },
    },
    {
        "name": "Timeline - Stepper",
        "zone_type": ZoneType.TIMELINE,
        "template_file": "landing_pages/zones/timeline.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/timeline.html

Horizontal stepper timeline for processes, workflows, or step-by-step guides.
Best for onboarding flows, checkout processes, or feature explanations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  title              Section heading text
  subtitle           Description text below heading

STEPS
  items              Array of step items:
    title            Step title (required)
    description      Step description text
    date             Optional date/label (e.g., "Step 1", "Day 1")
    icon             Optional emoji/icon (or use show_numbers config)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "stepper" (REQUIRED for this template)
  max_width          Container width (default: 4xl)
                     - "2xl" - 672px max width (narrow)
                     - "3xl" - 768px max width
                     - "4xl" - 896px max width (default)
                     - "5xl" - 1024px max width
                     - "6xl" - 1152px max width (wide)
                     - "full" - full width container
  padding_y          Vertical padding in Tailwind units (default: 12)
                     - "8"  - 2rem (32px) - compact
                     - "12" - 3rem (48px) - default
                     - "16" - 4rem (64px) - spacious
                     - "20" - 5rem (80px) - very spacious
  show_numbers       Show step numbers in circles (default: false)
                     - false - show icons or checkmarks
                     - true - show 1, 2, 3... (recommended for steppers)

COLORS
  background_color   Section background color (default: base-100)
                     - "base-100" - lightest background (default)
                     - "base-200" - light gray
                     - "base-300" - darker gray
                     - "neutral" - dark neutral
  line_color         Connecting line color (default: base-300)
                     - "base-200" - very light line
                     - "base-300" - light gray (default)
                     - "primary" - brand color line
  dot_color          Step circle color (default: primary)
                     - "primary" - brand color (default)
                     - "secondary" - secondary brand
                     - "accent" - accent color
                     - "success" - green (good for completed steps)
  ring_color         Ring around circles (default: base-100)
                     - "base-100" - matches light background (default)
                     - "base-200" - for base-200 backgrounds
  icon_text          Icon/number text color (default: primary-content)
                     - "primary-content" - contrasts primary (default)
                     - "white" - white text
  title_color        Step title text color (default: base-content)
                     - "base-content" - default text color
                     - "primary" - brand color

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Onboarding steps with numbers:
{
  "title": "How It Works",
  "subtitle": "Get started in just 3 simple steps",
  "items": [
    {"title": "Sign Up", "description": "Create your free account in seconds"},
    {"title": "Configure", "description": "Set up your preferences"},
    {"title": "Launch", "description": "Start using the platform"}
  ]
}
config: {"style": "stepper", "show_numbers": true}

Process flow with icons:
{
  "title": "Our Process",
  "items": [
    {"icon": "magnifying-glass", "title": "Discovery", "description": "We learn about your needs"},
    {"icon": "pencil", "title": "Design", "description": "We create the solution"},
    {"icon": "rocket", "title": "Delivery", "description": "We ship and iterate"}
  ]
}
config: {"style": "stepper"}

Checkout process:
{
  "title": "Checkout",
  "items": [
    {"date": "Step 1", "title": "Cart", "description": "Review your items"},
    {"date": "Step 2", "title": "Shipping", "description": "Enter your address"},
    {"date": "Step 3", "title": "Payment", "description": "Complete purchase"}
  ]
}
config: {"style": "stepper", "show_numbers": true, "dot_color": "success"}

Wide stepper with accent color:
config: {
  "style": "stepper",
  "max_width": "6xl",
  "dot_color": "accent",
  "line_color": "accent",
  "show_numbers": true
}

Dark theme stepper:
config: {
  "style": "stepper",
  "background_color": "neutral",
  "title_color": "white",
  "dot_color": "primary",
  "ring_color": "neutral"
}
""",
        "default_content": {
            "title": "How It Works",
            "subtitle": "Get started in just 3 simple steps",
            "items": [
                {
                    "title": "Create Account",
                    "description": "Sign up for free in under a minute. No credit card required.",
                },
                {
                    "title": "Set Up Your Profile",
                    "description": "Configure your preferences and connect your tools.",
                },
                {
                    "title": "Start Using",
                    "description": "You're all set! Begin exploring all features immediately.",
                },
            ],
        },
        "default_config": {
            "style": "stepper",
            "max_width": "4xl",
            "padding_y": "12",
            "background_color": "base-100",
            "line_color": "base-300",
            "dot_color": "primary",
            "ring_color": "base-100",
            "icon_text": "primary-content",
            "title_color": "base-content",
            "show_numbers": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
