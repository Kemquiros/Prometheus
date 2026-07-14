# tests/integration/test_encrypt_decrypt_roundtrip.py
"""Integration tests — full encrypt/decrypt roundtrip through CLI and factory."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from prometheus.cipher.factory import CryptoFactory
from prometheus.cli.app import app

runner = CliRunner()


class TestFactoryRoundtrip:
    """Full roundtrip through CryptoFactory."""

    def test_v2_roundtrip(self) -> None:
        factory = CryptoFactory(default_version="v2")
        ct = factory.encrypt("my-secret-key-12345", "hello world")
        pt = factory.decrypt("my-secret-key-12345", ct)
        assert pt == "hello world"

    def test_v1_roundtrip(self) -> None:
        factory = CryptoFactory(default_version="v1")
        ct = factory.encrypt("my-secret-key-12345", "hello world")
        pt = factory.decrypt("my-secret-key-12345", ct)
        assert pt == "hello world"

    def test_auto_detect_v1(self) -> None:
        v1_factory = CryptoFactory(default_version="v1")
        ct = v1_factory.encrypt("my-secret-key-12345", "test")
        auto_factory = CryptoFactory()
        pt = auto_factory.decrypt("my-secret-key-12345", ct)
        assert pt == "test"

    def test_auto_detect_v2(self) -> None:
        v2_factory = CryptoFactory(default_version="v2")
        ct = v2_factory.encrypt("my-secret-key-12345", "test")
        auto_factory = CryptoFactory()
        pt = auto_factory.decrypt("my-secret-key-12345", ct)
        assert pt == "test"

    def test_get_adapter_explicit(self) -> None:
        factory = CryptoFactory(default_version="auto")
        adapter = factory.get_adapter("v1")
        assert adapter.version == "v1"
        adapter = factory.get_adapter("v2")
        assert adapter.version == "v2"

    def test_unicode_v2(self) -> None:
        factory = CryptoFactory(default_version="v2")
        ct = factory.encrypt("my-secret-key-12345", "¡Hola mundo! 你好世界 🌍")
        pt = factory.decrypt("my-secret-key-12345", ct)
        assert pt == "¡Hola mundo! 你好世界 🌍"

    def test_empty_plaintext_v2(self) -> None:
        factory = CryptoFactory(default_version="v2")
        ct = factory.encrypt("my-secret-key-12345", "")
        pt = factory.decrypt("my-secret-key-12345", ct)
        assert pt == ""

    def test_long_plaintext_v2(self) -> None:
        factory = CryptoFactory(default_version="v2")
        long_text = "a" * 10000
        ct = factory.encrypt("my-secret-key-12345", long_text)
        pt = factory.decrypt("my-secret-key-12345", ct)
        assert pt == long_text


class TestCLIRoundtrip:
    """Full roundtrip through CLI commands."""

    def test_encrypt_decrypt_quiet(self) -> None:
        enc = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--format", "quiet"],
        )
        ct = enc.output.strip()
        dec = runner.invoke(
            app,
            ["decrypt", "--secret", "my-secret-key-12345", "--ciphertext", ct, "--format", "quiet"],
        )
        assert dec.exit_code == 0
        assert dec.output.strip() == "hello"

    def test_encrypt_decrypt_json(self) -> None:
        enc = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--format", "json"],
        )
        data = json.loads(enc.output)
        ct = data["ciphertext"]
        dec = runner.invoke(
            app,
            ["decrypt", "--secret", "my-secret-key-12345", "--ciphertext", ct, "--format", "json"],
        )
        dec_data = json.loads(dec.output)
        assert dec_data["plaintext"] == "hello"

    def test_encrypt_decrypt_v1_roundtrip(self) -> None:
        enc = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--algo", "v1", "--format", "quiet"],
        )
        ct = enc.output.strip()
        dec = runner.invoke(
            app,
            ["decrypt", "--secret", "my-secret-key-12345", "--ciphertext", ct, "--format", "quiet"],
        )
        assert dec.exit_code == 0
        assert dec.output.strip() == "hello"

    def test_wrong_secret_fails(self) -> None:
        enc = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--format", "quiet"],
        )
        ct = enc.output.strip()
        dec = runner.invoke(
            app,
            ["decrypt", "--secret", "wrong-secret-key-xxxxx", "--ciphertext", ct, "--format", "quiet"],
        )
        assert dec.exit_code == 1
