"""Migration CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from prometheus.cipher.factory import detect_version
from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.domain.value_objects import Ciphertext
from prometheus.migration.migrator import batch_migrate, migrate_ciphertext, scan_v1_ciphertexts

migration_app = typer.Typer(
    name="migrate",
    help="Migrate v1 ciphertexts to v2.",
    rich_markup_mode="rich",
)

console = Console()

SECRET_OPT = Annotated[str, typer.Option("--secret", "-s", prompt=True, help="Encryption secret")]
FILE_OPT = Annotated[str | None, typer.Option("--file", "-f", help="File with ciphertexts")]
CT_OPT = Annotated[str | None, typer.Option("--ciphertext", "-c", help="Single ciphertext")]
DRY_OPT = Annotated[bool, typer.Option("--dry-run", help="Show what would be migrated")]


def _read_file(file: str) -> list[str]:
    """Read lines from file."""
    path = Path(file)
    if not path.exists():
        console.print(f"[bold red]File not found:[/] {file}")
        raise typer.Exit(1)
    return path.read_text().splitlines()


@migration_app.command("scan")
def migrate_scan(
    file: Annotated[str, typer.Argument(help="File containing ciphertexts (one per line)")],
) -> None:
    """Scan file for v1 ciphertexts."""
    lines = _read_file(file)

    v1_ciphertexts = scan_v1_ciphertexts(lines)
    v2_count = len(lines) - len(v1_ciphertexts)

    table = Table(title="Migration Scan Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Total lines", str(len(lines)))
    table.add_row("v1 ciphertexts", str(len(v1_ciphertexts)))
    table.add_row("v2 ciphertexts (already modern)", str(v2_count))
    console.print(table)

    if v1_ciphertexts:
        console.print(
            Panel(
                f"[bold yellow]Found {len(v1_ciphertexts)} v1 ciphertexts that can be migrated.[/]",
                title="[bold purple]Action Required[/]",
                border_style="yellow",
            ),
        )


@migration_app.command("migrate")
def migrate_migrate(
    secret: SECRET_OPT,
    file: FILE_OPT = None,
    ciphertext: CT_OPT = None,
    dry_run: DRY_OPT = False,
) -> None:
    """Migrate v1 ciphertexts to v2."""
    if file is None and ciphertext is None:
        console.print("[bold red]Error:[/] Provide --file or --ciphertext")
        raise typer.Exit(1)

    if ciphertext:
        _migrate_single(secret, ciphertext, dry_run)
        return

    lines = _read_file(file)  # type: ignore[arg-type]
    v1_ciphertexts = scan_v1_ciphertexts(lines)

    if not v1_ciphertexts:
        console.print("[dim]No v1 ciphertexts found. Nothing to migrate.[/]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Migrating...", total=len(v1_ciphertexts))
        results = batch_migrate(secret, v1_ciphertexts)
        progress.update(task, advance=len(v1_ciphertexts))

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    table = Table(title="Migration Results")
    table.add_column("Status", style="cyan")
    table.add_column("Count", style="green")
    table.add_row("Successful", str(len(successful)))
    table.add_row("Failed", str(len(failed)))
    console.print(table)

    if dry_run:
        console.print("[yellow]Dry run — no changes made.[/]")

    if failed:
        console.print("[bold red]Some migrations failed:[/]")
        for r in failed:
            console.print(f"  - {r.old_ciphertext[:50]}... → {r.error}")


def _migrate_single(secret: str, ciphertext_str: str, dry_run: bool) -> None:
    """Migrate a single ciphertext."""
    ct = Ciphertext(ciphertext_str)
    result = migrate_ciphertext(secret, ct)

    if result.old_version == "v2":
        console.print("[dim]Ciphertext is already v2. No migration needed.[/]")
        return

    if not result.success:
        console.print(f"[bold red]Migration failed:[/] {result.error}")
        raise typer.Exit(1)

    if dry_run:
        console.print(f"[yellow]Would migrate:[/] {result.old_ciphertext[:50]}...")
        console.print(f"[green]To:[/] {result.new_ciphertext[:50]}...")
    else:
        console.print(
            Panel(
                f"[bold green]{result.new_ciphertext}[/]",
                title="[bold purple]Migrated (v1 → v2)[/]",
                border_style="purple",
            ),
        )


@migration_app.command("rollback")
def migrate_rollback(
    secret: SECRET_OPT,
    ciphertext: Annotated[str, typer.Option("--ciphertext", "-c", help="v2 ciphertext")] = "",
) -> None:
    """Rollback a v2 ciphertext to v1 (for emergency recovery)."""
    ct = Ciphertext(ciphertext)
    version = detect_version(ct)

    if version == "v1":
        console.print("[dim]Ciphertext is already v1. No rollback needed.[/]")
        return

    v1_adapter = V1LegacyAdapter()
    rolled = v1_adapter.encrypt(secret, ciphertext)

    console.print(
        Panel(
            f"[bold green]{rolled.value}[/]",
            title="[bold purple]Rolled back (v2 → v1)[/]",
            subtitle="[bold red]WARNING: v1 is NOT secure. Use only for emergency recovery.[/]",
            border_style="red",
        ),
    )
