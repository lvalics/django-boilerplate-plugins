"""
Table zone templates.
"""

from ._base import ZoneType

TABLE_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Table - Feature Comparison",
        "zone_type": ZoneType.TABLE,
        "template_file": "landing_pages/zones/table.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/table.html

Feature/pricing comparison table with checkmarks, X icons, and plan columns.
Ideal for pricing pages, feature matrices, and plan comparisons.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  title              Main section heading
                 * "Compare Plans"
                 * "Feature Comparison"
                 * "Choose Your Plan"

  subtitle           Description text below title
                 * "Find the perfect plan for your needs"
                 * "All plans include 24/7 support"
                 * "Compare features across all tiers"

  feature_column     Label for the features column (default: "Features")
                 * "Features"
                 * "What's Included"
                 * "Capabilities"

PLANS (columns)
  plans              Array of plan objects defining table columns:

    name             Plan name displayed in header
                 * "Free", "Basic", "Pro", "Enterprise"
                 * "Starter", "Growth", "Scale"
                 * "Monthly", "Annual"

    price            Price display text
                 * "$0", "$9", "$29", "$99"
                 * "Free", "Contact Us"
                 * "$29/mo", "$290/yr"

    period           Price period text (shown below price)
                 * "/month", "/mo"
                 * "/year", "/yr"
                 * "per user/month"

    badge            Optional badge text above plan name
                 * "Popular", "Best Value"
                 * "Recommended", "Most Chosen"
                 * "New", "Limited Time"

    badge_color      Badge color (DaisyUI color, default: primary)
                 * "primary" - brand color
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "success" - green
                 * "warning" - yellow/orange

    highlighted      Boolean to emphasize this plan (larger CTA button)
                 * true - larger button, draws attention
                 * false - standard button size

    cta              Call-to-action button object:
      text           Button text
                 * "Get Started", "Start Free"
                 * "Start Trial", "Contact Sales"
                 * "Upgrade Now", "Subscribe"
      url            Button URL
                 * "#", "/signup", "/contact"
                 * "/checkout?plan=pro"
      color          Button color (default: primary)
                 * "primary", "secondary", "accent"
                 * "ghost", "success"

FEATURES (rows)
  features           Array of feature objects defining table rows:

    name             Feature name/description displayed in first column
                 * "Team members", "Storage space"
                 * "API access", "Custom integrations"
                 * "Priority support", "SLA guarantee"

    tooltip          Optional help text shown on hover (info icon)
                 * "Maximum number of team members allowed"
                 * "Available with Pro plan or higher"
                 * "99.9% uptime guarantee"

    values           Array of values matching plans order:
                 * true/false - renders as checkmark/X icon
                 * "text" - displays as plain text
                 * Examples:
                   - [false, true, true] - X, check, check
                   - ["5 GB", "50 GB", "Unlimited"]
                   - ["Up to 5", "Up to 20", "Unlimited"]

CTA ROW
  show_cta           Show CTA buttons row at bottom (default: false)
                 * true - displays footer row with CTA buttons
                 * false - no footer row

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              Table style variant (REQUIRED: "comparison")
                 * "comparison" - feature comparison with icons

  max_width          Container maximum width (default: 6xl)
                 * "4xl" - 896px (compact tables)
                 * "5xl" - 1024px (medium tables)
                 * "6xl" - 1152px (default, wide tables)
                 * "7xl" - 1280px (extra wide)
                 * "full" - full width

  padding_y          Vertical section padding in Tailwind units (default: 12)
                 * "8"  - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
                 * "20" - 5rem (80px) - very spacious
                 * "24" - 6rem (96px) - extra spacious

COLORS
  background_color   Section background color (default: base-100)
                 * "base-100" - lightest/white (default)
                 * "base-200" - light gray
                 * "base-300" - medium gray
                 * "neutral" - dark neutral
                 * "primary" - brand color background

  header_bg          Table header row background (default: base-200)
                 * "base-200" - default light gray
                 * "base-300" - darker gray
                 * "primary" - brand color header
                 * "neutral" - dark header
                 * "transparent" - no background

  header_text        Header text color (default: base-content)
                 * "base-content" - default text color
                 * "white" - for dark backgrounds
                 * "primary" - brand color text
                 * "primary-content" - for primary background

  price_color        Price text color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "success" - green
                 * "base-content" - default text

  check_color        Checkmark icon color (default: success)
                 * "success" - green (default)
                 * "primary" - brand color
                 * "accent" - accent color
                 * "info" - blue

  x_color            X icon color for false values (default: base-content/30)
                 * "base-content/30" - faded (default)
                 * "base-content/50" - more visible
                 * "error" - red
                 * "error/50" - faded red

