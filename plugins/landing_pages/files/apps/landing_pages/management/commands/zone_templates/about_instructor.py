"""
About Instructor zone templates.
"""

from ._base import ZoneType

ABOUT_INSTRUCTOR_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "About - Single Column",
        "zone_type": ZoneType.ABOUT_INSTRUCTOR,
        "template_file": "landing_pages/zones/about_instructor.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/about_instructor.html

Centered single column about section with avatar, perfect for instructor bios.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

name            Person/company name (required)
title           Role or tagline (e.g., "Senior Product Designer")
photo           Avatar/image URL (headshot or logo)
bio             Biography text (supports HTML, rendered with |safe filter)
badge           Small badge/label above name (e.g., "Your Instructor")
credentials[]   Array of credential strings displayed as badges
social_links[]  Array of social link objects:
                • {platform: "twitter", url: "https://..."}
                • {platform: "linkedin", url: "https://..."}
                • {platform: "youtube", url: "https://..."}
                • {platform: "instagram", url: "https://..."}
                • {platform: "facebook", url: "https://..."}
                • {platform: "github", url: "https://..."}
buttons[]       Array of button objects: {text, url, target, style, size}
primary_cta     Primary CTA button object:
                • primary_cta.text - Button text
                • primary_cta.url - Button link URL
                • primary_cta.target - "_blank" for new tab (optional)
secondary_cta   Secondary CTA button object (same structure)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              Layout style (REQUIRED)
                 • "single-column" - centered content with avatar
                 • "two-column" - text in two columns
                 • "image-left" - photo left, content right
                 • "image-right" - content left, photo right
                 • "three-column" - values/features grid
                 • "team-grid" - team member cards
  max_width          Container max width (default: 6xl)
                 • "4xl" - 896px - narrow
                 • "5xl" - 1024px - medium
                 • "6xl" - 1152px - default
                 • "7xl" - 1280px - wide
  padding_y          Vertical padding in Tailwind units (default: 16)
                 • "8"  - 2rem (32px) - compact
                 • "12" - 3rem (48px) - medium
                 • "16" - 4rem (64px) - default
                 • "20" - 5rem (80px) - spacious
                 • "24" - 6rem (96px) - very spacious
  animate            Enable scroll animations (default: true)
                 • true - elements animate on scroll
                 • "false" - disable animations (string "false")

COLORS
  background_color   Section background color (default: base-100)
                 • "base-100" - lightest background (default)
                 • "base-200" - light gray
                 • "base-300" - darker gray
                 • "primary" - brand color background
                 • "neutral" - dark neutral
  badge_color        Badge color (default: primary)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "accent" - accent color
                 • "neutral" - gray
                 • "ghost" - subtle

AVATAR (single-column & team-grid styles)
  avatar_size        Avatar size in Tailwind units (default: 32)
                 • "16" - 64px - small
                 • "24" - 96px - medium
                 • "32" - 128px - default
                 • "40" - 160px - large
                 • "48" - 192px - extra large
  avatar_shape       Avatar border radius (default: full)
                 • "full" - circular avatar
                 • "xl" - rounded corners
                 • "lg" - slightly rounded
  ring_color         Ring color around avatar (default: primary)
                 • "primary" - brand color ring
                 • "secondary" - secondary brand
                 • "base-300" - subtle gray ring
                 • "accent" - accent color ring

TYPOGRAPHY
  name_size          Name text size on mobile (default: 3xl)
                 • "2xl" - smaller heading
                 • "3xl" - default
                 • "4xl" - larger heading
  name_size_md       Name text size on medium+ screens (default: 4xl)
                 • "3xl" - moderate size
                 • "4xl" - default
                 • "5xl" - large heading
  name_weight        Name font weight (default: bold)
                 • "semibold" - medium weight
                 • "bold" - default
                 • "extrabold" - heavy weight
  name_color         Name text color (default: base-content)
                 • "base-content" - default text color
                 • "primary" - brand color
                 • "white" - for dark backgrounds
  title_size         Title/role text size (default: xl)
                 • "lg" - smaller
                 • "xl" - default
                 • "2xl" - larger
  title_color        Title/role text color (default: primary)
                 • "primary" - brand color (default)
                 • "secondary" - secondary brand
                 • "base-content/70" - muted text
  bio_color          Bio text color (default: base-content/80)
                 • "base-content/80" - slightly muted (default)
                 • "base-content/70" - more muted
                 • "base-content" - full opacity

