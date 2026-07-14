"""Audit CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prometheus.cipher.factory import detect_version
from prometheus.domain.value_objects import Ciphertext
from prometheus.migration.migrator import scan_v1_ciphertexts

audit_app = typer.Typer(
    name="audit",
    help="Audit for weak v1 ciphertexts.",
    rich_markup_mode="rich",
)

console = Console()


@audit_app.command("scan")
def audit_scan(
    file: Annotated[str, typer.Argument(help="File to scan for v1 ciphertexts")],
) -> None:
    """Scan a file for v1 ciphertexts."""
    path = Path(file)
    if not path.exists():
        console.print(f"[bold red]File not found:[/] {file}")
        raise typer.Exit(1)

    lines = path.read_text().splitlines()
    v1_ciphertexts = scan_v1_ciphertexts(lines)
    v2_count = len(lines) - len(v1_ciphertexts)

    table = Table(title="Audit Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total lines", str(len(lines)))
    table.add_row("v1 ciphertexts (WEAK)", str(len(v1_ciphertexts)))
    table.add_row("v2 ciphertexts (secure)", str(v2_count))
    console.print(table)

    if v1_ciphertexts:
        console.print(
            Panel(
                f"[bold red]Found {len(v1_ciphertexts)} v1 ciphertexts![/]\n"
                "v1 uses XOR + SHA-256 (NOT cryptographically secure).\n"
                "Migrate to v2 with: prometheus migrate migrate --secret <key> --file <file>",
                title="[bold red]Security Warning[/]",
                border_style="red",
            ),
        )
    else:
        console.print("[bold green]All ciphertexts are v2 (secure).[/]")


@audit_app.command("file")
def audit_file(
    file: Annotated[str, typer.Argument(help="File to audit")],
) -> None:
    """Detailed audit of a file's ciphertexts."""
    path = Path(file)
    if not path.exists():
        console.print(f"[bold red]File not found:[/] {file}")
        raise typer.Exit(1)

    lines = path.read_text().splitlines()
    v1_count = 0
    v2_count = 0
    invalid_count = 0

    for _i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        try:
            ct = Ciphertext(stripped)
            version = detect_version(ct)
            if version == "v1":
                v1_count += 1
            else:
                v2_count += 1
        except Exception:
            invalid_count += 1

    table = Table(title=f"Audit: {file}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("v1 ciphertexts", str(v1_count))
    table.add_row("v2 ciphertexts", str(v2_count))
    table.add_row("Invalid lines", str(invalid_count))
    console.print(table)

    if v1_count > 0:
        console.print(
            f"[bold yellow]Warning: {v1_count} v1 ciphertexts found. "
            "Consider migrating to v2.[/]",
        )
