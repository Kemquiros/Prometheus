# ADR 0003: Crypto v2 Moderno — XChaCha20-Poly1305 + Argon2id

**Fecha**: 2026-07-14
**Estado**: Aceptado
**Autor**: NOVA

## Contexto
Necesitamos un algoritmo moderno, auditado y seguro para nuevos cifrados. Requisitos:
- **AEAD** (Authenticated Encryption with Associated Data)
- **Resistente a ataques de canal lateral** (const-time)
- **KDF resistente a GPU/ASIC** (Argon2id)
- **Nonce misuse resistant** (XChaCha20 > AES-GCM)
- **Librería estándar**: `cryptography` (auditada, wheels universales)

## Decisión
**XChaCha20-Poly1305 + Argon2id** via `cryptography.hazmat.primitives`

### Especificación v2
```
Payload v2 = version_byte || salt || nonce || ciphertext || tag
             1 byte       16 bytes   24 bytes   N bytes     16 bytes
```

| Campo | Tamaño | Descripción |
|-------|--------|-------------|
| `version` | 1 byte | `0x02` (magic byte) |
| `salt` | 16 bytes | Random por cifrado (Argon2id salt) |
| `nonce` | 24 bytes | Random por cifrado (XChaCha20 nonce) |
| `ciphertext` | variable | Plaintext cifrado |
| `tag` | 16 bytes | Poly1305 authentication tag |

### Derivación de Clave (KDF)
```python
# Argon2id parameters (OWASP 2024 recommendations)
argon2 = Argon2id(
    salt=salt,           # 16 bytes random
    time_cost=3,         # iterations
    memory_cost=65536,   # 64 MB
    parallelism=4,       # threads
    hash_length=32       # 256-bit key
)
key = argon2.derive(secret.encode('utf-8'))
```

### Cifrado (Encrypt)
```python
from cryptography.hazmat.primitives.ciphers.aead import XChaCha20Poly1305

aead = XChaCha20Poly1305(key)
ciphertext_with_tag = aead.encrypt(nonce, plaintext.encode(), associated_data=None)
# ciphertext_with_tag = ciphertext || tag (16 bytes appended)
```

### Formato Serializado
```python
payload = b'\x02' + salt + nonce + ciphertext_with_tag
return base64.b64encode(payload).decode('ascii')
# Ejemplo v2: "AqX..." (empieza con 'A' = 0x02 en base64)
```

### Descifrado (Decrypt)
```python
decoded = base64.b64decode(ciphertext)
version = decoded[0]
assert version == 0x02

salt = decoded[1:17]
nonce = decoded[17:41]
ciphertext_with_tag = decoded[41:]

key = argon2.derive(secret.encode('utf-8'))
aead = XChaCha20Poly1305(key)
plaintext = aead.decrypt(nonce, ciphertext_with_tag, None)
return plaintext.decode('utf-8')
```

## Parámetros Argon2id (OWASP 2024)
| Parámetro | Valor | Rationale |
|-----------|-------|-----------|
| `time_cost` | 3 | Balance CPU/latencia |
| `memory_cost` | 65536 (64 MB) | Resistente GPU, usable en CI |
| `parallelism` | 4 | Multi-core moderno |
| `hash_length` | 32 | 256-bit key para XChaCha20 |

## Dependencia
```toml
[project.optional-dependencies]
crypto = ["cryptography>=42.0", "argon2-cffi>=23.0"]
```
> `argon2-cffi` usa `argon2` C library (wheels manylinux/macos/win). No compila Rust.

## Fallback para Entornos Sin Argon2
Si `argon2-cffi` falla (entornos extraños), fallback documentado a **PBKDF2-HMAC-SHA256**:
```python
# Fallback ONLY — logged warning
key = hashlib.pbkdf2_hmac('sha256', secret.encode(), salt, 600000, dklen=32)
```
> Documentar en CLI: `--kdf pbkdf2` para forzar fallback.

## Test Vectors (RFC 8439 + Argon2 RFC 9106)
Usar vectores oficiales + generar propios para integración.

## Consecuencias
- **Seguridad**: AEAD moderno, forward secrecy por salt/nonce aleatorios
- **Performance**: ~1-2ms por operación en CPU moderno
- **Compatibilidad**: `cryptography` wheels en todas las plataformas
- **Auditoría**: Algoritmos estándar IETF/RFC

## Implementación
1. `prometheus/adapters/crypto/v2_modern.py` implementando `CryptoPort`
2. Tests: unit (vectors), property-based (hypothesis), integration
3. Factory: auto-detect v1 vs v2 por magic byte
4. CLI flag: `--algo v1|v2|auto` (default: auto=v2 para encrypt)