TABLE OPTIONS
  striped            Zebra striping for alternating rows (default: false)
                 * true - alternating row backgrounds
                 * false - uniform row backgrounds

  hover              Row hover effect (default: false)
                 * true - highlight row on hover
                 * false - no hover effect

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic pricing comparison:
{
  "title": "Simple Pricing",
  "plans": [
    {"name": "Free", "price": "$0", "cta": {"text": "Get Started", "url": "/signup"}},
    {"name": "Pro", "price": "$29", "period": "/mo", "cta": {"text": "Start Trial", "url": "/trial"}}
  ],
  "features": [
    {"name": "Projects", "values": ["3", "Unlimited"]},
    {"name": "Storage", "values": ["1 GB", "100 GB"]},
    {"name": "API Access", "values": [false, true]}
  ],
  "show_cta": true
}
config: {"style": "comparison"}

Three-tier with popular badge:
{
  "title": "Choose Your Plan",
  "subtitle": "All plans include 14-day free trial",
  "plans": [
    {"name": "Starter", "price": "$9", "period": "/mo",
     "cta": {"text": "Get Started", "url": "#", "color": "ghost"}},
    {"name": "Pro", "price": "$29", "period": "/mo", "badge": "Most Popular",
     "highlighted": true, "cta": {"text": "Start Free Trial", "url": "#"}},
    {"name": "Enterprise", "price": "Custom",
     "cta": {"text": "Contact Sales", "url": "#", "color": "ghost"}}
  ],
  "features": [
    {"name": "Team members", "values": ["Up to 5", "Up to 20", "Unlimited"]},
    {"name": "Storage", "values": ["5 GB", "50 GB", "Unlimited"]},
    {"name": "API access", "tooltip": "REST and GraphQL APIs", "values": [false, true, true]},
    {"name": "Priority support", "values": [false, true, true]},
    {"name": "Custom integrations", "values": [false, false, true]}
  ],
  "show_cta": true
}
config: {"style": "comparison", "striped": true, "hover": true}

Dark header style:
config: {
  "style": "comparison",
  "header_bg": "neutral",
  "header_text": "white",
  "price_color": "primary",
  "striped": true
}

