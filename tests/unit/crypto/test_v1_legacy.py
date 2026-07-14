# tests/unit/crypto/test_v1_legacy.py
"""Unit tests for V1LegacyAdapter — KNOWN-ANSWER TESTS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.domain.value_objects import Ciphertext

VECTORS_PATH = Path(__file__).parent.parent.parent / "vectors" / "v1_legacy.json"


class TestV1LegacyKnownAnswer:
    """KNOWN-ANSWER TESTS — verify against frozen test vectors.

    See ADR 0002: These vectors are IMMUTABLE.
    """

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V1LegacyAdapter()
        with open(VECTORS_PATH) as f:
            self.vectors = json.load(f)["vectors"]

    def test_version_property(self) -> None:
        assert self.adapter.version == "v1"

    @pytest.mark.parametrize(
        "vector",
        [v for v in json.load(open(VECTORS_PATH))["vectors"] if v["plaintext"]],
        ids=lambda v: f"{v['notes']}",
    )
    def test_known_answer_decrypt(self, vector: dict[str, Any]) -> None:
        """Each vector must decrypt to its expected plaintext."""
        ciphertext = Ciphertext(vector["ciphertext"])
        result = self.adapter.decrypt(vector["secret"], ciphertext)
        assert result == vector["plaintext"]

    @pytest.mark.parametrize(
        "vector",
        [v for v in json.load(open(VECTORS_PATH))["vectors"] if v["plaintext"]],
        ids=lambda v: f"{v['notes']}",
    )
    def test_known_answer_encrypt(self, vector: dict[str, Any]) -> None:
        """Each vector must encrypt to its expected ciphertext."""
        result = self.adapter.encrypt(vector["secret"], vector["plaintext"])
        assert result.value == vector["ciphertext"]

    def test_symmetry(self) -> None:
        """Encrypt then decrypt must return original plaintext."""
        secret = "symmetry-test-key"
        plaintext = "symmetry-test-password"
        ciphertext = self.adapter.encrypt(secret, plaintext)
        decrypted = self.adapter.decrypt(secret, ciphertext)
        assert decrypted == plaintext

    def test_deterministic_with_same_inputs(self) -> None:
        """Same inputs must produce same ciphertext (v1 is deterministic)."""
        secret = "deterministic-test"
        plaintext = "deterministic-password"
        ct1 = self.adapter.encrypt(secret, plaintext)
        ct2 = self.adapter.encrypt(secret, plaintext)
        assert ct1.value == ct2.value


class TestV1LegacySecurity:
    """Security property tests for v1 legacy."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.adapter = V1LegacyAdapter()

    def test_ciphertext_not_plaintext(self) -> None:
        """Ciphertext must differ from plaintext."""
        ct = self.adapter.encrypt("secret", "password")
        assert ct.value != "password"

    def test_different_keys_different_ciphertexts(self) -> None:
        """Different keys must produce different ciphertexts."""
        ct1 = self.adapter.encrypt("key-one", "password")
        ct2 = self.adapter.encrypt("key-two", "password")
        assert ct1.value != ct2.value
