# ADR 0004: Abstracción de Almacenamiento (Storage Ports)

**Fecha**: 2026-07-14
**Estado**: Aceptado
**Autor**: NOVA

## Contexto
Usuarios necesitan almacenar secretos/cifrados de forma distinta:
- **Desarrollo local**: archivo TOML/JSON en `~/.config/prometheus/`
- **Producción/CI**: OS keyring (macOS Keychain, Windows Credential Manager, libsecret)
- **Ephemeral**: variables de entorno
- **Equipos**: vault compartido (HashiCorp Vault, 1Password CLI, Bitwarden CLI) — futuro

El core no debe conocer detalles de almacenamiento.

## Decisión
**Puerto `StoragePort` + Adaptadores** (Strategy Pattern / Adapter Pattern)

### Interfaz (Port)
```python
# src/prometheus/core/ports/storage.py
from abc import ABC, abstractmethod
from typing import Protocol

class StoragePort(Protocol):
    """Puerto de almacenamiento — implementado por adaptadores."""
    
    def get_secret(self, name: str) -> str | None:
        """Obtiene secreto descifrado por nombre. None si no existe."""
        ...
    
    def store_secret(self, name: str, plaintext: str) -> None:
        """Cifra y almacena secreto."""
        ...
    
    def delete_secret(self, name: str) -> bool:
        """Elimina secreto. Retorna True si existía."""
        ...
    
    def list_secrets(self) -> list[str]:
        """Lista nombres de secretos almacenados."""
        ...
    
    def exists(self, name: str) -> bool:
        """Verifica existencia sin descifrar."""
        ...
```

### Adaptadores (Implementaciones)

#### 1. `FileStorageAdapter` — Archivo local (TOML)
```python
# src/prometheus/adapters/storage/file.py
class FileStorageAdapter:
    def __init__(self, path: Path, crypto: CryptoPort, profile: Profile):
        self.path = path
        self.crypto = crypto
        self.profile = profile
    
    def store_secret(self, name: str, plaintext: str) -> None:
        # Lee archivo, actualiza dict, cifra con crypto, escribe TOML
        data = self._load()
        ciphertext = self.crypto.encrypt(self.profile.secret, plaintext)
        data[name] = {"ciphertext": ciphertext, "version": "v2"}
        self._save(data)
```

#### 2. `KeyringStorageAdapter` — OS Keyring
```python
# src/prometheus/adapters/storage/keyring.py
import keyring

class KeyringStorageAdapter:
    SERVICE_NAME = "prometheus"
    
    def __init__(self, crypto: CryptoPort, profile: Profile):
        self.crypto = crypto
        self.profile = profile
    
    def store_secret(self, name: str, plaintext: str) -> None:
        ciphertext = self.crypto.encrypt(self.profile.secret, plaintext)
        # keyring guarda string — almacenamos JSON con metadata
        import json
        payload = json.dumps({"ciphertext": ciphertext, "version": "v2"})
        keyring.set_password(self.SERVICE_NAME, f"{self.profile.name}:{name}", payload)
    
    def get_secret(self, name: str) -> str | None:
        payload = keyring.get_password(self.SERVICE_NAME, f"{self.profile.name}:{name}")
        if not payload:
            return None
        import json
        data = json.loads(payload)
        return self.crypto.decrypt(self.profile.secret, data["ciphertext"])
```

#### 3. `EnvStorageAdapter` — Variables de Entorno
```python
# src/prometheus/adapters/storage/env.py
class EnvStorageAdapter:
    PREFIX = "PROMETHEUS_SECRET_"
    
    def __init__(self, crypto: CryptoPort, profile: Profile):
        self.crypto = crypto
        self.profile = profile
    
    def store_secret(self, name: str, plaintext: str) -> None:
        ciphertext = self.crypto.encrypt(self.profile.secret, plaintext)
        os.environ[f"{self.PREFIX}{name.upper()}"] = ciphertext
    
    def get_secret(self, name: str) -> str | None:
        ciphertext = os.environ.get(f"{self.PREFIX}{name.upper()}")
        if not ciphertext:
            return None
        return self.crypto.decrypt(self.profile.secret, ciphertext)
```

### Selección de Backend (Storage Manager)
```python
# src/prometheus/adapters/storage/manager.py
class StorageManager:
    def __init__(self, config: Config):
        self.config = config
    
    def get_backend(self, profile: Profile) -> StoragePort:
        backend_type = profile.storage or self.config.global.storage
        
        match backend_type:
            case "file":
                return FileStorageAdapter(
                    Path(profile.file_path or self.config.global.file_path),
                    self._get_crypto(profile),
                    profile
                )
            case "keyring":
                return KeyringStorageAdapter(
                    self._get_crypto(profile),
                    profile
                )
            case "env":
                return EnvStorageAdapter(
                    self._get_crypto(profile),
                    profile
                )
            case _:
                raise ValueError(f"Unknown storage backend: {backend_type}")
```

## Configuración (Profile)
```toml
# ~/.config/prometheus/config.toml
[global]
default_profile = "personal"
algorithm = "v2"
storage = "keyring"        # default global

[profiles.personal]
secret = "..."             # o prompt/keyring reference
algorithm = "v2"
storage = "file"           # override
file_path = "~/.config/prometheus/personal.toml"

[profiles.production]
secret = "..."             
algorithm = "v2"
storage = "keyring"        # OS keyring
```

## Consecuencias
| Aspecto | Impacto |
|---------|---------|
| **Testabilidad** | Core usa `StoragePort` protocol — mock trivial en tests |
| **Extensibilidad** | Nuevo backend = nueva clase implementando `StoragePort` |
| **Seguridad** | Keyring usa OS secure storage; file usa permisos 600 |
| **UX** | CLI: `prometheus config storage set keyring` |
| **Migración** | `prometheus migrate storage --from file --to keyring` |

## Seguridad
- **File adapter**: `chmod 600` al crear; warning si permisos > 600
- **Keyring adapter**: No guarda secret en texto plano — solo ciphertext
- **Env adapter**: Solo para CI/ephemeral — documentar riesgos

## Implementación
1. Protocol `StoragePort` en `core/ports/storage.py`
2. 3 adaptadores en `adapters/storage/`
3. `StorageManager` factory en `adapters/storage/manager.py`
4. Integración en `UseCases` (EncryptSecret, DecryptSecret, etc.)
5. CLI commands: `config storage`, `migrate storage`