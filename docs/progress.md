# Progreso del proyecto

## Preparación del análisis exploratorio descriptivo — código añadido, ejecución pendiente

Tras confirmar `persona.csv` como la fuente oficial de trabajo del proyecto, se añadió `data/proprosessing/exploratory_analysis.py` para describir las 11 vistas derivadas, respetando el universo de cada una y las etiquetas del JSON. El script valida los SHA-256 y dimensiones antes de leerlas, produce cobertura por variable, frecuencias agregadas y gráficos temáticos; limita el uso de estadísticos de magnitud a tipos cuantitativos declarados. Reporta conteos no ponderados y agrupa/omite celdas con menos de 10 casos en sus gráficos/tablas agregadas. No cambia ni el raw ni el maestro candidato.

**No se ejecutó ni se probó**: en el entorno actual `py -3.12` indicó que no hay Python instalado globalmente. No se usó `venv`, reservado para otro trabajo. Por tanto no hay hallazgos de distribución que deban interpretarse todavía. Especificación, salidas esperadas, comando y límites: [exploratory-analysis-persona.md](exploratory-analysis-persona.md). Una vez disponible Python 3.11+ con dependencias, ejecutar `python data/proprosessing/exploratory_analysis.py`; el programa crea un subdirectorio UTC nuevo sin sobrescribir corridas previas.

## Vistas analíticas por universos — implementadas y verificadas

Se añadieron al pipeline y notebook `build_thematic_views`, que generan vistas CSV derivadas después de escribir el maestro. La corrida vigente es `data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f/`, versión maestra `persona-1dbf937c73972a78`. Incluye 11 vistas: demografía (39.497), salud general (39.497), fecundidad mujeres 13–50 (11.328), asistencia infantil menores de 6 (3.434), bono menores de 5 (2.781), educación 4+ (37.354), empleo 7+ (35.366), candidatos secundarios (1.357), ingresos no laborales (39.497), ingresos/pobreza persona (39.497) y resumen hogar candidato (12.718 folios, 18 columnas). Las condiciones, claves, advertencias inferenciales y hashes constan en `thematic_views/views_manifest.json` y `view_coverage.csv`.

Empleo secundario conserva 1.356 casos con `s04e_25=1` y un registro con `s04e_26_cod` fuera del filtro, etiquetado para revisión; no se descartó silenciosamente. Se corrigió una primera auditoría hogar que contaba `NA` literal como valor. La validación final halló cero conflictos entre valores observados distintos en los campos candidatos. Para nueve campos, 17 folios tenían una copia observada única y otras filas marcadas ausentes; el resumen usa el valor observado y lo registra en `household_field_coalescing.csv`. El maestro y vista persona conservan sus celdas originales. `person_records_in_source` cuenta filas y no sustituye a `totper`.

Validaciones: 3 pruebas sintéticas con `unittest` pasaron, incluidas máscaras de edad/sexo, excepción secundaria, coalescencia de ausencia explícita, no mutación de entrada, conflicto entre valores observados y no sobrescritura. Una comparación independiente confirmó 39.497×275 del maestro, exactamente tres cambios S-01 contra raw, 11 claves sin duplicados, conteos y SHA-256 de cada vista y archivos de apoyo, enlace con `run_id`/versión, 300 hashes de artefactos y paridad AST entre `.py` y `.ipynb`. El hash del raw permanece igual. La inferencia oficial y los componentes completos del diseño muestral aún no están certificados; estas son vistas analíticas internas, no productos estadísticos publicados. Detalle en [thematic-views-persona.md](thematic-views-persona.md).

## Limpieza semántica S-01 — ejecutada y verificada

Se corrigió el enfoque: la corrida `20261004T200928Z_568e82e3039d_d3abfb0b5f` era una línea base técnica y no había cambiado celdas, por lo que no debía llamarse limpieza semántica. Se añadió S-01 al script y al notebook: en `phrs`, `shrs` y `tothrs`, valores numéricos mayores que 168 horas semanales pasan a `NA` en una salida candidata nueva, sin borrar filas. La regla usa el límite físico de horas por semana y la definición de unidad del DDI EH2025. La bitácora `semantic_cell_changes_restricted.csv` guarda fila CSV, columna, valor anterior/nuevo, regla y motivo; el raw no se toca.

Corrida candidata: `data/proprosessing/output/20261004T204302Z_568e82e3039d_d3abfb0b5f/`, versión `persona-1dbf937c73972a78`. Conserva 39.497 filas, 275 columnas y la clave/fila en el mismo orden. La comparación independiente raw→CSV halló exactamente 3 celdas diferentes: `tothrs` 192→NA y `phrs`/`tothrs` 171,5→NA en una fila. El hash SHA-256 del raw sigue igual al registrado en el manifiesto. Se validaron dimensiones del Parquet (39.497×275), las 275 gráficas, los 285 hashes de artefactos, la bitácora y la equivalencia AST de `clean_frame` y `run_pipeline` entre `.py` y notebook. La prueba sintética preservó 168, esquema, filas y fuente original.

Se añadió [semantic-cleaning-audit.md](semantic-cleaning-audit.md), que separa esta regla respaldada de discrepancias que requieren confirmación (edad/año, `totper`, referencias a integrantes, rangos DDI contradictorios y alertas IQR). Esto completa una primera regla semántica, no la auditoría semántica integral de las 275 variables. La salida es candidata, todavía no está publicada.

