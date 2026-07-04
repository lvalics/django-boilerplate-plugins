"""
Redirect zone templates.
"""

from ._base import ZoneType

REDIRECT_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Redirect - Immediate (301/302)",
        "zone_type": ZoneType.REDIRECT,
        "template_file": "landing_pages/zones/redirect.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/redirect.html

Immediate server-side redirect (301 permanent or 302 temporary).
No page content is shown - user is redirected before the page renders.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

redirect_url       Target URL to redirect to (required)
               • Absolute: "https://example.com/page"
               • Absolute: "https://newdomain.com/path/to/page"
               • Relative: "/other-page/"
               • Relative: "/products/sale/"
               • With query: "/search?q=keyword"

message            Optional message (only shown if delay > 0)
               • "We've moved! Taking you to our new home..."
               • "This page has been relocated."
               • "Redirecting to updated content..."
               • "Please wait while we redirect you."
               • "" (empty for immediate redirects)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

REDIRECT TYPE
  redirect_type      HTTP redirect status code (default: "302")
               • "301" - Permanent redirect
                 - SEO value transfers to new URL
                 - Browser caches the redirect
                 - Use for: retired pages, domain changes, URL restructuring
               • "302" - Temporary redirect
                 - No SEO transfer
                 - Browser does not cache
                 - Use for: A/B tests, maintenance, seasonal pages

DELAY TIMING
  delay              Seconds before redirect (default: 0)
               • 0 - immediate server-side redirect (no page shown)
               • 3 - short delay with countdown
               • 5 - medium delay for reading message
               • 10 - longer delay for important notices
               • Note: delay > 0 shows countdown page with message

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Permanent redirect (page moved):
{
  "content": {
    "redirect_url": "https://newsite.com/page",
    "message": ""
  },
  "config": {"redirect_type": "301", "delay": 0}
}

Temporary redirect (sale ended):
{
  "content": {
    "redirect_url": "/sale-ended/",
    "message": ""
  },
  "config": {"redirect_type": "302", "delay": 0}
}

Domain migration:
{
  "content": {
    "redirect_url": "https://newdomain.com/",
    "message": ""
  },
  "config": {"redirect_type": "301", "delay": 0}
}

═══════════════════════════════════════════════════════════════
USAGE NOTES
═══════════════════════════════════════════════════════════════

• Only ONE redirect zone per page (first active zone is used)
• Redirect zone takes priority over all other zones
• For immediate redirects (delay=0), no page content is shown
• For SEO, 301 redirects should be used for permanent moves
• 302 redirects are appropriate for temporary situations
""",
        "default_content": {
            "redirect_url": "https://example.com",
            "message": "",
        },
        "default_config": {
            "redirect_type": "302",
            "delay": 0,
        },
    },
    {
        "name": "Redirect - Delayed with Message",
        "zone_type": ZoneType.REDIRECT,
        "template_file": "landing_pages/zones/redirect.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/redirect.html

Redirect with animated countdown timer and custom message.
Shows a countdown page before redirecting the user.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

redirect_url       Target URL to redirect to (required)
               • Absolute: "https://example.com/new-page"
               • Absolute: "https://newdomain.com/"
               • Relative: "/new-location/"
               • Relative: "/updated-content/"
               • With params: "/page?ref=redirect"

message            Message displayed during countdown (optional)
               • "We've moved to a new home!"
               • "This page has been relocated. Redirecting..."
               • "This offer has ended. Returning to homepage..."
               • "Thank you! Redirecting to your dashboard..."
               • "Content moved. Taking you there now..."

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

DELAY TIMING
  delay              Seconds before redirect (default: 5)
               • 3 - quick redirect, brief message
               • 5 - standard delay (recommended)
               • 7 - slightly longer for reading
               • 10 - extended time for important messages
               • Note: Shows animated countdown circle

REDIRECT TYPE
  redirect_type      HTTP redirect status code (default: "301")
               • "301" - Permanent redirect (recommended for moved pages)
                 - SEO value transfers to new URL
                 - Use for: page moves, domain changes
               • "302" - Temporary redirect
                 - No SEO transfer
                 - Use for: maintenance, temporary moves

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Page moved permanently:
{
  "content": {
    "redirect_url": "https://newdomain.com/page",
    "message": "We've moved to a new home!"
  },
  "config": {"delay": 5, "redirect_type": "301"}
}

Maintenance redirect:
{
  "content": {
    "redirect_url": "/maintenance/",
    "message": "This page is temporarily unavailable."
  },
  "config": {"delay": 3, "redirect_type": "302"}
}

Campaign ended:
{
  "content": {
    "redirect_url": "/",
    "message": "This offer has ended. Returning to homepage..."
  },
  "config": {"delay": 5, "redirect_type": "302"}
}

Thank you page redirect:
{
  "content": {
    "redirect_url": "/dashboard/",
    "message": "Thank you for signing up! Redirecting to your dashboard..."
  },
  "config": {"delay": 5, "redirect_type": "302"}
}

Domain migration with notice:
{
  "content": {
    "redirect_url": "https://newbrand.com/",
    "message": "We've rebranded! Taking you to our new website..."
  },
  "config": {"delay": 7, "redirect_type": "301"}
}

═══════════════════════════════════════════════════════════════
TEMPLATE FEATURES
═══════════════════════════════════════════════════════════════

• Animated countdown circle with visual progress
• Numeric countdown display
• "Click here if not redirected" fallback link
• Meta refresh tag for JavaScript-disabled browsers
• Responsive centered layout
""",
        "default_content": {
            "redirect_url": "https://example.com",
            "message": "You are being redirected...",
        },
        "default_config": {
            "redirect_type": "301",
            "delay": 5,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
