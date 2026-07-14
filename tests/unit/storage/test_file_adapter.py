"""Tests for file-based StoragePort adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from prometheus.storage.adapter import FileStorageAdapter


@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    """Temporary storage directory."""
    return tmp_path / "secrets"


@pytest.fixture
def storage(storage_dir: Path) -> FileStorageAdapter:
    """FileStorageAdapter with temporary directory."""
    return FileStorageAdapter(storage_dir=storage_dir)


class TestFileStorageAdapterInit:
    """Tests for adapter initialization."""

    def test_creates_storage_dir(self, storage_dir: Path) -> None:
        FileStorageAdapter(storage_dir=storage_dir)
        assert storage_dir.exists()

    def test_default_storage_dir(self) -> None:
        adapter = FileStorageAdapter()
        assert adapter.storage_dir.exists()
        assert adapter.storage_dir.name == "prometheus"

    def test_storage_file_path(self, storage: FileStorageAdapter) -> None:
        assert storage.storage_file.name == "secrets.toml"


class TestFileStorageAdapterCRUD:
    """Tests for CRUD operations."""

    def test_store_and_get(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("my-api-key", "sk-12345")
        result = storage.get_secret("my-api-key")
        assert result == "sk-12345"

    def test_get_nonexistent(self, storage: FileStorageAdapter) -> None:
        assert storage.get_secret("nope") is None

    def test_exists(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("exists", "val")
        assert storage.exists("exists") is True
        assert storage.exists("nope") is False

    def test_list_secrets_empty(self, storage: FileStorageAdapter) -> None:
        assert storage.list_secrets() == []

    def test_list_secrets(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("a", "va")
        storage.store_secret("b", "vb")
        names = storage.list_secrets()
        assert sorted(names) == ["a", "b"]

    def test_delete_secret(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("del", "val")
        assert storage.delete_secret("del") is True
        assert storage.get_secret("del") is None

    def test_delete_nonexistent(self, storage: FileStorageAdapter) -> None:
        assert storage.delete_secret("nope") is False

    def test_overwrite_secret(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("key", "old")
        storage.store_secret("key", "new")
        assert storage.get_secret("key") == "new"


class TestFileStorageAdapterPersistence:
    """Tests for file-based persistence."""

    def test_file_created_on_store(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("x", "y")
        assert storage.storage_file.exists()

    def test_multiple_adapters_same_dir(self, storage_dir: Path) -> None:
        a1 = FileStorageAdapter(storage_dir=storage_dir)
        a1.store_secret("shared", "s1")

        a2 = FileStorageAdapter(storage_dir=storage_dir)
        assert a2.get_secret("shared") == "s1"

    def test_corrupt_file_returns_empty(self, storage_dir: Path) -> None:
        storage_dir.mkdir(parents=True, exist_ok=True)
        (storage_dir / "secrets.toml").write_text("not valid {{{")
        adapter = FileStorageAdapter(storage_dir=storage_dir)
        assert adapter.list_secrets() == []
        assert adapter.get_secret("any") is None


class TestFileStorageAdapterSecretIsolation:
    """Tests for secret isolation between names."""

    def test_different_names_independent(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("api-key", "key-123")
        storage.store_secret("db-pass", "pass-456")
        assert storage.get_secret("api-key") == "key-123"
        assert storage.get_secret("db-pass") == "pass-456"

    def test_empty_value(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("empty", "")
        assert storage.get_secret("empty") == ""

    def test_special_characters(self, storage: FileStorageAdapter) -> None:
        storage.store_secret("special", "p@$$w0rd!#%^&*()")
        assert storage.get_secret("special") == "p@$$w0rd!#%^&*()"

    def test_long_value(self, storage: FileStorageAdapter) -> None:
        long_val = "x" * 10000
        storage.store_secret("long", long_val)
        assert storage.get_secret("long") == long_val
