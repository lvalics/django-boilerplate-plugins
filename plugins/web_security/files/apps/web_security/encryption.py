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
    Get Fernet instance with key derived from SECRET_KEY.

    The key is derived using SHA-256 hash of SECRET_KEY, then base64 encoded
    to meet Fernet's 32-byte key requirement.

    Note: Changing SECRET_KEY will make existing encrypted data unreadable.
    """
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

    masked = {}
    for key, value in credentials.items():
        if isinstance(value, str) and any(s in key.lower() for s in sensitive_keys):
            if len(value) > visible_chars:
                masked[key] = value[:visible_chars] + "•" * 8
            else:
                masked[key] = "•" * 8
        else:
            masked[key] = value

    return masked
