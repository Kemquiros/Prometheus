# tests/conftest.py
"""Shared test fixtures for Prometheus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.cipher.v2_modern.adapter import V2ModernAdapter
from prometheus.domain.value_objects import Ciphertext

VECTORS_DIR = Path(__file__).parent / "vectors"


@pytest.fixture
def v1_adapter() -> V1LegacyAdapter:
    """V1 legacy adapter instance."""
    return V1LegacyAdapter()


@pytest.fixture
def v2_adapter() -> V2ModernAdapter:
    """V2 modern adapter instance."""
    return V2ModernAdapter()


@pytest.fixture
def v1_vectors() -> list[dict[str, Any]]:
    """Loaded v1 test vectors (KNOWN-ANSWER TESTS)."""
    with open(VECTORS_DIR / "v1_legacy.json") as f:
        data = json.load(f)
    return [v for v in data["vectors"] if v["plaintext"]]  # skip empty plaintext


@pytest.fixture
def sample_secret() -> str:
    """Sample secret for tests."""
    return "test-secret-key-12345"


@pytest.fixture
def sample_plaintext() -> str:
    """Sample plaintext for tests."""
    return "my-password-123!"


@pytest.fixture
def v1_ciphertext(sample_secret: str, sample_plaintext: str) -> Ciphertext:
    """A known v1 ciphertext for testing."""
    adapter = V1LegacyAdapter()
    return adapter.encrypt(sample_secret, sample_plaintext)
