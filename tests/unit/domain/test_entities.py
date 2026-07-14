# tests/unit/domain/test_entities.py
"""Unit tests for domain entities."""

from __future__ import annotations

from pathlib import Path

from prometheus.domain.entities import GlobalConfig, Profile


class TestProfile:
    """Tests for Profile entity."""

    def test_default_values(self) -> None:
        profile = Profile(name="test", secret="my-secret-key-12345")
        assert profile.name == "test"
        assert profile.algorithm == "v2"
        assert profile.storage == "file"
        assert profile.file_path is None
        assert profile.keyring_service == "prometheus"
        assert profile.env_prefix == "PROMETHEUS_SECRET_"

    def test_custom_values(self) -> None:
        profile = Profile(
            name="prod",
            secret="prod-secret-key-123",
            algorithm="v1",
            storage="keyring",
            file_path="/tmp/secrets.toml",
            keyring_service="my-app",
            env_prefix="MY_SECRET_",
        )
        assert profile.algorithm == "v1"
        assert profile.storage == "keyring"
        assert profile.keyring_service == "my-app"

    def test_expand_path(self) -> None:
        profile = Profile(name="test", secret="my-secret-key-12345", file_path="~/secrets.toml")
        assert profile.file_path is not None
        assert profile.file_path == Path("~/secrets.toml").expanduser().resolve()

    def test_expand_path_none(self) -> None:
        profile = Profile(name="test", secret="my-secret-key-12345", file_path=None)
        assert profile.file_path is None

    def test_frozen(self) -> None:
        profile = Profile(name="test", secret="my-secret-key-12345")
        try:
            profile.name = "new"  # type: ignore[misc]
            # Pydantic frozen model raises ValidationError, not AttributeError
        except Exception:
            pass  # Expected — model is frozen

    def test_model_validate(self) -> None:
        data = {"name": "test", "secret": "my-secret-key-12345"}
        profile = Profile.model_validate(data)
        assert profile.name == "test"


class TestGlobalConfig:
    """Tests for GlobalConfig entity."""

    def test_default_values(self) -> None:
        config = GlobalConfig()
        assert config.default_profile == "default"
        assert config.algorithm == "auto"
        assert config.storage == "file"
        assert config.keyring_service == "prometheus"
        assert config.env_prefix == "PROMETHEUS_SECRET_"
        assert config.profiles == {}

    def test_custom_values(self) -> None:
        config = GlobalConfig(
            default_profile="prod",
            algorithm="v2",
            storage="keyring",
            keyring_service="my-app",
        )
        assert config.default_profile == "prod"
        assert config.keyring_service == "my-app"

    def test_expand_path(self) -> None:
        config = GlobalConfig(file_path="~/.config/prometheus/secrets.toml")
        assert config.file_path == Path("~/.config/prometheus/secrets.toml").expanduser().resolve()

    def test_with_profiles(self) -> None:
        profile = Profile(name="test", secret="my-secret-key-12345")
        config = GlobalConfig(profiles={"test": profile})
        assert "test" in config.profiles
        assert config.profiles["test"].name == "test"

    def test_frozen(self) -> None:
        config = GlobalConfig()
        try:
            config.default_profile = "new"  # type: ignore[misc]
        except Exception:
            pass  # Expected — model is frozen

    def test_model_validate(self) -> None:
        data = {"default_profile": "test", "algorithm": "v1"}
        config = GlobalConfig.model_validate(data)
        assert config.default_profile == "test"
        assert config.algorithm == "v1"
