"""
Encryption utilities for sensitive data at rest.

Uses Fernet symmetric encryption with key derived from Django SECRET_KEY.
"""

import base64
import hashlib
import json
import logging

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)

# Prefix to identify encrypted data
ENCRYPTED_PREFIX = "enc:v1:"


def _get_fernet():
    """
    Get a Fernet instance.

    Prefers a dedicated ``WEB_SECURITY_ENCRYPTION_KEY`` (a urlsafe-base64 Fernet key).
    Set it to decouple encryption from ``SECRET_KEY`` so rotating ``SECRET_KEY`` does
    NOT make stored credentials undecryptable. Generate one with:
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

    Falls back to a key derived from ``SECRET_KEY`` (legacy behaviour) when the
    dedicated key is unset.
    """
    dedicated = getattr(settings, "WEB_SECURITY_ENCRYPTION_KEY", None)
    if dedicated:
        try:
            return Fernet(dedicated.encode() if isinstance(dedicated, str) else dedicated)
        except Exception as e:
            raise ValueError("WEB_SECURITY_ENCRYPTION_KEY is not a valid Fernet key") from e

    key_bytes = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt_data(data: dict) -> str:
    """
    Encrypt a dictionary to a string.

    Args:
        data: Dictionary to encrypt

    Returns:
        Encrypted string with version prefix
    """
    if not data:
        return ""

    try:
        json_bytes = json.dumps(data).encode("utf-8")
        encrypted = _get_fernet().encrypt(json_bytes)
        return ENCRYPTED_PREFIX + encrypted.decode("utf-8")
    except Exception as e:
        logger.error("Failed to encrypt data: %s", e)
        raise ValueError("Encryption failed") from e


def decrypt_data(encrypted_string: str) -> dict:
    """
    Decrypt an encrypted string back to a dictionary.

    Args:
        encrypted_string: Encrypted string with version prefix

    Returns:
        Decrypted dictionary
    """
    if not encrypted_string:
        return {}

    # Handle unencrypted legacy data (plain JSON)
    if not encrypted_string.startswith(ENCRYPTED_PREFIX):
        try:
            # Try to parse as JSON (legacy unencrypted data)
            return json.loads(encrypted_string)
        except (json.JSONDecodeError, TypeError):
            logger.warning("Data is neither encrypted nor valid JSON")
            return {}

    try:
        # Remove prefix and decrypt
        encrypted_bytes = encrypted_string[len(ENCRYPTED_PREFIX) :].encode("utf-8")
        decrypted = _get_fernet().decrypt(encrypted_bytes)
        return json.loads(decrypted.decode("utf-8"))
    except InvalidToken:
        logger.error("Failed to decrypt data - invalid token (wrong key?)")
        return {}
    except Exception as e:
        logger.error("Failed to decrypt data: %s", e)
        return {}


def encrypt_string(value: str) -> str:
    """Encrypt a single string value (e.g. an API key). Empty -> ''."""
    if not value:
        return ""
    try:
        encrypted = _get_fernet().encrypt(value.encode("utf-8"))
        return ENCRYPTED_PREFIX + encrypted.decode("utf-8")
    except Exception as e:
        logger.error("Failed to encrypt string: %s", e)
        raise ValueError("Encryption failed") from e


def decrypt_string(encrypted_string: str) -> str:
    """Decrypt a single string value. Legacy plaintext is returned unchanged."""
    if not encrypted_string:
        return ""
    if not encrypted_string.startswith(ENCRYPTED_PREFIX):
        return encrypted_string  # legacy plaintext value
    try:
        encrypted_bytes = encrypted_string[len(ENCRYPTED_PREFIX) :].encode("utf-8")
        return _get_fernet().decrypt(encrypted_bytes).decode("utf-8")
    except InvalidToken:
        logger.error("Failed to decrypt string - invalid token (wrong key? SECRET_KEY rotated?)")
        return ""
    except Exception as e:
        logger.error("Failed to decrypt string: %s", e)
        return ""


def is_encrypted(value: str) -> bool:
    """Check if a string value is encrypted."""
    return isinstance(value, str) and value.startswith(ENCRYPTED_PREFIX)


def mask_credentials(credentials: dict, visible_chars: int = 4) -> dict:
    """
    Mask sensitive values in credentials for display.

    Args:
        credentials: Dictionary of credentials
        visible_chars: Number of characters to show at start

    Returns:
        Dictionary with masked values
    """
    if not credentials:
        return {}

    # Keys that should be masked
    sensitive_keys = {
        "api_token",
        "secret_key",
        "access_key",
        "password",
        "token",
        "key",
        "secret",
    }

    # Fully mask sensitive values. Do not reveal a plaintext prefix/suffix of a
    # secret: even a few leading characters aid guessing/correlation.
    masked = {}
    for key, value in credentials.items():
        if isinstance(value, str) and value and any(s in key.lower() for s in sensitive_keys):
            masked[key] = "•" * 8
        else:
            masked[key] = value

    return masked