## Estado vigente — 4 de octubre de 2026

El pipeline local de `data/persona.csv` se ejecutó correctamente con Python 3.12 en `20261004T171822Z_568e82e3039d_d3abfb0b5f/`. Conservó 39.497 filas, redujo 275 columnas a 150 mediante L-80 y generó perfiles, comparación, bitácora local, manifiesto, CSV/Parquet candidatos y 275 gráficos. El raw no se modificó; el SHA-256 verificado es `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`. La entrada de datos es solo `data/persona.csv`; el JSON se usa únicamente como diccionario de metadatos.

El resultado es candidato y no está publicado: la exclusión se calculó sin ajustar por universos, y `s04c_17a` (salario líquido) excedió L-80 con 81,3505 % de ausencia técnica. Debe revisarse esa y otras columnas condicionales antes de análisis de ingresos. No se eliminaron filas, no se imputó y los atípicos IQR solo se marcaron para revisión. La diferencia entre el esquema local y el F27 oficial también sigue sin resolverse.

Se documentó el alcance de la evaluación de universos y el inventario de las 125 exclusiones en [observaciones-universos-persona.md](observaciones-universos-persona.md). El perfil sí fue individual por variable; la interpretación de ausencias por elegibilidad no se calculó para todas. El inventario muestra grupos de edad/sexo, subpreguntas laborales y campos sin universo, por lo que no se deben tratar las exclusiones como decisión semántica definitiva.

Revisión focalizada de ocupación secundaria: el DDI ubica `s04e_26_cod` después del filtro `s04e_25` (realizó otro trabajo). En `persona.csv`, 1.356 personas tienen respuesta afirmativa al filtro y las 1.356 tienen código; hay un registro codificado fuera del filtro. La ausencia global del código (96,5643 %) es por tanto principalmente estructural para este campo. Se documentó conservarlo en vistas de ocupación secundaria y revisar la excepción sin corrección automática. ANDA reporta 1.476 válidos para la ficha F27; el conteo local de 1.357 difiere y refuerza la necesidad de reconciliar procedencia. No se modificó el raw ni se generó/publicó una nueva versión limpia.

En la rama secundaria, el DDI declara que `s04e_28` aplica a los códigos 1/2/7 de `s04e_27`; en la copia local, 137 de 138 elegibles respondieron (0,7246 % faltante elegible frente a 89,8968 % global). Para `s04f_31a`, se observaron 133 montos en la rama de segundo trabajo; el cruce sugiere un filtro de categoría ocupacional, pero está pendiente de cotejar con el cuestionario. Estos agregados amplían la revisión, pero no reemplazan la auditoría de universos para el resto de columnas.

Se reconstruyeron dos filtros más del DDI para empleo principal: `s04c_17a` aplica a códigos 1/2/8 de `s04b_12` (7.370 elegibles locales; 7.366 respuestas; 4 faltantes, 0,0543 %), y `s04b_13` a códigos 1/2/7 (7.054 elegibles; 7.053 respuestas; 1 faltante, 0,0142 %). ANDA informa respectivamente 7.387 y 7.108 valores válidos en F27. Esta diferencia refuerza la incertidumbre de procedencia, pero ambas variables demuestran que L-80 global las habría excluido pese a tener completitud superior al 99,9 % en su universo. Se agregaron cifras y referencias a `observaciones-universos-persona.md`.

Inventario de metadatos de las exclusiones: 47 de 125 contienen `pre_question_text` explícito en el DDI; 78 no. El texto debe convertirse en reglas probadas contra la estructura real antes de aplicarlo, y la discrepancia con F27 sigue impidiendo asumir que el esquema y filtros corresponden exactamente a esta copia.

Se generó `docs/universe-matrix-persona.csv`, un inventario de las 125 exclusiones con porcentaje global, universo y precondición DDI, estado, disposición previa y tarea siguiente. La matriz clasifica 44 condiciones explícitas aún por mapear, 75 universos por revisar, 4 reglas cotejadas, 1 hipótesis y 1 extensión local. En esta fase no se editaron valores, columnas ni el código del pipeline; no se generó un nuevo candidato. El CSV fuente mantiene su SHA-256 original.

Flask, PostgreSQL, publicación inmutable y pruebas automatizadas siguen pendientes. Las secciones históricas siguientes conservan el estado que tenía el proyecto en las fechas indicadas; cuando difieran, prevalece este estado vigente.

## Estado al 28 de septiembre de 2026

| Área | Estado | Evidencia |
| --- | --- | --- |
| Estructura Git | Iniciada | Un primer commit con archivos de documentación vacíos; remoto configurado |
| Dataset de ejemplo | Disponible localmente | `data/persona.csv`, 34.568.646 bytes, 39.497 registros y 275 columnas observados; archivo sin seguimiento en Git |
| Documentación de arquitectura | Redactada | README, AGENTS y documentos de `docs/` |
| Backend/API | No iniciado | No existe carpeta de aplicación Flask ni código ejecutable |
| Frontend/dashboard | No iniciado | No existen templates, recursos estáticos ni dashboard |
| Base de datos/migraciones | No iniciado | No hay esquema ni servidor configurado en este repositorio |
| Pipeline de limpieza | No iniciado | No hay código ni versión limpia generada aquí |
| Análisis automatizado | No iniciado | No hay cálculos reproducibles implementados aquí |
| Pruebas y despliegue | No iniciados | No hay suite ni comandos de arranque |

