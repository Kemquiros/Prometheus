"""Storage CLI commands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prometheus.storage.adapter import FileStorageAdapter

storage_app = typer.Typer(
    name="store",
    help="Manage encrypted secret storage.",
    rich_markup_mode="rich",
)

console = Console()


@storage_app.command("set")
def store_set(
    name: Annotated[str, typer.Argument(help="Secret name")],
    value: Annotated[str, typer.Option("--value", "-v", prompt=True, help="Secret value")],
) -> None:
    """Store a secret."""
    adapter = FileStorageAdapter()
    adapter.store_secret(name, value)
    console.print(
        Panel(
            f"[bold green]Secret '{name}' stored[/]",
            title="[bold purple]Secret Stored[/]",
            border_style="purple",
        ),
    )


@storage_app.command("get")
def store_get(
    name: Annotated[str, typer.Argument(help="Secret name")],
) -> None:
    """Retrieve a secret."""
    adapter = FileStorageAdapter()
    value = adapter.get_secret(name)

    if value is None:
        console.print(f"[bold red]Secret '{name}' not found.[/]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold green]{value}[/]",
            title=f"[bold purple]Secret: {name}[/]",
            border_style="purple",
        ),
    )


@storage_app.command("list")
def store_list() -> None:
    """List all stored secrets."""
    adapter = FileStorageAdapter()
    secrets = adapter.list_secrets()

    if not secrets:
        console.print("[dim]No secrets stored. Use 'prometheus store set' to add one.[/]")
        return

    table = Table(title="Stored Secrets")
    table.add_column("Name", style="cyan")

    for name in sorted(secrets):
        table.add_row(name)

    console.print(table)


@storage_app.command("delete")
def store_delete(
    name: Annotated[str, typer.Argument(help="Secret name")],
) -> None:
    """Delete a secret."""
    adapter = FileStorageAdapter()
    if adapter.delete_secret(name):
        console.print(f"[bold green]Secret '{name}' deleted.[/]")
    else:
        console.print(f"[bold red]Secret '{name}' not found.[/]")
        raise typer.Exit(1)


@storage_app.command("exists")
def store_exists(
    name: Annotated[str, typer.Argument(help="Secret name")],
) -> None:
    """Check if a secret exists."""
    adapter = FileStorageAdapter()
    if adapter.exists(name):
        console.print(f"[green]Secret '{name}' exists.[/]")
    else:
        console.print(f"[red]Secret '{name}' does not exist.[/]")
        raise typer.Exit(1)
