# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ConfigPort adapter (TOML config file)
- StoragePort adapter (file-based secret storage)
- Profile management (multiple encryption profiles)
- CLI commands: `config`, `profile`, `store`, `migrate`, `audit`
- v1→v2 migration with dry-run support
- stdin pipe support for encrypt/decrypt
- Audit command for scanning weak v1 ciphertexts
- JSON and quiet output formats
- CONTRIBUTING.md
- CHANGELOG.md

### Changed
- Refactored to hexagonal architecture
- Renamed module from `prometheus.crypto` to `prometheus.cipher`
- Moved to src layout (`src/prometheus/`)
- Switched to hatchling build backend

### Deprecated
- None

### Removed
- None

### Fixed
- None

### Security
- v1 crypto is now immutable and clearly marked as legacy
- v2 uses ChaCha20-Poly1305 + Argon2id (modern, secure)

## [1.0.0] - 2026-07-14

### Added
- Initial release
- Crypto v1 (XOR + SHA-256 + Base64)
- Basic CLI encrypt/decrypt
