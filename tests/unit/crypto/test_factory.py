# tests/unit/crypto/test_factory.py
"""Tests for CryptoFactory — auto-detect and adapter selection."""

from __future__ import annotations

import pytest

from prometheus.cipher.factory import CryptoFactory, detect_version, get_crypto, get_crypto_for_ciphertext
from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.cipher.v2_modern.adapter import V2ModernAdapter
from prometheus.domain.value_objects import Ciphertext


class TestDetectVersion:
    """Version auto-detection tests."""

    def test_v1_ciphertext_detected(self) -> None:
        ct = Ciphertext("g/u55oK9j97hrpeX+w==")
        assert detect_version(ct) == "v1"

    def test_v2_ciphertext_detected(self) -> None:
        adapter = V2ModernAdapter()
        ct = adapter.encrypt("secret-12345", "password")
        assert detect_version(ct) == "v2"

    def test_empty_ciphertext_is_v1(self) -> None:
        ct = Ciphertext("some-data")
        assert detect_version(ct) == "v1"


class TestGetCrypto:
    """Adapter factory tests."""

    def test_get_v1(self) -> None:
        adapter = get_crypto("v1")
        assert isinstance(adapter, V1LegacyAdapter)
        assert adapter.version == "v1"

    def test_get_v2(self) -> None:
        adapter = get_crypto("v2")
        assert isinstance(adapter, V2ModernAdapter)
        assert adapter.version == "v2"

    def test_get_auto_returns_v2(self) -> None:
        adapter = get_crypto("auto")
        assert isinstance(adapter, V2ModernAdapter)
        assert adapter.version == "v2"

    def test_get_crypto_for_ciphertext_v1(self) -> None:
        ct = Ciphertext("g/u55oK9j97hrpeX+w==")
        adapter = get_crypto_for_ciphertext(ct)
        assert isinstance(adapter, V1LegacyAdapter)

    def test_get_crypto_for_ciphertext_v2(self) -> None:
        adapter = V2ModernAdapter()
        ct = adapter.encrypt("secret-12345", "password")
        result_adapter = get_crypto_for_ciphertext(ct)
        assert isinstance(result_adapter, V2ModernAdapter)


class TestCryptoFactory:
    """Stateful factory tests."""

    def test_default_version_is_v2(self) -> None:
        factory = CryptoFactory()
        adapter = factory.get_adapter()
        assert isinstance(adapter, V2ModernAdapter)

    def test_encrypt_with_v2(self) -> None:
        factory = CryptoFactory(default_version="v2")
        ct = factory.encrypt("secret-12345", "password")
        assert ct.value.startswith("v2|")

    def test_decrypt_auto_detects_v1(self) -> None:
        factory = CryptoFactory()
        v1_adapter = V1LegacyAdapter()
        ct = v1_adapter.encrypt("secret-12345", "password")
        result = factory.decrypt("secret-12345", ct)
        assert result == "password"

    def test_decrypt_auto_detects_v2(self) -> None:
        factory = CryptoFactory()
        ct = factory.encrypt("secret-12345", "password")
        result = factory.decrypt("secret-12345", ct)
        assert result == "password"