"""
Email validation and normalization utilities (vendored so the plugin is self-contained).

Configuration via Django settings (can be set from .env):

    # Enable/disable disposable email blocking (default: True)
    EMAIL_BLOCK_DISPOSABLE = True  # env: EMAIL_BLOCK_DISPOSABLE

    # Additional disposable domains to block (extends default list)
    EMAIL_DISPOSABLE_DOMAINS = ["custom-temp.com", "another-temp.org"]

    # Enable/disable role-based email blocking (default: False)
    EMAIL_BLOCK_ROLE_BASED = False  # env: EMAIL_BLOCK_ROLE_BASED

    # Additional role prefixes to block (extends default list)
    EMAIL_ROLE_PREFIXES = ["sales", "marketing"]
"""
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

# =============================================================================
# Default disposable email domains
# =============================================================================
DEFAULT_DISPOSABLE_DOMAINS = {
    # Popular temporary email services
    "tempmail.com",
    "temp-mail.org",
    "tempmail.net",
    "temp-mail.io",
    "guerrillamail.com",
    "guerrillamail.org",
    "guerrillamail.net",
    "guerrillamail.biz",
    "guerrillamail.de",
    "guerrillmail.com",
    "sharklasers.com",
    "grr.la",
    "guerrillamailblock.com",
    "pokemail.net",
    "spam4.me",
    # 10 Minute Mail variants
    "10minutemail.com",
    "10minutemail.net",
    "10minutemail.org",
    "10minmail.com",
    "10mail.org",
    # Mailinator and variants
    "mailinator.com",
    "mailinator.net",
    "mailinator.org",
    "mailinater.com",
    "mailinator2.com",
    "notmailinator.com",
    "chammy.info",
    "tradermail.info",
    "mailin8r.com",
    "mailinator.us",
    # Yopmail
    "yopmail.com",
    "yopmail.fr",
    "yopmail.net",
    "cool.fr.nf",
    "jetable.fr.nf",
    "nospam.ze.tc",
    "nomail.xl.cx",
    "mega.zik.dj",
    "speed.1s.fr",
    "courriel.fr.nf",
    "moncourrier.fr.nf",
    "monemail.fr.nf",
    # Throwaway Mail
    "throwawaymail.com",
    "throwaway.email",
    "throam.com",
    "wegwerfmail.de",
    "wegwerfmail.net",
    "wegwerfmail.org",
    # Fake Inbox
    "fakeinbox.com",
    "fakemailgenerator.com",
    "emailfake.com",
    "fakemail.fr",
    "fakemailgenerator.net",
    # Trash Mail
    "trashmail.com",
    "trashmail.net",
    "trashmail.org",
    "trashmail.me",
    "trash-mail.com",
    "trashemail.de",
    # Discard Mail
    "discardmail.com",
    "discardmail.de",
    "discard.email",
    "spambog.com",
    "spambog.de",
    "spambog.ru",
    # Other popular ones
    "getnada.com",
    "getairmail.com",
    "mohmal.com",
    "emailondeck.com",
    "tempail.com",
    "tempr.email",
    "dispostable.com",
    "mailcatch.com",
    "mytemp.email",
    "tempinbox.com",
    "burnermail.io",
    "inboxkitten.com",
    "maildrop.cc",
    "mailsac.com",
    "harakirimail.com",
    "33mail.com",
    "spamgourmet.com",
    "mintemail.com",
    "tempsky.com",
    "crazymailing.com",
    "mailnesia.com",
    "spamex.com",
    "nwytg.net",
    "mailpoof.com",
}

# =============================================================================
# Default role-based email prefixes
# =============================================================================
DEFAULT_ROLE_PREFIXES = {
    # Generic roles
    "info",
    "contact",
    "hello",
    "hi",
    "enquiry",
    "enquiries",
    "inquiry",
    "general",
    # Admin/Tech roles
    "admin",
    "administrator",
    "webmaster",
    "postmaster",
    "hostmaster",
    "root",
    "sysadmin",
    "tech",
    "support",
    "help",
    "helpdesk",
    # No-reply addresses
    "noreply",
    "no-reply",
    "donotreply",
    "do-not-reply",
    "mailer-daemon",
    "bounce",
    "bounces",
    # Business roles
    "sales",
    "marketing",
    "hr",
    "jobs",
    "careers",
    "recruitment",
    "billing",
    "invoices",
    "accounts",
    "accounting",
    "finance",
    "legal",
    "abuse",
    "spam",
    "security",
    "privacy",
    "compliance",
    # Team addresses
    "team",
    "staff",
    "office",
    "all",
    "everyone",
    "company",
    # Service addresses
    "newsletter",
    "news",
    "updates",
    "notifications",
    "alerts",
    "subscribe",
    "unsubscribe",
    "feedback",
    "suggestions",
}


def _get_disposable_domains() -> set:
    """Get the set of disposable email domains to block."""
    domains = DEFAULT_DISPOSABLE_DOMAINS.copy()
    # Add custom domains from settings
    custom = getattr(settings, "EMAIL_DISPOSABLE_DOMAINS", [])
    if custom:
        domains.update(d.lower() for d in custom)
    return domains


