"""v1→v2 migration utilities."""

from __future__ import annotations

from dataclasses import dataclass

from prometheus.cipher.factory import detect_version, get_crypto_for_ciphertext
from prometheus.cipher.v2_modern.adapter import V2ModernAdapter
from prometheus.domain.value_objects import Ciphertext


@dataclass(frozen=True)
class MigrationResult:
    """Result of a single ciphertext migration."""

    old_ciphertext: str
    new_ciphertext: str
    old_version: str
    new_version: str
    plaintext: str
    success: bool
    error: str | None = None


def migrate_ciphertext(secret: str, ciphertext: Ciphertext) -> MigrationResult:
    """Migrate a single ciphertext from v1 to v2.

    If ciphertext is already v2, returns it as-is with success=True.
    If ciphertext is v1, decrypts with v1 and re-encrypts with v2.
    """
    old_version = detect_version(ciphertext)

    try:
        adapter = get_crypto_for_ciphertext(ciphertext)
        plaintext = adapter.decrypt(secret, ciphertext)
    except Exception as e:
        return MigrationResult(
            old_ciphertext=ciphertext.value,
            new_ciphertext="",
            old_version=old_version,
            new_version="v2",
            plaintext="",
            success=False,
            error=str(e),
        )

    if old_version == "v2":
        return MigrationResult(
            old_ciphertext=ciphertext.value,
            new_ciphertext=ciphertext.value,
            old_version="v2",
            new_version="v2",
            plaintext=plaintext,
            success=True,
        )

    v2_adapter = V2ModernAdapter()
    new_ct = v2_adapter.encrypt(secret, plaintext)

    return MigrationResult(
        old_ciphertext=ciphertext.value,
        new_ciphertext=new_ct.value,
        old_version="v1",
        new_version="v2",
        plaintext=plaintext,
        success=True,
    )


def scan_v1_ciphertexts(lines: list[str]) -> list[str]:
    """Scan lines for v1 ciphertexts (not starting with 'v2|')."""
    v1_ciphertexts = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("v2|"):
            v1_ciphertexts.append(stripped)
    return v1_ciphertexts


def batch_migrate(
    secret: str,
    ciphertexts: list[str],
) -> list[MigrationResult]:
    """Migrate a batch of ciphertexts from v1 to v2."""
    results = []
    for ct_str in ciphertexts:
        ct = Ciphertext(ct_str)
        result = migrate_ciphertext(secret, ct)
        results.append(result)
    return results
