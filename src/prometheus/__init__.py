# src/prometheus/__init__.py
"""Prometheus Crypto — World-class CLI for symmetric encryption of secrets."""

__version__ = "2.0.0.dev0"
__author__ = "Kemquiros"

from prometheus.cipher.factory import CryptoFactory, get_crypto
from prometheus.domain.value_objects import Ciphertext

__all__ = [
    "Ciphertext",
    "CryptoFactory",
    "__version__",
    "get_crypto",
]
