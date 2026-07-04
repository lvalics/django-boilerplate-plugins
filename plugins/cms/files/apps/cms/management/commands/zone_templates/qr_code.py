"""
QR Code zone templates.
"""

from ._base import ZoneType

QR_CODE_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "QR Code - Default",
        "zone_type": ZoneType.QR_CODE,
        "template_file": "cms/zones/qr_code.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/qr_code.html

Simple centered QR code with optional title and description.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

url             URL to encode in QR code
            * If omitted, uses current page URL automatically
            * Example: "https://example.com/landing"
title           Optional heading above QR code
            * Example: "Scan to Visit"
description     Optional text below QR code
            * Example: "Point your camera at the QR code to open the link."

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "default" (simple centered layout)
  padding_y          Vertical padding in Tailwind units (default: 12)
                 * "8"  - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
                 * "20" - 5rem (80px) - very spacious
                 * "24" - 6rem (96px) - extra spacious

QR CODE
  qr_size            QR code size in pixels (default: 200)
                 * "150" - small QR code
                 * "200" - standard size (default)
                 * "250" - larger QR code
                 * "300" - large QR code
                 * "400" - extra large
  qr_color           QR code color hex without # (default: 000000)
                 * "000000" - black (default)
                 * "1a1a1a" - dark gray
                 * "0066cc" - blue
                 * "6b21a8" - purple
                 * "059669" - green

COLORS
  background_color   Section background color (default: base-100)
                 * "base-100" - lightest background (default)
                 * "base-200" - light gray
                 * "base-300" - darker gray
                 * "primary" - brand color background
                 * "neutral" - dark neutral
  title_color        Heading text color (default: base-content)
                 * "base-content" - default text color
                 * "primary" - brand color
                 * "white" - for dark backgrounds
                 * "base-content/80" - slightly muted
                 * "neutral" - neutral dark

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple page link:
{
  "url": "https://example.com",
  "title": "Visit Our Website",
  "description": "Scan this code with your phone camera."
}
config: {"style": "default"}

App download:
{
  "url": "https://apps.apple.com/app/myapp",
  "title": "Download Our App",
  "description": "Available on iOS and Android."
}
config: {"style": "default", "qr_size": "250", "qr_color": "0066cc"}

Event check-in:
{
  "url": "https://event.example.com/checkin/abc123",
  "title": "Check In Here"
}
config: {"style": "default", "padding_y": "16"}

