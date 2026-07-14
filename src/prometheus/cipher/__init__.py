# src/prometheus/crypto/__init__.py
"""Crypto package — adapters for cryptographic operations."""

from .factory import CryptoFactory, get_crypto
from .v1_legacy.adapter import V1LegacyAdapter
from .v2_modern.adapter import V2ModernAdapter

__all__ = ["CryptoFactory", "V1LegacyAdapter", "V2ModernAdapter", "get_crypto"]
