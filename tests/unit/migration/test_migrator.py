"""Tests for v1→v2 migration."""

from __future__ import annotations

import pytest

from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.cipher.v2_modern.adapter import V2ModernAdapter
from prometheus.migration.migrator import MigrationResult, migrate_ciphertext


@pytest.fixture
def v1_adapter() -> V1LegacyAdapter:
    return V1LegacyAdapter()


@pytest.fixture
def v2_adapter() -> V2ModernAdapter:
    return V2ModernAdapter()


class TestMigrateCiphertext:
    """Tests for migrate_ciphertext function."""

    def test_migrate_v1_to_v2(self, v1_adapter: V1LegacyAdapter) -> None:
        secret = "my-secret-key"
        plaintext = "password123"
        v1_ct = v1_adapter.encrypt(secret, plaintext)

        result = migrate_ciphertext(secret, v1_ct)

        assert result.success is True
        assert result.old_version == "v1"
        assert result.new_version == "v2"
        assert result.plaintext == plaintext

    def test_migrate_already_v2(self, v2_adapter: V2ModernAdapter) -> None:
        secret = "my-secret-key"
        plaintext = "password123"
        v2_ct = v2_adapter.encrypt(secret, plaintext)

        result = migrate_ciphertext(secret, v2_ct)

        assert result.success is True
        assert result.old_version == "v2"
        assert result.new_version == "v2"
        assert result.plaintext == plaintext

    def test_migrate_wrong_secret_produces_garbage(self, v1_adapter: V1LegacyAdapter) -> None:
        secret = "correct-secret"
        plaintext = "password123"
        v1_ct = v1_adapter.encrypt(secret, plaintext)

        result = migrate_ciphertext("wrong-secret", v1_ct)

        assert result.success is True
        assert result.plaintext != plaintext
        assert result.new_version == "v2"

    def test_migrate_preserves_plaintext(self, v1_adapter: V1LegacyAdapter) -> None:
        secret = "key"
        plaintext = "super-secret-password-123!@#$%"
        v1_ct = v1_adapter.encrypt(secret, plaintext)

        result = migrate_ciphertext(secret, v1_ct)

        assert result.success is True
        assert result.plaintext == plaintext

    def test_migrate_special_characters(self, v1_adapter: V1LegacyAdapter) -> None:
        secret = "key"
        plaintext = "p@$$w0rd!#%^&*()"
        v1_ct = v1_adapter.encrypt(secret, plaintext)

        result = migrate_ciphertext(secret, v1_ct)

        assert result.success is True
        assert result.plaintext == plaintext

    def test_migrate_long_plaintext(self, v1_adapter: V1LegacyAdapter) -> None:
        secret = "key"
        plaintext = "x" * 10000
        v1_ct = v1_adapter.encrypt(secret, plaintext)

        result = migrate_ciphertext(secret, v1_ct)

        assert result.success is True
        assert result.plaintext == plaintext


class TestMigrationResult:
    """Tests for MigrationResult dataclass."""

    def test_success_result(self) -> None:
        result = MigrationResult(
            old_ciphertext="old",
            new_ciphertext="new",
            old_version="v1",
            new_version="v2",
            plaintext="secret",
            success=True,
        )
        assert result.success is True
        assert result.error is None

    def test_failure_result(self) -> None:
        result = MigrationResult(
            old_ciphertext="old",
            new_ciphertext="",
            old_version="v1",
            new_version="v2",
            plaintext="",
            success=False,
            error="Decryption failed",
        )
        assert result.success is False
        assert result.error == "Decryption failed"
