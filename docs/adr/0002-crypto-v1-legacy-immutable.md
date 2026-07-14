# ADR 0002: Soporte Legacy Crypto v1 — INMUTABLE

**Fecha**: 2026-07-14
**Estado**: Aceptado
**Autor**: NOVA

## Contexto
Usuarios existentes tienen contraseñas cifradas con el algoritmo v1 actual (XOR + SHA256 + Base64/latin1). **Cualquier cambio que rompa descifrado v1 es inaceptable** — rompemos confianza y datos.

## Decisión
**El adaptador v1 (`V1LegacyAdapter`) es INMUTABLE** una vez implementado y testeado.

### Reglas de Oro
1. **Nunca modificar** `prometheus/adapters/crypto/v1_legacy.py` después de `v2.0.0`
2. **Nunca modificar** vectores de prueba en `tests/vectors/v1_legacy.json`
3. **Factory default**: v2 para *nuevos* cifrados; v1 solo para *descifrar* existentes
4. **Detección automática**: payloads sin byte de versión = v1 legacy

### Formato v1 Legacy (actual)
```python
# Salida actual: base64(latin1(xor_sha256(password, secret)))
# Sin prefijo, sin versión, sin metadatos
# Ejemplo: "g/u55oK9j97hrpeX+w=="
```

### Estrategia de Detección en Factory
```python
def detect_version(ciphertext: str) -> AlgorithmVersion:
    try:
        decoded = base64.b64decode(ciphertext)
        if decoded and decoded[0] == 0x02:  # v2 magic byte
            return AlgorithmVersion.V2_MODERN
    except Exception:
        pass
    return AlgorithmVersion.V1_LEGACY  # Default: asume v1
```

## Vectores de Prueba Congelados (OBLIGATORIOS)
Archivo: `tests/vectors/v1_legacy.json`
```json
{
  "algorithm": "v1_xor_sha256_base64_latin1",
  "description": "Known-answer tests for legacy v1 algorithm. NEVER MODIFY.",
  "vectors": [
    {"secret": "testkey", "plaintext": "mipassword123", "ciphertext": "g/u55oK9j97hrpeX+w=="},
    {"secret": "secret123", "plaintext": "mipassword", "ciphertext": "wqnD47rSvubc8w=="},
    {"secret": "mysecret", "plaintext": "pass", "ciphertext": "hvDd4A=="}
  ]
}
```

## Tests de Contrato v1
```python
# tests/contract/test_crypto_port.py
def test_v1_legacy_adapter_conforms_to_crypto_port(v1_adapter, v1_vectors):
    for vec in v1_vectors:
        # Encrypt (v1 no se usa para nuevos, pero debe funcionar)
        result = v1_adapter.encrypt(vec["secret"], vec["plaintext"])
        assert isinstance(result, str)
        
        # Decrypt DEBE funcionar con vectores oficiales
        decrypted = v1_adapter.decrypt(vec["secret"], vec["ciphertext"])
        assert decrypted == vec["plaintext"]
```

## Consecuencias
- **Mantenimiento**: v1 legacy permanece para siempre como adaptador de compatibilidad
- **Seguridad**: v1 NO es seguro para nuevos datos — documentación clara + warning en CLI
- **Migración**: Use case `MigrateV1toV2` re-encripta con v2 explícitamente

## Implementación
1. Copiar `prometheus/crypto.py` actual → `prometheus/adapters/crypto/v1_legacy.py` (wrapper)
2. Crear `tests/vectors/v1_legacy.json` con vectores actuales
3. Implementar `CryptoPort` protocol
4. Tests de contrato + property-based (hypothesis)
5. Marcar archivo como `final` en tipo hint / docstring