Minimal without CTAs:
{
  "title": "Feature Matrix",
  "plans": [{"name": "Basic"}, {"name": "Standard"}, {"name": "Premium"}],
  "features": [
    {"name": "Feature A", "values": [true, true, true]},
    {"name": "Feature B", "values": [false, true, true]},
    {"name": "Feature C", "values": [false, false, true]}
  ],
  "show_cta": false
}
config: {"style": "comparison", "padding_y": "8"}
""",
        "default_content": {
            "title": "Compare Plans",
            "subtitle": "Choose the plan that fits your needs",
            "feature_column": "Features",
            "plans": [
                {
                    "name": "Starter",
                    "price": "$9",
                    "period": "/month",
                    "cta": {"text": "Get Started", "url": "#", "color": "ghost"},
                },
                {
                    "name": "Professional",
                    "price": "$29",
                    "period": "/month",
                    "badge": "Most Popular",
                    "badge_color": "primary",
                    "highlighted": True,
                    "cta": {"text": "Start Free Trial", "url": "#", "color": "primary"},
                },
                {
                    "name": "Enterprise",
                    "price": "$99",
                    "period": "/month",
                    "cta": {"text": "Contact Sales", "url": "#", "color": "ghost"},
                },
            ],
            "features": [
                {"name": "Team members", "values": ["Up to 5", "Up to 20", "Unlimited"]},
                {"name": "Storage", "values": ["5 GB", "50 GB", "Unlimited"]},
                {"name": "Projects", "values": ["3", "Unlimited", "Unlimited"]},
                {
                    "name": "API access",
                    "tooltip": "REST API access for integrations",
                    "values": [False, True, True],
                },
                {"name": "Custom integrations", "values": [False, False, True]},
                {"name": "Priority support", "values": [False, True, True]},
                {"name": "SLA guarantee", "values": [False, False, True]},
            ],
            "show_cta": True,
        },
        "default_config": {
            "style": "comparison",
            "max_width": "6xl",
            "padding_y": "12",
            "background_color": "base-100",
            "header_bg": "base-200",
            "header_text": "base-content",
            "price_color": "primary",
            "check_color": "success",
            "x_color": "base-content/30",
            "striped": True,
            "hover": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Table - Data Table",
        "zone_type": ZoneType.TABLE,
        "template_file": "landing_pages/zones/table.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/table.html

Standard data table for displaying structured information with rich cell types.
Supports avatars, badges, links, and custom alignment.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

SECTION HEADER
  title              Main section heading
                 * "Our Team"
                 * "Recent Orders"
                 * "Product Catalog"

  subtitle           Description text below title
                 * "Meet the people behind our success"
                 * "Your recent purchase history"
                 * "Browse our complete collection"

  caption            Table caption for accessibility (shown above table)
                 * "List of team members and their roles"
                 * "Order history for the last 30 days"
                 * "Available products and pricing"

TABLE STRUCTURE
  headers            Array of column headers (simple strings or objects):

    Simple format:
                 * ["Name", "Email", "Role", "Status"]
                 * ["Product", "Price", "Stock", "Action"]

    Object format with alignment:
                 * {"label": "Name", "align": "left"}
                 * {"label": "Price", "align": "right"}
                 * {"label": "Status", "align": "center"}

  rows               Array of row arrays, each cell can be:

    Simple text:
                 * "John Smith"
                 * "$29.99"
                 * "Active"

    With avatar/image:
                 * {"value": "John Smith", "image": "/photo.jpg"}
                 * {"value": "John", "image": "/photo.jpg", "subtitle": "john@email.com"}

    With badge:
                 * {"value": "Active", "badge": true}
                 * {"value": "Active", "badge": true, "badge_color": "success"}
                 * {"value": "Pending", "badge": true, "badge_color": "warning"}
                 * Badge colors: ghost, primary, secondary, accent, success, warning, error, info

    With link:
                 * {"value": "View Details", "link": "/details/123"}
                 * {"value": "Edit", "link": "/edit/123"}

    With styling:
                 * {"value": "$99.00", "align": "right"}
                 * {"value": "Total", "bold": true}
                 * {"value": "$199.00", "align": "right", "bold": true}

FOOTER ROW
  footer_row         Optional footer row (same format as regular rows)
                 * ["Total", "", "", {"value": "$299.00", "align": "right", "bold": true}]
                 * ["", "", "Subtotal:", "$199.00"]

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              Table style variant (default: "default")
                 * "default" - standard data table

  max_width          Container maximum width (default: 6xl)
                 * "4xl" - 896px (compact tables)
                 * "5xl" - 1024px (medium tables)
                 * "6xl" - 1152px (default, wide tables)
                 * "7xl" - 1280px (extra wide)
                 * "full" - full width

  padding_y          Vertical section padding in Tailwind units (default: 12)
                 * "8"  - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
                 * "20" - 5rem (80px) - very spacious

COLORS
  background_color   Section background color (default: base-100)
                 * "base-100" - lightest/white (default)
                 * "base-200" - light gray
                 * "base-300" - medium gray
                 * "neutral" - dark neutral

  header_bg          Table header row background (default: base-200)
                 * "base-200" - default light gray
                 * "base-300" - darker gray
                 * "primary" - brand color header
                 * "neutral" - dark header

  header_text        Header text color (default: base-content)
                 * "base-content" - default text color
                 * "white" - for dark backgrounds
                 * "primary-content" - for primary background

  footer_bg          Footer row background (default: base-200)
                 * "base-200" - default light gray
                 * "base-300" - darker gray
                 * "transparent" - no background

  link_color         Link color for cells with links (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "info" - blue

TABLE OPTIONS
  striped            Zebra striping for alternating rows (default: false)
                 * true - alternating row backgrounds
                 * false - uniform row backgrounds

  hover              Row hover effect (default: false)
                 * true - highlight row on hover
                 * false - no hover effect

  bordered           Show row borders (default: false)
                 * true - border between rows
                 * false - no borders

  shadow             Add shadow and rounded corners to table (default: false)
                 * true - shadow-lg and rounded-lg
                 * false - flat table

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Team directory with avatars:
{
  "title": "Our Team",
  "headers": ["Name", "Position", "Department", "Status"],
  "rows": [
    [
      {"value": "John Smith", "image": "/photos/john.jpg", "subtitle": "john@company.com"},
      "CEO & Founder",
      "Executive",
      {"value": "Active", "badge": true, "badge_color": "success"}
    ],
    [
      {"value": "Sarah Johnson", "image": "/photos/sarah.jpg", "subtitle": "sarah@company.com"},
      "CTO",
      "Engineering",
      {"value": "Active", "badge": true, "badge_color": "success"}
    ]
  ]
}
config: {"style": "default", "striped": true, "hover": true, "shadow": true}

Order history with footer:
{
  "title": "Recent Orders",
  "caption": "Orders from the last 30 days",
  "headers": [
    {"label": "Order ID", "align": "left"},
    {"label": "Product", "align": "left"},
    {"label": "Date", "align": "left"},
    {"label": "Amount", "align": "right"}
  ],
  "rows": [
    ["#12345", "Pro Plan", "2024-01-15", {"value": "$29.00", "align": "right"}],
    ["#12346", "Storage Add-on", "2024-01-16", {"value": "$9.00", "align": "right"}]
  ],
  "footer_row": [
    {"value": "Total", "bold": true}, "", "", {"value": "$38.00", "align": "right", "bold": true}
  ]
}
config: {"style": "default", "bordered": true}

Product catalog with links:
{
  "title": "Products",
  "headers": ["Product", "Category", "Price", "Action"],
  "rows": [
    ["Widget Pro", "Hardware", "$99.00", {"value": "View Details", "link": "/products/widget-pro"}],
    ["Service Plus", "Services", "$49.00/mo", {"value": "View Details", "link": "/products/service-plus"}]
  ]
}
config: {"style": "default", "hover": true, "link_color": "primary"}

Dark header compact table:
config: {
  "style": "default",
  "padding_y": "8",
  "header_bg": "neutral",
  "header_text": "white",
  "striped": true,
  "shadow": true
}

Minimal bordered table:
config: {
  "style": "default",
  "bordered": true,
  "shadow": false,
  "striped": false
}
""",
        "default_content": {
            "title": "Our Team",
            "subtitle": "",
            "caption": "",
            "headers": [
                {"label": "Name", "align": "left"},
                {"label": "Position", "align": "left"},
                {"label": "Department", "align": "left"},
                {"label": "Status", "align": "center"},
            ],
            "rows": [
                [
                    {
                        "value": "John Smith",
                        "image": "https://flowbite.com/docs/images/people/profile-picture-1.jpg",
                        "subtitle": "john@company.com",
                    },
                    "CEO & Founder",
                    "Executive",
                    {"value": "Active", "badge": True, "badge_color": "success"},
                ],
                [
                    {
                        "value": "Sarah Johnson",
                        "image": "https://flowbite.com/docs/images/people/profile-picture-2.jpg",
                        "subtitle": "sarah@company.com",
                    },
                    "CTO",
                    "Engineering",
                    {"value": "Active", "badge": True, "badge_color": "success"},
                ],
                [
                    {
                        "value": "Michael Brown",
                        "image": "https://flowbite.com/docs/images/people/profile-picture-3.jpg",
                        "subtitle": "michael@company.com",
                    },
                    "Lead Designer",
                    "Design",
                    {"value": "Away", "badge": True, "badge_color": "warning"},
                ],
            ],
            "footer_row": [],
        },
        "default_config": {
            "style": "default",
            "max_width": "6xl",
            "padding_y": "12",
            "background_color": "base-100",
            "header_bg": "base-200",
            "header_text": "base-content",
            "footer_bg": "base-200",
            "link_color": "primary",
            "striped": True,
            "hover": True,
            "bordered": False,
            "shadow": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