## Validaciones realizadas durante la documentación

- Inventario de archivos y tamaños del repositorio.
- Lectura del encabezado y conteo de registros del CSV local.
- Lectura del diccionario disponible en la carpeta vecina.
- Revisión del historial y estado de Git: un commit inicial; `data/` sin seguimiento.

No se ejecutaron perfilamiento completo, limpieza, pruebas estadísticas ni validación oficial del origen del dataset. Los controles y métricas específicos de calidad siguen pendientes.

## Próximo hito

Resolver los datos faltantes del contrato de `persona.csv` y comenzar la Etapa 0 de `implementation-plan.md`. Al implementar una función, registrar aquí fecha, commit, evidencia de pruebas, criterios de aceptación alcanzados y limitaciones. No sustituir el estado real por una descripción aspiracional.

## Compendio académico incorporado el 3 de octubre de 2026

Se agregó [el índice del curso](../CURSO_DATA_MINING.md) y doce capítulos en `curso/` con teoría, fórmulas y ejemplos del material local. Los capítulos identifican sus fuentes, diferencian resultados reportados de desarrollos explicativos y excluyen contenido de plataformas, instalación y uso de software. Preparación y minería de texto incluyen ejercicios complementarios cuya procedencia está señalada.

Se revisaron la cobertura de los temas, las referencias locales y los cálculos del ejemplo de asociación. Esta incorporación es documental: no implementa funciones de la aplicación ni modifica el dataset de ejemplo. El estado de implementación descrito anteriormente se conserva.

## Revisión y cambio de alcance del 3 de octubre de 2026

Por solicitud del usuario, el proyecto queda centrado en la limpieza de `data/persona.csv` con fundamento en `curso/`, mediante un sistema Flask conectado a PostgreSQL para la bitácora. Se sustituyó la arquitectura anterior por vistas Jinja, servicios Flask, SQLAlchemy/Alembic, worker separado y pandas sobre archivos versionados. El soporte genérico de otros datasets queda fuera de la primera entrega.

Se actualizaron README, AGENTS, visión, requisitos, arquitectura, contrato, bitácora, dashboard, criterios de aceptación, pruebas y plan. Se agregó [la metodología de limpieza](cleaning-methodology.md) con referencias del curso, diagnóstico técnico y catálogo L-01 a L-12. Los permisos y eventos persistentes deben existir desde la primera carga. CA-17 a CA-19 son criterios nuevos **pendientes**, no logros implementados.

### Evidencia de la revisión técnica del CSV

Se ejecutó un recorrido de lectura en PowerShell con `Microsoft.VisualBasic.FileIO.TextFieldParser`, delimitador coma, comillas habilitadas y `TrimWhiteSpace = $false`. Se comprobó ancho de cada registro, encabezados repetidos, clave compuesta como texto, tokens exactos y validez numérica/positividad de `factor`. No se imprimieron filas ni se modificó el archivo.

- 39.497 registros, 275 columnas y 34.568.646 bytes.
- Cero encabezados duplicados, errores de parseo detectados o registros con ancho incorrecto.
- Cero claves textuales `(folio, nro)` repetidas o ausentes como vacío/`NA`.
- 771.655 celdas exactamente vacías, 5.489.754 con token exacto `NA` y 1.192.066 con texto exacto `0`.
- Cero valores de `factor` ausentes, no numéricos/no finitos o no positivos.
- SHA-256: `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`.

Comando de hash utilizado, repetible desde la raíz:

```powershell
Get-FileHash -LiteralPath data/persona.csv -Algorithm SHA256
```

El recorrido fue una comprobación puntual de consola, no un script de perfilamiento incorporado al repositorio. No confirma dominios, universos, duplicados exactos de fila ni diseño muestral. La lectura inicial tampoco demuestra que todos los faltantes sean errores; los códigos y saltos siguen pendientes de diccionario confirmado. Estos hallazgos complementan el diagnóstico del 28 de septiembre sin equivaler a limpieza ni a cumplimiento de criterios de aceptación.

### Estado de entrega

La actualización es exclusivamente documental. No se implementó Flask, no se conectó PostgreSQL y no se generó una versión limpia. No existen comandos reales de instalación, arranque o pruebas de la aplicación. El siguiente hito es la etapa 0 del plan actualizado: contrato de personas, reglas justificadas y base Flask/PostgreSQL, con permisos y bitácora desde el inicio.

Verificación documental realizada: `git diff --check` sin errores de espacios; búsqueda con `rg -n 'FastAPI|React|DuckDB|Polars|import_job' README.md AGENTS.md docs` sin referencias activas a la arquitectura reemplazada; comprobación de 35 enlaces locales en 13 documentos con PowerShell y `Test-Path`, sin enlaces rotos. Se repitió `Get-FileHash -LiteralPath data/persona.csv -Algorithm SHA256` y coincidió con el hash del diagnóstico. No se ejecutaron pruebas de aplicación porque no hay código implementado. Los cambios permanecen en el árbol de trabajo, sin crear commit.

## Pipeline de preprocesamiento preparado el 4 de octubre de 2026

Se completaron las fuentes previstas `data/proprosessing/preprocessing.py` y `data/proprosessing/preprocessing.ipynb`; el notebook se generó a partir de los bloques del script. Se agregó `data/proprosessing/data_dictionary.md` con una entrada por encabezado de la copia actual. El código incluye configuración, lectura conservadora, perfil por columna, resumen descriptivo, alertas IQR para tipos cuantitativos documentados, normalización sintáctica de espacios exteriores (excepto identificadores), comparación antes/después, CSV/Parquet candidatos y gráficos antes/después por columna en láminas. No elimina outliers ni imputa por defecto. Las interpretaciones no confirmadas quedan señaladas.