CREDENTIALS & CTA
  credential_style   Credential badge style (default: outline)
                 • "outline" - outlined badges (default)
                 • "primary" - filled primary
                 • "secondary" - filled secondary
                 • "ghost" - subtle background
  primary_btn_color  Primary button color (default: primary)
                 • "primary" - brand color (default)
                 • "secondary" - secondary brand
                 • "accent" - accent color
                 • Any DaisyUI color or hex
  primary_btn_style  Primary button style (default: solid)
                 • "solid" - filled (default)
                 • "outline" - outlined
                 • "ghost" - transparent
  secondary_btn_color Secondary button color (default: ghost)
                 • "ghost" - subtle (default)
                 • Any DaisyUI color
  secondary_btn_style Secondary button style (default: ghost)
                 • "ghost" - transparent (default)
                 • "outline" - outlined
                 • "solid" - filled

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple instructor bio:
{
  "badge": "Your Instructor",
  "name": "Jane Smith",
  "title": "Senior Developer & Educator",
  "photo": "https://example.com/jane.jpg",
  "bio": "10+ years building web applications.",
  "social_links": [{"platform": "twitter", "url": "#"}]
}
config: {"style": "single-column"}

With credentials and CTA:
{
  "name": "Dr. John Doe",
  "title": "AI Research Lead",
  "photo": "/media/john.jpg",
  "bio": "Former Google engineer...",
  "credentials": ["Ph.D. Stanford", "Ex-Google", "100K+ Students"],
  "primary_cta": {"text": "View My Courses", "url": "/courses"},
  "secondary_cta": {"text": "Contact Me", "url": "/contact"}
}
config: {"style": "single-column", "avatar_size": "48", "ring_color": "accent"}

