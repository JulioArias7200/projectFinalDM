# Vistas temáticas derivadas de `persona.csv`

## Propósito y criterio estadístico

Las vistas reducen columnas y, cuando hay un universo DDI suficientemente claro, limitan filas a ese universo. No reemplazan al maestro de persona, no corrigen la fuente y no representan muestras independientes. La entrada es exclusivamente `data/persona.csv`; las vistas se derivan de la salida maestra candidata de la misma ejecución y llevan su `run_id`, `version_id` y SHA-256.

El esquema F27 consultado declara 39.485 casos y 276 variables; la copia local tiene 39.497 filas y 275 columnas. Las etiquetas y reglas oficiales son evidencia para interpretar la copia, pero no eliminan esta diferencia de procedencia. Ninguna vista se certifica para estimación inferencial. Se retienen `factor`, `estrato` y `upm` en las vistas de persona como contexto del diseño; su presencia no acredita que el diseño completo o la varianza estén implementados. Las estimaciones de subpoblación deben calcularse como dominio de encuesta con el procedimiento compatible con el diseño, no como una muestra nueva sin sus estratos/conglomerados.

Las preguntas tienen cortes y saltos. Por ello salud general, ingresos no laborales e ingresos/pobreza se entregan en filas-persona completas, y se exige interpretar ausencia por variable/universo. Las vistas filtradas declaran el criterio y denominador. No se eliminan columnas por ausencia global >80 %.

## Vistas generadas

Ubicación de esta versión: `data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f/thematic_views/`.

| Archivo | Unidad/filas | Criterio y uso |
|---|---:|---|
| `demografia_persona.csv` | Persona, 39.497 | `s01*`, claves y diseño muestral; conserva el universo completo. |
| `salud_general_persona.csv` | Persona, 39.497 | `s02a_*` más edad/sexo y contexto; mantiene a todos porque el módulo general es universal. |
| `salud_fecundidad_mujeres_13_50.csv` | Persona, 11.328 | `s01a_02 = 2` y `s01a_03` entre 13 y 50 inclusive; universo DDI de fecundidad. |
| `salud_asistencia_infantil_menores_6.csv` | Persona, 3.434 | Edad `s01a_03 < 6`; vista para el submódulo de asistencia infantil. |
| `salud_bono_menores_5.csv` | Persona, 2.781 | Edad `s01a_03 < 5`; vista del submódulo infantil, respetando filtros más específicos por pregunta. |
| `educacion_personas_4_mas.csv` | Persona, 37.354 | Edad `s01a_03 >= 4`; universos internos de inasistencia/TIC pueden ser más estrechos. |
| `empleo_personas_7_mas.csv` | Persona, 35.366 | Edad `s01a_03 >= 7`; los campos de ocupación/ingresos tienen filtros adicionales. |
| `empleo_secundario_casos.csv` | Persona, 1.357 | Incluye 1.356 respuestas afirmativas `s04e_25 = 1` y un caso con `s04e_26_cod` informado pese al filtro negativo. La excepción se marca `reported_data_with_negative_filter_review`, no se corrige ni oculta. Solo los casos elegibles confirmados sirven para estimaciones del módulo. |
| `ingresos_no_laborales_persona.csv` | Persona, 39.497 | Variables `s05*` con todos los registros; los universos por fuente de ingreso son variables. No implica agregación de hogar. |
| `ingresos_pobreza_persona.csv` | Persona, 39.497 | Variables personales y del hogar lado a lado. `yhog`, `yhogpc` y los indicadores pueden repetirse por persona; no promediar ni contar como observaciones de hogar. |
| `hogar_resumen_persona_candidato.csv` | Hogar (`folio`), 12.718 | Una fila por folio. Incluye valores no faltantes únicos por hogar más `person_records_in_source`, que cuenta filas del CSV y no sustituye a `totper`. `factor` se omite porque es ponderador de persona. |

## Control de conflictos a nivel de hogar

La validación correcta trata `NA`, vacío y tokens declarados faltantes como ausencias, no como valores observados diferentes. No se encontraron hogares con dos valores observados distintos en los campos candidatos; `household_field_conflicts.csv` se conserva como informe agregado (vacío en esta corrida). Para nueve campos (`totper`, `yhog`, `yhogpc`, `p0`, `p1`, `p2`, `pext0`, `pext1`, `pext2`), 17 folios tenían una sola copia observada y otras copias ausentes. El resumen toma esa única observación concordante y el artefacto `household_field_coalescing.csv` registra el conteo por campo, sin folios. Las filas persona y el maestro retienen cada marcador original. `z` y `zext` no necesitaron coalescencia.

La coalescencia no certifica el significado estadístico de estos campos. La extensión local `totper` no figura en el esquema F27, y `person_records_in_source` es solo el conteo de filas agrupadas por folio; no sustituye a `totper`. Antes de publicar estadísticas de pobreza debe confirmarse quién se considera miembro del hogar, el nivel/ponderador de análisis y la discrepancia de `totper` respecto al roster.

## Artefactos y reproducibilidad

- `views_manifest.json`: unidad, filtro, clave, filas/columnas, cautelas, procedencia/versiones y SHA-256 por cada CSV.
- `view_coverage.csv`: resumen de denominadores, salida y estado inferencial de cada vista.
- `household_field_conflicts.csv`: cantidades agregadas de inconsistencias intrahogar, sin identificadores.
- `household_field_coalescing.csv`: hogares con un único valor observado y copias ausentes; describe la consolidación solo en la vista hogar.
- El manifiesto principal de la corrida incluye hashes de las vistas y archivos de apoyo. Los datos de identificación y salud son microdatos restringidos; estas extracciones no están anonimizadas ni listas para compartir.

Las secciones de vivienda, alimentación, gastos, equipamiento y discriminación no aparecen como variables de `persona.csv` y no se incorporaron desde los otros archivos de EH2025. Requieren otro alcance explícito y otra fuente; no se simularon ni unieron aquí.

## Ejecución

Desde la raíz del repositorio, con PowerShell y Python global 3.12 (el entorno virtual reservado para el otro trabajo no se usa):

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" data/proprosessing/preprocessing.py
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m unittest discover -s tests -v
```

En notebook, ejecutar en orden las celdas de `data/proprosessing/preprocessing.ipynb`. Cada corrida genera una carpeta candidata nueva e inmutable bajo `data/proprosessing/output/`, con maestro, vistas y manifiestos.

Pruebas realizadas para esta entrega: máscaras sintéticas y conteos esperados de universos, unicidad de claves en todas las vistas, tamaño/columnas del maestro, diff raw→maestro, SHA-256, hashes de artefactos, registro de conflictos intrahogar y equivalencia AST de las funciones temáticas/ejecución entre script y notebook. La integración inferencial de la encuesta sigue fuera de esta etapa; Flask consulta la versión publicada usando el catálogo JSON.
