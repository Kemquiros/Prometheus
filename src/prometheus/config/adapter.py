"""TOML-based ConfigPort adapter."""

from __future__ import annotations

from pathlib import Path

import tomli_w
import tomllib
from platformdirs import user_config_dir

from prometheus.domain.entities import GlobalConfig, Profile
from prometheus.domain.ports import ConfigPort

APP_NAME = "prometheus"
DEFAULT_CONFIG_FILE = "config.toml"


class TomlConfigAdapter(ConfigPort):
    """ConfigPort implementation using TOML files."""

    def __init__(self, config_dir: Path | None = None) -> None:
        if config_dir is None:
            config_dir = Path(user_config_dir(APP_NAME))
        self.config_dir = config_dir
        self.config_file = config_dir / DEFAULT_CONFIG_FILE
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config: GlobalConfig | None = None

    def load(self) -> GlobalConfig:
        """Load global configuration from TOML file."""
        if self._config is not None:
            return self._config

        if not self.config_file.exists():
            self._config = GlobalConfig()
            return self._config

        try:
            raw = self.config_file.read_bytes()
            data = tomllib.loads(raw.decode("utf-8"))
            profiles_raw = data.pop("profiles", {})
            profiles = {}
            for name, pdata in profiles_raw.items():
                profiles[name] = Profile(name=name, **pdata)
            self._config = GlobalConfig(**data, profiles=profiles)
        except Exception:
            self._config = GlobalConfig()

        return self._config

    def save(self, config: GlobalConfig) -> None:
        """Save global configuration to TOML file."""
        data: dict[str, object] = {
            "default_profile": config.default_profile,
            "algorithm": config.algorithm,
            "storage": config.storage,
            "file_path": str(config.file_path),
            "keyring_service": config.keyring_service,
            "env_prefix": config.env_prefix,
        }

        profiles_data: dict[str, dict[str, object]] = {}
        for name, profile in config.profiles.items():
            pdata: dict[str, object] = {
                "secret": profile.secret,
                "algorithm": profile.algorithm,
                "storage": profile.storage,
                "keyring_service": profile.keyring_service,
                "env_prefix": profile.env_prefix,
            }
            if profile.file_path is not None:
                pdata["file_path"] = str(profile.file_path)
            profiles_data[name] = pdata
        if profiles_data:
            data["profiles"] = profiles_data

        with self.config_file.open("wb") as f:
            tomli_w.dump(data, f)

        self._config = config

    def get_profile(self, name: str) -> Profile | None:
        """Get profile by name."""
        config = self.load()
        return config.profiles.get(name)

    def set_profile(self, profile: Profile) -> None:
        """Create or update profile."""
        config = self.load()
        profiles = dict(config.profiles)
        profiles[profile.name] = profile
        new_config = config.model_copy(update={"profiles": profiles})
        self.save(new_config)

    def delete_profile(self, name: str) -> bool:
        """Delete profile. Returns True if existed."""
        config = self.load()
        if name not in config.profiles:
            return False
        profiles = dict(config.profiles)
        del profiles[name]
        new_config = config.model_copy(update={"profiles": profiles})
        self.save(new_config)
        return True

    def list_profiles(self) -> list[Profile]:
        """List all profiles."""
        config = self.load()
        return list(config.profiles.values())
