# Validación final y muestra de auditoría de `persona.csv`

## Estado de ejecución

En la etapa de validación inicial, `persona-317279aafe9023a2` era una candidata no publicada. La sección final de este informe registra la publicación JSON posterior para uso interno con limitaciones semánticas. `data/persona.csv` permanece intacto y su SHA-256 es `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`.

La ejecución del 4 de octubre de 2026 preservó las 39.497 filas, las 275 columnas, el esquema y la secuencia de claves `(folio,nro)`. No encontró filas idénticas repetidas, claves repetidas ni componentes vacíos de clave. La conciliación independiente confirmó exactamente 12.516 celdas normalizadas por S-02 y 3 celdas modificadas por S-01; no detectó otras diferencias. Las 12.519 entradas de la bitácora concuerdan con el antes y después. Los 300 hashes registrados para artefactos de la candidata coinciden.

Los diez controles están en `PASS`. Esto valida integridad estructural, transformaciones declaradas y trazabilidad, no la veracidad de cada respuesta ni todos los dominios semánticos. Por existir diferencias entre el CSV local y el esquema F27, los problemas sin evidencia suficiente siguen pendientes; `PASS` por sí solo no equivale a certificación semántica completa ni activa el puntero de publicación.

## Muestra de control de calidad

Se seleccionaron 381 hogares de los 12.718 hogares observados, mediante estratos de departamento por área. La asignación tomó al menos 15 hogares por estrato poblado cuando el tamaño lo permitió y distribuyó el remanente proporcionalmente. Se incluyeron todas las filas persona de cada hogar seleccionado: 1.216 filas en total. La selección es determinista y usa una semilla derivada del SHA-256 del raw. El diseño y los pesos de selección por estrato están en `sample_design_RESTRICTED.csv`.

Esta muestra es una herramienta de QA, no un subconjunto que reemplace el maestro ni una muestra para estimaciones poblacionales o entrenamiento de modelos. La selección es estratificada y conglomerada por hogar; no se le atribuye automáticamente el margen de error de muestreo aleatorio simple. Los archivos con números de fila del CSV son restringidos porque permiten volver a registros originales, aunque no incluyan folio, número de persona ni respuestas.

## Observación intrahogar: `totper`

En la muestra, los valores observados de los campos candidatos a constantes del hogar fueron constantes dentro de los 381 hogares. Sin embargo, `totper` coincidió con el número de filas persona observadas en 69 hogares y difirió en 312; no hubo casos sin comparación disponible o ambiguos según el control. Es una señal de revisión, no prueba de error: `totper` es una extensión local que no figura en el esquema F27 y su definición/universo no está confirmado. La auditoría previa de todo el archivo también encontró concordancia en solo 2.433 de 12.718 hogares. Por ello se conserva el campo sin alteración y no se usa como conteo de miembros o denominador hasta resolver procedencia y definición. Las filas agrupadas por `folio` describen el roster presente en este CSV y no determinan por sí solas quién cuenta como miembro del hogar.

## Ejecución y pruebas

Comando ejecutado desde la raíz del proyecto con Python global 3.12.9:

```powershell
& 'C:\Users\julio\AppData\Local\Programs\Python\Python312\python.exe' data/proprosessing/final_validation_sampling.py --candidate data/proprosessing/output/20261004T231539Z_568e82e3039d_d3abfb0b5f --sample-households 381
```

La corrida quedó en `data/proprosessing/validation/20261004T235027Z_20261004T231539Z_568e82e3039d_d3abfb0b5f/`. Resultado agregado: 10 de 10 controles PASS, 381 hogares seleccionados, 1.216 filas persona, 18 estratos poblados y cero claves duplicadas en la muestra. La secuencia de claves de las filas seleccionadas coincide entre raw y candidata.

Pruebas automatizadas ejecutadas:

```powershell
& 'C:\Users\julio\AppData\Local\Programs\Python\Python312\python.exe' -m unittest discover -s tests -v
```

Resultado: **8/8 pruebas sintéticas aprobadas**. “Sintéticas” significa que esas pruebas usan registros pequeños inventados para comprobar comportamientos del código (por ejemplo, asignación reproducible y bloqueo de duplicados); no son filas de `persona.csv` ni resultados estadísticos del dataset. La corrida real sobre el CSV está documentada arriba por separado.

## Límites y artefactos

Solo se usó `data/persona.csv` y la candidata ya generada. Sin formularios originales, metadatos de procedencia confirmados o los otros archivos de la encuesta, no se pueden confirmar las respuestas verdaderas, todos los universos/saltos ni la interpretación de extensiones locales. No se eliminaron filas, columnas ni atípicos adicionales en esta etapa.

- `validation_results.json`: resultados agregados de los controles y diseño de muestra.
- `sample_design_RESTRICTED.csv`: asignaciones y pesos por estrato.
- `sampled_source_rows_RESTRICTED.csv`: correspondencia restringida a números de fila fuente, sin IDs de hogar/persona ni respuestas.
- `sample_internal_checks.csv`: diagnósticos agregados, solo para revisión.
- `artifact_hashes.json`: hashes de artefactos verificados.
- `data/proprosessing/final_validation_sampling.py`: implementación reproducible de la auditoría y selección.

## Publicación interna JSON — 4 de octubre de 2026

Tras la validación se publicó la copia inmutable en `data/proprosessing/versions/persona-317279aafe9023a2/`. El archivo CSV publicado conserva SHA-256 `317279aafe9023a2b17b8a7da69c87de75ea04e28d5c121cedc30b6392975ffc`, 39.497 filas y 275 columnas. El catálogo `data/audit_log.json` contiene el puntero `published_version_id`, el registro de versión y el evento `PUBLISH_VERSION` en una sustitución atómica del mismo JSON. El dashboard ahora resuelve esa versión a partir del catálogo y no selecciona la corrida más reciente en `output/`; las siete páginas principales respondieron HTTP 200 en la verificación.

La prueba de publicación con fixture sintética cubre publicación, reintento idempotente, bloqueo ante validación fallida y actualizaciones concurrentes de bitácora. La publicación real vuelve a ejecutar validación censal y verifica los 300 hashes de artefactos después de copiar la corrida. El estado queda explícitamente `published_internal_with_semantic_limitations`; los dominios y universos pendientes siguen restringidos a uso interno. La bitácora JSON local requiere permisos del sistema operativo y respaldo del catálogo junto a la carpeta de versiones.
