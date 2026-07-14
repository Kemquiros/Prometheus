"""Domain Events for event-driven architecture."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """Base domain event."""

    event_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: str = ""


@dataclass(frozen=True, slots=True)
class SecretEncrypted(DomainEvent):
    """Event fired when a secret is encrypted."""

    secret_name: str = ""
    algorithm_version: str = "v2"
    profile_name: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SecretDecrypted(DomainEvent):
    """Event fired when a secret is decrypted."""

    secret_name: str = ""
    algorithm_version: str = "v2"
    profile_name: str = "default"


@dataclass(frozen=True, slots=True)
class MigrationCompleted(DomainEvent):
    """Event fired when v1 to v2 migration completes."""

    total_secrets: int = 0
    migrated: int = 0
    failed: int = 0
    skipped: int = 0
    dry_run: bool = False
    details: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class KeyRotated(DomainEvent):
    """Event fired when encryption key is rotated."""

    profile_name: str = ""
    old_algorithm: str = ""
    new_algorithm: str = ""
    secrets_reencrypted: int = 0