**No se ejecutaron el script, el notebook ni pruebas**, según solicitud del usuario, que hará su revisión. Esta entrega no demuestra que el código se ejecute correctamente ni que los resultados satisfagan los criterios; requiere validar el entorno de Python y cotejar contrato y definiciones de la encuesta. La bitácora PostgreSQL y publicación Flask aún no están integradas en este pipeline local. Los artefactos de resultado se crearán solo al ejecutar el pipeline. Comando propuesto desde la raíz del proyecto: `python data/proprosessing/preprocessing.py`; notebook: abrir `data/proprosessing/preprocessing.ipynb` en Jupyter y ejecutar sus celdas en orden.

El 4 de octubre el usuario reportó `FileNotFoundError` al crear `plots/columns`, porque su carpeta padre `plots` aún no existía. Se corrigió el orden de creación en el script y se regeneró el notebook desde sus bloques. No se reejecutó el pipeline; queda pendiente la revisión del usuario.

Tras la repetición del mismo traceback, se comprobó que los archivos guardados en el workspace tenían el arreglo, mientras que la salida del notebook conservaba la traza y el código antiguo. Se hizo la creación recursiva de ambas carpetas explícita (`parents=True, exist_ok=True`) y se volvió a generar el notebook limpiando resultados guardados y copiando las celdas del script. El análisis no se ejecutó; el usuario deberá cerrar la copia abierta sin guardarla y abrir el archivo actualizado desde el workspace para que Jupyter descarte el estado en memoria.

## Etiquetas del diccionario en el análisis — 4 de octubre de 2026

El pipeline lee el JSON canónico `data/proprosessing/data_dictionary.json` al iniciar y genera una vista Markdown legible; utiliza la descripción, sección y tipo semántico para etiquetar los perfiles y comparaciones, los títulos de gráficos y las láminas de contacto. Los informes conservan el nombre técnico de cada columna y agregan `display_name`/`description`, para que la interpretación sea legible sin perder trazabilidad. Se precisaron las definiciones disponibles para `depto`, `s01a_02` a `s01a_10` y 216 campos de las secciones de migración, salud, educación, empleo e ingresos mediante descripciones de grupo; donde el diccionario local no distingue subcampos o códigos, se marca esa incertidumbre en vez de asignar una interpretación inventada. El notebook contiene las mismas celdas del script y carga el diccionario desde su ruta dentro del proyecto.

No se ejecutó el pipeline ni se generaron resultados; queda pendiente la revisión/ejecución del usuario y el cotejo de dominios con el cuestionario oficial de la edición.
## Regla de exclusión de columnas y análisis por variable — 4 de octubre de 2026

Se añadió al pipeline y al notebook un perfil por columna con faltantes, errores de registro verificables, estado de evaluación del dominio, porcentaje combinado, umbral configurable del 80% y proceso/decisión. La regla L-80 excluye del dataset candidato las columnas no clave cuyo porcentaje combinado sea estrictamente mayor al 80%; registra valores y motivos en `rule_execution_log.csv`, `comparison_all_columns.csv` y una sección del diccionario generado. Las columnas obligatorias de clave nunca se eliminan y bloquean una ejecución si rebasan el umbral. Cada variable mantiene su comparación antes/después; las gráficas identifican columnas excluidas. El archivo raw permanece sin cambios. Dominios semánticos no confirmados no se computan como mal registro. La metodología de limpieza documenta definición y limitaciones.

No se ejecutó el pipeline ni el notebook sobre los datos. El entorno de esta sesión no expone Python para compilar o correrlos; la validación se limita a revisión del código y estructura JSON del notebook, y requiere confirmación del usuario en su entorno Jupyter.
## Diccionario JSON como fuente única — 4 de octubre de 2026

Se creó `data/proprosessing/data_dictionary.json` con metadatos del dataset y 275 variables indexadas por su código, incluidas descripción, etiqueta para gráficos, sección, tipo semántico, sensibilidad y estado de definición. `preprocessing.py` ahora valida y carga ese JSON como fuente canónica; los títulos de cada gráfico individual y las láminas usan la etiqueta descriptiva guardada allí, manteniendo el código de columna para trazabilidad. Cada ejecución copia el JSON, registra su SHA-256 en el manifiesto y genera desde él el informe `data_dictionary.md` con análisis por columna. El notebook se regenera desde los bloques del script. No se ejecutó el análisis ni se modificó `persona.csv`.
## Gráficas rediseñadas para lectura por columna — 4 de octubre de 2026

Se simplificó la lectura visual del notebook: la vista general ahora muestra hasta 25 columnas con mayor ausencia técnica en barras horizontales etiquetadas con el código y una descripción corta. Cada variable tiene un PNG individual de tamaño legible: categorías/códigos comparan frecuencias raw y candidato en barras horizontales, vacíos y tokens NA se distinguen, y conteos pequeños se agrupan/suprimen; magnitudes semánticas confirmadas usan histogramas superpuestos con los mismos intervalos; identificadores muestran completitud, no categorías. Las columnas excluidas muestran su distribución observada en raw y la razón de exclusión. El notebook explica esta clave visual y enseña una imagen de ejemplo por cada sección, junto con la ruta de todos los PNG. La alerta de atípicos continúa en las tablas y no elimina valores.

