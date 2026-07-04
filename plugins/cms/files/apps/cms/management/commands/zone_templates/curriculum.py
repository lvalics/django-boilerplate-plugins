"""
Curriculum zone templates.
"""

from ._base import ZoneType

CURRICULUM_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Curriculum - Accordion",
        "zone_type": ZoneType.CURRICULUM,
        "template_file": "cms/zones/curriculum.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/curriculum.html

Course curriculum or content outline with expandable accordion sections.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title
  title            Section heading
  subtitle         Description text
  stats[]          Summary stats: {icon, value, label}

MODULES
  modules[]        Array of modules/sections:
    icon             Module emoji/icon
    title            Module heading
    description      Module description
    duration         Time estimate (e.g., "2 hours")
    lessons[]        Array of lessons:
      title            Lesson name
      duration         Lesson time
      badge            Optional badge text
      badge_color      Badge color (default: secondary)

CTA
  cta.text         Button text
  cta.url          Button URL
  cta.subtext      Text below button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style            Display style (default: accordion)
                   - "accordion" - expandable sections (default)
                   - "cards" - grid of module cards
                   - "timeline" - vertical timeline
                   - "numbered-list" - simple numbered steps

LAYOUT
  padding_y        Vertical padding in Tailwind units (default: 16)
                   - "8"  - 2rem (32px) - compact
                   - "12" - 3rem (48px)
                   - "16" - 4rem (64px) - default
                   - "20" - 5rem (80px) - spacious
                   - "24" - 6rem (96px) - very spacious
  max_width        Container width (default: 4xl)
                   - "2xl" - 672px - narrow content
                   - "3xl" - 768px
                   - "4xl" - 896px - default
                   - "5xl" - 1024px
                   - "6xl" - 1152px - wide content
  background_color Section background (default: base-100)
                   - "base-100" - lightest background (default)
                   - "base-200" - light gray
                   - "base-300" - darker gray
                   - "primary" - brand color background
                   - "neutral" - dark background

HEADER STYLING
  header_align     Header text alignment (default: center)
                   - "center" - centered text (default)
                   - "left" - left-aligned
                   - "right" - right-aligned
  header_margin    Header bottom margin (default: 12)
                   - "8"  - 2rem
                   - "10" - 2.5rem
                   - "12" - 3rem - default
                   - "16" - 4rem
  badge_color      Badge color (default: primary)
                   - "primary", "secondary", "accent"
                   - "info", "success", "warning", "error"
  title_size       Title text size (default: 3xl)
                   - "2xl", "3xl", "4xl", "5xl"
  title_size_md    Title size on md screens (default: 4xl)
                   - "3xl", "4xl", "5xl"
  title_weight     Title font weight (default: bold)
                   - "semibold", "bold", "extrabold"
  title_color      Title text color (default: base-content)
                   - "base-content" - default text
                   - "primary" - brand color
                   - "white" - for dark backgrounds
  subtitle_size    Subtitle text size (default: lg)
                   - "base", "lg", "xl"
  subtitle_color   Subtitle text color (default: base-content/70)
                   - "base-content/70" - 70% opacity (default)
                   - "base-content/60" - lighter
                   - "base-content" - full opacity
  subtitle_max_width  Subtitle max width (default: 2xl)
                      - "xl", "2xl", "3xl"
  stat_color       Stats text color (default: base-content/70)
                   - "base-content/70", "base-content/60"
                   - "primary", "secondary"

ACCORDION OPTIONS
  collapse_style   Collapse indicator style (default: plus)
                   - "plus" - plus/minus icon (default)
                   - "arrow" - arrow icon
  first_open       Open first item by default (default: false)
                   - true - first module expanded
                   - false - all collapsed
  numbered         Show module numbers (default: false)
                   - true - show number badges
                   - false - show module icons
  number_color     Number badge color (default: primary)
                   - "primary", "secondary", "accent"
                   - "info", "success", "warning"
  number_size      Number badge size (default: lg)
                   - "md", "lg", "xl"
  show_duration    Show duration badges (default: false)
                   - true - display duration on each module
                   - false - hide duration
  duration_style   Duration badge style (default: ghost)
                   - "ghost" - subtle style (default)
                   - "outline" - outlined
                   - "primary", "secondary" - colored
  show_lesson_count  Show lesson count (default: false)
                     - true - show "X lessons" text
                     - false - hide count
  module_title_size  Module title size (default: lg)
                     - "base", "lg", "xl"
  module_title_weight  Module title weight (default: semibold)
                       - "medium", "semibold", "bold"

