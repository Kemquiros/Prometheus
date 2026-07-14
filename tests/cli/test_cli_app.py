# tests/cli/test_cli_app.py
"""CLI tests using Typer's CliRunner."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from prometheus.cli.app import app

runner = CliRunner()


class TestEncryptCommand:
    """Tests for `prometheus encrypt` command."""

    def test_encrypt_default_format(self) -> None:
        result = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello"],
        )
        assert result.exit_code == 0
        assert "Encrypted" in result.output

    def test_encrypt_quiet_format(self) -> None:
        result = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--format", "quiet"],
        )
        assert result.exit_code == 0
        assert "v2|" in result.output

    def test_encrypt_json_format(self) -> None:
        result = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--format", "json"],
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert "ciphertext" in data
        assert "version" in data
        assert data["version"] == "v2"

    def test_encrypt_v1_algo(self) -> None:
        result = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--algo", "v1", "--format", "quiet"],
        )
        assert result.exit_code == 0
        assert "v2|" not in result.output

    def test_encrypt_v2_algo(self) -> None:
        result = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--algo", "v2", "--format", "quiet"],
        )
        assert result.exit_code == 0
        assert "v2|" in result.output


class TestDecryptCommand:
    """Tests for `prometheus decrypt` command."""

    def test_decrypt_default_format(self) -> None:
        result = runner.invoke(
            app,
            ["decrypt", "--secret", "my-secret-key-12345", "--ciphertext", "v2|abc|def|ghi|jkl"],
        )
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_decrypt_quiet_format(self) -> None:
        result = runner.invoke(
            app,
            ["decrypt", "--secret", "my-secret-key-12345", "--ciphertext", "v2|abc|def|ghi|jkl", "--format", "quiet"],
        )
        assert result.exit_code == 1
        assert "Error" in result.output

    def test_decrypt_json_format_error(self) -> None:
        result = runner.invoke(
            app,
            ["decrypt", "--secret", "my-secret-key-12345", "--ciphertext", "v2|abc|def|ghi|jkl", "--format", "json"],
        )
        assert result.exit_code == 1


class TestVersionCommand:
    """Tests for `prometheus version` command."""

    def test_version(self) -> None:
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "2.0.0" in result.output
        assert "Hexagonal" in result.output


class TestInfoCommand:
    """Tests for `prometheus info` command."""

    def test_info(self) -> None:
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Architecture" in result.output
        assert "Security" in result.output
        assert "Links" in result.output
        assert "Hexagonal" in result.output


class TestInteractiveCommand:
    """Tests for `prometheus interactive` command."""

    def test_interactive_finish(self) -> None:
        result = runner.invoke(app, ["interactive"], input="f\n")
        assert result.exit_code == 0
        assert "Goodbye" in result.output

    def test_interactive_version(self) -> None:
        result = runner.invoke(app, ["interactive"], input="v\nf\n")
        assert result.exit_code == 0
        assert "2.0.0" in result.output

    def test_interactive_encrypt(self) -> None:
        result = runner.invoke(
            app,
            ["interactive"],
            input="e\nmy-secret-key-12345\nhello\nf\n",
        )
        assert result.exit_code == 0
        assert "Encrypted" in result.output

    def test_interactive_decrypt(self) -> None:
        ct_result = runner.invoke(
            app,
            ["encrypt", "--secret", "my-secret-key-12345", "--plaintext", "hello", "--format", "quiet"],
        )
        ct = ct_result.output.strip()
        result = runner.invoke(
            app,
            ["interactive"],
            input=f"d\nmy-secret-key-12345\n{ct}\nf\n",
        )
        assert result.exit_code == 0
        assert "Decrypted" in result.output

    def test_interactive_invalid_option(self) -> None:
        result = runner.invoke(app, ["interactive"], input="x\nf\n")
        assert result.exit_code == 0
        assert "Invalid option" in result.output


class TestMainModule:
    """Test __main__ entry point."""

    def test_main_entry(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "prometheus" in result.output.lower()
