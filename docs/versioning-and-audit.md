# Versiones y bitácora JSON

## Decisión e implementación vigentes

La persistencia de catálogo y eventos es JSON local, según la decisión del usuario. No se utiliza PostgreSQL. `data/audit_log.json` es el documento de catálogo: contiene versiones, el puntero `published_version_id` y una lista append-only de eventos. Las salidas de datos se guardan como archivos inmutables, no dentro del JSON.

La versión publicada actualmente es `persona-317279aafe9023a2`, estado `published_internal_with_semantic_limitations`. Se encuentra en `data/proprosessing/versions/persona-317279aafe9023a2/`. El maestro CSV contiene 39.497 × 275 y su hash es `317279aafe9023a2b17b8a7da69c87de75ea04e28d5c121cedc30b6392975ffc`. La candidata original sigue preservada en `output/`.

## Publicación

El comando `data/proprosessing/publish_validated_candidate.py` ejecuta la validación censal sobre la candidata. Rechaza cualquier control fallido; revisa esquema, filas, clave, diffs S-01/S-02, bitácora restringida y hashes. Después:

1. Copia la corrida completa a un directorio staging dentro de `versions/`.
2. Comprueba de nuevo los hashes de todos los artefactos del manifiesto.
3. Añade a una copia del manifiesto el resultado y estado semántico limitado.
4. Renombra staging a su ID de versión sin reemplazar carpetas existentes.
5. Bajo lock de archivo, actualiza el puntero, registra la versión y agrega `PUBLISH_VERSION` en una sola sustitución atómica de `audit_log.json`.

Una candidata inválida no cambia el puntero. Si el proceso termina después del cambio de nombre y antes de escribir el catálogo, el directorio queda huérfano y no se considera publicado. El reintento de la versión ya publicada devuelve la carpeta existente sin agregar eventos duplicados.

Comando ejecutado para la versión actual:

```powershell
python data/proprosessing/publish_validated_candidate.py --candidate data/proprosessing/output/20261004T231539Z_568e82e3039d_d3abfb0b5f --actor project_owner
```

El dashboard resuelve exclusivamente la versión del puntero JSON. Las candidatas sin registro no se presentan como publicadas.

## Bitácora y datos sensibles

Cada evento contiene ID, fecha UTC, actor, acción, entidad y detalles agregados. El servicio agrega eventos bajo un lock entre procesos y reemplaza JSON atómicamente; rechaza documentos JSON corruptos en actualizaciones para evitar sobrescribirlos con valores vacíos. El registro actual conserva eventos anteriores y agrega el evento real de publicación.

No registrar filas persona, respuestas sensibles ni valores antes/después en el catálogo. La bitácora de cambios por celda está en `semantic_cell_changes_restricted.csv`, dentro del artefacto versionado; controlar acceso al directorio `data/`. JSON local no implementa por sí mismo roles: autenticación, autorización por acción y protección de exportaciones siguen pendientes.

## Alcance y limitaciones operativas

Las escrituras se serializan con un archivo `.lock` creado de forma exclusiva; una terminación abrupta puede dejarlo y requerir revisión manual. Esta solución está orientada a una instancia local. No ofrece transacciones distribuidas, alta disponibilidad, recuperación automática de trabajos ni coordinación entre varias máquinas. Respaldar juntos `data/audit_log.json` y `data/proprosessing/versions/`; probar la restauración del respaldo antes de confiar en ella.

Una corrección futura debe derivarse como versión nueva con regla/evidencia, nunca editar la versión publicada en sitio. Restaurar también significa publicar otra versión derivada, sin eliminar eventos ni artefactos anteriores.