ITEM STYLING
  item_bg          Item background (default: base-200)
                   - "base-100" - lightest
                   - "base-200" - default
                   - "base-300" - darker
  item_gap         Gap between items (default: 4)
                   - "2", "3", "4", "6", "8"
  item_padding     Item content padding (default: 6)
                   - "4", "5", "6", "8"
  rounded          Border radius (default: xl)
                   - "lg", "xl", "2xl", "3xl"
  shadow           Shadow size (optional)
                   - "sm", "md", "lg", "xl"
  border           Show border (default: false)
                   - true - show border
                   - false - no border
  border_color     Border color (default: base-300)
                   - "base-200", "base-300"
                   - "primary/20", "secondary/20"

LESSON STYLING
  lesson_icon      Lesson icon style (default: arrow)
                   - "arrow" - chevron arrow (default)
                   - "play" - play button circle
                   - "check" - checkmark
                   - "dot" - simple dot
                   - "number" - numbered circles
  lesson_icon_color  Lesson icon color (default: primary)
                     - "primary", "secondary", "accent"
                     - "success", "info", "warning"
  lesson_gap       Gap between lessons (default: 2)
                   - "1", "2", "3", "4"
  lesson_padding   Lesson padding (default: 2)
                   - "1", "2", "3", "4"
  lesson_rounded   Lesson border radius (default: lg)
                   - "md", "lg", "xl"
  lesson_bg        Lesson background (optional)
                   - "base-100", "base-200", "base-300"
  lesson_hover     Lesson hover background (optional)
                   - "base-200", "base-300", "primary/10"
  desc_color       Description text color (default: base-content/80)
                   - "base-content/80", "base-content/70"
                   - "base-content/60"

CTA OPTIONS
  cta_margin       CTA top margin (default: 12)
                   - "8", "10", "12", "16"
  cta_style        CTA button style (default: primary)
                   - "primary", "secondary", "accent"
                   - "outline", "ghost"
  cta_size         CTA button size (optional)
                   - "sm", "md", "lg"

ANIMATION
  animate          Enable scroll animations (default: true)
                   - true - enable animations (default)
                   - "false" - disable animations

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Basic course curriculum:
{
  "badge": "Course Content",
  "title": "What You'll Learn",
  "subtitle": "A comprehensive curriculum from beginner to expert",
  "modules": [
    {
      "icon": "1",
      "title": "Getting Started",
      "description": "Set up your environment and learn fundamentals",
      "duration": "1.5 hours",
      "lessons": [
        {"title": "Introduction", "duration": "10 min"},
        {"title": "Setup", "duration": "20 min"}
      ]
    }
  ],
  "cta": {"text": "Enroll Now", "url": "#enroll"}
}
config: {"first_open": true, "numbered": true, "show_duration": true}

With summary stats:
{
  "title": "Complete Course Outline",
  "stats": [
    {"icon": "📚", "value": "8", "label": "Modules"},
    {"icon": "🎬", "value": "45", "label": "Lessons"},
    {"icon": "⏱️", "value": "12h", "label": "Total"}
  ],
  "modules": [...]
}
config: {"lesson_icon": "play", "show_lesson_count": true}

Dark theme with custom styling:
config: {
  "background_color": "neutral",
  "title_color": "white",
  "subtitle_color": "white/70",
  "item_bg": "base-100",
  "shadow": "lg"
}