def _get_role_prefixes() -> set:
    """Get the set of role-based email prefixes to block."""
    prefixes = DEFAULT_ROLE_PREFIXES.copy()
    # Add custom prefixes from settings
    custom = getattr(settings, "EMAIL_ROLE_PREFIXES", [])
    if custom:
        prefixes.update(p.lower() for p in custom)
    return prefixes


def is_disposable_email(email: str) -> bool:
    """
    Check if email is from a disposable/temporary email provider.

    Args:
        email: Email address to check

    Returns:
        True if email is from a disposable domain
    """
    if not email or "@" not in email:
        return False

    domain = email.lower().split("@")[-1]
    disposable_domains = _get_disposable_domains()

    # Check exact match
    if domain in disposable_domains:
        return True

    # Check if subdomain of a disposable domain
    for disp_domain in disposable_domains:
        if domain.endswith("." + disp_domain):
            return True

    return False


def is_role_based_email(email: str) -> bool:
    """
    Check if email is a role-based address (info@, admin@, etc.).

    Args:
        email: Email address to check

    Returns:
        True if email is role-based
    """
    if not email or "@" not in email:
        return False

    local = email.lower().split("@")[0]
    role_prefixes = _get_role_prefixes()

    # Check exact match
    if local in role_prefixes:
        return True

    # Check if starts with role prefix followed by number or separator
    for prefix in role_prefixes:
        if local.startswith(prefix) and len(local) > len(prefix):
            next_char = local[len(prefix)]
            if next_char in "0123456789_-.+":
                return True

    return False


def normalize_email(email: str) -> str:
    """
    Normalize email address to lowercase and strip whitespace.

    Args:
        email: Email address to normalize

    Returns:
        Normalized email address (lowercase, stripped)
    """
    if not email:
        return ""
    return email.lower().strip()


