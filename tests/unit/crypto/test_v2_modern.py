# tests/unit/crypto/test_v2_modern.py
"""Unit tests for V2ModernAdapter — property-based + deterministic tests."""

from __future__ import annotations

import base64

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from prometheus.cipher.v2_modern.adapter import V2ModernAdapter
from prometheus.domain.value_objects import Ciphertext


class TestV2ModernBasic:
    """Basic functionality tests for v2 modern adapter."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V2ModernAdapter()

    def test_version_property(self) -> None:
        assert self.adapter.version == "v2"

    def test_encrypt_returns_v2_prefix(self) -> None:
        ct = self.adapter.encrypt("secret-key-12345", "password")
        assert ct.value.startswith("v2|")

    def test_ciphertext_has_five_components(self) -> None:
        ct = self.adapter.encrypt("secret-key-12345", "password")
        parts = ct.value.split("|")
        assert len(parts) == 5

    def test_ciphertext_components_are_valid_base64(self) -> None:
        ct = self.adapter.encrypt("secret-key-12345", "password")
        parts = ct.value.split("|")
        for part in parts[1:]:  # skip version prefix
            decoded = base64.b64decode(part)
            assert len(decoded) > 0

    def test_roundtrip_basic(self) -> None:
        secret = "roundtrip-test-key-12345"
        plaintext = "roundtrip-test-password"
        ct = self.adapter.encrypt(secret, plaintext)
        result = self.adapter.decrypt(secret, ct)
        assert result == plaintext

    def test_nondeterministic_encryption(self) -> None:
        """Each encryption must produce different ciphertext (random salt/nonce)."""
        secret = "nondeterministic-test"
        plaintext = "same-password"
        ct1 = self.adapter.encrypt(secret, plaintext)
        ct2 = self.adapter.encrypt(secret, plaintext)
        assert ct1.value != ct2.value

    def test_different_secrets_different_ciphertexts(self) -> None:
        ct1 = self.adapter.encrypt("secret-one-12345", "password")
        ct2 = self.adapter.encrypt("secret-two-12345", "password")
        assert ct1.value != ct2.value

    def test_different_plaintexts_different_ciphertexts(self) -> None:
        ct1 = self.adapter.encrypt("secret-12345", "password-one")
        ct2 = self.adapter.encrypt("secret-12345", "password-two")
        assert ct1.value != ct2.value


class TestV2ModernSecurity:
    """Security property tests for v2 modern adapter."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V2ModernAdapter()

    def test_ciphertext_not_plaintext(self) -> None:
        ct = self.adapter.encrypt("secret-12345", "password")
        assert ct.value != "password"

    def test_wrong_secret_fails_decryption(self) -> None:
        ct = self.adapter.encrypt("correct-secret-123", "password")
        with pytest.raises(Exception):  # AEAD verification failure
            self.adapter.decrypt("wrong-secret-1234", ct)

    def test_tampered_ciphertext_fails(self) -> None:
        """Tampered ciphertext must fail Poly1305 MAC verification."""
        ct = self.adapter.encrypt("secret-12345", "password")
        parts = ct.value.split("|")
        # Tamper with ciphertext
        ct_bytes = base64.b64decode(parts[3])
        tampered = bytes([ct_bytes[0] ^ 0xFF]) + ct_bytes[1:]
        parts[3] = base64.b64encode(tampered).decode("ascii")
        tampered_ct = Ciphertext("|".join(parts))
        with pytest.raises(Exception):
            self.adapter.decrypt("secret-12345", tampered_ct)

    def test_salt_is_random_per_encryption(self) -> None:
        """Each encryption must use a different random salt."""
        ct1 = self.adapter.encrypt("secret-12345", "password")
        ct2 = self.adapter.encrypt("secret-12345", "password")
        salt1 = base64.b64decode(ct1.components["salt"])
        salt2 = base64.b64decode(ct2.components["salt"])
        assert salt1 != salt2

    def test_nonce_is_random_per_encryption(self) -> None:
        """Each encryption must use a different random nonce."""
        ct1 = self.adapter.encrypt("secret-12345", "password")
        ct2 = self.adapter.encrypt("secret-12345", "password")
        nonce1 = base64.b64decode(ct1.components["nonce"])
        nonce2 = base64.b64decode(ct2.components["nonce"])
        assert nonce1 != nonce2


class TestV2ModernUnicode:
    """Unicode support tests."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V2ModernAdapter()

    def test_spanish_unicode(self) -> None:
        secret = "unicode-key-12345"
        plaintext = "contraseña-secreta-áéíóú-ñ"
        ct = self.adapter.encrypt(secret, plaintext)
        assert self.adapter.decrypt(secret, ct) == plaintext

    def test_emoji(self) -> None:
        secret = "emoji-key-123456"
        plaintext = "🔐🔒🔑"
        ct = self.adapter.encrypt(secret, plaintext)
        assert self.adapter.decrypt(secret, ct) == plaintext

    def test_cjk_characters(self) -> None:
        secret = "cjk-key-1234567"
        plaintext = "中文日本語한국어"
        ct = self.adapter.encrypt(secret, plaintext)
        assert self.adapter.decrypt(secret, ct) == plaintext


class TestV2ModernEdgeCases:
    """Edge case tests."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V2ModernAdapter()

    def test_empty_plaintext(self) -> None:
        secret = "empty-test-key-12345"
        ct = self.adapter.encrypt(secret, "")
        result = self.adapter.decrypt(secret, ct)
        assert result == ""

    def test_long_plaintext(self) -> None:
        secret = "long-test-key-12345"
        plaintext = "x" * 10000
        ct = self.adapter.encrypt(secret, plaintext)
        result = self.adapter.decrypt(secret, ct)
        assert result == plaintext

    def test_binary_like_content(self) -> None:
        secret = "binary-key-12345"
        plaintext = "\x00\x01\x02\x03\xff\xfe\xfd"
        ct = self.adapter.encrypt(secret, plaintext)
        result = self.adapter.decrypt(secret, ct)
        assert result == plaintext

    def test_newlines_and_tabs(self) -> None:
        secret = "whitespace-key-1234"
        plaintext = "line1\nline2\ttab\rcarriage"
        ct = self.adapter.encrypt(secret, plaintext)
        result = self.adapter.decrypt(secret, ct)
        assert result == plaintext


class TestV2ModernPropertyBased:
    """Property-based tests using Hypothesis."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V2ModernAdapter()

    @given(
        plaintext=st.text(min_size=0, max_size=500),
        secret=st.from_regex(r"[a-zA-Z0-9]{8,50}", fullmatch=True),
    )
    @settings(max_examples=30, deadline=None)
    def test_roundtrip_property(self, plaintext: str, secret: str) -> None:
        ct = self.adapter.encrypt(secret, plaintext)
        result = self.adapter.decrypt(secret, ct)
        assert result == plaintext
