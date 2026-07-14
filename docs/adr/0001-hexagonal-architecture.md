# ADR 0001: Arquitectura Hexagonal (Ports & Adapters)

**Fecha**: 2026-07-14
**Estado**: Aceptado
**Autor**: NOVA

## Contexto
Prometheus ha crecido de un script monolítico a una herramienta CLI que necesita:
- Soportar múltiples algoritmos criptográficos (v1 legacy + v2 modern)
- Múltiples backends de almacenamiento (archivo, keyring OS, variables de entorno)
- Múltiples interfaces de salida (terminal rico, JSON, quiet)
- Configuración flexible (TOML, YAML, env vars)
- Testabilidad completa sin I/O real

## Decisión
Adoptar **Arquitectura Hexagonal** (Ports & Adapters) con:

### Dominio Puro (sin dependencias externas)
```
prometheus/domain/
├── entities/        # Secret, Ciphertext, Profile, AlgorithmVersion
├── ports/           # Protocolos: CryptoPort, ConfigPort, StoragePort, OutputPort
├── use_cases/       # EncryptSecret, DecryptSecret, MigrateV1toV2, RotateKey, GenerateKey
├── value_objects/   # SecretKey, Plaintext, Ciphertext, AlgorithmVersion
└── events/          # Domain events: SecretEncrypted, SecretDecrypted, MigrationCompleted
```

### Adaptadores (implementaciones concretas)
```
prometheus/adapters/
├── crypto/
│   ├── v1_legacy.py      # INMUTABLE - wrap crypto.py actual
│   ├── v2_modern.py      # XChaCha20-Poly1305 + Argon2id
│   └── factory.py        # Auto-detect version
├── config/
│   └── pydantic_toml.py  # Pydantic Settings + TOML
├── storage/
│   ├── file.py           # JSON/TOML file backend
│   ├── keyring.py        # OS keyring (macOS/Windows/Linux)
│   └── env.py            # Environment variables
├── cli/
│   ├── typer_app.py      # Typer + Rich console
│   └── formatters.py     # JSON, table, quiet, verbose
└── platform/
    └── keyring_backend.py
```

### CLI (Capa fina - solo wiring)
```
prometheus/cli/main.py    # Entry point, dependency injection
```

## Consecuencias

### Positivas
- **Testabilidad**: Domain 100% testeable sin mocks complejos
- **Swapping**: Cambiar crypto/storage/config sin tocar use cases
- **Extensibilidad**: Nuevos algoritmos/backends = nuevos adaptadores
- **Separación de responsabilidades**: Cada capa tiene un único motivo de cambio

### Negativas
- **Complejidad inicial**: Más archivos, más abstracciones
- **Curva de aprendizaje**: Equipo debe entender puertos/adaptadores

### Neutrales
- Requiere inyección de dependencias (usar `dependency-injector` o manual)
- Tests de contrato obligatorios para cada puerto

## Implementación
1. Crear protocolos en `domain/ports/`
2. Implementar adaptadores en `adapters/`
3. Use cases en `domain/use_cases/` reciben puertos por constructor
4. CLI hace wiring en `main.py`
5. Tests de contrato para cada puerto