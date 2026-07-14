"""Config and profile CLI commands."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from prometheus.config.adapter import TomlConfigAdapter
from prometheus.domain.entities import Profile

config_app = typer.Typer(
    name="config",
    help="Manage Prometheus configuration.",
    rich_markup_mode="rich",
)

profile_app = typer.Typer(
    name="profile",
    help="Manage encryption profiles.",
    rich_markup_mode="rich",
)

console = Console()


@config_app.command("show")
def config_show() -> None:
    """Show current configuration."""
    adapter = TomlConfigAdapter()
    config = adapter.load()

    table = Table(title="Prometheus Configuration", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Default Profile", config.default_profile)
    table.add_row("Algorithm", config.algorithm)
    table.add_row("Storage", config.storage)
    table.add_row("File Path", str(config.file_path))
    table.add_row("Keyring Service", config.keyring_service)
    table.add_row("Env Prefix", config.env_prefix)
    table.add_row("Profiles", str(len(config.profiles)))
    console.print(table)


@config_app.command("init")
def config_init() -> None:
    """Initialize default configuration file."""
    adapter = TomlConfigAdapter()
    config = adapter.load()
    adapter.save(config)
    console.print(
        Panel(
            f"[bold green]Config created at:[/] {adapter.config_file}",
            title="[bold purple]Config Initialized[/]",
            border_style="purple",
        ),
    )


@profile_app.command("create")
def profile_create(
    name: Annotated[str, typer.Argument(help="Profile name")],
    secret: Annotated[str, typer.Option("--secret", "-s", prompt=True, help="Encryption secret")],
    algorithm: Annotated[str, typer.Option("--algo", help="Algorithm: v1, v2, auto")] = "v2",
) -> None:
    """Create or update an encryption profile."""
    adapter = TomlConfigAdapter()
    profile = Profile(name=name, secret=secret, algorithm=algorithm)  # type: ignore[arg-type]
    adapter.set_profile(profile)
    console.print(
        Panel(
            f"[bold green]Profile '{name}' saved[/]",
            title="[bold purple]Profile Created[/]",
            border_style="purple",
        ),
    )


@profile_app.command("list")
def profile_list() -> None:
    """List all profiles."""
    adapter = TomlConfigAdapter()
    profiles = adapter.list_profiles()

    if not profiles:
        console.print("[dim]No profiles configured. Use 'prometheus profile create' to add one.[/]")
        return

    table = Table(title="Encryption Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Algorithm", style="green")
    table.add_column("Storage", style="yellow")
    table.add_column("Secret", style="dim")

    MASK_LEN = 4
    for p in profiles:
        masked = p.secret[:MASK_LEN] + "****" if len(p.secret) > MASK_LEN else "****"
        table.add_row(p.name, p.algorithm, p.storage, masked)

    console.print(table)


@profile_app.command("show")
def profile_show(
    name: Annotated[str, typer.Argument(help="Profile name")],
) -> None:
    """Show profile details."""
    adapter = TomlConfigAdapter()
    profile = adapter.get_profile(name)

    if profile is None:
        console.print(f"[bold red]Profile '{name}' not found.[/]")
        raise typer.Exit(1)

    table = Table(title=f"Profile: {name}", show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Name", profile.name)
    table.add_row("Algorithm", profile.algorithm)
    table.add_row("Storage", profile.storage)
    table.add_row("File Path", str(profile.file_path) if profile.file_path else "default")
    table.add_row("Keyring Service", profile.keyring_service)
    table.add_row("Env Prefix", profile.env_prefix)
    console.print(table)


@profile_app.command("delete")
def profile_delete(
    name: Annotated[str, typer.Argument(help="Profile name")],
) -> None:
    """Delete a profile."""
    adapter = TomlConfigAdapter()
    if adapter.delete_profile(name):
        console.print(f"[bold green]Profile '{name}' deleted.[/]")
    else:
        console.print(f"[bold red]Profile '{name}' not found.[/]")
        raise typer.Exit(1)