Dark theme:
config: {
  "style": "default",
  "background_color": "neutral",
  "title_color": "white",
  "qr_color": "ffffff"
}
""",
        "default_content": {
            "url": "https://example.com",
            "title": "Scan to Visit",
            "description": "Point your camera at the QR code to open the link.",
        },
        "default_config": {
            "style": "default",
            "padding_y": "12",
            "qr_size": "200",
            "qr_color": "000000",
            "background_color": "base-100",
            "title_color": "base-content",
        },
    },
    {
        "name": "QR Code - Card",
        "zone_type": ZoneType.QR_CODE,
        "template_file": "cms/zones/qr_code.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/qr_code.html

QR code in a card with title, description, and optional help link.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

url             URL to encode in QR code
            * If omitted, uses current page URL automatically
            * Example: "https://example.com/app"
title           Card title displayed below QR code
            * Example: "Start listening instantly"
description     Card description text
            * Example: "Use your phone's camera to scan the QR code."

HELP LINK
  help_link.text  Help link text
              * Example: "What's a QR code?"
  help_link.url   Help link URL
              * Example: "/help/qr-codes"

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "card" (REQUIRED for this template)
  padding_y          Vertical padding in Tailwind units (default: 12)
                 * "8"  - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
                 * "20" - 5rem (80px) - very spacious
                 * "24" - 6rem (96px) - extra spacious

QR CODE
  qr_size            QR code size in pixels (default: 200)
                 * "150" - small QR code
                 * "200" - standard size (default)
                 * "250" - larger QR code
                 * "300" - large QR code
                 * "400" - extra large
  qr_color           QR code color hex without # (default: 000000)
                 * "000000" - black (default)
                 * "1a1a1a" - dark gray
                 * "0066cc" - blue
                 * "6b21a8" - purple
                 * "059669" - green
  qr_bg              QR code container background (default: white)
                 * "white" - white background (default)
                 * "base-100" - theme light background
                 * "gray-100" - light gray
                 * "transparent" - no background
                 * "base-200" - slightly darker

COLORS
  background_color   Section background color (default: base-100)
                 * "base-100" - lightest background (default)
                 * "base-200" - light gray
                 * "base-300" - darker gray
                 * "primary" - brand color background
                 * "neutral" - dark neutral
  card_bg            Card background color (default: base-200)
                 * "base-100" - white/light
                 * "base-200" - light gray (default)
                 * "base-300" - darker gray
                 * "white" - pure white
                 * "neutral" - dark card
  link_color         Help link color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "info" - blue
                 * "neutral" - neutral gray

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

App download card:
{
  "url": "https://example.com/app",
  "title": "Start listening instantly",
  "description": "Use your phone's camera to scan the QR code and download our app.",
  "help_link": {"text": "What's a QR code?", "url": "/help/qr"}
}
config: {"style": "card"}

Event ticket:
{
  "url": "https://event.example.com/ticket/12345",
  "title": "Your Event Ticket",
  "description": "Present this code at the entrance for check-in.",
  "help_link": {"text": "Ticket FAQ", "url": "/faq"}
}
config: {"style": "card", "qr_size": "250"}

Menu or document link:
{
  "url": "https://restaurant.example.com/menu",
  "title": "View Our Menu",
  "description": "Scan to see today's specials and full menu."
}
config: {"style": "card", "card_bg": "base-100"}

Payment QR:
{
  "url": "https://pay.example.com/abc123",
  "title": "Scan to Pay",
  "description": "Quick and secure payment via mobile."
}
config: {"style": "card", "qr_color": "059669", "link_color": "success"}

Dark theme card:
config: {
  "style": "card",
  "background_color": "neutral",
  "card_bg": "base-200",
  "qr_bg": "white"
}
""",
        "default_content": {
            "url": "https://example.com/app",
            "title": "Start listening instantly",
            "description": "Use your phone's camera to scan the QR code and download our app.",
            "help_link": {"text": "What's a QR code?", "url": "#"},
        },
        "default_config": {
            "style": "card",
            "padding_y": "12",
            "qr_size": "200",
            "qr_color": "000000",
            "qr_bg": "white",
            "background_color": "base-100",
            "card_bg": "base-200",
            "link_color": "primary",
        },
    },
    {
        "name": "QR Code - Share Profile",
        "zone_type": ZoneType.QR_CODE,
        "template_file": "cms/zones/qr_code.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/qr_code.html

Profile card with avatar, name, handle, and QR code for sharing.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

url             Profile URL to encode in QR code
            * Example: "https://example.com/profile/johndoe"
avatar          Profile image URL
            * Full URL or relative path
            * Example: "https://example.com/avatars/johndoe.jpg"
name            Display name shown above QR code
            * Example: "John Doe"
handle          Username or handle (shown muted)
            * Example: "@johndoe"
description     Share message text below QR code
            * Example: "Scan to follow me and stay connected!"

CTA BUTTON
  cta.text        Button text
              * Example: "View Profile"
  cta.url         Button URL
              * Example: "https://example.com/profile/johndoe"

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "profile" (REQUIRED for this template)
  padding_y          Vertical padding in Tailwind units (default: 12)
                 * "8"  - 2rem (32px) - compact
                 * "12" - 3rem (48px) - default
                 * "16" - 4rem (64px) - spacious
                 * "20" - 5rem (80px) - very spacious
                 * "24" - 6rem (96px) - extra spacious

QR CODE
  qr_size            QR code size in pixels (default: 200)
                 * "150" - small QR code
                 * "200" - standard size (default)
                 * "250" - larger QR code
                 * "300" - large QR code
                 * "400" - extra large
  qr_color           QR code color hex without # (default: 000000)
                 * "000000" - black (default)
                 * "1a1a1a" - dark gray
                 * "0066cc" - blue
                 * "6b21a8" - purple
                 * "059669" - green
  qr_width           Tailwind width class for QR container (default: 56)
                 * "48" - 12rem (192px) - smaller
                 * "56" - 14rem (224px) - default
                 * "64" - 16rem (256px) - larger
                 * "72" - 18rem (288px) - large
                 * "80" - 20rem (320px) - extra large

COLORS
  background_color   Section background color (default: base-100)
                 * "base-100" - lightest background (default)
                 * "base-200" - light gray
                 * "base-300" - darker gray
                 * "primary" - brand color background
                 * "neutral" - dark neutral
  card_bg            Card background color (default: base-200)
                 * "base-100" - white/light
                 * "base-200" - light gray (default)
                 * "base-300" - darker gray
                 * "white" - pure white
                 * "neutral" - dark card
  ring_color         Avatar ring/border color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "success" - green
                 * "info" - blue
  title_color        Name text color (default: base-content)
                 * "base-content" - default text color
                 * "primary" - brand color
                 * "white" - for dark backgrounds
                 * "neutral" - neutral dark
                 * "base-content/80" - slightly muted
  btn_color          CTA button color (default: primary)
                 * "primary" - brand color (default)
                 * "secondary" - secondary brand
                 * "accent" - accent color
                 * "success" - green
                 * "neutral" - neutral

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Social profile share:
{
  "url": "https://example.com/profile/johndoe",
  "avatar": "https://example.com/avatars/johndoe.jpg",
  "name": "John Doe",
  "handle": "@johndoe",
  "description": "Scan to follow me and stay connected!",
  "cta": {"text": "View Profile", "url": "https://example.com/profile/johndoe"}
}
config: {"style": "profile"}

Business card:
{
  "url": "https://company.example.com/team/jsmith",
  "avatar": "https://company.example.com/photos/jsmith.jpg",
  "name": "Jane Smith",
  "handle": "VP of Engineering",
  "description": "Connect with me for partnership opportunities.",
  "cta": {"text": "Contact Me", "url": "mailto:jane@example.com"}
}
config: {"style": "profile", "ring_color": "accent", "btn_color": "accent"}

Artist/Creator profile:
{
  "url": "https://music.example.com/artist/dj-beats",
  "avatar": "https://music.example.com/artists/dj-beats.jpg",
  "name": "DJ Beats",
  "handle": "@djbeats",
  "description": "Scan to listen to my latest tracks!",
  "cta": {"text": "Listen Now", "url": "https://music.example.com/artist/dj-beats"}
}
config: {"style": "profile", "qr_color": "6b21a8", "ring_color": "secondary"}

Influencer profile:
{
  "url": "https://instagram.com/influencer",
  "avatar": "https://example.com/photos/influencer.jpg",
  "name": "Lifestyle Guru",
  "handle": "@lifestyleguru",
  "description": "Follow for daily tips and inspiration!"
}
config: {"style": "profile", "qr_size": "250", "qr_width": "64"}

Dark theme profile:
config: {
  "style": "profile",
  "background_color": "neutral",
  "card_bg": "base-200",
  "title_color": "base-content",
  "ring_color": "primary",
  "btn_color": "primary"
}
""",
        "default_content": {
            "url": "https://example.com/profile/johndoe",
            "avatar": "https://flowbite.com/docs/images/people/profile-picture-3.jpg",
            "name": "John Doe",
            "handle": "@johndoe",
            "description": "Scan to follow me and stay connected!",
            "cta": {"text": "View Profile", "url": "#"},
        },
        "default_config": {
            "style": "profile",
            "padding_y": "12",
            "qr_size": "200",
            "qr_color": "000000",
            "qr_width": "56",
            "background_color": "base-100",
            "card_bg": "base-200",
            "ring_color": "primary",
            "title_color": "base-content",
            "btn_color": "primary",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
