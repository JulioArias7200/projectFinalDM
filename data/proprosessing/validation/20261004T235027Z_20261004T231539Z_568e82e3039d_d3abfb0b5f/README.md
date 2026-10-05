# Validación final y muestra de auditoría de `persona.csv`

- Fecha UTC: 20261004T235027Z
- Candidata examinada: `data/proprosessing/output/20261004T231539Z_568e82e3039d_d3abfb0b5f`
- Versión candidata: `persona-317279aafe9023a2`
- Estado de controles automáticos: **PASSED**
- Filas/columnas: 39,497 × 275 (raw) y 39,497 × 275 (candidata).
- Hash SHA-256 raw: `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`

## Validación censal del archivo

- PASS — source hash matches manifest.
- PASS — candidate preserves 39,497 rows × 275 columns.
- PASS — schema and dimensions match raw.
- PASS — (folio,nro) sequence preserved.
- PASS — no exact duplicate rows in source.
- PASS — no duplicate candidate person keys.
- PASS — no blank candidate key components.
- PASS — only declared S-01/S-02 transformations exist.
- PASS — restricted cell audit matches raw and candidate.
- PASS — all candidate artifact hashes match.
- Celdas reconciliadas: 0;
  S-01: 3;
  S-02: 12516.
- Bitácora restringida: 12,519 entradas y coincidencia antes/después: True.
- Artefactos verificados por hash: 300/300.

## Muestra estratificada de control

Se seleccionaron 381 hogares de 12,718, estratificados por las combinaciones observadas de departamento y área; se incluyen todas las filas de persona de cada hogar seleccionado (1,216 filas). La asignación usa mínimo de 15 hogares por estrato poblado cuando el tamaño lo permite, y distribuye el resto proporcionalmente.
Semilla reproducible derivada del hash SHA-256: `6237066445484562714`. La muestra es para QA; no reemplaza ni reduce el maestro. El diseño se estratifica y agrupa por hogar, por lo que no se atribuye automáticamente el margen de error de una muestra aleatoria simple. Las probabilidades y pesos por estrato están en `sample_design_RESTRICTED.csv`.
El archivo `sampled_source_rows_RESTRICTED.csv` contiene números de fila del raw para inspección, sin claves ni respuestas. `sample_internal_checks.csv` informa consistencia intrahogar y la comparación exploratoria de `totper` con el roster observado; estos resultados son alertas, no reglas correctivas.

## Interpretación y límites

Los controles censales comprueban estructura, unicidad, preservación de claves, transformaciones declaradas, bitácora y hashes. La muestra permite revisar coherencia interna en hogares seleccionados. Como solo está disponible `persona.csv`, no es posible verificar que las respuestas coincidan con formularios originales ni confirmar todos los universos, dominios o valores verdaderos. Los problemas no decidibles se conservan como pendientes; no se eliminaron filas, columnas ni valores atípicos adicionales.
La candidata sigue sin publicarse. Un estado PASS certifica que se cumplieron los controles declarados aquí, no que cada respuesta observada sea verdadera o que el instrumento coincida con F27.

## Archivos

- `validation_results.json`: controles censales, linaje y tamaño de la muestra.
- `sample_design_RESTRICTED.csv`: asignación, probabilidades y pesos por estrato.
- `sampled_source_rows_RESTRICTED.csv`: filas seleccionadas del CSV fuente; tratar como restringido.
- `sample_internal_checks.csv`: conteos agregados de consistencia interna en la muestra.
