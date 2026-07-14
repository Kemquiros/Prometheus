# src/prometheus/cli/app.py
"""Main CLI application — Typer + Rich console."""

from __future__ import annotations

import json
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prometheus.cipher.factory import CryptoFactory
from prometheus.cli.commands.config import config_app, profile_app
from prometheus.cli.commands.migrate import migration_app
from prometheus.cli.commands.storage import storage_app
from prometheus.domain.value_objects import Ciphertext

app = typer.Typer(
    name="prometheus",
    help="World-class CLI for symmetric encryption of secrets.",
    epilog="For more info: https://kemquiros.github.io/Prometheus/",
    add_completion=True,
    rich_markup_mode="rich",
)

app.add_typer(config_app)
app.add_typer(profile_app)
app.add_typer(storage_app)
app.add_typer(migration_app)

console = Console()

# Type annotations
SecretOption = Annotated[
    str,
    typer.Option("--secret", "-s", prompt=True, help="Encryption secret"),
]
CiphertextOption = Annotated[
    str,
    typer.Option("--ciphertext", "-c", prompt=True, help="Ciphertext to decrypt"),
]
PlaintextOption = Annotated[
    str,
    typer.Option("--plaintext", "-p", prompt=True, help="Plaintext to encrypt"),
]
VersionOption = Annotated[str, typer.Option("--algo", help="Algorithm version: v1, v2, auto")]
FormatOption = Annotated[
    str,
    typer.Option("--format", "-f", help="Output format: auto, json, quiet"),
]


BANNER = r"""
[bold purple]
   ____                _           __
  / __ \____  _____(_)___  _____/ /______
 / / / / __ \/ ___/ / __ \/ ___/ __/ ___/
/ /_/ / /_/ / /__/ / /_/ (__  ) /_(__  )
\____/ .___/\___/_/\____/____/\__/____/
    /_/
[/]
[bold white]Password Encryption & Decryption Tool[/]
[dim]Version 2.0.0 | Hexagonal Architecture[/]
"""


def print_banner() -> None:
    """Display startup banner."""
    console.print(BANNER)


def print_version() -> None:
    """Display version info."""
    version_table = Table(title="Prometheus Crypto", show_header=False)
    version_table.add_column("Key", style="cyan")
    version_table.add_column("Value", style="green")
    version_table.add_row("Version", "2.0.0")
    version_table.add_row("Architecture", "Hexagonal (Ports & Adapters)")
    version_table.add_row("Crypto v1", "XOR + SHA-256 + Base64 (legacy)")
    version_table.add_row("Crypto v2", "XChaCha20-Poly1305 + Argon2id")
    version_table.add_row("License", "MIT")
    console.print(version_table)


@app.command()
def encrypt(
    secret: SecretOption,
    plaintext: PlaintextOption,
    version: VersionOption = "auto",
    output_format: FormatOption = "auto",
) -> None:
    """Encrypt plaintext with a secret key.

    Examples:
        prometheus encrypt -s "my-secret" -p "password123"

        prometheus encrypt --secret "prod-key" --plaintext "db-pass" --version v2

    """
    factory = CryptoFactory(default_version=version)  # type: ignore[arg-type]
    try:
        ciphertext = factory.encrypt(secret, plaintext)
        if output_format == "json":
            console.print_json(
                json.dumps(
                    {
                        "ciphertext": ciphertext.value,
                        "version": ciphertext.version,
                        "algorithm": ciphertext.version,
                    },
                ),
            )
        elif output_format == "quiet":
            console.print(ciphertext.value)
        else:
            console.print()
            console.print(
                Panel(
                    f"[bold green]{ciphertext.value}[/]",
                    title="[bold purple]Encrypted[/]",
                    subtitle=f"algorithm: {ciphertext.version}",
                    border_style="purple",
                ),
            )
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}", style="red")
        raise typer.Exit(1) from None


