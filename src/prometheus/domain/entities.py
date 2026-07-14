"""Domain Entities."""

from dataclasses import field
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, field_validator

AlgorithmVersion = Literal["v1", "v2", "auto"]
StorageBackend = Literal["file", "keyring", "env"]


class Profile(BaseModel):
    """Configuration profile for encryption operations."""

    name: str
    secret: str = Field(..., description="Encryption secret (or reference)")
    algorithm: AlgorithmVersion = "v2"
    storage: StorageBackend = "file"
    file_path: Path | None = None
    keyring_service: str = "prometheus"
    env_prefix: str = "PROMETHEUS_SECRET_"

    @field_validator("file_path", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path | None) -> Path | None:
        if v is None:
            return None
        return Path(v).expanduser().resolve()

    model_config = {
        "frozen": True,
        "validate_assignment": True,
    }


class GlobalConfig(BaseModel):
    """Global application configuration."""

    default_profile: str = "default"
    algorithm: AlgorithmVersion = "auto"
    storage: StorageBackend = "file"
    file_path: Path = Path("~/.config/prometheus/secrets.toml").expanduser()
    keyring_service: str = "prometheus"
    env_prefix: str = "PROMETHEUS_SECRET_"

    profiles: dict[str, Profile] = field(default_factory=dict)

    @field_validator("file_path", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser().resolve()

    model_config = {
        "frozen": True,
        "validate_assignment": True,
    }
