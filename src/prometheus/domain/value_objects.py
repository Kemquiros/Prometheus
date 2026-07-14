"""Domain Value Objects."""

from __future__ import annotations

from dataclasses import dataclass

from typing_extensions import Self

# Constants for validation
MIN_SECRET_KEY_LENGTH = 8
V2_COMPONENT_COUNT = 5


class SecretKeyError(ValueError):
    """Raised when secret key is invalid."""


class PlaintextError(ValueError):
    """Raised when plaintext is invalid."""


class CiphertextError(ValueError):
    """Raised when ciphertext is invalid."""


@dataclass(frozen=True, slots=True)
class SecretKey:
    """Secret key for encryption/decryption."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            msg = "Secret key cannot be empty"
            raise SecretKeyError(msg)
        if len(self.value) < MIN_SECRET_KEY_LENGTH:
            msg = f"Secret key must be at least {MIN_SECRET_KEY_LENGTH} characters"
            raise SecretKeyError(msg)

    def __str__(self) -> str:
        return "***REDACTED***"

    def __repr__(self) -> str:
        return f"SecretKey({self})"


@dataclass(frozen=True, slots=True)
class Plaintext:
    """Plaintext data to encrypt."""

    value: str

    def __post_init__(self) -> None:
        if self.value is None:
            msg = "Plaintext cannot be None"
            raise PlaintextError(msg)

    def __str__(self) -> str:
        return "***REDACTED***"

    def __repr__(self) -> str:
        return f"Plaintext({self})"


@dataclass(frozen=True, slots=True)
class Ciphertext:
    """Encrypted ciphertext with version metadata."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            msg = "Ciphertext cannot be empty"
            raise CiphertextError(msg)

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_v1_legacy(cls, b64_ciphertext: str) -> Self:
        """Create from v1 legacy format (raw base64)."""
        return cls(b64_ciphertext)

    @classmethod
    def from_v2_modern(cls, salt_b64: str, nonce_b64: str, ct_b64: str, tag_b64: str) -> Self:
        """Create from v2 modern format."""
        return cls(f"v2|{salt_b64}|{nonce_b64}|{ct_b64}|{tag_b64}")

    @property
    def version(self) -> str:
        """Extract version prefix if present."""
        if self.value.startswith("v2|"):
            return "v2"
        return "v1"

    @property
    def is_v2(self) -> bool:
        return self.value.startswith("v2|")

    @property
    def components(self) -> dict[str, str]:
        """Parse v2 components."""
        if not self.is_v2:
            return {"raw": self.value}
        parts = self.value.split("|")
        if len(parts) != V2_COMPONENT_COUNT:
            msg = f"Invalid v2 ciphertext format: {self.value}"
            raise CiphertextError(msg)
        return {
            "version": parts[0],
            "salt": parts[1],
            "nonce": parts[2],
            "ciphertext": parts[3],
            "tag": parts[4],
        }
