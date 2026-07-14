# tests/contract/test_crypto_port.py
"""Contract tests for CryptoPort — ALL adapters must pass these tests."""

from __future__ import annotations

from typing import Any

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from prometheus.domain.value_objects import Ciphertext

# This test class validates that any CryptoPort implementation
# satisfies the protocol contract. Add new adapters here.


class TestCryptoPortContract:
    """Contract tests that ALL CryptoPort implementations must satisfy."""

    def test_adapter_has_version_property(self, adapter: Any) -> None:
        """Every adapter must expose a `version` property."""
        assert hasattr(adapter, "version")
        assert adapter.version in ("v1", "v2")

    def test_encrypt_returns_ciphertext(self, adapter: Any, sample_secret: str, sample_plaintext: str) -> None:
        """encrypt() must return a Ciphertext value object."""
        result = adapter.encrypt(sample_secret, sample_plaintext)
        assert isinstance(result, Ciphertext)
        assert result.value  # not empty

    def test_decrypt_returns_string(self, adapter: Any, sample_secret: str, sample_plaintext: str) -> None:
        """decrypt() must return a string (plaintext)."""
        ciphertext = adapter.encrypt(sample_secret, sample_plaintext)
        result = adapter.decrypt(sample_secret, ciphertext)
        assert isinstance(result, str)

    def test_roundtrip_identity(self, adapter: Any, sample_secret: str, sample_plaintext: str) -> None:
        """decrypt(encrypt(x)) must equal x for all x."""
        ciphertext = adapter.encrypt(sample_secret, sample_plaintext)
        decrypted = adapter.decrypt(sample_secret, ciphertext)
        assert decrypted == sample_plaintext

    def test_different_plaintexts_different_ciphertexts(self, adapter: Any, sample_secret: str) -> None:
        """Different plaintexts must produce different ciphertexts."""
        ct1 = adapter.encrypt(sample_secret, "password-one")
        ct2 = adapter.encrypt(sample_secret, "password-two")
        assert ct1.value != ct2.value

    def test_different_secrets_different_ciphertexts(self, adapter: Any, sample_plaintext: str) -> None:
        """Different secrets must produce different ciphertexts."""
        ct1 = adapter.encrypt("secret-alpha", sample_plaintext)
        ct2 = adapter.encrypt("secret-beta", sample_plaintext)
        assert ct1.value != ct2.value

    def test_unicode_roundtrip(self, adapter: Any) -> None:
        """Unicode characters must survive roundtrip (v2 only — v1 is latin1-limited)."""
        if adapter.version == "v1":
            pytest.skip("v1 legacy uses latin1 encoding — full Unicode not supported")
        plaintext = "contraseña-secreta-áéíóú-ñ-Ü-中文-日本語"
        secret = "unicode-test-key-12345"
        ciphertext = adapter.encrypt(secret, plaintext)
        decrypted = adapter.decrypt(secret, ciphertext)
        assert decrypted == plaintext

    def test_empty_string_roundtrip(self, adapter: Any) -> None:
        """Empty plaintext must survive roundtrip (v2 only — v1 produces empty ciphertext)."""
        if adapter.version == "v1":
            pytest.skip("v1 legacy cannot encrypt empty strings")
        secret = "empty-test-key-12345"
        ciphertext = adapter.encrypt(secret, "")
        decrypted = adapter.decrypt(secret, ciphertext)
        assert decrypted == ""

    def test_special_characters_roundtrip(self, adapter: Any) -> None:
        """Special characters must survive roundtrip."""
        plaintext = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        secret = "special-chars-key-12345"
        ciphertext = adapter.encrypt(secret, plaintext)
        decrypted = adapter.decrypt(secret, ciphertext)
        assert decrypted == plaintext

    @given(
        plaintext=st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=("Cs",))),
        secret=st.from_regex(r"[a-zA-Z0-9]{8,50}", fullmatch=True),
    )
    @settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_based_roundtrip(self, adapter: Any, plaintext: str, secret: str) -> None:
        """Property-based: roundtrip must hold for arbitrary non-empty inputs."""
        if adapter.version == "v1":
            pytest.skip("v1 legacy has limited character support — property tests are v2-only")
        ciphertext = adapter.encrypt(secret, plaintext)
        decrypted = adapter.decrypt(secret, ciphertext)
        assert decrypted == plaintext


@pytest.fixture(params=["v1", "v2"])
def adapter(request: pytest.FixtureRequest) -> Any:
    """Parameterized adapter fixture — runs all contract tests for both v1 and v2."""
    if request.param == "v1":
        from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
        return V1LegacyAdapter()
    from prometheus.cipher.v2_modern.adapter import V2ModernAdapter
    return V2ModernAdapter()
