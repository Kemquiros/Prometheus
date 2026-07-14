"""File-based StoragePort adapter."""

from __future__ import annotations

from pathlib import Path

import tomli_w
import tomllib
from platformdirs import user_data_dir

APP_NAME = "prometheus"
DEFAULT_STORAGE_FILE = "secrets.toml"


class FileStorageAdapter:
    """StoragePort implementation using encrypted TOML files."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        if storage_dir is None:
            storage_dir = Path(user_data_dir(APP_NAME))
        self.storage_dir = storage_dir
        self.storage_file = storage_dir / DEFAULT_STORAGE_FILE
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._secrets: dict[str, str] | None = None

    def _load(self) -> dict[str, str]:
        """Load secrets from file."""
        if self._secrets is not None:
            return self._secrets

        if not self.storage_file.exists():
            self._secrets = {}
            return self._secrets

        try:
            raw = self.storage_file.read_bytes()
            data = tomllib.loads(raw.decode("utf-8"))
            self._secrets = dict(data.get("secrets", {}))
        except Exception:
            self._secrets = {}

        return self._secrets

    def _save(self) -> None:
        """Save secrets to file."""
        data: dict[str, dict[str, str]] = {"secrets": self._secrets or {}}
        with self.storage_file.open("wb") as f:
            tomli_w.dump(data, f)

    def get_secret(self, name: str) -> str | None:
        """Get secret by name. None if not found."""
        secrets = self._load()
        return secrets.get(name)

    def store_secret(self, name: str, plaintext: str) -> None:
        """Store secret."""
        secrets = self._load()
        secrets[name] = plaintext
        self._save()

    def delete_secret(self, name: str) -> bool:
        """Delete secret. Returns True if existed."""
        secrets = self._load()
        if name not in secrets:
            return False
        del secrets[name]
        self._save()
        return True

    def list_secrets(self) -> list[str]:
        """List all secret names."""
        secrets = self._load()
        return list(secrets.keys())

    def exists(self, name: str) -> bool:
        """Check if secret exists."""
        secrets = self._load()
        return name in secrets