Dark background:
config: {
  "style": "single-column",
  "background_color": "neutral",
  "name_color": "white",
  "bio_color": "white/70",
  "title_color": "primary"
}
""",
        "default_content": {
            "badge": "Your Instructor",
            "name": "Sarah Mitchell",
            "title": "Senior Product Designer & Educator",
            "photo": "https://i.pravatar.cc/300?img=32",
            "bio": "With over 15 years of experience in product design, I've worked with Fortune 500 companies and startups alike. My passion is helping others unlock their creative potential and build products that truly matter.\n\nI've taught over 50,000 students worldwide and my courses have been featured in major publications.",
            "credentials": ["Google UX Certificate", "Stanford Design Thinking", "10+ Years Experience"],
            "social_links": [
                {"platform": "twitter", "url": "#"},
                {"platform": "linkedin", "url": "#"},
                {"platform": "youtube", "url": "#"},
            ],
            "primary_cta": {"text": "Learn More", "url": "#about"},
        },
        "default_config": {
            "style": "single-column",
            "max_width": "6xl",
            "padding_y": "16",
            "background_color": "base-100",
            "animate": True,
            "badge_color": "primary",
            "avatar_size": "32",
            "avatar_shape": "full",
            "ring_color": "primary",
            "name_size": "3xl",
            "name_size_md": "4xl",
            "name_weight": "bold",
            "name_color": "base-content",
            "title_size": "xl",
            "title_color": "primary",
            "bio_color": "base-content/80",
            "credential_style": "outline",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
        },
    },
    {
        "name": "About - Two Column",
        "zone_type": ZoneType.ABOUT_INSTRUCTOR,
        "template_file": "landing_pages/zones/about_instructor.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/about_instructor.html

Two-column text layout for company stories or detailed about sections.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

name            Heading text (required)
title           Subtitle/tagline
badge           Badge above heading
intro           Left column content (supports HTML)
bio             Right column content (supports HTML)
credentials[]   Array of credential strings
social_links[]  Array of {platform, url} objects
buttons[]       Array of button objects: {text, url, target, style, size}
primary_cta     Primary CTA: {text, url, target}
secondary_cta   Secondary CTA: {text, url, target}

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "two-column" (REQUIRED)
  gap                Gap between columns (default: 12)
                 • "8"  - 2rem (32px) - compact
                 • "10" - 2.5rem (40px)
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px) - spacious
  max_width          Container max width (default: 6xl)
  padding_y          Vertical padding (default: 16)
  animate            Enable scroll animations (default: true)

COLORS
  background_color   Section background (default: base-100)
  badge_color        Badge color (default: primary)
  title_color        Title text color (default: primary)

CREDENTIALS & CTA
  credential_style   Credential badge style (default: outline)
  primary_btn_color  Primary button color (default: primary)
  primary_btn_style  Primary button style (default: solid)
  secondary_btn_color Secondary button color (default: ghost)
  secondary_btn_style Secondary button style (default: ghost)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Company story:
{
  "badge": "Our Story",
  "name": "Building the Future",
  "title": "Innovation meets simplicity",
  "intro": "<p>Founded in 2019 with a simple mission...</p>",
  "bio": "<p>Today, we serve 100,000+ customers globally.</p>",
  "credentials": ["Y Combinator '20", "Forbes 30 Under 30"],
  "primary_cta": {"text": "Join Our Team", "url": "/careers"}
}
config: {"style": "two-column", "gap": "16"}

Minimal layout:
config: {
  "style": "two-column",
  "gap": "8",
  "background_color": "base-200"
}
""",
        "default_content": {
            "badge": "Our Story",
            "name": "Building the Future",
            "title": "Innovation meets simplicity",
            "intro": "Founded in 2019, we set out with a simple mission: make powerful tools accessible to everyone. What started as a small team of dreamers has grown into a global community of creators.",
            "bio": "Today, we serve over 100,000 customers in 50+ countries. Our team of 50+ passionate individuals works tirelessly to push the boundaries of what's possible.\n\nWe believe that the best products are built when you truly listen to your users.",
            "credentials": ["Y Combinator '20", "TechCrunch Disrupt Finalist", "Forbes 30 Under 30"],
            "primary_cta": {"text": "Join Our Journey", "url": "#join"},
        },
        "default_config": {
            "style": "two-column",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "12",
            "background_color": "base-100",
            "animate": True,
            "badge_color": "primary",
            "title_color": "primary",
            "credential_style": "outline",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
        },
    },
    {
        "name": "About - Image Left",
        "zone_type": ZoneType.ABOUT_INSTRUCTOR,
        "template_file": "landing_pages/zones/about_instructor.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/about_instructor.html

Photo on left, content on right - ideal for founder/instructor profiles.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

name            Person name (required)
title           Role/title
photo           Photo URL (required for this style)
bio             Biography text (supports HTML)
badge           Badge above name
credentials[]   Array of credential strings
social_links[]  Array of {platform, url} objects
buttons[]       Array of button objects: {text, url, target, style, size}
primary_cta     Primary CTA: {text, url, target}
secondary_cta   Secondary CTA: {text, url, target}

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "image-left" (REQUIRED)
  gap                Gap between image and content (default: 12)
                 • "8"  - 2rem (32px) - compact
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px) - spacious
  image_width        Image column width (default: 2/5)
                 • "1/3" - narrow image
                 • "2/5" - default
                 • "1/2" - half width
  max_width          Container max width (default: 6xl)
  padding_y          Vertical padding (default: 16)
  animate            Enable scroll animations (default: true)