No se ejecutaron gráficas ni el pipeline sobre el CSV en esta sesión. La revisión visual final requiere correr el notebook en Jupyter con el entorno del usuario.
Ajuste de legibilidad: se dejaron de generar láminas comprimidas porque hacían ilegibles las etiquetas. Desde esta actualización cada columna se guarda como PNG individual. El notebook muestra un ejemplo por sección y ofrece la ruta para abrir cualquiera de las 275 imágenes; la clave de color es azul para raw y verde para el candidato.
## Revisión de gráficas generadas y alertas de esquema — 4 de octubre de 2026

Se inspeccionaron PNG y perfiles de la ejecución existente `20261004T140252Z_568e82e3039d_a6b074cbe3` (39.497 filas, 275 columnas). Es una ejecución anterior al cambio de gráficas: su manifiesto conserva el límite de 12 categorías, genera láminas de contacto y no registra hash del diccionario JSON; por tanto, no valida la versión actual del script.

Hallazgos agregados del CSV: `s01a_04a` tiene 31 valores distintos, exactamente 1–31; su barra grande `Otros` agrupaba los 19 días no mostrados (22.527 filas), no era un único atípico. `s01a_03` tiene 99 valores distintos (0–98) aunque el diccionario la describe como sexo; se agregó una alerta de alta cardinalidad y visualización completa de hasta 100 categorías, pero el dominio sigue sin confirmar y no se clasifican automáticamente como errores. `area` contiene dos códigos (1: 30.103; 2: 9.394). `nro` tiene 15 valores y se debe mostrar como orden del integrante, no solo como una comprobación de faltantes. `folio` tiene 12.718 identificadores de hogar distintos entre 39.497 filas; por ser identificador no se grafica su distribución.

La gráfica antigua «Estados de ausencia técnicos por columna» medía porcentajes de celdas vacías, con espacios o tokens literales de ausencia; no medía errores semánticos ni distinguía saltos legítimos del cuestionario. Ocultaba los códigos de columnas y las líneas antes/después se superponían porque la normalización exterior no cambiaba estos faltantes. El código actual reemplaza esa vista con barras etiquetadas de las 25 variables de mayor ausencia, y las imágenes individuales incluyen todos los códigos de columnas con cardinalidad de hasta 100. **El pipeline actualizado no se ejecutó** porque no hay un intérprete Python disponible en esta sesión; los cambios requieren una nueva ejecución Jupyter para verificar los PNG nuevos.

## Diccionario DDI oficial de EH2025_Persona — 4 de octubre de 2026

Se consultó y procesó el DDI oficial del archivo F27 del [catálogo ANDA del INE](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona). `data/proprosessing/data_dictionary.json` ahora contiene las 276 variables oficiales con sus etiquetas, formato, preguntas, universo, rangos, categorías, instrucciones y notas de imputación; `data_dictionary.md` presenta una vista legible. Las columnas que solo están en el CSV quedan aparte en `local_extensions`. `preprocessing.py` y el cargador del notebook combinan esas extensiones al producir rótulos, manteniendo aparte el listado oficial.

La comparación de encabezados verificó que el catálogo oficial declara 39.485 casos y 276 variables, mientras `data/persona.csv` tiene 39.497 filas y 275 columnas. Solo en F27 aparecen `s01b_10a`, `s05c_09be` y `s05c_09aa`; solo en el CSV local aparecen `s05c_09e` y `totper`. El DDI confirma que `s01a_02` es sexo y `s01a_03` es edad; esto corrige la descripción anterior del diccionario local para esas dos columnas. No se confirma que el archivo local sea la misma versión EH2025 y no se deben aplicar dominios o saltos oficiales a los campos discrepantes sin resolver la procedencia.

Verificaciones realizadas: carga de JSON con `ConvertFrom-Json`, conteo de 276 variables oficiales y 2 extensiones, comprobación de diferencias del encabezado contra F27 y cotejo de los rótulos de sexo/edad. El bloque de carga de extensiones fue actualizado en ambos archivos. No se ejecutó el pipeline ni el notebook completo; no se generaron salidas de limpieza o gráficos en este cambio.

## Implementación de limpieza enfocada en `persona.csv` — 4 de octubre de 2026

El alcance confirmado procesa exclusivamente `data/persona.csv`. El pipeline no carga otras fuentes de datos ni realiza uniones; consulta `data/proprosessing/data_dictionary.json` únicamente como metadatos. Esta restricción está reflejada en el contrato y el manifiesto.

Actualicé `preprocessing.py` y regeneré `preprocessing.ipynb` desde sus celdas para que ambos contengan el mismo pipeline. Cada ficha y perfil ahora puede mostrar el universo de la pregunta tomado del JSON. La normalización de espacios exteriores se limita a campos cuyo diccionario los identifica como códigos o magnitudes; se preservan respuestas de texto libre. La validación de `(folio, nro)` trata tokens de ausencia como claves incompletas y bloquea la salida. El manifiesto incluirá la comparación de esquema local frente al F27 oficial, incluidos campos que sobran o faltan.

