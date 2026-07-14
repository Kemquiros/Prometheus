# Contributing to Prometheus

Thank you for your interest in contributing to Prometheus! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip or poetry

### Setup

```bash
# Clone the repository
git clone https://github.com/Kemquiros/Prometheus.git
cd Prometheus

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

# Install in development mode
pip install -e ".[crypto,dev]"

# Install pre-commit hooks
pre-commit install
```

## Code Style

- **Formatter:** Ruff (configured in `pyproject.toml`)
- **Linter:** Ruff
- **Type Checker:** mypy (strict mode)
- **Line Length:** 100 characters max

Run all checks before committing:

```bash
ruff check src/ tests/
mypy src/prometheus/
pytest tests/
```

## Testing

We use pytest with the following structure:

```
tests/
├── contract/       # Contract tests for ports
├── unit/          # Unit tests
│   ├── cipher/    # Crypto adapter tests
│   ├── config/    # Config adapter tests
│   ├── storage/   # Storage adapter tests
│   ├── migration/ # Migration tests
│   └── domain/    # Domain entity tests
├── integration/   # Integration tests
└── vectors/       # Test vectors
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=prometheus

# Run specific test category
pytest -m unit
pytest -m integration
pytest -m contract
```

### Test Requirements

- All new features must include tests
- Maintain or improve code coverage (currently >90%)
- Use property-based testing (Hypothesis) for crypto code
- Test vectors must be frozen for backward compatibility

## Architecture

Prometheus follows hexagonal architecture (Ports & Adapters):

- **Domain** (`src/prometheus/domain/`): Core business logic, no I/O dependencies
- **Ports** (`src/prometheus/domain/ports.py`): Interfaces for external systems
- **Adapters** (`src/prometheus/*/adapter.py`): Implementations of ports
- **CLI** (`src/prometheus/cli/`): Typer-based command interface

### Key Principles

1. **v1 is immutable:** Never modify `src/prometheus/cipher/v1_legacy/` after v2.0.0
2. **Ports before implementations:** Define interfaces first
3. **Test the contract:** Port tests ensure adapter compatibility

## Commit Messages

Use conventional commits:

```
feat: add new feature
fix: bug fix
docs: documentation changes
test: add or modify tests
refactor: code refactoring
chore: maintenance tasks
```

Example:

```
feat: add keyring adapter for macOS Keychain

- Implement KeyringPort interface
- Add tests for macOS Keychain backend
- Update pyproject.toml with keyring dependency
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes
3. Run all checks (lint, type, tests)
4. Update documentation if needed
5. Submit PR with clear description

### PR Checklist

- [ ] Tests pass (`pytest`)
- [ ] Linter passes (`ruff check src/ tests/`)
- [ ] Type checker passes (`mypy src/prometheus/`)
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if applicable)

## Security

- Never commit secrets or credentials
- Use `bandit` to scan for security issues
- Report vulnerabilities via GitHub Security Advisories

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
