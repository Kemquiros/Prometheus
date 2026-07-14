# src/prometheus/domain/ports.py
"""Domain Ports (Interfaces) — Protocols for hexagonal architecture."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from prometheus.domain.entities import GlobalConfig, Profile
    from prometheus.domain.value_objects import Ciphertext


@runtime_checkable
class CryptoPort(Protocol):
    """Port for cryptographic operations — implemented by v1 and v2 adapters."""

    def encrypt(self, secret: str, plaintext: str) -> Ciphertext:
        """Encrypt plaintext with secret. Returns Ciphertext with version metadata."""
        ...

    def decrypt(self, secret: str, ciphertext: Ciphertext) -> str:
        """Decrypt ciphertext with secret. Auto-detects version."""
        ...

    @property
    def version(self) -> str:
        """Algorithm version identifier (v1|v2)."""
        ...


@runtime_checkable
class ConfigPort(Protocol):
    """Port for configuration management."""

    def load(self) -> GlobalConfig:
        """Load global configuration."""
        ...

    def save(self, config: GlobalConfig) -> None:
        """Save global configuration."""
        ...

    def get_profile(self, name: str) -> Profile | None:
        """Get profile by name."""
        ...

    def set_profile(self, profile: Profile) -> None:
        """Create or update profile."""
        ...

    def delete_profile(self, name: str) -> bool:
        """Delete profile. Returns True if existed."""
        ...

    def list_profiles(self) -> list[Profile]:
        """List all profiles."""
        ...


@runtime_checkable
class StoragePort(Protocol):
    """Port for secret storage backends."""

    def get_secret(self, name: str) -> str | None:
        """Get decrypted secret by name. None if not found."""
        ...

    def store_secret(self, name: str, plaintext: str) -> None:
        """Encrypt and store secret."""
        ...

    def delete_secret(self, name: str) -> bool:
        """Delete secret. Returns True if existed."""
        ...

    def list_secrets(self) -> list[str]:
        """List all secret names."""
        ...

    def exists(self, name: str) -> bool:
        """Check if secret exists without decrypting."""
        ...


@runtime_checkable
class OutputPort(Protocol):
    """Port for output formatting."""

    def print_result(self, data: dict[str, Any], output_format: str = "auto") -> None:
        """Print formatted result."""
        ...

    def print_error(self, message: str, details: str | None = None) -> None:
        """Print error message."""
        ...

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        ...

    def confirm(self, message: str, default: bool = False) -> bool:
        """Ask for user confirmation."""
        ...

    def prompt_secret(self, prompt: str) -> str:
        """Prompt for secret input (hidden)."""
        ...


@runtime_checkable
class EventPublisher(Protocol):
    """Port for domain event publishing."""

    def publish(self, event: Any) -> None:
        """Publish a domain event."""
        ...

    def subscribe(self, event_type: type, handler: Any) -> None:
        """Subscribe to a domain event type."""
        ...
