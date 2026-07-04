"""
Order Form zone templates.
"""

from ._base import ZoneType

ORDER_FORM_TEMPLATES = [
    # ═══════════════════════════════════════════════════════════════════════════
    # STANDARD TEMPLATES (order_form.html)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Contact (Default)",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/order_form.html

Dynamic form builder with all field types. Supports contact forms, order forms,
lead generation, surveys, and more. Uses DaisyUI styling with card wrapper.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

HEADER
  title              Form title/heading (displayed above form)
  description        Subtitle/description text below title

FORM FIELDS
  form_fields[]      Array of field objects (see FIELD TYPES below)

SUBMIT & FEEDBACK
  submit_text        Submit button text (default: "Submit")
  success_message    Message shown after successful submission
  redirect_url       Optional URL to redirect after success
  footer_text        Text shown below submit button (e.g., privacy notice)
                     Example: "Confidențialitate: datele dumneavoastră sunt în siguranță."

═══════════════════════════════════════════════════════════════
FIELD TYPES (form_fields array items)
═══════════════════════════════════════════════════════════════

All fields share these common properties:
  name               Field name (required, used as form key)
  type               Field type (required, see types below)
  label              Display label
  placeholder        Placeholder text
  required           Boolean - is field required
  width              "full" | "half" | "third" (grid width)
  help_text          Help text shown below field
  default_value      Pre-filled value

TEXT INPUT TYPES
  type: "text"       Standard text input
  type: "email"      Email input with validation
  type: "tel"        Phone number input
  type: "url"        URL input with validation
  type: "password"   Password input (masked)
  type: "number"     Numeric input
    - min            Minimum value
    - max            Maximum value
    - step           Step increment
  type: "date"       Date picker
  type: "time"       Time picker
  type: "datetime-local"  Date & time picker
  type: "color"      Color picker

  Additional text properties:
    - min_length     Minimum character length
    - max_length     Maximum character length
    - pattern        Regex validation pattern

TEXTAREA
  type: "textarea"   Multi-line text area
    - rows           Number of visible rows (default: 4)
    - min_length     Minimum character length
    - max_length     Maximum character length

SELECT (Dropdown)
  type: "select"     Dropdown selection
    - options[]      Array of {label, value, disabled?} objects

RADIO (Single choice)
  type: "radio"      Radio button group
    - options[]      Array of {label, value, disabled?} objects

CHECKBOX
  type: "checkbox"   Single checkbox (boolean)
    - (label is shown next to checkbox)

CHECKBOX GROUP (Multiple choice)
  type: "checkbox_group"   Multiple checkboxes
    - options[]      Array of {label, value, disabled?} objects

FILE UPLOAD
  type: "file"       Single file upload
    - accept         Allowed file types (e.g., "image/*,.pdf")
    - max_size       Maximum file size in MB (default: 10)

  type: "file_multiple"  Multiple file upload
    - accept         Allowed file types
    - max_size       Maximum file size per file in MB
    - max_files      Maximum number of files (default: 5)

HIDDEN & HONEYPOT
  type: "hidden"     Hidden field (pre-filled with default_value)
  type: "honeypot"   Spam trap field (invisible to users)

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  style              "card" | "flat" (default: card)
  columns            1 | 2 (form grid columns, default: 1)
  max_width          Container max width: "sm" | "md" | "lg" | "xl" | "2xl"
  card_width         Card max width: "md" | "lg" | "xl" | "2xl"
  card_centered      Boolean - center card horizontally (default: true)
  padding_y          Vertical padding: "8" | "12" | "16" | "20"
  padding_y_lg       Desktop vertical padding

COLORS
  background_color   Section background: "base-100" | "base-200" | "base-300"
  card_bg            Card background color (default: base-100)

BUTTONS
  btn_color          Button color: "primary" | "secondary" | "accent" | "success"
  btn_style          Button style: "solid" | "outline" | "ghost"
  btn_width          Button width: "full" | "half" | "auto"
  btn_centered       Boolean - center button (default: false)

FORM OPTIONS
  show_required      Boolean - show asterisk on required fields
  label_position     "top" | "floating" (default: top)
  checkbox_style     "checkbox" | "toggle" (for checkbox type)

SPAM PROTECTION
  enable_honeypot    Boolean - enable honeypot field (default: true)
  honeypot_name      Honeypot field name (default: "website")

FILE UPLOAD OPTIONS
  upload_style       "default" | "dropzone" (drag & drop area)
  enable_crop        Boolean - enable image cropping (dropzone only)
  crop_aspect_ratio  Crop aspect ratio (e.g., 1 for square, 1.5 for 3:2)
  crop_min_width     Minimum crop width in pixels
  crop_min_height    Minimum crop height in pixels

EMAIL NOTIFICATIONS (config JSON)
  Configure email notifications sent when form is submitted.

  notification_email_to      Primary recipient email address
                             Example: "contact@company.com"
  notification_email_cc      CC recipient(s), comma-separated
                             Example: "manager@company.com, sales@company.com"
  notification_email_subject Email subject line (supports placeholders)
                             Example: "New inquiry from {name} - {company}"
                             Placeholders: Use form field names in {braces}
  notification_email_enabled Boolean - enable email notifications (default: false)

  Subject placeholders:
    - {field_name}    Replaced with submitted form field value
    - {landing_page}  Replaced with landing page title
    - {date}          Replaced with submission date

  Example config:
  {
    "notification_email_enabled": true,
    "notification_email_to": "contact@company.ro",
    "notification_email_cc": "sales@company.ro, manager@company.ro",
    "notification_email_subject": "New request: {name} - {company}"
  }

  NOTE: Email notifications are sent in addition to:
  - Customer confirmation (if email field is present)

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Simple Contact Form:
{
  "title": "Contact Us",
  "description": "Fill out the form below and we'll get back to you.",
  "form_fields": [
    {"name": "name", "type": "text", "label": "Name", "required": true, "placeholder": "Your name"},
    {"name": "email", "type": "email", "label": "Email", "required": true, "placeholder": "your@email.com"},
    {"name": "message", "type": "textarea", "label": "Message", "required": true, "rows": 4}
  ],
  "submit_text": "Send Message",
  "success_message": "Thank you! We'll be in touch soon.",
  "footer_text": "Your data is safe with us."
}
config: {"style": "card", "btn_color": "primary"}

Romanian Magazine Contact Form:
{
  "title": "Vă rugăm completați formularul de mai jos. Revenim în maximum 24 de ore.",
  "form_fields": [
    {"name": "nume", "type": "text", "label": "Nume", "required": true, "placeholder": "Numele dumneavoastră"},
    {"name": "prenume", "type": "text", "label": "Prenume", "required": true, "placeholder": "Prenumele dumneavoastră"},
    {"name": "companie", "type": "text", "label": "Companie", "placeholder": "Ce companie reprezentați"},
    {"name": "email", "type": "email", "label": "Adresă de email", "required": true, "placeholder": "Adresă de email"},
    {"name": "telefon", "type": "tel", "label": "Număr de telefon", "placeholder": "Număr de telefon"},
    {"name": "detalii", "type": "textarea", "label": "Detalii suplimentare", "rows": 4,
     "placeholder": "Ce detalii suplimentare doriți să aflați despre Revista Ghidul Primăriilor?"}
  ],
  "submit_text": "Trimiteți solicitarea",
  "success_message": "Mulțumim! Vă vom contacta în cel mai scurt timp.",
  "footer_text": "Confidențialitate: datele dumneavoastră sunt în siguranță."
}
config: {"style": "card", "btn_color": "primary", "btn_width": "full", "show_required": false}
""",
        "default_content": {
            "title": "Contact Us",
            "description": "Fill out the form below and we'll get back to you as soon as possible.",
            "form_fields": [
                {
                    "name": "name",
                    "type": "text",
                    "label": "Full Name",
                    "width": "half",
                    "required": True,
                    "placeholder": "John Doe",
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Email Address",
                    "width": "half",
                    "required": True,
                    "placeholder": "john@example.com",
                },
                {
                    "name": "phone",
                    "type": "tel",
                    "label": "Phone Number",
                    "width": "half",
                    "placeholder": "+1 (555) 000-0000",
                },
                {
                    "name": "subject",
                    "type": "select",
                    "label": "Subject",
                    "width": "half",
                    "required": True,
                    "options": [
                        {"label": "Select a subject...", "value": ""},
                        {"label": "General Inquiry", "value": "general"},
                        {"label": "Technical Support", "value": "support"},
                        {"label": "Sales Question", "value": "sales"},
                        {"label": "Other", "value": "other"},
                    ],
                },
                {
                    "name": "message",
                    "type": "textarea",
                    "label": "Message",
                    "required": True,
                    "rows": 4,
                    "placeholder": "How can we help you?",
                },
            ],
            "submit_text": "Send Message",
            "success_message": "Thank you for your message! We'll be in touch soon.",
        },
        "default_config": {
            "style": "card",
            "card_bg": "base-100",
            "columns": 1,
            "btn_color": "primary",
            "btn_style": "solid",
            "max_width": "lg",
            "card_width": "xl",
            "card_centered": True,
            "show_required": True,
            "label_position": "top",
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-200",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Romanian Magazine Contact",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form.html",
        "is_active": True,
        "description": """Romanian language contact form for magazine inquiries.

Single column layout with fields: Nume, Prenume, Companie, Email, Telefon, Detalii.
Includes privacy notice footer text.
""",
        "default_content": {
            "title": "Vă rugăm completați formularul de mai jos. Revenim în maximum 24 de ore.",
            "description": "",
            "form_fields": [
                {
                    "name": "nume",
                    "type": "text",
                    "label": "Nume",
                    "width": "full",
                    "required": True,
                    "placeholder": "Numele dumneavoastră",
                },
                {
                    "name": "prenume",
                    "type": "text",
                    "label": "Prenume",
                    "width": "full",
                    "required": True,
                    "placeholder": "Prenumele dumneavoastră",
                },
                {
                    "name": "companie",
                    "type": "text",
                    "label": "Companie",
                    "width": "full",
                    "required": False,
                    "placeholder": "Ce companie reprezentați",
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Adresă de email",
                    "width": "full",
                    "required": True,
                    "placeholder": "Adresă de email",
                },
                {
                    "name": "telefon",
                    "type": "tel",
                    "label": "Număr de telefon",
                    "width": "full",
                    "required": False,
                    "placeholder": "Număr de telefon",
                },
                {
                    "name": "detalii",
                    "type": "textarea",
                    "label": "Detalii suplimentare",
                    "width": "full",
                    "required": False,
                    "rows": 4,
                    "placeholder": "Ce detalii suplimentare doriți să aflați despre Revista Ghidul Primăriilor? Revenim cu toate detaliile în cel mai scurt timp.",
                },
            ],
            "submit_text": "Trimiteți solicitarea",
            "success_message": "Mulțumim! Solicitarea dumneavoastră a fost trimisă cu succes. Vă vom contacta în cel mai scurt timp.",
            "footer_text": "Confidențialitate: datele dumneavoastră sunt în siguranță.",
        },
        "default_config": {
            "style": "card",
            "card_bg": "base-100",
            "columns": 1,
            "btn_color": "primary",
            "btn_style": "solid",
            "btn_width": "full",
            "max_width": "lg",
            "card_width": "xl",
            "card_centered": True,
            "show_required": False,
            "label_position": "top",
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-100",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Lead Generation",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form.html",
        "is_active": True,
        "description": """Lead generation form with two-column layout.

Ideal for downloading resources, signing up for newsletters, or requesting demos.
""",
        "default_content": {
            "title": "Get Your Free Guide",
            "description": "Enter your details to download instantly.",
            "form_fields": [
                {
                    "name": "first_name",
                    "type": "text",
                    "label": "First Name",
                    "width": "half",
                    "required": True,
                    "placeholder": "First name",
                },
                {
                    "name": "last_name",
                    "type": "text",
                    "label": "Last Name",
                    "width": "half",
                    "required": True,
                    "placeholder": "Last name",
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Work Email",
                    "width": "full",
                    "required": True,
                    "placeholder": "you@company.com",
                },
                {
                    "name": "company",
                    "type": "text",
                    "label": "Company",
                    "width": "half",
                    "placeholder": "Company name",
                },
                {
                    "name": "job_title",
                    "type": "text",
                    "label": "Job Title",
                    "width": "half",
                    "placeholder": "Your role",
                },
                {
                    "name": "consent",
                    "type": "checkbox",
                    "label": "I agree to receive marketing communications",
                    "required": True,
                },
            ],
            "submit_text": "Download Now",
            "success_message": "Thank you! Check your email for the download link.",
        },
        "default_config": {
            "style": "card",
            "card_bg": "base-100",
            "columns": 2,
            "btn_color": "success",
            "btn_style": "solid",
            "btn_width": "full",
            "max_width": "lg",
            "card_width": "xl",
            "card_centered": True,
            "show_required": True,
            "label_position": "top",
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-200",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Minimal",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form.html",
        "is_active": True,
        "description": """Minimal flat-style form without card wrapper.

Simple email capture or newsletter signup form.
""",
        "default_content": {
            "title": "Stay Updated",
            "description": "Subscribe to our newsletter for the latest updates.",
            "form_fields": [
                {
                    "name": "email",
                    "type": "email",
                    "label": "Email Address",
                    "required": True,
                    "placeholder": "Enter your email",
                },
            ],
            "submit_text": "Subscribe",
            "success_message": "Thank you for subscribing!",
            "footer_text": "We respect your privacy. Unsubscribe at any time.",
        },
        "default_config": {
            "style": "flat",
            "columns": 1,
            "btn_color": "primary",
            "btn_style": "solid",
            "btn_width": "full",
            "max_width": "md",
            "card_centered": True,
            "show_required": False,
            "label_position": "top",
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-100",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    # FLOATING LABELS TEMPLATES (order_form_floating.html)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Floating Labels (Default)",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form_floating.html",
        "is_active": True,
        "description": """TEMPLATE: landing_pages/zones/order_form_floating.html

Modern form with floating labels (Flowbite style). Labels animate from placeholder
position to above the field when focused or filled. Includes real-time validation.

═══════════════════════════════════════════════════════════════
CONTENT FIELDS (content JSON)
═══════════════════════════════════════════════════════════════

Same as order_form.html:
  title              Form title/heading
  description        Subtitle/description text
  form_fields[]      Array of field objects (same types as standard form)
  submit_text        Submit button text
  success_message    Message shown after successful submission
  redirect_url       Optional redirect URL after success
  footer_text        Text shown below submit button (e.g., privacy notice)

═══════════════════════════════════════════════════════════════
FIELD TYPES (form_fields array items)
═══════════════════════════════════════════════════════════════

Supports all field types from standard form:
  - text, email, tel, url, password, number (with floating label)
  - date, time, datetime-local (with floating label)
  - textarea (with floating label)
  - select, radio, checkbox, checkbox_group (standard labels)
  - file, file_multiple (with dropzone option)
  - hidden, honeypot, color

═══════════════════════════════════════════════════════════════
CONFIG OPTIONS (config JSON)
═══════════════════════════════════════════════════════════════

LAYOUT
  columns            1 | 2 (form grid columns, default: 1)
  max_width          Container max width: "sm" | "md" | "lg" | "xl"
  card_width         Content max width: "md" | "lg" | "xl" | "2xl"
  card_centered      Boolean - center content horizontally (default: true)
  padding_y          Vertical padding: "8" | "12" | "16" | "20"
  padding_y_lg       Desktop vertical padding

COLORS
  background_color   Section background: "base-100" | "base-200" | "base-300"
  focus_color        Input focus/accent color: "primary" | "secondary" | "accent"
                     (Used for input borders on focus and button color)

BUTTONS
  btn_color          Button background color (default: uses focus_color)
  btn_width          Button width: "full" | "half" | "auto"
  btn_centered       Boolean - center button (default: false)

FORM OPTIONS
  show_required      Boolean - show asterisk on required fields
  checkbox_style     "checkbox" | "toggle" (for checkbox type)

SPAM PROTECTION
  enable_honeypot    Boolean - enable honeypot field (default: true)
  honeypot_name      Honeypot field name (default: "website")

FILE UPLOAD OPTIONS
  upload_style       "default" | "dropzone" (drag & drop area)
  enable_crop        Boolean - enable image cropping (dropzone only)
  crop_aspect_ratio  Crop aspect ratio
  crop_min_width     Minimum crop width in pixels
  crop_min_height    Minimum crop height in pixels

═══════════════════════════════════════════════════════════════
VALIDATION FEATURES (automatic)
═══════════════════════════════════════════════════════════════

Real-time validation on blur with error messages:
  - Required field validation
  - Email format validation
  - URL format validation
  - Number format validation
  - Pattern matching validation
  - Min/max length validation

Error styling:
  - Red border on invalid fields
  - Error message below field
  - Clears on input

═══════════════════════════════════════════════════════════════
EXAMPLE CONFIGURATIONS
═══════════════════════════════════════════════════════════════

Modern Contact Form:
{
  "title": "Get in Touch",
  "description": "We'd love to hear from you.",
  "form_fields": [
    {"name": "name", "type": "text", "label": "Your Name", "required": true},
    {"name": "email", "type": "email", "label": "Email Address", "required": true},
    {"name": "phone", "type": "tel", "label": "Phone Number"},
    {"name": "message", "type": "textarea", "label": "Your Message", "required": true, "rows": 4}
  ],
  "submit_text": "Send Message",
  "success_message": "Thank you! We'll respond within 24 hours.",
  "footer_text": "Your information is secure and will never be shared."
}
config: {"focus_color": "primary", "btn_width": "full"}

Romanian Floating Form:
{
  "title": "Completați formularul de mai jos",
  "form_fields": [
    {"name": "nume", "type": "text", "label": "Nume", "required": true},
    {"name": "prenume", "type": "text", "label": "Prenume", "required": true},
    {"name": "email", "type": "email", "label": "Adresă de email", "required": true},
    {"name": "telefon", "type": "tel", "label": "Număr de telefon"},
    {"name": "mesaj", "type": "textarea", "label": "Mesajul dumneavoastră", "rows": 4}
  ],
  "submit_text": "Trimite",
  "footer_text": "Datele dumneavoastră sunt în siguranță."
}
config: {"focus_color": "primary", "background_color": "base-100"}
""",
        "default_content": {
            "title": "Get in Touch",
            "description": "We'd love to hear from you. Fill out the form below.",
            "form_fields": [
                {
                    "name": "name",
                    "type": "text",
                    "label": "Your Name",
                    "required": True,
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Email Address",
                    "required": True,
                },
                {
                    "name": "phone",
                    "type": "tel",
                    "label": "Phone Number",
                },
                {
                    "name": "message",
                    "type": "textarea",
                    "label": "Your Message",
                    "required": True,
                    "rows": 4,
                },
            ],
            "submit_text": "Send Message",
            "success_message": "Thank you! We'll respond within 24 hours.",
        },
        "default_config": {
            "columns": 1,
            "max_width": "lg",
            "card_width": "xl",
            "card_centered": True,
            "focus_color": "primary",
            "btn_color": "primary",
            "btn_width": "full",
            "show_required": True,
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-200",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Floating Labels Romanian",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form_floating.html",
        "is_active": True,
        "description": """Romanian floating labels contact form.

Modern style with animated labels, single column layout, privacy notice.
""",
        "default_content": {
            "title": "Vă rugăm completați formularul de mai jos. Revenim în maximum 24 de ore.",
            "description": "",
            "form_fields": [
                {
                    "name": "nume",
                    "type": "text",
                    "label": "Nume",
                    "required": True,
                },
                {
                    "name": "prenume",
                    "type": "text",
                    "label": "Prenume",
                    "required": True,
                },
                {
                    "name": "companie",
                    "type": "text",
                    "label": "Companie",
                    "required": False,
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Adresă de email",
                    "required": True,
                },
                {
                    "name": "telefon",
                    "type": "tel",
                    "label": "Număr de telefon",
                    "required": False,
                },
                {
                    "name": "detalii",
                    "type": "textarea",
                    "label": "Detalii suplimentare",
                    "required": False,
                    "rows": 4,
                },
            ],
            "submit_text": "Trimiteți solicitarea",
            "success_message": "Mulțumim! Solicitarea dumneavoastră a fost trimisă cu succes.",
            "footer_text": "Confidențialitate: datele dumneavoastră sunt în siguranță.",
        },
        "default_config": {
            "columns": 1,
            "max_width": "lg",
            "card_width": "xl",
            "card_centered": True,
            "focus_color": "primary",
            "btn_color": "primary",
            "btn_width": "full",
            "show_required": False,
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-100",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - Floating Labels Two Column",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form_floating.html",
        "is_active": True,
        "description": """Two-column floating labels form for lead generation.

Name fields side by side, email/company side by side, with consent checkbox.
""",
        "default_content": {
            "title": "Download Your Free Resource",
            "description": "Enter your details below to get instant access.",
            "form_fields": [
                {
                    "name": "first_name",
                    "type": "text",
                    "label": "First Name",
                    "width": "half",
                    "required": True,
                },
                {
                    "name": "last_name",
                    "type": "text",
                    "label": "Last Name",
                    "width": "half",
                    "required": True,
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Work Email",
                    "width": "half",
                    "required": True,
                },
                {
                    "name": "company",
                    "type": "text",
                    "label": "Company",
                    "width": "half",
                },
                {
                    "name": "consent",
                    "type": "checkbox",
                    "label": "I agree to receive marketing emails",
                    "required": True,
                },
            ],
            "submit_text": "Get Access",
            "success_message": "Success! Check your email for the download link.",
            "footer_text": "We respect your privacy. Unsubscribe anytime.",
        },
        "default_config": {
            "columns": 2,
            "max_width": "lg",
            "card_width": "xl",
            "card_centered": True,
            "focus_color": "success",
            "btn_color": "success",
            "btn_width": "full",
            "show_required": True,
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-200",
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Order Form - File Upload with Floating Labels",
        "zone_type": ZoneType.ORDER_FORM,
        "template_file": "landing_pages/zones/order_form_floating.html",
        "is_active": True,
        "description": """Application form with file uploads and floating labels.

Dropzone-style file upload with contact fields.
""",
        "default_content": {
            "title": "Submit Your Application",
            "description": "Upload your documents and we'll review them shortly.",
            "form_fields": [
                {
                    "name": "name",
                    "type": "text",
                    "label": "Full Name",
                    "width": "half",
                    "required": True,
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "Email",
                    "width": "half",
                    "required": True,
                },
                {
                    "name": "phone",
                    "type": "tel",
                    "label": "Phone",
                    "width": "half",
                },
                {
                    "name": "position",
                    "type": "select",
                    "label": "Position",
                    "width": "half",
                    "required": True,
                    "options": [
                        {"label": "Select position...", "value": ""},
                        {"label": "Developer", "value": "developer"},
                        {"label": "Designer", "value": "designer"},
                        {"label": "Manager", "value": "manager"},
                        {"label": "Other", "value": "other"},
                    ],
                },
                {
                    "name": "resume",
                    "type": "file",
                    "label": "Resume/CV",
                    "required": True,
                    "accept": ".pdf,.doc,.docx",
                    "max_size": 10,
                    "help_text": "PDF, DOC, or DOCX (max 10MB)",
                },
                {
                    "name": "cover_letter",
                    "type": "textarea",
                    "label": "Cover Letter",
                    "rows": 5,
                },
            ],
            "submit_text": "Submit Application",
            "success_message": "Thank you! We'll review your application and get back to you.",
        },
        "default_config": {
            "columns": 2,
            "max_width": "xl",
            "card_width": "2xl",
            "card_centered": True,
            "focus_color": "primary",
            "btn_color": "primary",
            "btn_width": "full",
            "show_required": True,
            "enable_honeypot": True,
            "honeypot_name": "website",
            "background_color": "base-200",
            "upload_style": "dropzone",
        },
    },
]
