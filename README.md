# Limpieza y bitácora JSON de `persona.csv`

Proyecto de minería de datos para preparar `data/persona.csv` mediante pipeline Python y una interfaz Flask. Por decisión del usuario, la persistencia de versiones y eventos usa JSON local; no depende de PostgreSQL. Las reglas se fundamentan en `curso/` y en el diccionario disponible. El archivo fuente es de solo lectura.

## Estado

La versión técnica validada `persona-317279aafe9023a2` conserva 39.497 filas y 275 columnas. Está publicada para uso interno mediante el catálogo JSON, con limitaciones semánticas explícitas. S-01 marcó como inválidas tres celdas con más de 168 horas semanales; S-02 normalizó 12.516 respuestas en 13 columnas abiertas definidas; la auditoría L-06 no encontró duplicados y no eliminó filas. No se imputaron datos ni se quitaron columnas por ausencia global.

La auditoría estructural y de artefactos pasó 10/10 controles; la suite tiene 11 pruebas aprobadas. Esto no certifica la semántica de las 275 columnas: `totper`, dominios, universos y discrepancias de procedencia siguen documentados como pendientes. La publicación es interna y no respalda inferencias oficiales.

- CSV publicado: `data/proprosessing/versions/persona-317279aafe9023a2/persona_clean_master.csv`
- Parquet de la misma versión: `data/proprosessing/versions/persona-317279aafe9023a2/persona_clean_master.parquet`
- Catálogo y bitácora JSON: `data/audit_log.json`
- Validación y muestreo: `docs/final-validation-sampling-persona.md`
- Dictamen semántico: `docs/semantic-cleaning-audit.md`

## Ejecutar

Desde la raíz, con Python 3.11+ y dependencias del proyecto instaladas:

```powershell
python data/proprosessing/preprocessing.py
python data/proprosessing/publish_validated_candidate.py --candidate data/proprosessing/output/<run_id>
python dashboard/app.py
```

La publicación vuelve a ejecutar las verificaciones censales, copia toda la corrida a una carpeta de versión inmutable y activa el puntero JSON mediante escritura atómica. El dashboard consume solo la versión registrada en `data/audit_log.json`, no una carpeta candidata elegida por fecha. No se sobrescribe el raw ni una versión anterior.

Las pruebas usan fixtures inventadas, nunca registros reales:

```powershell
python -m unittest discover -s tests -v
```

## Alcance semántico

El usuario confirmó `persona.csv` como el único microdato de trabajo. El diccionario F27 disponible no coincide exactamente en casos/columnas con esta copia; `totper` es una extensión local y no tiene definición confirmada. Las observaciones sin decisión concluyente se preservan. Ver [metodología](docs/cleaning-methodology.md), [contrato](docs/data-contract.md), [progreso](docs/progress.md) y [arquitectura JSON](docs/architecture.md).

## Documentación

| Documento | Contenido |
|---|---|
| [Requisitos](docs/requirements.md) | Comportamiento esperado y reglas de datos |
| [Criterios de aceptación](docs/acceptance-criteria.md) | Verificaciones y estado |
| [Trazabilidad](docs/versioning-and-audit.md) | Versiones y eventos persistidos en JSON |
| [Análisis exploratorio](docs/exploratory-analysis-persona.md) | Perfiles y análisis por variable/universo |
| [Escenarios de prueba](docs/test-scenarios.md) | Casos sintéticos y reales documentados |

La próxima etapa del dashboard está especificada en [la propuesta de análisis por universos](docs/dashboard-universe-plan.md). Es una decisión documentada, todavía no implementada como cálculos estadísticos dinámicos.

## Límites de operación

El catálogo JSON está pensado para uso local y una instancia de aplicación. Es una escritura atómica de un archivo, no una base transaccional distribuida. Protege eventos contra edición/borrado desde el servicio, pero permisos del sistema operativo y copias de seguridad del directorio `data/` siguen siendo responsabilidad del entorno. El dashboard no cuenta todavía con autenticación completa ni aprobación multiusuario de cambios.
