# src/prometheus/cipher/v2_modern/adapter.py
"""V2 Modern Crypto Adapter — ChaCha20-Poly1305 + Argon2id."""

from __future__ import annotations

import base64
import hashlib
import os
import warnings

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from prometheus.domain.value_objects import Ciphertext

try:
    from argon2.low_level import Type as Argon2Type
    from argon2.low_level import hash_secret_raw

    HAS_ARGON2 = True
except ImportError:
    HAS_ARGON2 = False

# Argon2id parameters (OWASP 2024 recommendations)
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 4
ARGON2_HASH_LENGTH = 32
ARGON2_SALT_LENGTH = 16

# ChaCha20-Poly1305 constants
NONCE_LENGTH = 12  # 96-bit nonce for ChaCha20-Poly1305
TAG_LENGTH = 16

# Magic byte for v2 version detection
VERSION_BYTE = b"\x02"


class V2ModernAdapter:
    """Adapter for v2 modern ChaCha20-Poly1305 + Argon2id encryption.

    This is the recommended adapter for all new encryption operations.
    Provides AEAD (Authenticated Encryption with Associated Data) with
    forward secrecy via random salt and nonce per encryption.

    Algorithm:
    1. Derive 256-bit key via Argon2id(secret, random_salt)
    2. Encrypt with ChaCha20-Poly1305(key, random_nonce, plaintext)
    3. Output: v2|salt_b64|nonce_b64|ciphertext_b64|tag_b64
    """

    def __init__(
        self,
        time_cost: int = ARGON2_TIME_COST,
        memory_cost: int = ARGON2_MEMORY_COST,
        parallelism: int = ARGON2_PARALLELISM,
    ) -> None:
        self._time_cost = time_cost
        self._memory_cost = memory_cost
        self._parallelism = parallelism

    @property
    def version(self) -> str:
        return "v2"

    def _derive_key(self, secret: str, salt: bytes) -> bytes:
        """Derive 256-bit key using Argon2id.

        Falls back to PBKDF2-SHA256 if argon2-cffi is not available.
        """
        if HAS_ARGON2:
            return hash_secret_raw(
                secret.encode("utf-8"),
                salt,
                time_cost=self._time_cost,
                memory_cost=self._memory_cost,
                parallelism=self._parallelism,
                hash_len=ARGON2_HASH_LENGTH,
                type=Argon2Type.ID,
            )
        warnings.warn(
            "argon2-cffi not available, falling back to PBKDF2-SHA256. "
            "Install prometheus-crypto[crypto] for Argon2id support.",
            stacklevel=2,
        )
        return self._derive_key_pbkdf2(secret, salt)

    def _derive_key_pbkdf2(self, secret: str, salt: bytes) -> bytes:
        """PBKDF2-SHA256 fallback (600k iterations per OWASP 2024)."""
        return hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 600000, dklen=32)

    def encrypt(self, secret: str, plaintext: str) -> Ciphertext:
        """Encrypt plaintext with ChaCha20-Poly1305 + Argon2id.

        Returns Ciphertext with v2 prefix: v2|salt_b64|nonce_b64|ct_b64|tag_b64
        """
        salt = os.urandom(ARGON2_SALT_LENGTH)
        nonce = os.urandom(NONCE_LENGTH)
        key = self._derive_key(secret, salt)

        aead = ChaCha20Poly1305(key)
        ciphertext_with_tag = aead.encrypt(nonce, plaintext.encode("utf-8"), None)

        # Split ciphertext and tag (last 16 bytes)
        ciphertext = ciphertext_with_tag[:-TAG_LENGTH]
        tag = ciphertext_with_tag[-TAG_LENGTH:]

        # Encode components to base64
        salt_b64 = base64.b64encode(salt).decode("ascii")
        nonce_b64 = base64.b64encode(nonce).decode("ascii")
        ct_b64 = base64.b64encode(ciphertext).decode("ascii")
        tag_b64 = base64.b64encode(tag).decode("ascii")

        return Ciphertext(f"v2|{salt_b64}|{nonce_b64}|{ct_b64}|{tag_b64}")

    def decrypt(self, secret: str, ciphertext: Ciphertext) -> str:
        """Decrypt v2 ciphertext with ChaCha20-Poly1305 + Argon2id.

        Reconstructs the 256-bit key from the salt embedded in the ciphertext,
        then decrypts and verifies authenticity via Poly1305 MAC.
        """
        if not ciphertext.value.startswith("v2|"):
            msg = "Invalid v2 ciphertext format: expected 'v2|...' prefix"
            raise ValueError(msg)

        components = ciphertext.components
        salt = base64.b64decode(components["salt"])
        nonce = base64.b64decode(components["nonce"])
        ciphertext_bytes = base64.b64decode(components["ciphertext"])
        tag = base64.b64decode(components["tag"])

        key = self._derive_key(secret, salt)

        aead = ChaCha20Poly1305(key)
        plaintext = aead.decrypt(nonce, ciphertext_bytes + tag, None)

        return plaintext.decode("utf-8")