@app.command()
def decrypt(
    secret: SecretOption,
    ciphertext: CiphertextOption,
    output_format: FormatOption = "auto",
) -> None:
    """Decrypt ciphertext with a secret key.

    Examples:
        prometheus decrypt -s "my-secret" -c "g/u55oK9j97hrpeX+w=="

        prometheus decrypt --secret "prod-key" --ciphertext "v2|...|..."

    """
    ct = Ciphertext(ciphertext)
    factory = CryptoFactory()
    try:
        plaintext = factory.decrypt(secret, ct)
        if output_format == "json":
            console.print_json(
                json.dumps(
                    {
                        "plaintext": plaintext,
                        "version": ct.version,
                    },
                ),
            )
        elif output_format == "quiet":
            console.print(plaintext)
        else:
            console.print()
            console.print(
                Panel(
                    f"[bold green]{plaintext}[/]",
                    title="[bold purple]Decrypted[/]",
                    subtitle=f"algorithm: {ct.version}",
                    border_style="purple",
                ),
            )
    except Exception as e:
        console.print(f"[bold red]Error:[/] {e}", style="red")
        raise typer.Exit(1) from None


@app.command()
def interactive() -> None:
    """Interactive mode — encrypt/decrypt with guided prompts."""
    print_banner()

    while True:
        console.print("\n[bold purple]Choose operation:[/]")
        console.print("  [cyan](e)[/] Encrypt")
        console.print("  [cyan](d)[/] Decrypt")
        console.print("  [cyan](v)[/] Show version")
        console.print("  [cyan](f)[/] Finish")

        operation = console.input("[bold purple]>> [/]").strip().lower()

        if operation == "f":
            console.print("[bold green]Goodbye![/]")
            break
        if operation == "v":
            print_version()
        elif operation in ("e", "d"):
            secret = console.input("[bold purple]Secret:[/] ")
            if operation == "e":
                plaintext = console.input("[bold purple]Password:[/] ")
                ciphertext = CryptoFactory().encrypt(secret, plaintext)
                console.print(
                    Panel(
                        f"[bold green]{ciphertext.value}[/]",
                        title="[bold purple]Encrypted[/]",
                        subtitle=f"algorithm: {ciphertext.version}",
                        border_style="purple",
                    ),
                )
            elif operation == "d":
                ciphertext_str = console.input("[bold purple]Ciphertext:[/] ")
                ct = Ciphertext(ciphertext_str)
                plaintext = CryptoFactory().decrypt(secret, ct)
                console.print(
                    Panel(
                        f"[bold green]{plaintext}[/]",
                        title="[bold purple]Decrypted[/]",
                        subtitle=f"algorithm: {ct.version}",
                        border_style="purple",
                    ),
                )
        else:
            console.print("[bold red]Invalid option. Use (e), (d), (v), or (f).[/]")


@app.command()
def version() -> None:
    """Show version and algorithm information."""
    print_version()


@app.command()
def info() -> None:
    """Show detailed information about Prometheus."""
    print_banner()
    print_version()

    console.print("\n[bold purple]Architecture:[/]")
    console.print("  Hexagonal (Ports & Adapters)")
    console.print("  - Domain: Pure business logic, no I/O")
    console.print("  - Ports: CryptoPort, ConfigPort, StoragePort, OutputPort")
    console.print("  - Adapters: v1 legacy, v2 modern, file, keyring, env")

    console.print("\n[bold purple]Security:[/]")
    console.print("  - v1: XOR + SHA-256 + Base64 (legacy, NOT recommended)")
    console.print("  - v2: XChaCha20-Poly1305 + Argon2id (modern, recommended)")
    console.print("  - All encryption uses random salt + nonce (forward secrecy)")

    console.print("\n[bold purple]Links:[/]")
    console.print("  - Docs: https://kemquiros.github.io/Prometheus/")
    console.print("  - GitHub: https://github.com/Kemquiros/Prometheus")
    console.print("  - Issues: https://github.com/Kemquiros/Prometheus/issues")


if __name__ == "__main__":
    app()