Se ejecutó el pipeline con Python 3.12 y se generó el candidato inmutable `data/proprosessing/output/20261004T171822Z_568e82e3039d_d3abfb0b5f/`. Entraron 39.497 registros y 275 columnas; el candidato conserva las 39.497 filas y 150 columnas. L-80 excluyó 125 columnas por superar estrictamente el 80 % de celdas incompletas o formatos mal registrados comprobables. Se generaron perfiles antes/después, comparación, bitácora local de reglas, copia del diccionario JSON/Markdown, Parquet y 275 imágenes. La inspección visual corrigió el histograma del salario de una columna excluida: ahora muestra la distribución numérica del raw con bins, sin transformar ni recortar datos.

La regla L-80 se aplicó sobre todas las filas según el umbral solicitado, no sobre el subconjunto elegible de cada pregunta. Por ello `s04c_17a` (salario líquido; universo condicional) se excluyó con 81,3505 % de ausencia técnica. Esta columna y otras ausencias debidas a saltos requieren una decisión analítica antes de publicar o usar el candidato para estimar ingresos. Los atípicos IQR son alertas; no se eliminan observaciones ni se imputan valores. El manifiesto registra que el esquema local no coincide exactamente con F27 (39.497/275 frente a 39.485/276; tres columnas oficiales ausentes y dos locales adicionales).

Comando usado para completar la ejecución desde la raíz en este entorno: `& 'C:\Users\julio\AppData\Local\Programs\Python\Python312\python.exe' data\proprosessing\preprocessing.py`. El notebook y el script tienen las mismas fuentes de celdas, verificado estructuralmente. El CSV raw mantiene su hash SHA-256 anterior. Esta salida es un candidato local; no está publicada en Flask/PostgreSQL. La integración Flask/PostgreSQL, pruebas automáticas y la confirmación de procedencia exacta siguen pendientes.

## Auditoría por universo — empleo y fecundidad/salud materna — 4 de octubre de 2026

Se avanzó la revisión de las columnas excluidas mecánicamente por L-80, sin editar el archivo fuente ni crear una nueva salida limpia. En empleo quedaron documentados cuatro ejemplos de subpoblaciones en `observaciones-universos-persona.md`. En fecundidad se agregaron denominadores locales y advertencias de versión para `s02b_06b` a `s02b_14a`. Se actualizó `docs/universe-matrix-persona.csv` (125 filas) agregando `local_eligible_n`, `local_answered_n`, `local_missing_eligible_n` y `local_eligibility_basis`: nueve máscaras locales se registran con estado provisional `LOCAL_RULE_CHECKED_DDI_MATCH`, cinco filas quedan bloqueadas con `DDI_CONFLICT_REQUIRES_PROVENANCE`, y el resto conserva el estado de trabajo previo. La matriz no declara limpieza ni aprobación final.

Hallazgo bloqueante: el contrato local de `s02b_10` indica año >=2017, mientras la ficha oficial F27 de `s02b_09b` ordena continuar si el último hijo nació después de 2020. Bajo el corte local no conciliado, 3.452 mujeres son elegibles, 2.711 tienen respuesta y 741 están vacías/NA; esta tasa no se toma como calidad confirmada. ANDA informa 6.226 válidos de `s02b_09b`; localmente se observan 6.339. Se detectaron además aparentes desajustes entre etiquetas y `pre_question_text` para `s02b_11` y `s02b_14a`, por lo cual no se ejecutan automáticamente esos textos como reglas.

Se verificó que la matriz mantiene 125 filas y que SHA-256 de `data/persona.csv` es `568E82E3039D991A1EE0D8E2056448F8C465C03FFA838330C4F1522DD77BDDC8`, sin cambio respecto del origen auditado. `git diff --check` no reportó errores de whitespace; solo advirtió conversiones de fin de línea CRLF. No se ejecutó el pipeline/notebook ni se aplicaron transformaciones porque falta reconciliar procedencia y versión del instrumento. Próximo trabajo: auditar el resto de salud, después educación, empleo pendiente, ingresos y derivadas; resolver formalmente discrepancias; aprobar y probar reglas en datos sintéticos; solo entonces regenerar candidato inmutable.

## Conciliación de procedencia y esquema de `persona.csv` — 4 de octubre de 2026

Se completó la revisión estructural de la fuente y se documentó en `docs/source-reconciliation-persona.md`. Se compararon el CSV de solo lectura, los nombres del DDI JSON local y el manifiesto de `20261004T171822Z_568e82e3039d_d3abfb0b5f`; no se cargaron otros microdatos. Un lector CSV de streaming (PowerShell/.NET con parser compatible con comillas escapadas y UTF-8 estricto) contó 39.497 registros y 275 columnas. Todas las filas tenían 275 campos; no encontró nombres de encabezado duplicados ni registros con comillas abiertas. SHA-256: `568E82E3039D991A1EE0D8E2056448F8C465C03FFA838330C4F1522DD77BDDC8`; tamaño 34.568.646 bytes. Primeros bytes `22-66-6F-6C`: no hay BOM; el archivo es legible como UTF-8 estricto.

La comparación de conjuntos halló 273 encabezados compartidos, tres presentes solo en F27 (`s01b_10a`, `s05c_09be`, `s05c_09aa`) y dos solo locales (`s05c_09e`, `totper`). La diferencia de conteo es +12 filas frente a los 39.485 casos declarados en el DDI/ANDA. El manifiesto del candidato previo coincide en hash, tamaño, 39.497 filas y 275 columnas, y confirma que fue candidato no publicado; la misma evidencia no resuelve quién produjo/entregó el raw ni su licencia. Se registró el estado `SCHEMA_MISMATCH_PROVENANCE_UNRESOLVED`. Ninguna fila, columna o valor de `persona.csv` se cambió; no se generó un nuevo candidato. La codificación del manifiesto previo era `utf-8-sig`; como el archivo no tiene BOM, queda aclarado que ello solo funcionó como lector UTF-8 tolerante a BOM y no es evidencia sobre procedencia.

