"""Benchmark CLI commands."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.table import Table

from prometheus.cipher.v1_legacy.adapter import V1LegacyAdapter
from prometheus.cipher.v2_modern.adapter import V2ModernAdapter

if TYPE_CHECKING:
    from prometheus.domain.value_objects import Ciphertext

benchmark_app = typer.Typer(
    name="bench",
    help="Run performance benchmarks.",
    rich_markup_mode="rich",
)

console = Console()

ITERATIONS_OPT = Annotated[
    int,
    typer.Option("--iterations", "-n", help="Number of iterations"),
]


def _bench_v1_enc(
    secret: str, plaintext: str, n: int,
) -> float:
    """Benchmark v1 encrypt."""
    adapter = V1LegacyAdapter()
    start = time.perf_counter()
    for _ in range(n):
        adapter.encrypt(secret, plaintext)
    return time.perf_counter() - start


def _bench_v2_enc(
    secret: str, plaintext: str, n: int,
) -> float:
    """Benchmark v2 encrypt."""
    adapter = V2ModernAdapter()
    start = time.perf_counter()
    for _ in range(n):
        adapter.encrypt(secret, plaintext)
    return time.perf_counter() - start


def _bench_v1_dec(
    secret: str, ct: Ciphertext, n: int,
) -> float:
    """Benchmark v1 decrypt."""
    adapter = V1LegacyAdapter()
    start = time.perf_counter()
    for _ in range(n):
        adapter.decrypt(secret, ct)
    return time.perf_counter() - start


def _bench_v2_dec(
    secret: str, ct: Ciphertext, n: int,
) -> float:
    """Benchmark v2 decrypt."""
    adapter = V2ModernAdapter()
    start = time.perf_counter()
    for _ in range(n):
        adapter.decrypt(secret, ct)
    return time.perf_counter() - start


@benchmark_app.command("run")
def bench_run(
    iterations: ITERATIONS_OPT = 1000,
) -> None:
    """Run encrypt/decrypt benchmarks for v1 and v2."""
    secret = "benchmark-secret"  # noqa: S105
    plaintext = "benchmark-plaintext"

    console.print(f"[bold purple]Running benchmarks ({iterations} iterations)...[/]")

    v1_enc_time = _bench_v1_enc(secret, plaintext, iterations)
    v2_enc_time = _bench_v2_enc(secret, plaintext, iterations)

    v1 = V1LegacyAdapter()
    v2 = V2ModernAdapter()
    v1_ct = v1.encrypt(secret, plaintext)
    v2_ct = v2.encrypt(secret, plaintext)

    v1_dec_time = _bench_v1_dec(secret, v1_ct, iterations)
    v2_dec_time = _bench_v2_dec(secret, v2_ct, iterations)

    table = Table(title="Benchmark Results")
    table.add_column("Operation", style="cyan")
    table.add_column("v1 (legacy)", style="yellow")
    table.add_column("v2 (modern)", style="green")
    table.add_column("Ratio", style="white")

    v1_enc_us = (v1_enc_time / iterations) * 1_000_000
    v2_enc_us = (v2_enc_time / iterations) * 1_000_000
    enc_ratio = v2_enc_us / v1_enc_us if v1_enc_us > 0 else 0

    v1_dec_us = (v1_dec_time / iterations) * 1_000_000
    v2_dec_us = (v2_dec_time / iterations) * 1_000_000
    dec_ratio = v2_dec_us / v1_dec_us if v1_dec_us > 0 else 0

    table.add_row(
        "Encrypt",
        f"{v1_enc_us:.1f} us/op",
        f"{v2_enc_us:.1f} us/op",
        f"{enc_ratio:.1f}x",
    )
    table.add_row(
        "Decrypt",
        f"{v1_dec_us:.1f} us/op",
        f"{v2_dec_us:.1f} us/op",
        f"{dec_ratio:.1f}x",
    )
    table.add_row(
        "Total",
        f"{(v1_enc_us + v1_dec_us):.1f} us/op",
        f"{(v2_enc_us + v2_dec_us):.1f} us/op",
        f"{(v2_enc_us + v2_dec_us) / (v1_enc_us + v1_dec_us):.1f}x",
    )

    console.print(table)

    console.print(
        "\n[dim]Note: v2 is slower but uses authenticated encryption "
        "(ChaCha20-Poly1305) with Argon2id key derivation. "
        "Security > speed.[/]",
    )
