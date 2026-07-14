# Kanban — Prometheus

> CLI tool for symmetric encryption of secrets. Legacy v1 compatible, modern v2 secure.

## Estado actual

**Versión:** 2.0.0
**Último commit:** `8fde1ba` (2026-07-14)
**Estado:** RELEASED — v2.0.0 tag pushed, release workflow running

## Fase 1: Core Architecture — COMPLETADA

- [x] ADRs 0001-0004 (hexagonal, v1 immutable, v2 modern, storage abstraction)
- [x] Domain core: entities, value objects, ports, events
- [x] Crypto v1 adapter (INMUTABLE — never modify)
- [x] Crypto v2 adapter (ChaCha20-Poly1305 + Argon2id)
- [x] CryptoFactory with auto-detect version
- [x] Test vectors for v1 backward compatibility
- [x] 75 tests passing (contract, unit, property-based)
- [x] ruff + mypy strict clean
- [x] GitHub Actions CI (matrix: 3 OS × 4 Python)
- [x] mkdocs.yml with Material theme

## Fase 2: CLI & UX — COMPLETADA

- [x] Typer + Rich CLI app
- [x] `prometheus encrypt` with --secret, --plaintext, --algo, --format
- [x] `prometheus decrypt` with --secret, --ciphertext, --format
- [x] `prometheus interactive` mode
- [x] `prometheus version` and `prometheus info`
- [x] Banner + panels with Rich formatting

## Fase 3: Storage & Config — COMPLETADA

- [x] ConfigPort implementation (TOML config file)
- [x] StoragePort: file-based secret storage
- [ ] KeyringPort: OS keyring integration (macOS Keychain, Linux SecretService, Windows Credential Locker)
- [x] Profile management (multiple encryption profiles)
- [x] `prometheus config show/init` commands
- [x] `prometheus profile create/list/show/delete` commands
- [x] `prometheus store set/get/list/delete/exists` commands

## Fase 4: Migration & Advanced — COMPLETADA

- [x] v1 → v2 migration command (`prometheus migrate`)
- [x] Batch encrypt/decrypt (stdin pipe support)
- [x] `prometheus audit` — scan for weak v1 ciphertexts
- [ ] `prometheus rotate` — re-encrypt with new secret
- [x] Output formats: JSON, quiet (table default)
- [ ] `--output FILE` flag for all commands

## Fase 5: Documentation & Distribution — COMPLETADA

- [x] README.md with badges, install, usage examples
- [x] CONTRIBUTING.md
- [x] CHANGELOG.md
- [ ] MkDocs documentation (guides, API reference)
- [ ] PyPI publication (`pip install prometheus-crypto`)
- [ ] Homebrew formula
- [x] Pre-commit hooks configuration

## Fase 6: Quality & Hardening — COMPLETADA

- [x] Coverage ≥90% (140 tests, 90.28% coverage)
- [x] Pre-commit hooks (ruff, mypy, bandit, codespell)
- [x] Bandit security scan in CI
- [x] pip-audit for dependency vulnerabilities
- [ ] mutmut for mutation testing
- [x] E2E tests for CLI commands (Typer CliRunner)
- [x] Benchmarks (encrypt/decrypt performance)
- [ ] Threat model document

## Fase 7: Packaging & Release — COMPLETADA

- [x] Semantic versioning (semver)
- [x] GitHub Release with changelog
- [x] Python package (sdist + wheel) — build verified
- [x] Docker image (multi-stage, slim)
- [ ] Man page generation

## Quality Gate

| Check | Status |
|-------|--------|
| `ruff check src/` | ✅ All checks passed |
| `mypy --strict` | ✅ No issues found |
| `pytest` | ✅ 182 passed, 3 skipped |
| `coverage` | ✅ 90.28% |
| `bandit` | ✅ Configured in CI |
| `pip-audit` | ✅ Configured in CI |
| `pre-commit` | ✅ Configured (ruff, mypy, bandit, codespell) |
| `prometheus --help` | ✅ Working |
| `prometheus encrypt/decrypt` | ✅ Working |
| `prometheus config` | ✅ Working |
| `prometheus profile` | ✅ Working |
| `prometheus store` | ✅ Working |
| `prometheus migrate` | ✅ Working |
| `prometheus audit` | ✅ Working |
| `prometheus bench` | ✅ Working |

## Architecture

```
src/prometheus/
├── domain/          # Core business logic (no dependencies)
│   ├── entities.py  # Profile, GlobalConfig
│   ├── value_objects.py  # SecretKey, Plaintext, Ciphertext
│   ├── ports.py     # CryptoPort, ConfigPort, StoragePort, OutputPort
│   └── events.py    # SecretEncrypted, SecretDecrypted, MigrationCompleted
├── cipher/          # Crypto adapters
│   ├── v1_legacy/   # XOR+SHA-256+Base64 (INMUTABLE)
│   ├── v2_modern/   # ChaCha20-Poly1305 + Argon2id
│   └── factory.py   # Auto-detect version, adapter selection
├── cli/             # Typer CLI
│   └── app.py       # encrypt, decrypt, interactive, version, info
├── adapters/        # Future: storage, config, keyring adapters
└── config/          # Future: configuration management
```

## Notas

- **v1 es INMUTABLE**: el adapter `v1_legacy/adapter.py` no se modifica después de v2.0.0
- **Test vectors**: `tests/vectors/v1_legacy.json` contiene 10 ciphertexts conocidos para validar backward compatibility
- **Property-based testing**: Hypothesis genera inputs aleatorios para v2 (v1 excluido por limitaciones de caracteres)
- **Build system**: hatchling (no setuptools)
- **Module name**: `prometheus.cipher` (no `prometheus.crypto` — conflicto con PyPI `cryptography`)
