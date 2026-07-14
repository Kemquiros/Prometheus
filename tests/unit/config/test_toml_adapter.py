"""Tests for TOML ConfigPort adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from prometheus.config.adapter import TomlConfigAdapter
from prometheus.domain.entities import GlobalConfig, Profile


@pytest.fixture
def config_dir(tmp_path: Path) -> Path:
    """Temporary config directory."""
    return tmp_path / ".config" / "prometheus"


@pytest.fixture
def adapter(config_dir: Path) -> TomlConfigAdapter:
    """TomlConfigAdapter with temporary directory."""
    return TomlConfigAdapter(config_dir=config_dir)


class TestTomlConfigAdapterInit:
    """Tests for adapter initialization."""

    def test_creates_config_dir(self, config_dir: Path) -> None:
        TomlConfigAdapter(config_dir=config_dir)
        assert config_dir.exists()

    def test_default_config_dir(self) -> None:
        adapter = TomlConfigAdapter()
        assert adapter.config_dir.name == "prometheus"

    def test_config_file_path(self, adapter: TomlConfigAdapter) -> None:
        assert adapter.config_file.name == "config.toml"


class TestTomlConfigAdapterLoadSave:
    """Tests for load/save operations."""

    def test_load_creates_default(self, adapter: TomlConfigAdapter) -> None:
        config = adapter.load()
        assert isinstance(config, GlobalConfig)
        assert config.default_profile == "default"
        assert config.algorithm == "auto"

    def test_save_and_load(self, adapter: TomlConfigAdapter) -> None:
        config = GlobalConfig(algorithm="v2", default_profile="prod")
        adapter.save(config)
        loaded = adapter.load()
        assert loaded.algorithm == "v2"
        assert loaded.default_profile == "prod"

    def test_load_preserves_profiles(self, adapter: TomlConfigAdapter) -> None:
        profile = Profile(name="test", secret="my-secret", algorithm="v1")
        config = GlobalConfig(profiles={"test": profile})
        adapter.save(config)
        loaded = adapter.load()
        assert "test" in loaded.profiles
        assert loaded.profiles["test"].secret == "my-secret"


class TestTomlConfigAdapterProfiles:
    """Tests for profile management."""

    def test_set_and_get_profile(self, adapter: TomlConfigAdapter) -> None:
        profile = Profile(name="prod", secret="prod-secret", algorithm="v2")
        adapter.set_profile(profile)
        result = adapter.get_profile("prod")
        assert result is not None
        assert result.secret == "prod-secret"

    def test_get_nonexistent_profile(self, adapter: TomlConfigAdapter) -> None:
        assert adapter.get_profile("nope") is None

    def test_list_profiles_empty(self, adapter: TomlConfigAdapter) -> None:
        adapter.load()  # ensure config exists
        assert adapter.list_profiles() == []

    def test_list_profiles(self, adapter: TomlConfigAdapter) -> None:
        adapter.set_profile(Profile(name="a", secret="a-s", algorithm="v1"))
        adapter.set_profile(Profile(name="b", secret="b-s", algorithm="v2"))
        profiles = adapter.list_profiles()
        names = {p.name for p in profiles}
        assert names == {"a", "b"}

    def test_delete_profile(self, adapter: TomlConfigAdapter) -> None:
        adapter.set_profile(Profile(name="del", secret="d-s"))
        assert adapter.delete_profile("del") is True
        assert adapter.get_profile("del") is None

    def test_delete_nonexistent_profile(self, adapter: TomlConfigAdapter) -> None:
        adapter.load()
        assert adapter.delete_profile("nope") is False

    def test_set_profile_updates_existing(self, adapter: TomlConfigAdapter) -> None:
        adapter.set_profile(Profile(name="x", secret="old"))
        adapter.set_profile(Profile(name="x", secret="new"))
        result = adapter.get_profile("x")
        assert result is not None
        assert result.secret == "new"


class TestTomlConfigAdapterFilePersistence:
    """Tests for file-based persistence."""

    def test_config_file_created_on_save(self, adapter: TomlConfigAdapter) -> None:
        adapter.save(GlobalConfig())
        assert adapter.config_file.exists()

    def test_multiple_adapters_same_dir(self, config_dir: Path) -> None:
        a1 = TomlConfigAdapter(config_dir=config_dir)
        a1.set_profile(Profile(name="shared", secret="s1"))

        a2 = TomlConfigAdapter(config_dir=config_dir)
        result = a2.get_profile("shared")
        assert result is not None
        assert result.secret == "s1"

    def test_corrupt_file_returns_default(self, config_dir: Path) -> None:
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "config.toml").write_text("not valid toml {{{")
        adapter = TomlConfigAdapter(config_dir=config_dir)
        config = adapter.load()
        assert config.default_profile == "default"