Validación de esta actualización documental: recuento 275/275 por fila y 125 filas en la matriz de universos; `git diff --check` sin errores de whitespace (solo advertencias habituales de fin de línea CRLF); SHA-256 de la fuente idéntico. No se corrió el pipeline ni los tests del proyecto. Para cerrar procedencia falta obtener documento/URL de entrega, versión del cuestionario, licencia, explicación del +12, de las tres columnas ausentes y de las dos extensiones locales. Las reglas semánticas del DDI F27 siguen bloqueadas como reglas productivas hasta esa conciliación.

## Revisión estadística del trabajo de conciliación — 4 de octubre de 2026

Esta revisión es posterior a las entradas de auditoría de fecundidad del mismo día y reemplaza la clasificación provisional de “cinco conflictos”: la evidencia oficial confirma dos textos `pre_question_text`, por lo que solo `s02b_10` queda como conflicto de corte confirmado.

Se hizo una revisión crítica de las conclusiones anteriores y se contrastaron los textos de fecundidad con fichas oficiales ANDA. Dictamen: la conciliación de filas/columnas, integridad estructural y reserva de procedencia estaba bien planteada; no era una validación estadística completa. Se corrigió una interpretación incorrecta: `utf-8-sig` es un codec que acepta UTF-8 con/sin BOM, por lo que el manifiesto no afirmó la existencia de BOM; el archivo efectivamente no tiene BOM y pasa lectura UTF-8 estricta.

Se encontró que la ficha oficial F27 también muestra para `s02b_11` la pre-pregunta de nacidos vivos y para `s02b_14a` la del subsidio del último embarazo. Por tanto, la observación anterior de posible desalineación local no estaba sustentada. No obstante, texto de pre-pregunta no es necesariamente una regla de salto. En particular, los 1.695 vacíos de `s02b_14a` bajo el filtro amplio `s02b_13=1` coinciden en margen con 1.695 respuestas “no” en `s02b_14`, mientras hay 382 valores de meses para 382 “sí” locales en `s02b_14`; se requiere revisar el flujo del cuestionario y la tabla cruzada antes de llamar a esos vacíos no respuesta.

La sensibilidad `s02b_10` se calculó para ambos cortes: bajo año >=2017, 3.452 casos / 2.711 respuestas / 741 vacíos; bajo año >2020, 1.856 / 1.716 / 140 (7,5431 %). Sigue siendo exploratoria por la diferencia de versión y 6.339 vs 6.226 años válidos local/oficial. La clave candidata `(folio,nro)` se comprobó como completa y única en valores textuales exactos: cero claves vacías/NA o repetidas; 12.718 folios distintos. Se detectó además un `nro=15`; el DDI oficial declara rango 1–14. Se registra como alerta de dominio, sin corregir ni rechazar esa fila.

Se añadió `docs/review-statistical-quality-persona.md`, se corrigieron observaciones/metodología en `docs/observaciones-universos-persona.md`, `docs/data-contract.md` y `docs/source-reconciliation-persona.md`, y se revisaron los estados de `docs/universe-matrix-persona.csv`. La matriz vigente queda en 71 `UNIVERSE_PENDING`, 38 `DDI_PRECONDITION_NEEDS_MAPPING`, 13 reglas cotejadas provisionales, 1 conflicto confirmado (`s02b_10`), 1 hipótesis laboral y 1 extensión local. No se alteró `persona.csv`, no se ejecutó el pipeline ni pruebas del proyecto. Fuentes oficiales contrastadas: fichas F27 de `s02b_11`, `s02b_14a`, `s02b_09b` y `nro`.

## Auditoría de universos — salud general/niñez y educación — 4 de octubre de 2026

Se analizaron 15 columnas excluidas por el candidato L-80 en salud general/niñez y educación. Se registraron máscaras, elegibles, respuestas y faltantes elegibles en `docs/universe-matrix-persona.csv`, y la interpretación variable por variable en `docs/observaciones-universos-persona.md`. Diez máscaras quedaron cotejadas provisionalmente con las precondiciones/universos del DDI (incluidas las dos especificaciones de salud, salud infantil por edad y ramas de educación); tres patrones locales (`s02a_05`, `s02d_17`, `s02d_17a`) siguen como hipótesis, y `s03b_12` queda sin validar porque cuatro valores observados están fuera de la máscara candidata. `s02a_01b` conserva sin máscara los conteos globales 74 observados/39.423 ausentes, sin llamarlos faltantes de elegibles.