def is_valid_email(email: str) -> bool:
    """
    Check if email is valid using Django's email validator.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False

    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def validate_and_normalize_email(email: str) -> tuple[str | None, str | None]:
    """
    Validate and normalize email address.

    Checks performed:
    1. Basic format validation
    2. Disposable email blocking (if EMAIL_BLOCK_DISPOSABLE=True)
    3. Role-based email blocking (if EMAIL_BLOCK_ROLE_BASED=True)
    4. Domain typo detection and suggestions
    5. Django email validator

    Args:
        email: Email address to validate and normalize

    Returns:
        Tuple of (normalized_email, error_message)
        - If valid: (normalized_email, None)
        - If invalid: (None, error_message)
    """
    if not email:
        return None, _("Email address is required.")

    # Normalize first
    normalized = normalize_email(email)

    # Basic format checks before Django validator
    if not normalized:
        return None, _("Email address is required.")

    # Check for obviously invalid patterns
    if " " in normalized:
        return None, _("Email address cannot contain spaces.")

    if "@" not in normalized:
        return None, _("Email address must contain @.")

    # Check for multiple @ symbols
    if normalized.count("@") > 1:
        return None, _("Email address is not valid (too many @).")

    # Split into local and domain parts
    local, domain = normalized.rsplit("@", 1)

    if not local:
        return None, _("Email address is not valid (missing local part).")

    if not domain:
        return None, _("Email address is not valid (missing domain).")

    # Check domain has at least one dot
    if "." not in domain:
        return None, _("Email domain is not valid (missing .com/.org etc).")

    # Check domain doesn't start or end with dot
    if domain.startswith(".") or domain.endswith("."):
        return None, _("Email domain is not valid.")

    # Check for disposable email (if enabled)
    if getattr(settings, "EMAIL_BLOCK_DISPOSABLE", True):
        if is_disposable_email(normalized):
            logger.warning(f"Disposable email blocked: {normalized}")
            return None, _("Disposable email addresses are not allowed.")

    # Check for role-based email (if enabled)
    if getattr(settings, "EMAIL_BLOCK_ROLE_BASED", False):
        if is_role_based_email(normalized):
            logger.warning(f"Role-based email blocked: {normalized}")
            return None, _(
                "Please use a personal email address, not a role-based one "
                "(e.g., info@, admin@, support@)."
            )

    # Valid domains that look like typos - DO NOT correct these
    valid_domains = {
        "mail.com",  # Real email provider, NOT a typo for gmail
        "googlemail.com",  # Official Gmail alias in some countries
        "hmail.com",  # Real domain
        "ail.com",  # Real domain
        "ao.com",  # Real domain
        "gmx.com",  # Real provider
        "gmx.net",  # Real provider
        "gmx.de",  # Real provider (Germany)
        "gmx.at",  # Real provider (Austria)
        "gmx.ch",  # Real provider (Switzerland)
        "yahoo.ro",  # Yahoo Romania
    }

    # Regional TLD patterns to preserve (don't suggest .com for these)
    # Matches: yahoo.co.uk, yahoo.co.jp, hotmail.co.uk, etc.
    regional_tld_pattern = (
        ".co.uk", ".co.jp", ".co.in", ".co.za", ".co.nz", ".co.kr",
        ".com.au", ".com.br", ".com.mx", ".com.ar", ".com.tr",
    )

    # Skip typo detection for known valid domains and regional TLDs
    if domain in valid_domains or domain.endswith(regional_tld_pattern):
        # Continue directly to Django validator
        try:
            validate_email(normalized)
        except ValidationError:
            return None, _("Email address is not valid.")
        return normalized, None

    # Check for common typos in popular domains
    common_domains = {
        # Gmail variants
        "gmial.com": "gmail.com",
        "gamil.com": "gmail.com",
        "gmai.com": "gmail.com",
        "gmailcom": "gmail.com",
        "gmail.om": "gmail.com",
        "gnail.com": "gmail.com",
        "gmal.com": "gmail.com",
        "gemail.com": "gmail.com",
        "gmail.cm": "gmail.com",  # missing 'o'
        "gmaul.com": "gmail.com",  # u next to i
        "gmsil.com": "gmail.com",  # s next to a
        "ggmail.com": "gmail.com",  # double g
        "gmil.com": "gmail.com",  # missing 'a'
        "gmaik.com": "gmail.com",  # k next to l
        "gmaio.com": "gmail.com",  # o next to l
        # Yahoo variants (NOT yahoo.co.uk, yahoo.co.jp - those are valid!)
        "yaho.com": "yahoo.com",
        "yahooo.com": "yahoo.com",
        "yahoocom": "yahoo.com",
        "yhoo.com": "yahoo.com",
        "tahoo.com": "yahoo.com",  # t next to y
        "uahoo.com": "yahoo.com",  # u next to y
        "yah00.com": "yahoo.com",  # zeros for o's
        # Hotmail variants
        "hotmal.com": "hotmail.com",
        "hotmai.com": "hotmail.com",
        "hotmailcom": "hotmail.com",
        "hotamil.com": "hotmail.com",
        "hotmial.com": "hotmail.com",
        "hotmeil.com": "hotmail.com",
        "hotmsil.com": "hotmail.com",  # s next to a
        "jotmail.com": "hotmail.com",  # j next to h
        # Outlook variants
        "outlok.com": "outlook.com",
        "outloo.com": "outlook.com",
        "outlookcom": "outlook.com",
        "outlool.com": "outlook.com",  # l next to k
        "outllok.com": "outlook.com",  # double l
        "putlook.com": "outlook.com",  # p next to o
        "oytlook.com": "outlook.com",  # y next to u
        # iCloud variants
        "iclud.com": "icloud.com",
        "icould.com": "icloud.com",  # transposition
        "iclod.com": "icloud.com",  # missing 'u'
        "icoud.com": "icloud.com",  # missing 'l'
        # Protonmail variants
        "protonmal.com": "protonmail.com",
        "protonmai.com": "protonmail.com",
        "protonmial.com": "protonmail.com",
        "protonmeil.com": "protonmail.com",
        "protnmail.com": "protonmail.com",
        # AOL variants
        "aolcom": "aol.com",
        "aool.com": "aol.com",
        # Live.com variants
        "livecom": "live.com",
        "liive.com": "live.com",
        "livve.com": "live.com",
        # MSN variants
        "msncom": "msn.com",
        "msnn.com": "msn.com",
        # GMX variants
        "gmxcom": "gmx.com",
        "gnx.com": "gmx.com",
    }

    # Check for TLD typos (keyboard proximity errors)
    # These catch patterns like gmail.con, yahoo.cpm, etc.
    tld_typos = {
        ".con": ".com",  # n next to m
        ".cpm": ".com",  # p next to o
        ".vom": ".com",  # v next to c
        ".xom": ".com",  # x next to c
        ".ocm": ".com",  # transposition
        ".comm": ".com",  # double m
        ".com,": ".com",  # trailing comma
        ".co,": ".com",  # trailing comma
    }

    # First check TLD typos
    for typo_tld, correct_tld in tld_typos.items():
        if domain.endswith(typo_tld):
            corrected_domain = domain[: -len(typo_tld)] + correct_tld
            logger.warning(
                f"TLD typo in email domain: {domain} -> {corrected_domain} for email {normalized}"
            )
            return None, _(
                "Did you mean %(suggested)s instead of %(domain)s?"
            ) % {"suggested": corrected_domain, "domain": domain}

    # Then check specific domain typos
    if domain in common_domains:
        suggested = common_domains[domain]
        logger.warning(
            f"Possible typo in email domain: {domain} -> {suggested} for email {normalized}"
        )
        # Translators: %(suggested)s is the correct domain, %(domain)s is what user typed
        return None, _(
            "Did you mean %(suggested)s instead of %(domain)s?"
        ) % {"suggested": suggested, "domain": domain}

    # Use Django's validator for final check
    try:
        validate_email(normalized)
    except ValidationError:
        return None, _("Email address is not valid.")

    return normalized, None