Minimal accordion (no numbers or duration):
config: {
  "numbered": false,
  "show_duration": false,
  "collapse_style": "arrow",
  "lesson_icon": "check"
}
""",
        "default_content": {
            "badge": "Course Content",
            "title": "What You'll Learn",
            "subtitle": "A comprehensive curriculum designed to take you from beginner to expert",
            "stats": [
                {"icon": "📚", "value": "8", "label": "Modules"},
                {"icon": "🎬", "value": "45", "label": "Lessons"},
                {"icon": "⏱️", "value": "12h", "label": "Total"},
            ],
            "modules": [
                {
                    "icon": "🚀",
                    "title": "Getting Started",
                    "description": "Set up your environment and learn the fundamentals",
                    "duration": "1.5 hours",
                    "lessons": [
                        {"title": "Introduction to the Course", "duration": "10 min"},
                        {"title": "Setting Up Your Environment", "duration": "20 min"},
                        {"title": "Your First Project", "duration": "30 min"},
                    ],
                },
                {
                    "icon": "📖",
                    "title": "Core Concepts",
                    "description": "Master the essential building blocks",
                    "duration": "3 hours",
                    "lessons": [
                        {"title": "Understanding the Basics", "duration": "45 min"},
                        {"title": "Working with Data", "duration": "1 hour"},
                        {"title": "Best Practices", "duration": "30 min"},
                    ],
                },
                {
                    "icon": "🎯",
                    "title": "Advanced Techniques",
                    "description": "Take your skills to the next level",
                    "duration": "4 hours",
                    "lessons": [
                        {"title": "Advanced Patterns", "duration": "1 hour"},
                        {"title": "Performance Optimization", "duration": "1 hour"},
                        {"title": "Real-World Projects", "duration": "2 hours"},
                    ],
                },
            ],
            "cta": {"text": "Enroll Now", "url": "#enroll", "subtext": "30-day money-back guarantee"},
        },
        "default_config": {
            "style": "accordion",
            "padding_y": "16",
            "max_width": "4xl",
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
            "first_open": True,
            "numbered": True,
            "number_color": "primary",
            "number_size": "lg",
            "show_duration": True,
            "duration_style": "ghost",
            "item_bg": "base-200",
            "item_gap": "4",
            "rounded": "xl",
            "module_title_size": "lg",
            "module_title_weight": "semibold",
            "lesson_icon": "play",
            "lesson_icon_color": "primary",
            "lesson_gap": "2",
            "lesson_padding": "2",
            "lesson_rounded": "lg",
            "desc_color": "base-content/80",
            "cta_margin": "12",
            "cta_style": "primary",
            "animate": True,
        },
    },
    {
        "name": "Curriculum - Cards Grid",
        "zone_type": ZoneType.CURRICULUM,
        "template_file": "cms/zones/curriculum.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/curriculum.html

Curriculum displayed as a responsive grid of module cards.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title
  title            Section heading
  subtitle         Description text
  stats[]          Summary stats: {icon, value, label}

MODULES
  modules[]        Array of modules:
    icon             Module emoji/icon
    title            Module heading
    description      Module description
    duration         Time estimate
    lessons[]        Optional lessons array (shows count)

CTA
  cta.text         Button text
  cta.url          Button URL
  cta.subtext      Text below button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style            REQUIRED: "cards"

LAYOUT
  padding_y        Vertical padding (default: 16)
                   - "12", "16", "20", "24"
  max_width        Container width (default: 4xl)
                   - "3xl", "4xl", "5xl", "6xl"
  background_color Section background (default: base-100)
                   - "base-100", "base-200", "base-300"
                   - "primary", "neutral"
  columns          Grid columns (default: 2)
                   - "2" - two columns (default)
                   - "3" - three columns on large screens

CARD STYLING
  item_bg          Card background (default: base-200)
                   - "base-100", "base-200", "base-300"
  item_gap         Gap between cards (default: 6)
                   - "4", "6", "8"
  shadow           Card shadow (optional)
                   - "sm", "md", "lg", "xl"
  hover_effect     Enable hover animation (default: false)
                   - true - lift and shadow on hover
                   - false - no hover effect
  numbered         Show module numbers (default: false)
                   - true - number badges instead of icons
                   - false - show module icons
  number_color     Number badge color (default: primary)
                   - "primary", "secondary", "accent"

HEADER STYLING
  header_align     Header alignment (default: center)
  badge_color      Badge color (default: primary)
  title_size       Title size (default: 3xl)
  title_color      Title color (default: base-content)
  subtitle_size    Subtitle size (default: lg)
  subtitle_color   Subtitle color (default: base-content/70)

TEXT STYLING
  module_title_size  Module title size (default: lg)
  desc_color         Description color (default: base-content/70)

CTA OPTIONS
  cta_margin       CTA top margin (default: 12)
  cta_style        CTA button style (default: primary)
  cta_size         CTA button size (optional)

ANIMATION
  animate          Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Two-column module grid:
{
  "title": "Course Modules",
  "subtitle": "Everything you need to master the subject",
  "modules": [
    {"icon": "📋", "title": "Planning", "description": "Learn to plan effectively", "duration": "2h"},
    {"icon": "🛠️", "title": "Building", "description": "Build real projects", "duration": "4h"},
    {"icon": "🧪", "title": "Testing", "description": "Ensure quality", "duration": "2h"},
    {"icon": "🚀", "title": "Deploying", "description": "Launch with confidence", "duration": "1.5h"}
  ]
}
config: {"style": "cards", "columns": "2", "numbered": true}

Three-column with hover effects:
config: {
  "style": "cards",
  "columns": "3",
  "shadow": "md",
  "hover_effect": true,
  "item_bg": "base-100"
}

Numbered cards on dark background:
config: {
  "style": "cards",
  "background_color": "neutral",
  "title_color": "white",
  "subtitle_color": "white/70",
  "item_bg": "base-100",
  "numbered": true,
  "shadow": "lg"
}
""",
        "default_content": {
            "title": "Course Modules",
            "subtitle": "Everything you need to master the subject",
            "modules": [
                {
                    "icon": "📋",
                    "title": "Planning & Strategy",
                    "description": "Learn to plan effectively and set clear goals",
                    "duration": "2 hours",
                },
                {
                    "icon": "🛠️",
                    "title": "Implementation",
                    "description": "Build real projects with hands-on exercises",
                    "duration": "4 hours",
                },
                {
                    "icon": "🧪",
                    "title": "Testing & QA",
                    "description": "Ensure quality results with thorough testing",
                    "duration": "2 hours",
                },
                {
                    "icon": "🚀",
                    "title": "Deployment",
                    "description": "Launch with confidence and best practices",
                    "duration": "1.5 hours",
                },
            ],
        },
        "default_config": {
            "style": "cards",
            "padding_y": "16",
            "max_width": "4xl",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "columns": "2",
            "item_bg": "base-200",
            "item_gap": "6",
            "shadow": "md",
            "hover_effect": True,
            "numbered": True,
            "number_color": "primary",
            "module_title_size": "lg",
            "desc_color": "base-content/70",
            "animate": True,
        },
    },
    {
        "name": "Curriculum - Timeline",
        "zone_type": ZoneType.CURRICULUM,
        "template_file": "cms/zones/curriculum.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/curriculum.html

Curriculum displayed as a vertical timeline with connected steps.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title
  title            Section heading
  subtitle         Description text
  stats[]          Summary stats: {icon, value, label}

MODULES
  modules[]        Array of timeline items:
    icon             Item emoji/icon (shown in dot if not numbered)
    title            Step/phase heading
    description      Step description
    duration         Optional time estimate
    lessons[]        Optional list of sub-items:
      title            Sub-item text

CTA
  cta.text         Button text
  cta.url          Button URL
  cta.subtext      Text below button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style            REQUIRED: "timeline"

LAYOUT
  padding_y        Vertical padding (default: 16)
                   - "12", "16", "20", "24"
  max_width        Container width (default: 4xl)
                   - "3xl", "4xl", "5xl", "6xl"
  background_color Section background (default: base-100)
                   - "base-100", "base-200", "base-300"
                   - "primary", "neutral"

TIMELINE STYLING
  timeline_offset  Vertical line left offset (default: 6)
                   - "4", "5", "6", "8"
  timeline_color   Vertical line color (default: base-300)
                   - "base-200", "base-300", "primary/30"
  timeline_padding Left padding for content (default: 16)
                   - "12", "14", "16", "20"
  dot_size         Timeline dot size (default: 12)
                   - "10", "12", "14"
  dot_bg           Dot background color (default: primary)
                   - "primary", "secondary", "accent"
                   - "success", "info"
  dot_text         Dot text/icon color (default: primary-content)
                   - "primary-content", "white", "base-content"
  dot_ring         Ring around dot (optional)
                   - "base-100", "base-200", "white"

ITEM STYLING
  item_bg          Item card background (default: base-200)
                   - "base-100", "base-200", "base-300"
  item_gap         Gap between items (default: 8)
                   - "6", "8", "10", "12"
  item_padding     Item content padding (default: 6)
                   - "4", "5", "6", "8"
  rounded          Border radius (default: xl)
                   - "lg", "xl", "2xl"
  shadow           Card shadow (optional)
                   - "sm", "md", "lg"
  numbered         Show step numbers (default: false)
                   - true - numbers in dots
                   - false - show icons

TEXT STYLING
  module_title_size  Title size (default: lg)
  module_title_weight  Title weight (default: semibold)
  desc_color         Description color (default: base-content/70)
  lesson_icon_color  Sub-item dot color (default: primary)

HEADER STYLING
  header_align     Header alignment (default: center)
  badge_color      Badge color (default: primary)
  title_size       Title size (default: 3xl)
  title_color      Title color (default: base-content)
  subtitle_size    Subtitle size (default: lg)
  subtitle_color   Subtitle color (default: base-content/70)

CTA OPTIONS
  cta_margin       CTA top margin (default: 12)
  cta_style        CTA button style (default: primary)

ANIMATION
  animate          Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Learning path timeline:
{
  "title": "Learning Path",
  "subtitle": "Your journey from beginner to expert",
  "modules": [
    {
      "title": "Week 1-2: Foundations",
      "description": "Build a solid understanding of core concepts",
      "lessons": [{"title": "Basic concepts"}, {"title": "Hands-on exercises"}]
    },
    {
      "title": "Week 3-4: Intermediate",
      "description": "Expand your skills with advanced topics",
      "lessons": [{"title": "Advanced patterns"}, {"title": "Project work"}]
    }
  ]
}
config: {"style": "timeline", "numbered": true}

Timeline with custom dot styling:
config: {
  "style": "timeline",
  "dot_bg": "success",
  "dot_ring": "base-100",
  "timeline_color": "success/30",
  "shadow": "sm"
}

Minimal timeline:
config: {
  "style": "timeline",
  "numbered": false,
  "item_bg": "base-100",
  "timeline_color": "base-200"
}

Dark theme timeline:
config: {
  "style": "timeline",
  "background_color": "neutral",
  "title_color": "white",
  "subtitle_color": "white/70",
  "item_bg": "base-100",
  "dot_ring": "neutral"
}
""",
        "default_content": {
            "title": "Learning Path",
            "subtitle": "Your journey from beginner to expert",
            "modules": [
                {
                    "title": "Week 1-2: Foundations",
                    "description": "Build a solid understanding of core concepts and fundamental techniques",
                    "lessons": [
                        {"title": "Basic concepts and terminology"},
                        {"title": "Hands-on exercises and practice"},
                    ],
                },
                {
                    "title": "Week 3-4: Intermediate",
                    "description": "Expand your skills with advanced topics and real-world applications",
                    "lessons": [
                        {"title": "Advanced patterns and strategies"},
                        {"title": "Project work and case studies"},
                    ],
                },
                {
                    "title": "Week 5-6: Advanced",
                    "description": "Master complex techniques and industry best practices",
                    "lessons": [{"title": "Expert techniques and optimization"}, {"title": "Final capstone project"}],
                },
            ],
        },
        "default_config": {
            "style": "timeline",
            "padding_y": "16",
            "max_width": "4xl",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "timeline_offset": "6",
            "timeline_color": "base-300",
            "timeline_padding": "16",
            "dot_size": "12",
            "dot_bg": "primary",
            "dot_text": "primary-content",
            "dot_ring": "base-100",
            "item_bg": "base-200",
            "item_gap": "8",
            "item_padding": "6",
            "rounded": "xl",
            "shadow": "sm",
            "numbered": True,
            "module_title_size": "lg",
            "module_title_weight": "semibold",
            "desc_color": "base-content/70",
            "lesson_icon_color": "primary",
            "animate": True,
        },
    },
    {
        "name": "Curriculum - Numbered Steps",
        "zone_type": ZoneType.CURRICULUM,
        "template_file": "cms/zones/curriculum.html",
        "is_active": True,
        "description": """TEMPLATE: cms/zones/curriculum.html

Simple numbered list of steps or phases - ideal for process explanations.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  badge            Badge text above title
  title            Section heading
  subtitle         Description text
  stats[]          Summary stats: {icon, value, label}

MODULES
  modules[]        Array of steps:
    title            Step heading
    description      Step description
    lessons[]        Optional sub-items with checkmarks:
      title            Sub-item text

CTA
  cta.text         Button text
  cta.url          Button URL
  cta.subtext      Text below button

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

STYLE
  style            REQUIRED: "numbered-list"

LAYOUT
  padding_y        Vertical padding (default: 16)
                   - "12", "16", "20", "24"
  max_width        Container width (default: 4xl)
                   - "3xl", "4xl", "5xl", "6xl"
  background_color Section background (default: base-100)
                   - "base-100", "base-200", "base-300"
                   - "primary", "neutral"

NUMBER STYLING
  number_size      Number circle size (default: 12)
                   - "10", "12", "14", "16"
  number_rounded   Number circle shape (default: full)
                   - "full" - circle (default)
                   - "xl", "2xl" - rounded square
  number_bg        Number background color (default: primary)
                   - "primary", "secondary", "accent"
                   - "success", "info", "warning"
  number_text      Number text color (default: primary-content)
                   - "primary-content", "white", "base-content"
  number_gap       Gap between number and content (default: 6)
                   - "4", "5", "6", "8"

ITEM STYLING
  item_gap         Gap between items (default: 6)
                   - "4", "6", "8", "10"
  module_title_size  Title size (default: xl)
                     - "lg", "xl", "2xl"
  module_title_weight  Title weight (default: semibold)
                       - "medium", "semibold", "bold"
  desc_color         Description color (default: base-content/70)
                     - "base-content/70", "base-content/60"
  lesson_icon_color  Checkmark color for sub-items (default: success)
                     - "success", "primary", "accent"

HEADER STYLING
  header_align     Header alignment (default: center)
  badge_color      Badge color (default: primary)
  title_size       Title size (default: 3xl)
  title_color      Title color (default: base-content)
  subtitle_size    Subtitle size (default: lg)
  subtitle_color   Subtitle color (default: base-content/70)

CTA OPTIONS
  cta_margin       CTA top margin (default: 12)
  cta_style        CTA button style (default: primary)
  cta_size         CTA button size (optional)

ANIMATION
  animate          Enable scroll animations (default: true)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

How it works steps:
{
  "title": "How It Works",
  "subtitle": "Simple steps to get started",
  "modules": [
    {
      "title": "Sign Up",
      "description": "Create your free account in just 2 minutes",
      "lessons": [{"title": "Email verification"}, {"title": "Profile setup"}]
    },
    {
      "title": "Choose Your Plan",
      "description": "Select the plan that fits your needs"
    },
    {
      "title": "Start Learning",
      "description": "Access all content immediately"
    }
  ],
  "cta": {"text": "Get Started Free", "url": "#signup"}
}
config: {"style": "numbered-list"}

Custom number colors:
config: {
  "style": "numbered-list",
  "number_bg": "success",
  "number_text": "success-content",
  "lesson_icon_color": "success"
}

Larger numbers with square shape:
config: {
  "style": "numbered-list",
  "number_size": "14",
  "number_rounded": "xl",
  "module_title_size": "2xl"
}

Dark theme steps:
config: {
  "style": "numbered-list",
  "background_color": "neutral",
  "title_color": "white",
  "subtitle_color": "white/70",
  "desc_color": "white/60"
}
""",
        "default_content": {
            "title": "How It Works",
            "subtitle": "Simple steps to get started",
            "modules": [
                {
                    "title": "Sign Up",
                    "description": "Create your free account in just 2 minutes",
                    "lessons": [{"title": "Email verification"}, {"title": "Profile setup"}],
                },
                {
                    "title": "Choose Your Plan",
                    "description": "Select the plan that fits your needs",
                    "lessons": [{"title": "Compare features"}, {"title": "Flexible billing options"}],
                },
                {
                    "title": "Start Learning",
                    "description": "Access all content immediately",
                    "lessons": [{"title": "Video lessons"}, {"title": "Downloadable resources"}],
                },
            ],
            "cta": {"text": "Get Started Free", "url": "#signup"},
        },
        "default_config": {
            "style": "numbered-list",
            "padding_y": "16",
            "max_width": "4xl",
            "background_color": "base-100",
            "header_align": "center",
            "header_margin": "12",
            "title_size": "3xl",
            "title_size_md": "4xl",
            "title_color": "base-content",
            "subtitle_size": "lg",
            "subtitle_color": "base-content/70",
            "number_size": "12",
            "number_rounded": "full",
            "number_bg": "primary",
            "number_text": "primary-content",
            "number_gap": "6",
            "item_gap": "6",
            "module_title_size": "xl",
            "module_title_weight": "semibold",
            "desc_color": "base-content/70",
            "lesson_icon_color": "success",
            "cta_margin": "12",
            "cta_style": "primary",
            "animate": True,
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
]