Conteos de estado de las 125 variables en la matriz: 66 `UNIVERSE_PENDING`, 30 `DDI_PRECONDITION_NEEDS_MAPPING`, 19 `LOCAL_RULE_CHECKED_DDI_MATCH`, 4 `DDI_RULE_CHECKED_AGAINST_LOCAL`, 3 `LOCAL_PATTERN_PENDING_CONFIRMATION`, 1 `DDI_CONFLICT_REQUIRES_PROVENANCE`, 1 `HYPOTHESIS_PENDING` y 1 `LOCAL_EXTENSION_NO_OFFICIAL_CONTRACT`. Se mantuvieron las columnas de decisión anterior y cambio de valores fuente como auditoría histórica; no se editaron ni normalizaron valores. SHA-256 de `data/persona.csv` permanece `568E82E3039D991A1EE0D8E2056448F8C465C03FFA838330C4F1522DD77BDDC8`. No se ejecutó pipeline ni pruebas: esta etapa es documental y de conteo exploratorio. La versión exacta del archivo sigue sin resolverse; las máscaras no son reglas productivas.

## Ajuste del pipeline a dataset maestro completo — 4 de octubre de 2026

El usuario confirmó `data/persona.csv` como fuente definitiva de trabajo. Esta instrucción fija el archivo de entrada del proyecto, pero no afirma que coincida exactamente con la publicación F27. Se corrigió el enfoque del pipeline y del notebook: L-80 ahora es exclusivamente una alerta de perfil, ya no elimina ninguna variable del maestro. La versión derivada conservará todas las filas y columnas; únicamente podrá recortar espacios exteriores en columnas cuyo tipo semántico lo autorice, mientras preserva IDs, texto libre y tokens de ausencia. La clave `(folio,nro)` se valida; ante nulos o duplicados el job se detiene, sin deduplicación. No se imputan valores ni se corrigen dominios o atípicos.

Se actualizó la documentación de alcance y contrato. Los 150 campos del candidato histórico se señalan expresamente como una salida previa no adecuada para maestro.

**Pendiente de ejecución:** no se pudo ejecutar el pipeline en esta sesión porque el entorno no tiene Python instalado accesible: `venv/pyvenv.cfg` apunta a `C:\Users\julio\AppData\Local\Programs\Python\Python312\python.exe`, ruta inexistente aquí, y `py.exe` no encuentra una instalación. Por ello no se generó un CSV/Parquet nuevo ni gráficos actuales; no se declara este candidato ejecutado ni validado. La sincronización de celdas de código entre `.py` e `.ipynb` se comprobó comparando los 10 bloques de script con las 10 celdas de código (coinciden). SHA-256 del raw no se modificó en los cambios documentales/de código: `568E82E3039D991A1EE0D8E2056448F8C465C03FFA838330C4F1522DD77BDDC8`. No se ejecutaron pruebas Python.

## Ejecución y pruebas del maestro completo — 4 de octubre de 2026

Se ejecutó `data/proprosessing/preprocessing.py` con Python global 3.13.14 de pgAdmin (sin usar el entorno virtual del otro trabajo); las dependencias requeridas se instalaron en una carpeta temporal para esta prueba. Corrida: `20261004T200928Z_568e82e3039d_d3abfb0b5f`. Generó `persona_clean_master.csv`, `persona_clean_master.parquet`, perfiles antes/después, comparación, bitácora local, manifiesto y 275 gráficos en `data/proprosessing/output/20261004T200928Z_568e82e3039d_d3abfb0b5f/`. El manifiesto registra 39.497 filas, 275 columnas, SHA-256 fuente `568E82E3039D991A1EE0D8E2056448F8C465C03FFA838330C4F1522DD77BDDC8`, versión Python/dependencias y SHA-256 del script ejecutado `E3F8DD8BAB702A9832D161EEC9E035E8C39261F35E2E2C3230190F66C4395C7C`.

Verificaciones ejecutadas: el script compiló con `py_compile`; las 10 celdas de código del notebook compilaron y coinciden con los 10 bloques del script; lectura CSV independiente confirmó encabezados, 39.497 registros, ancho constante, orden y unicidad/completitud de `(folio,nro)`. El Parquet reporta 39.497 × 275; perfiles antes/después tienen 275 variables; existen 275 PNG. Las comparaciones streaming encontraron cero celdas con cambios de valor (no se encontraron espacios exteriores elegibles para recortar). Pruebas sintéticas confirmaron que una variable con 100 % de ausencia se retiene, el trim es idempotente y una clave duplicada bloquea el trabajo. `git diff --check` pasó.

Diagnóstico agregado de esta corrida: 125 columnas superan 80 % de ausencia/formato técnico global; todas se conservan. Se registran 49 variables con alertas IQR exploratorias y 0 registros mal formados detectados por los chequeos limitados implementados (dominios de `area`/`depto` y formato numérico solo donde el tipo está confirmado). Esos ceros no significan que los 275 dominios estén validados. Por tanto esta salida es una **versión maestra técnica**, no una limpieza semántica completa ni una publicación. No se imputaron, corrigieron ni eliminaron registros. El usuario confirma el CSV como fuente definitiva del proyecto; las diferencias con F27 y las reglas de cuestionario aún limitan interpretación y limpieza por universo. Flask/PostgreSQL y bitácora persistente no se ejecutaron.

Seguimiento de metadatos de versión: el manifiesto de la corrida también contiene `source_file_id`, `version_id` (`persona-705a06e2840f9dc0`), `output_dataset_sha256` (`705A06E2840F9DC0AAEF82BFEED8DB6D41349F7BE433A15D1C630FD4C6665321`) y hashes SHA-256 de 284 artefactos (sin auto-hash del manifiesto). El código se ajustó para incluir esos metadatos automáticamente en las próximas ejecuciones. La versión hash diferencia la serialización CSV inmutable; al comparar celdas CSV con raw, el contenido y orden de filas no cambiaron.