IMAGE STYLING
  image_style        Image display style
                 • "rounded" - rounded corners (default)
                 • "circle" - circular image
  rounded            Border radius when image_style=rounded (default: 2xl)
                 • "lg" - 8px
                 • "xl" - 12px
                 • "2xl" - 16px (default)
                 • "3xl" - 24px
  shadow             Shadow size (default: xl)
                 • "md" - medium shadow
                 • "lg" - large shadow
                 • "xl" - extra large (default)
                 • "2xl" - very large shadow

COLORS
  background_color   Section background (default: base-100)
  badge_color        Badge color (default: primary)
  title_color        Title text color (default: primary)
  name_size          Name text size (default: 3xl)
  name_size_md       Name size on medium screens (default: 4xl)

CREDENTIALS & CTA
  credential_style   Credential badge style (default: outline)
  primary_btn_color  Primary button color (default: primary)
  primary_btn_style  Primary button style (default: solid)
  secondary_btn_color Secondary button color (default: ghost)
  secondary_btn_style Secondary button style (default: ghost)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Founder profile:
{
  "badge": "Founder",
  "name": "Michael Chen",
  "title": "CEO & Co-founder",
  "photo": "https://example.com/michael.jpg",
  "bio": "After a decade at Google, I started this company...",
  "credentials": ["Ex-Google", "Stanford MBA"],
  "social_links": [{"platform": "linkedin", "url": "#"}],
  "primary_cta": {"text": "Read My Story", "url": "/about/founder"}
}
config: {"style": "image-left", "image_style": "rounded", "shadow": "2xl"}

Circular photo:
config: {
  "style": "image-left",
  "image_style": "circle",
  "image_width": "1/3"
}

