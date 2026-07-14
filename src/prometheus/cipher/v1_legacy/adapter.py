# src/prometheus/crypto/v1_legacy/adapter.py
"""V1 Legacy Crypto Adapter — INMUTABLE. Do not modify after v2.0.0."""

from __future__ import annotations

import base64
import hashlib

from prometheus.domain.value_objects import Ciphertext


class V1LegacyAdapter:
    """Adapter for v1 legacy XOR+SHA256+Base64 encryption.

    WARNING: This algorithm is NOT cryptographically secure.
    Use V2ModernAdapter for new encryption operations.
    This adapter exists solely for backward compatibility with
    existing v1 ciphertexts.

    DO NOT MODIFY THIS FILE after v2.0.0 release.
    See ADR 0002 for rationale.
    """

    @property
    def version(self) -> str:
        return "v1"

    def encrypt(self, secret: str, plaintext: str) -> Ciphertext:
        """Encrypt plaintext using v1 legacy algorithm.

        NOTE: This method is retained for backward compatibility only.
        New encryption should use v2 via CryptoFactory.
        """
        key = hashlib.sha256(secret.encode("utf-8")).hexdigest()
        secret_index = len(secret) - 1
        key_index = len(key) // 2
        encrypted_result = ""

        for char in plaintext:
            temp_int = ord(char) + ord(secret[secret_index])
            temp_int = temp_int % 256
            temp_int = temp_int ^ ord(key[key_index])
            encrypted_result += chr(temp_int)

            secret_index -= 1
            key_index -= 1

            if secret_index < 0:
                secret_index = len(secret) - 1
            if key_index < 0:
                key_index = len(key) - 1

        b64 = base64.b64encode(encrypted_result.encode("latin1")).decode("utf-8")
        return Ciphertext(b64)

    def decrypt(self, secret: str, ciphertext: Ciphertext) -> str:
        """Decrypt v1 legacy ciphertext."""
        encrypted_bytes = base64.b64decode(ciphertext.value.encode("utf-8")).decode("latin1")
        key = hashlib.sha256(secret.encode("utf-8")).hexdigest()
        secret_index = len(secret) - 1
        key_index = len(key) // 2
        decrypted_result = ""

        for char in encrypted_bytes:
            temp = ord(char) ^ ord(key[key_index])
            temp = (temp - ord(secret[secret_index])) % 256
            decrypted_result += chr(temp)

            secret_index -= 1
            key_index -= 1

            if secret_index < 0:
                secret_index = len(secret) - 1
            if key_index < 0:
                key_index = len(key) - 1

        return decrypted_result
