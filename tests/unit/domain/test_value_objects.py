# tests/unit/domain/test_value_objects.py
"""Unit tests for domain value objects."""

from __future__ import annotations

import pytest

from prometheus.domain.value_objects import (
    V2_COMPONENT_COUNT,
    Ciphertext,
    CiphertextError,
    Plaintext,
    SecretKey,
    SecretKeyError,
)


class TestSecretKey:
    """Tests for SecretKey value object."""

    def test_valid_key(self) -> None:
        key = SecretKey("my-secret-key-12345")
        assert key.value == "my-secret-key-12345"

    def test_str_redacted(self) -> None:
        key = SecretKey("my-secret-key-12345")
        assert str(key) == "***REDACTED***"

    def test_repr(self) -> None:
        key = SecretKey("my-secret-key-12345")
        assert repr(key) == "SecretKey(***REDACTED***)"

    def test_empty_key_raises(self) -> None:
        with pytest.raises(SecretKeyError, match="cannot be empty"):
            SecretKey("")

    def test_whitespace_only_key_raises(self) -> None:
        with pytest.raises(SecretKeyError, match="cannot be empty"):
            SecretKey("   ")

    def test_short_key_raises(self) -> None:
        with pytest.raises(SecretKeyError, match="at least 8 characters"):
            SecretKey("short")

    def test_minimum_length_key(self) -> None:
        key = SecretKey("12345678")
        assert key.value == "12345678"

    def test_frozen(self) -> None:
        key = SecretKey("my-secret-key-12345")
        with pytest.raises(AttributeError):
            key.value = "new-value"  # type: ignore[misc]


class TestPlaintext:
    """Tests for Plaintext value object."""

    def test_valid_plaintext(self) -> None:
        pt = Plaintext("hello world")
        assert pt.value == "hello world"

    def test_empty_string_is_valid(self) -> None:
        pt = Plaintext("")
        assert pt.value == ""

    def test_str_redacted(self) -> None:
        pt = Plaintext("hello world")
        assert str(pt) == "***REDACTED***"

    def test_repr(self) -> None:
        pt = Plaintext("hello world")
        assert repr(pt) == "Plaintext(***REDACTED***)"

    def test_frozen(self) -> None:
        pt = Plaintext("hello")
        with pytest.raises(AttributeError):
            pt.value = "new"  # type: ignore[misc]


class TestCiphertext:
    """Tests for Ciphertext value object."""

    def test_valid_v1(self) -> None:
        ct = Ciphertext("abc123")
        assert ct.value == "abc123"
        assert ct.version == "v1"
        assert ct.is_v2 is False

    def test_valid_v2(self) -> None:
        ct = Ciphertext("v2|salt|nonce|ct|tag")
        assert ct.version == "v2"
        assert ct.is_v2 is True

    def test_empty_raises(self) -> None:
        with pytest.raises(CiphertextError, match="cannot be empty"):
            Ciphertext("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(CiphertextError, match="cannot be empty"):
            Ciphertext("   ")

    def test_str_returns_value(self) -> None:
        ct = Ciphertext("abc123")
        assert str(ct) == "abc123"

    def test_from_v1_legacy(self) -> None:
        ct = Ciphertext.from_v1_legacy("abc123")
        assert ct.value == "abc123"
        assert ct.version == "v1"

    def test_from_v2_modern(self) -> None:
        ct = Ciphertext.from_v2_modern("salt", "nonce", "ct", "tag")
        assert ct.value == "v2|salt|nonce|ct|tag"
        assert ct.version == "v2"

    def test_components_v1(self) -> None:
        ct = Ciphertext("abc123")
        assert ct.components == {"raw": "abc123"}

    def test_components_v2(self) -> None:
        ct = Ciphertext("v2|salt|nonce|ct|tag")
        components = ct.components
        assert components["version"] == "v2"
        assert components["salt"] == "salt"
        assert components["nonce"] == "nonce"
        assert components["ciphertext"] == "ct"
        assert components["tag"] == "tag"

    def test_components_v2_invalid_format(self) -> None:
        ct = Ciphertext("v2|only|three")
        with pytest.raises(CiphertextError, match="Invalid v2 ciphertext format"):
            _ = ct.components

    def test_frozen(self) -> None:
        ct = Ciphertext("abc")
        with pytest.raises(AttributeError):
            ct.value = "new"  # type: ignore[misc]


class TestConstants:
    """Tests for module constants."""

    def test_v2_component_count(self) -> None:
        assert V2_COMPONENT_COUNT == 5