Wide image layout:
config: {
  "style": "image-left",
  "image_width": "1/2",
  "gap": "16"
}
""",
        "default_content": {
            "badge": "Meet the Founder",
            "name": "Michael Chen",
            "title": "CEO & Co-founder",
            "photo": "https://i.pravatar.cc/400?img=60",
            "bio": "After spending a decade at top tech companies, I realized something was broken in how we build software. So I left my comfortable job and started this company with a vision to change things.\n\nOur tools have now helped 10,000+ teams ship better products, faster.",
            "credentials": ["Ex-Google", "Stanford MBA", "3x Founder"],
            "social_links": [
                {"platform": "twitter", "url": "#"},
                {"platform": "linkedin", "url": "#"},
            ],
            "primary_cta": {"text": "Read My Story", "url": "#story"},
        },
        "default_config": {
            "style": "image-left",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "12",
            "image_width": "2/5",
            "image_style": "rounded",
            "rounded": "2xl",
            "shadow": "xl",
            "background_color": "base-100",
            "animate": True,
            "badge_color": "primary",
            "name_size": "3xl",
            "name_size_md": "4xl",
            "title_color": "primary",
            "credential_style": "outline",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
        },
    },
    {
        "name": "About - Image Right",
        "zone_type": ZoneType.ABOUT_INSTRUCTOR,
        "template_file": "landing_pages/zones/about_instructor.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/about_instructor.html

Content on left, photo on right - mirror of image-left layout.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

name            Person name (required)
title           Role/title
photo           Photo URL (required for this style)
bio             Biography text (supports HTML)
badge           Badge above name
credentials[]   Array of credential strings
social_links[]  Array of {platform, url} objects
buttons[]       Array of button objects: {text, url, target, style, size}
primary_cta     Primary CTA: {text, url, target}
secondary_cta   Secondary CTA: {text, url, target}

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "image-right" (REQUIRED)
  gap                Gap between content and image (default: 12)
                 • "8"  - 2rem (32px) - compact
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px) - spacious
  image_width        Image column width (default: 2/5)
                 • "1/3" - narrow image
                 • "2/5" - default
                 • "1/2" - half width
  max_width          Container max width (default: 6xl)
  padding_y          Vertical padding (default: 16)
  animate            Enable scroll animations (default: true)

IMAGE STYLING
  image_style        Image display style
                 • "rounded" - rounded corners (default)
                 • "circle" - circular image
  rounded            Border radius (default: 2xl)
                 • "lg" - 8px
                 • "xl" - 12px
                 • "2xl" - 16px (default)
                 • "3xl" - 24px
  shadow             Shadow size (default: xl)
                 • "md" - medium shadow
                 • "lg" - large shadow
                 • "xl" - extra large (default)
                 • "2xl" - very large shadow

COLORS
  background_color   Section background (default: base-100)
  badge_color        Badge color (default: primary)
  title_color        Title text color (default: primary)
  name_size          Name text size (default: 3xl)
  name_size_md       Name size on medium screens (default: 4xl)

CREDENTIALS & CTA
  credential_style   Credential badge style (default: outline)
  primary_btn_color  Primary button color (default: primary)
  primary_btn_style  Primary button style (default: solid)
  secondary_btn_color Secondary button color (default: ghost)
  secondary_btn_style Secondary button style (default: ghost)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Coach/trainer profile:
{
  "badge": "Your Coach",
  "name": "Emma Rodriguez",
  "title": "Fitness & Wellness Expert",
  "photo": "https://example.com/emma.jpg",
  "bio": "Certified personal trainer with 12 years experience...",
  "credentials": ["ACE Certified", "Published Author"],
  "social_links": [{"platform": "instagram", "url": "#"}],
  "primary_cta": {"text": "Start Your Journey", "url": "/programs"}
}
config: {"style": "image-right"}

Large photo with minimal shadow:
config: {
  "style": "image-right",
  "image_width": "1/2",
  "shadow": "md",
  "rounded": "3xl"
}

Circular portrait:
config: {
  "style": "image-right",
  "image_style": "circle",
  "image_width": "1/3"
}
""",
        "default_content": {
            "badge": "Your Coach",
            "name": "Emma Rodriguez",
            "title": "Fitness & Wellness Expert",
            "photo": "https://i.pravatar.cc/400?img=44",
            "bio": "Certified personal trainer with 12 years of experience transforming lives. I've helped thousands of clients achieve their fitness goals through personalized programs and sustainable lifestyle changes.\n\nMy approach combines science-backed training methods with practical nutrition guidance.",
            "credentials": ["ACE Certified", "Nutrition Coach", "Published Author"],
            "social_links": [
                {"platform": "instagram", "url": "#"},
                {"platform": "youtube", "url": "#"},
            ],
            "primary_cta": {"text": "Start Your Journey", "url": "#start"},
        },
        "default_config": {
            "style": "image-right",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "12",
            "image_width": "2/5",
            "image_style": "rounded",
            "rounded": "2xl",
            "shadow": "xl",
            "background_color": "base-100",
            "animate": True,
            "badge_color": "primary",
            "name_size": "3xl",
            "name_size_md": "4xl",
            "title_color": "primary",
            "credential_style": "outline",
            "primary_btn_color": "primary",
            "primary_btn_style": "solid",
        },
    },
    {
        "name": "About - Three Column",
        "zone_type": ZoneType.ABOUT_INSTRUCTOR,
        "template_file": "landing_pages/zones/about_instructor.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/about_instructor.html

Three-column layout for company values, features, or pillars.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  title           Section heading (required)
  subtitle        Subtitle text below heading
  badge           Badge above heading

COLUMNS
  columns[]       Array of column objects:
                  • icon - Emoji or icon character
                  • image - Image URL (optional, use instead of icon)
                  • heading - Column heading text
                  • text - Column description text

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "three-column" (REQUIRED)
  gap                Gap between columns (default: 8)
                 • "6"  - 1.5rem (24px) - compact
                 • "8"  - 2rem (32px) - default
                 • "10" - 2.5rem (40px)
                 • "12" - 3rem (48px) - spacious
  header_margin      Margin below header (default: 12)
                 • "8"  - 2rem (32px)
                 • "10" - 2.5rem (40px)
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px)
  max_width          Container max width (default: 6xl)
  padding_y          Vertical padding (default: 16)
  animate            Enable scroll animations (default: true)

