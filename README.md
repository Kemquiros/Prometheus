# Prometheus

[![CI](https://github.com/Kemquiros/Prometheus/actions/workflows/ci.yml/badge.svg)](https://github.com/Kemquiros/Prometheus/actions)
[![Python](https://img.shields.io/pypi/pyversions/prometheus-crypto)](https://pypi.org/project/prometheus-crypto/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

World-class CLI for symmetric encryption of secrets. Legacy v1 compatible, modern v2 secure.

## Features

- **Crypto v2 (recommended):** ChaCha20-Poly1305 + Argon2id — authenticated encryption with forward secrecy
- **Crypto v1 (legacy):** XOR + SHA-256 + Base64 — backward compatible, NOT recommended for new encryption
- **Auto-detect:** Automatically detects algorithm version from ciphertext format
- **Interactive mode:** Guided prompts for encrypt/decrypt operations
- **Multiple output formats:** Human-readable panels, JSON, quiet mode

## Install

```bash
pip install prometheus-crypto
```

Or with optional Argon2id support (recommended):

```bash
pip install "prometheus-crypto[crypto]"
```

## Quick Start

### Encrypt

```bash
# Interactive mode
prometheus encrypt --secret "my-secret-key" --plaintext "password123"

# JSON output
prometheus encrypt --secret "my-secret-key" --plaintext "password123" --format json

# Quiet output (just the ciphertext)
prometheus encrypt --secret "my-secret-key" --plaintext "password123" --format quiet

# Force v1 legacy algorithm
prometheus encrypt --secret "my-secret-key" --plaintext "password123" --algo v1
```

### Decrypt

```bash
# Auto-detect version from ciphertext
prometheus decrypt --secret "my-secret-key" --ciphertext "v2|salt|nonce|ct|tag"

# JSON output
prometheus decrypt --secret "my-secret-key" --ciphertext "v2|salt|nonce|ct|tag" --format json
```

### Interactive Mode

```bash
prometheus interactive
```

```
Choose operation:
  (e) Encrypt
  (d) Decrypt
  (v) Show version
  (f) Finish
>> e
Secret: my-secret-key
Password: password123
┌─────────────── Encrypted ───────────────┐
│ v2|...                                  │
└──────────────── algorithm: v2 ──────────┘
```

### Version & Info

```bash
prometheus version    # Algorithm info
prometheus info       # Full architecture details
```

## Architecture

```
src/prometheus/
├── domain/          # Core business logic (no dependencies)
│   ├── entities.py  # Profile, GlobalConfig
│   ├── value_objects.py  # SecretKey, Plaintext, Ciphertext
│   ├── ports.py     # CryptoPort, ConfigPort, StoragePort, OutputPort
│   └── events.py    # Domain events
├── cipher/          # Crypto adapters
│   ├── v1_legacy/   # XOR + SHA-256 + Base64 (INMUTABLE)
│   ├── v2_modern/   # ChaCha20-Poly1305 + Argon2id
│   └── factory.py   # Auto-detect version, adapter selection
├── cli/             # Typer + Rich CLI
│   └── app.py       # encrypt, decrypt, interactive, version, info
└── adapters/        # Future: storage, config, keyring adapters
```

Hexagonal architecture (Ports & Adapters):
- **Domain** is pure business logic with zero I/O dependencies
- **Ports** define interfaces (CryptoPort, ConfigPort, StoragePort, OutputPort)
- **Adapters** implement those interfaces for concrete technologies

## Security

### v2 (Recommended)

- **Key derivation:** Argon2id (OWASP 2024: 3 iterations, 64MB memory, 4 parallelism)
- **Fallback:** PBKDF2-SHA256 (600k iterations) if argon2-cffi is not installed
- **Encryption:** ChaCha20-Poly1305 AEAD (12-byte nonce, 16-byte tag)
- **Forward secrecy:** Random salt + nonce per encryption
- **Format:** `v2|salt_b64|nonce_b64|ciphertext_b64|tag_b64`

### v1 (Legacy)

- **NOT cryptographically secure**
- XOR + SHA-256 + Base64/latin1 encoding
- Retained solely for backward compatibility with existing v1 ciphertexts
- **Do not use for new encryption** — use v2 instead

## Development

### Setup

```bash
git clone https://github.com/Kemquiros/Prometheus.git
cd Prometheus
python -m venv .venv
source .venv/bin/activate
pip install -e ".[crypto,dev]"
```

### Quality

```bash
ruff check src/ tests/         # Lint
mypy src/prometheus/ --strict  # Type check
pytest tests/ -v               # Tests
```

### Test Coverage

```bash
pytest tests/ --cov=prometheus --cov-report=term-missing
```

Coverage threshold: 90% (enforced in CI).

## License

MIT — see [LICENSE.md](LICENSE.md)
