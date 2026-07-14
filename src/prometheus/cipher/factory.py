# src/prometheus/crypto/factory.py
"""Crypto Factory — auto-detect version and instantiate correct adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.cipher.v2_modern.adapter import V2ModernAdapter

if TYPE_CHECKING:
    from prometheus.domain.value_objects import Ciphertext

AlgorithmVersion = Literal["v1", "v2", "auto"]


def detect_version(ciphertext: Ciphertext) -> Literal["v1", "v2"]:
    """Auto-detect algorithm version from ciphertext format.

    v2 ciphertexts start with "v2|" prefix.
    Everything else is treated as v1 legacy.
    """
    if ciphertext.value.startswith("v2|"):
        return "v2"
    return "v1"


def get_crypto(version: AlgorithmVersion = "auto") -> V1LegacyAdapter | V2ModernAdapter:
    """Get the correct crypto adapter based on version.

    - "v1": Always returns V1LegacyAdapter (for decrypting legacy ciphertexts)
    - "v2": Always returns V2ModernAdapter (for new encryption)
    - "auto": Returns V2ModernAdapter (default for new encryption)
    """
    if version == "v1":
        return V1LegacyAdapter()
    return V2ModernAdapter()


def get_crypto_for_ciphertext(ciphertext: Ciphertext) -> V1LegacyAdapter | V2ModernAdapter:
    """Get the correct adapter to decrypt a specific ciphertext.

    Auto-detects version from ciphertext format.
    """
    version = detect_version(ciphertext)
    return get_crypto(version)


class CryptoFactory:
    """Stateful factory for crypto operations with profile-aware version selection."""

    def __init__(self, default_version: AlgorithmVersion = "auto"):
        self._default_version = default_version

    def get_adapter(
        self,
        version: AlgorithmVersion | None = None,
    ) -> V1LegacyAdapter | V2ModernAdapter:
        """Get adapter for explicit version or default."""
        return get_crypto(version or self._default_version)

    def encrypt(
        self,
        secret: str,
        plaintext: str,
        version: AlgorithmVersion | None = None,
    ) -> Ciphertext:
        """Encrypt with specified version or default.

        Default is always v2 for new encryption.
        """
        adapter = self.get_adapter(version or self._default_version)
        return adapter.encrypt(secret, plaintext)

    def decrypt(self, secret: str, ciphertext: Ciphertext) -> str:
        """Decrypt auto-detecting version from ciphertext."""
        adapter = get_crypto_for_ciphertext(ciphertext)
        return adapter.decrypt(secret, ciphertext)