IMAGE STYLING
  rounded            Border radius for column images (default: xl)
                 • "lg" - 8px
                 • "xl" - 12px (default)
                 • "2xl" - 16px

COLORS
  background_color   Section background (default: base-100)
  badge_color        Badge color (default: primary)
  name_size          Heading text size (default: 3xl)
  name_size_md       Heading size on medium screens (default: 4xl)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Company values:
{
  "badge": "Our Values",
  "title": "What Drives Us",
  "subtitle": "These principles guide everything we do",
  "columns": [
    {"icon": "🎯", "heading": "Customer Focus", "text": "Every decision starts with the customer."},
    {"icon": "💡", "heading": "Innovation", "text": "We embrace new ideas."},
    {"icon": "🤝", "heading": "Transparency", "text": "Honest communication always."}
  ]
}
config: {"style": "three-column"}

With images instead of icons:
{
  "title": "Our Services",
  "columns": [
    {"image": "/img/dev.jpg", "heading": "Development", "text": "Custom solutions."},
    {"image": "/img/design.jpg", "heading": "Design", "text": "Beautiful interfaces."},
    {"image": "/img/consulting.jpg", "heading": "Consulting", "text": "Expert guidance."}
  ]
}
config: {"style": "three-column", "rounded": "2xl", "gap": "10"}

Compact layout:
config: {
  "style": "three-column",
  "gap": "6",
  "header_margin": "8",
  "padding_y": "12"
}
""",
        "default_content": {
            "badge": "Our Values",
            "title": "What Drives Us",
            "subtitle": "These principles guide everything we do",
            "columns": [
                {
                    "icon": "🎯",
                    "heading": "Customer Obsessed",
                    "text": "Every decision starts with the customer. We listen, learn, and build solutions that truly solve problems.",
                },
                {
                    "icon": "💡",
                    "heading": "Innovation First",
                    "text": "We're not afraid to challenge the status quo. Great ideas can come from anywhere, and we embrace them all.",
                },
                {
                    "icon": "🤝",
                    "heading": "Transparency Always",
                    "text": "No hidden agendas, no fine print. We believe in honest communication with our customers and team.",
                },
            ],
        },
        "default_config": {
            "style": "three-column",
            "max_width": "6xl",
            "padding_y": "16",
            "gap": "8",
            "header_margin": "12",
            "rounded": "xl",
            "background_color": "base-100",
            "animate": True,
            "badge_color": "primary",
            "name_size": "3xl",
            "name_size_md": "4xl",
        },
    },
    {
        "name": "About - Team Grid",
        "zone_type": ZoneType.ABOUT_INSTRUCTOR,
        "template_file": "landing_pages/zones/about_instructor.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/about_instructor.html

Team member grid with avatars and social links.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  title           Section heading (required)
  subtitle        Subtitle text below heading
  badge           Badge above heading

TEAM MEMBERS
  team[]          Array of team member objects:
                  • name - Member name (required)
                  • role - Job title/role
                  • photo - Avatar URL
                  • bio - Short bio text
                  • social_links[] - Array of {platform, url}

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "team-grid" (REQUIRED)
  columns            Grid columns on large screens (default: 3)
                 • "2" - two columns
                 • "3" - three columns (default)
                 • "4" - four columns
  gap                Gap between team cards (default: 8)
                 • "6"  - 1.5rem (24px) - compact
                 • "8"  - 2rem (32px) - default
                 • "10" - 2.5rem (40px)
                 • "12" - 3rem (48px) - spacious
  header_margin      Margin below header (default: 12)
                 • "8"  - 2rem (32px)
                 • "12" - 3rem (48px) - default
                 • "16" - 4rem (64px)
  max_width          Container max width (default: 6xl)
  padding_y          Vertical padding (default: 16)
  animate            Enable scroll animations (default: true)

AVATAR STYLING
  avatar_size        Avatar size in Tailwind units (default: 32)
                 • "20" - 80px - small
                 • "24" - 96px - medium-small
                 • "32" - 128px - default
                 • "40" - 160px - large
  avatar_shape       Avatar border radius (default: full)
                 • "full" - circular (default)
                 • "xl" - rounded corners
                 • "lg" - slightly rounded
  ring_color         Ring color around avatar (default: base-300)
                 • "base-300" - subtle gray (default)
                 • "primary" - brand color
                 • "secondary" - secondary brand
                 • "accent" - accent color

COLORS
  background_color   Section background (default: base-100)
  badge_color        Badge color (default: primary)
  title_color        Role text color (default: primary)
  name_size          Heading text size (default: 3xl)
  name_size_md       Heading size on medium screens (default: 4xl)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Leadership team:
{
  "badge": "Leadership",
  "title": "Meet Our Team",
  "subtitle": "The people driving our vision",
  "team": [
    {
      "name": "Alex Johnson",
      "role": "CEO",
      "photo": "https://example.com/alex.jpg",
      "bio": "15 years in tech leadership",
      "social_links": [{"platform": "linkedin", "url": "#"}]
    },
    {
      "name": "Sarah Kim",
      "role": "CTO",
      "photo": "https://example.com/sarah.jpg",
      "bio": "Former Google engineer",
      "social_links": [{"platform": "github", "url": "#"}]
    }
  ]
}
config: {"style": "team-grid", "columns": "2"}

Four-column grid:
config: {
  "style": "team-grid",
  "columns": "4",
  "avatar_size": "24",
  "gap": "6"
}

With branded ring:
config: {
  "style": "team-grid",
  "ring_color": "primary",
  "avatar_size": "40"
}

Compact team display:
config: {
  "style": "team-grid",
  "columns": "4",
  "avatar_size": "20",
  "gap": "6",
  "header_margin": "8"
}
""",
        "default_content": {
            "badge": "Our Team",
            "title": "Meet the Experts",
            "subtitle": "The passionate people behind our success",
            "team": [
                {
                    "name": "Alex Johnson",
                    "role": "Lead Developer",
                    "photo": "https://i.pravatar.cc/150?img=52",
                    "bio": "Full-stack expert with 10+ years experience",
                    "social_links": [{"platform": "github", "url": "#"}, {"platform": "linkedin", "url": "#"}],
                },
                {
                    "name": "Jessica Lee",
                    "role": "Head of Design",
                    "photo": "https://i.pravatar.cc/150?img=31",
                    "bio": "Award-winning designer and UX specialist",
                    "social_links": [{"platform": "twitter", "url": "#"}, {"platform": "linkedin", "url": "#"}],
                },
                {
                    "name": "Marcus Williams",
                    "role": "Marketing Director",
                    "photo": "https://i.pravatar.cc/150?img=53",
                    "bio": "Growth expert with startup experience",
                    "social_links": [{"platform": "twitter", "url": "#"}, {"platform": "linkedin", "url": "#"}],
                },
                {
                    "name": "Priya Sharma",
                    "role": "Customer Success",
                    "photo": "https://i.pravatar.cc/150?img=27",
                    "bio": "Passionate about making customers happy",
                    "social_links": [{"platform": "linkedin", "url": "#"}],
                },
            ],
        },
        "default_config": {
            "style": "team-grid",
            "max_width": "6xl",
            "padding_y": "16",
            "columns": "4",
            "gap": "8",
            "header_margin": "12",
            "avatar_size": "24",
            "avatar_shape": "full",
            "ring_color": "base-300",
            "background_color": "base-100",
            "animate": True,
            "badge_color": "primary",
            "title_color": "primary",
            "name_size": "3xl",
            "name_size_md": "4xl",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
