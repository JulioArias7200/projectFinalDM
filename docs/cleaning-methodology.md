# Metodología de limpieza de `persona.csv`

## Objetivo y alcance

Preparar `data/persona.csv`, identificado por el usuario como un dataset muy sucio, para análisis descriptivo confiable y trazable. La versión `persona-317279aafe9023a2` retiene 39.497 filas y 275 columnas, aplica S-01/S-02, pasa validación estructural y se publica internamente mediante catálogo JSON. La limpieza semántica integral permanece pendiente para dominios/universos sin evidencia suficiente.

La teoría explica cómo elegir un tratamiento; el diccionario disponible determina parcialmente qué significa cada variable. Por instrucción del usuario, esta etapa analiza solo `persona.csv` y no analiza el cuestionario. No existe una regla de limpieza universal para las 275 columnas. El perfil cubre todas ellas y valida estructura/claves; las reglas semánticas se habilitan solo con evidencia disponible. Las columnas sin definición confirmada se conservan y marcan pendientes; no se declara validación integral mientras persistan esos pendientes.

El INE documenta el archivo F27 [EH2025_Persona](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona). El usuario confirma `data/persona.csv` como fuente definitiva de trabajo para este proyecto. La comparación con el DDI F27 encontró 39.485 frente a 39.497 casos, 276 frente a 275 columnas y diferencias en nombres; por tanto el DDI es referencia auxiliar para variables coincidentes, no evidencia de que ambas versiones sean idénticas. El JSON conserva por separado las variables F27 y las extensiones locales, sin inferir equivalencias.

## Fundamento en la carpeta `curso/`

| Referencia | Aplicación al dataset | Evidencia requerida |
| --- | --- | --- |
| [Tipos de datos](../curso/02_tipos_de_datos.md) | Separar identificadores, categorías codificadas, ordinales y magnitudes; distinguir persona/hogar | Diccionario de columnas, nivel, escala, unidad y universo |
| [Estadística descriptiva](../curso/03_estadistica_descriptiva.md) | Frecuencias, cardinalidad, cuantiles, dispersión y gráficos de diagnóstico | Perfil por variable con denominador y método |
| [Preparación y calidad](../curso/05_preparacion_de_datos.md) | Duplicados, faltantes, no aplicabilidad, rangos, imputación y transformaciones | Reglas justificadas e impacto antes/después |
| [Metodologías](../curso/10_metodologias.md) | Aplicar comprensión, preparación, evaluación y entrega siguiendo CRISP-DM/KDD | Decisiones y entregables por fase |
| [Calidad y ciclo de vida](../curso/11_calidad_y_ciclo_de_vida.md) | Evaluación de riesgos, reproducibilidad y seguimiento de cambios | Validaciones, historial y límites conocidos |
| [Inferencia](../curso/04_estadistica_inferencial.md) | Diferenciar descripción observada de inferencia poblacional | Supuestos y diseño confirmado antes de inferir |

Los capítulos de clasificación, regresión, agrupamiento y asociación no obligan a entrenar modelos para limpiar el dataset. Si se propone una imputación mediante modelo, exige evaluación y justificación propias. Los ejercicios del curso no autorizan a eliminar registros incompletos, convertir códigos en medidas ni reemplazar faltantes con medias de forma general.

## Diagnóstico técnico de referencia

La revisión de lectura del 3 de octubre de 2026 recorrió el CSV con `Microsoft.VisualBasic.FileIO.TextFieldParser` en PowerShell, con delimitador coma, comillas habilitadas y sin recortar espacios. Se calcularon tamaño y SHA-256 con `Get-Item` y `Get-FileHash`. No se imprimieron filas ni se modificó el archivo. Esta revisión puntual no es un pipeline implementado ni una prueba automatizada del sistema.

| Control | Resultado observado |
| --- | ---: |
| Registros / columnas | 39.497 / 275 |
| Bytes | 34.568.646 |
| Encabezados duplicados | 0 |
| Errores de parseo / registros con ancho incorrecto | 0 / 0 |
| Claves `(folio, nro)` vacías o con token exacto `NA` | 0 |
| Repeticiones de `(folio, nro)` comparadas como texto | 0 |
| Celdas exactamente vacías | 771.655 |
| Celdas con token exacto `NA` | 5.489.754 |
| Celdas con texto exacto `0` | 1.192.066 |
| `factor` ausente, no numérico/no finito o no positivo | 0 |

SHA-256 del archivo revisado: `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`.

## Resultado de la ejecución local

La corrida histórica `20261004T171822Z_568e82e3039d_d3abfb0b5f`, guardada en `data/proprosessing/output/20261004T171822Z_568e82e3039d_d3abfb0b5f/`, procesó únicamente `data/persona.csv`; leyó el JSON del diccionario como metadatos, sin agregar registros ni unir fuentes. El manifiesto registra el mismo hash SHA-256 del origen indicado arriba. Su salida de 150 columnas fue reemplazada como maestro por una corrida posterior que conserva el esquema completo.

En esa corrida histórica el candidato conservó 39.497 filas y solo 150 de las 275 columnas de origen. L-80 excluyó 125 columnas por superar el 80 % técnico global. Esta exclusión se reconsideró y ya no forma parte del maestro vigente: el maestro retiene las 275 columnas y trata L-80 como alerta. La versión interna actual incorpora S-01/S-02, perfiles/gráficos y 11 vistas temáticas. El CSV de entrada no se sobrescribió; la bitácora/puntero se persiste en JSON local y Flask lee la versión seleccionada por ese catálogo.

El porcentaje L-80 se calculó sobre el total de filas, no sobre la población elegible según saltos del cuestionario. `s04c_17a` (salario líquido) quedó excluida al registrar 81,3505 % de ausencia técnica, aunque es una pregunta de universo condicional. Sus no respuestas pueden corresponder a personas fuera del universo. La exclusión debe revisarse antes de estudiar salarios o publicar el candidato. Los tokens técnicos de ausencia tampoco se clasificaron como errores de respuesta. La ejecución no eliminó filas, no imputó y no suprimió atípicos: IQR se usa solo como alerta.

La revisión posterior del DDI identificó que `s04e_26_cod` corresponde a la clasificación de la ocupación secundaria y está precedida por `s04e_25` («¿realizó otro trabajo?»). En el CSV local, 1.356 casos responden sí y los 1.356 tienen código; un caso adicional tiene código sin respuesta afirmativa al filtro. Su 96,5643 % de ausencia global es estructural casi en su totalidad, por lo que esta columna debe conservarse en análisis de la ocupación secundaria. Entre las 125 variables que L-80 excluyó, 47 tienen una precondición textual no vacía en el DDI y 78 no la tienen; la interpretación y codificación de esas instrucciones está pendiente variable por variable. Este ejemplo valida la necesidad del análisis por universo, pero no permite generalizar un único filtro a todas las preguntas de empleo.

También se siguió la precondición del DDI para `s04e_28`: códigos 1, 2 o 7 de `s04e_27`. El subconjunto elegible local tiene 138 filas y 1 ausencia (0,7246 %), frente a 89,8968 % global. Para `s04f_31a`, los 133 montos observados se concentran en códigos de trabajador que parecen remunerados, pero al faltar precondición explícita en los metadatos se deja como hipótesis, sin aplicar regla. Los conteos y límites están en [observaciones de universos](observaciones-universos-persona.md).

Dos variables de empleo principal muestran el mismo efecto: `s04c_17a` requiere `s04b_12 ∈ {1,2,8}` y tiene 4 faltantes de 7.370 elegibles; `s04b_13` requiere `s04b_12 ∈ {1,2,7}` y tiene 1 faltante de 7.054 elegibles. Ambas cruzan L-80 al usar el total de filas, pero no al usar su universo documentado. Los conteos F27 difieren de los locales (7.387 y 7.108 válidos, respectivamente), de modo que conservamos la regla como candidata trazable y no afirmamos que el microdato local sea exactamente la descarga F27.

La conciliación de esquema continúa siendo un bloqueo para validación semántica completa: el DDI F27 declara 39.485 casos y 276 variables, frente a 39.497 filas y 275 columnas locales; tres campos F27 no aparecen en el CSV y dos nombres son extensiones locales (`s05c_09e`, `totper`). La procedencia exacta debe confirmarse antes de aplicar saltos y dominios como reglas definitivas.

La inspección de referencia del 3 de octubre no incluía deduplicación exacta; esta se incorporó después al pipeline. La candidata actual confirmó cero filas idénticas y cero claves duplicadas/incompletas. Siguen pendientes dominios completos, universos y clasificación causal de faltantes por pregunta. La codificación definitiva permanece pendiente de procedencia. La clave es candidata para esta copia y se valida en cada carga. Un peso positivo no confirma el diseño muestral.

## Procedimiento de limpieza

1. **Comprensión:** identificar edición, diccionario, cuestionario, permisos y objetivo analítico. Crear el contrato de columnas y clasificar campos sensibles.
2. **Conservación e ingesta:** guardar bytes originales y metadatos; separar archivo, ejecución y versión. Leer inicialmente los campos como texto para evitar conversiones automáticas de `NA`, identificadores o ceros.
3. **Perfil:** medir por columna tokens, tipos candidatos, categorías y valores extremos; comprobar encabezados, clave y duplicados exactos. Conservar el perfil inicial sin corregir datos.
4. **Diseño de reglas:** seleccionar columnas y universos; documentar condición, acción, fundamento del curso, evidencia del diccionario y política de rechazo. Revisar las reglas antes de ejecutarlas.
5. **Preparación:** ejecutar reglas en orden con validaciones intermedias; registrar impacto en `rule_execution`. Mantener marcas de origen para faltantes, derivaciones e imputaciones, y cuarentena restringida cuando corresponda.
6. **Evaluación:** comparar distribuciones, conteos y faltantes; revisar efectos no previstos y reconciliar entradas con salidas. Un menor número de faltantes no demuestra por sí solo mejor calidad.
7. **Entrega:** materializar una versión inmutable y publicar únicamente tras validación. Mostrar alcance validado, pendientes y resultados desde esa versión. Toda corrección posterior crea otra versión.

## Catálogo inicial de reglas por implementar

| ID | Problema o control | Tratamiento permitido | Referencia / condición |
| --- | --- | --- | --- |
| L-01 | Encabezados y número de campos | Bloquear esquema inesperado; aislar errores recuperables de parseo | Preparación; contrato de las 275 columnas de esta copia |
| L-02 | Identificadores y clave | Preservar como texto, validar ausencia y unicidad de `(folio, nro)`; bloquear edición si no es estable | Tipos y preparación; no usar `folio` solo |
| L-03 | Espacios o formatos inconsistentes | Normalizar únicamente columnas autorizadas; conservar valor de origen y detectar colisiones | Preparación; no recortar texto libre o claves sin regla |
| L-04 | Vacío, `NA`, cero y no aplica | Clasificar estados por columna y universo; conservar causa/origen aunque el valor analítico use nulo | Tipos y preparación; saltos confirmados del cuestionario |
| L-05 | Tipos y códigos | Convertir magnitudes con formato explícito; validar categorías contra diccionario, sin promediar códigos | Tipos; no inferir etiquetas de `area`, `depto`, `condact` o `niv_ed` |
| L-06 | Duplicados exactos o de clave | Reportar grupos; conservar/cuarentenar según política aprobada, sin elegir fila arbitraria. Duplicado confirmado bloquea la candidata, no elimina filas | Preparación; confirmar identidad y regla de conservación |
| L-07 | Rangos y extremos | Validar rangos confirmados; usar cuantiles/IQR como alertas de revisión, sin borrar automáticamente | Descriptiva y preparación; 96–99 no son siempre edades inválidas |
| L-08 | Dependencias y nivel persona/hogar | Validar saltos y relaciones solo con semántica y tolerancias documentadas | Preparación; no sumar `yhog` repetido por persona como total de hogares |
| L-09 | Ponderador de encuesta | Comprobar `factor` numérico, finito y positivo donde aplique; bloquear ponderación si no está confirmado | Inferencia y contrato de encuesta; no inventar pesos |
| L-10 | Faltantes que requieren imputación | Por defecto conservarlos; habilitar método por variable, universo y objetivo solo tras aprobación | Preparación; registrar máscara, donantes/modelo, semilla y evaluación |
| L-11 | Transformaciones o discretización | Crear columnas derivadas separadas con fórmula, unidades y límites explícitos | Preparación; no reemplazar `niv_ed` con el ejemplo didáctico de `aestudio` |
| L-12 | Correcciones manuales | Propuesta con clave, versión, antes/después, razón y actor; aprobar y aplicar como parche | Preparación y bitácora; control de permisos y conflicto |

Cada definición incluye `rule_id`, versión, orden, columnas, universo, condición, acción, severidad, política de cuarentena, parámetros, `theory_ref`, referencia del diccionario, actor y aprobación. La ejecución agrega conteos, métricas antes/después, estado y versión de código. Una regla de solo validación puede afectar cero celdas y aun producir alertas; distinguir filas examinadas, modificadas y rechazadas.

## Validación y publicación

- Reconciliar registros parseados, aceptados y cuarentenados; declarar por separado cualquier deduplicación o agregación autorizada.
- Validar esquema, unicidad de clave, tipos, dominios confirmados y reglas cruzadas. Los errores críticos impiden publicar.
- Comparar por columna estados de ausencia, categorías y distribución numérica con el mismo universo antes/después. Separar cambios de valores de cambios en la composición de registros.
- Guardar manifiesto con hashes, contrato, reglas, código, conteos y limitaciones; persistir bitácora y actualizar puntero de publicación en transacción.
- No usar «limpio» como garantía de que todas las variables están completas. Informar faltantes legítimos, excepciones y alcance semántico validado. Si faltan definiciones, el resultado puede servir como versión técnica interna, pero sus variables pendientes no alimentan indicadores públicos.

La primera entrega se acepta con reglas y pruebas sintéticas de faltantes, duplicados, tipos, atípicos, conflictos y publicación segura, además de un reporte técnico del archivo real sin exponer personas. No exige imputación para todas las variables ni eliminar todo `NA`.

### S-02 — Normalización de respuestas textuales abiertas

La conversión a minúsculas se limita a una lista explícita de campos de respuesta abierta identificados como “Especifique” en las etiquetas del diccionario local. No se aplica a identificadores, categorías codificadas, valores numéricos ni tokens de ausencia. El valor original se conserva en `data/persona.csv`; cada celda modificada se registra en la bitácora restringida con regla, fila, columna, antes/después y motivo. Esta transformación facilita comparaciones textuales sin afirmar que las respuestas son equivalentes semánticamente. Las columnas no clasificadas como texto abierto se preservan hasta que se confirme su naturaleza.

### Resultado empírico de duplicados y texto — 2026-10-04

La inspección de solo lectura de `persona.csv` encontró cero filas idénticas repetidas y cero duplicados/nulos en la clave candidata `(folio,nro)`. El pipeline repetirá estos controles y detendrá la construcción de una nueva candidata si aparece un conflicto; no elimina automáticamente registros. El diagnóstico encontró respuestas alfabéticas en campos identificadores y en campos textuales abiertos, así como tokens y valores que no son texto libre. Por eso una conversión indiscriminada a minúsculas sería incorrecta. S-02 transforma solo las 13 columnas enumeradas en `LOWERCASE_TEXT_RESPONSE_COLUMNS`; los demás valores mantienen su forma original.

### Regla adicional de calidad por columna (L-80)

En la corrida histórica `20261004T171822Z_...`, L-80 se calculó sobre todas las filas y excluyó 125 columnas; la revisión posterior demostró que ese denominador causa falsos descartes. Por ejemplo, `s04c_17a` pasó de 81,3505 % de ausencia global a 4 faltantes de 7.370 elegibles al aplicar su filtro DDI. Por tanto, las 125 exclusiones de ese candidato son **históricas y provisionales**; no se aplican al maestro vigente, que conserva el esquema completo.

La regla se redefine para la siguiente versión del pipeline: (1) el conjunto maestro conserva las columnas de origen; (2) para cada variable se reporta ausencia global y, cuando se pueda reconstruir un filtro documentado, `N elegible`, `N respondido`, `N faltante elegible` y su porcentaje; (3) L-80 solo puede excluir una variable de una vista analítica por defecto si el porcentaje supera estrictamente 80 % **dentro del universo elegible confirmado**; (4) si no existe regla de elegibilidad confirmada, la variable se conserva y se marca `REVIEW_UNIVERSE`, sin tratar no elegibles como errores. Las variables excluidas de una vista permanecen disponibles en el maestro y en vistas focalizadas. No se modifica `data/persona.csv`.

Las primeras reglas candidatas respaldadas directamente por el DDI son `s04b_13` con `s04b_12 ∈ {1,2,7}`, `s04c_17a` con `s04b_12 ∈ {1,2,8}`, `s04e_26_cod` con `s04e_25 = 1` y `s04e_28` con `s04e_25 = 1` más `s04e_27 ∈ {1,2,7}`. Deben guardarse con referencia DDI, versión, prueba de máscara y reporte de valores fuera del filtro. El resto requiere cotejo variable por variable; no extrapolar estos filtros.

### Seguimiento de auditoría por universos (2026-10-04)

La auditoría de universos queda como actividad de preparación anterior a ejecutar L-80. La matriz de exclusiones registra denominadores locales solo para reglas cotejadas; una regla marcada `LOCAL_RULE_CHECKED_DDI_MATCH` aún es provisional si la procedencia/esquema de la copia no coincide plenamente con F27. `DDI_CONFLICT_REQUIRES_PROVENANCE` bloquea cualquier máscara automática. Ejemplo bloqueado: `s02b_10`, cuyo DDI local marca `s02b_09b >= 2017` y la ficha oficial consultada marca `s02b_09b > 2020`; tampoco se resuelve una diferencia de 6.339 frente a 6.226 valores locales/oficiales para el año. Los porcentajes por elegibles de una regla conflictiva no se usan para excluir, corregir ni imputar.

Los nueve nuevos casos de fecundidad con conteo elegible/respondido se registran en `universe-matrix-persona.csv` junto con los conteos, la expresión de filtro y la base de evidencia. Los cinco conflictos señalados no tienen regla automatizable. Los datos crudos siguen intactos. Se debe terminar el inventario entero de 125 exclusiones por área temática y reconciliar DDI/cuestionario/copia local antes de promover una versión nueva; el umbral global anterior solo describe al candidato histórico y no define el dataset maestro.

## Versión maestra conservadora — 4 de octubre de 2026

La decisión vigente conserva las 39.497 filas y las 275 columnas de `persona.csv`. L-80 mide ausencia/formato técnico global para priorizar revisión; **no elimina columnas** porque los saltos y subuniversos hacen que la ausencia global no mida la calidad entre personas elegibles. El candidato histórico `20261004T171822Z_568e82e3039d_d3abfb0b5f` (150 columnas) es solo evidencia de una corrida previa y no es el maestro final.

La línea base técnica aplicaba estructura/clave, normalización tipada y perfiles, pero no transformaba ningún valor. La regla S-01 descrita abajo es la única excepción semántica incorporada desde entonces. `NA`, vacío, cero y no aplica no se colapsan; no se imputan valores, no se eliminan filas, categorías, extremos ni variables. Los dominios desconocidos y discrepancias entre preguntas quedan como incidencias, no como correcciones.

La versión publicada internamente se etiqueta `published_internal_with_semantic_limitations`: pasó manifiesto, esquema, clave, recuentos, diferencias y artefactos. Esto no afirma limpieza semántica integral. La persistencia elegida es JSON local; se conserva la advertencia por diferencias con F27 y saltos no confirmados.

## Resultado ejecutado y validado — versión maestra técnica — 4 de octubre de 2026

La ejecución `20261004T200928Z_568e82e3039d_d3abfb0b5f` escribió `persona_clean_master.csv` y `persona_clean_master.parquet` con 39.497 filas y 275 columnas. Retuvo íntegro el esquema, pues L-80 global solo genera una alerta; los universos incompletos impiden usarlo como descarte. El hash SHA-256 de `persona.csv` sigue igual. Las claves `(folio,nro)` se compararon en streaming entre raw y salida: todas son completas, únicas y conservan orden/valor. También se contaron todas las filas/campos, se validó el metadato Parquet, los perfiles y 275 gráficos. No cambió ningún valor de celda: no había espacios exteriores que las reglas tipadas pudieran recortar. Por eso el resultado es una línea base reproducible, no una limpieza de errores semánticos; no imputar/eliminar/corregir es deliberado hasta tener regla validada.

### Primera regla semántica aplicada (S-01)

La versión posterior `20261004T204302Z_568e82e3039d_d3abfb0b5f` aplica el primer dominio físico verificable: `phrs`, `shrs` y `tothrs` representan horas semanales según el DDI F27; más de 168 horas por semana es imposible. Se cambiaron a `NA` exactamente tres celdas, conservando las filas y el resto del esquema. La bitácora restringida identifica fila CSV, variable, valor anterior, valor nuevo y justificación. Una comparación independiente confirmó que esas fueron las únicas diferencias frente a raw; se validaron clave/orden, Parquet, notebook/script y hashes de 285 artefactos. La fuente no se modificó.

S-01 no completa la limpieza semántica del dataset. Las anomalías sobre edad/año, `totper`, referencias de roster, dominios de códigos y valores monetarios permanecen en revisión sin alteración automática. Ver [auditoría semántica](semantic-cleaning-audit.md) y evidencia en [progreso](progress.md).

### Vistas por sección y universo

La corrida candidata vigente agrega 11 vistas documentadas por unidad, selección y universo; no particiona ni descarta la fuente maestra. Salud general y campos con saltos conservan todos los registros cuando no hay un filtro universal por vista. Educación usa edad ≥4 y empleo edad ≥7; los submódulos de fecundidad, niñez y ocupación secundaria tienen vistas separadas. Los casos secundarios con respuesta contradictoria se retienen con bandera de revisión. El resumen hogar es una fila por `folio`, no detecta conflicto entre valores observados y consolida una copia observada única cuando las otras filas tienen ausencia explícita; nueve variables requieren ese paso en 17 folios cada una. La consolidación se limita a la vista hogar, se audita, y no cambia ni el maestro ni la vista por persona.

Las vistas conservan variables de diseño disponibles, sin declarar inferencia válida. Para estimar subpoblaciones se debe aplicar método de dominio compatible con el diseño; no interpretar la tabla filtrada como muestra independiente. Los contenidos, conteos y advertencias están en [thematic-views-persona.md](thematic-views-persona.md). No se incluyeron secciones que no están en el único input permitido (`persona.csv`).

Diagnósticos: 125 columnas superan 80 % ausencia global; 49 magnitudes tienen alertas IQR (no son errores confirmados); ningún registro fue marcado mal formado por las validaciones limitadas activas. Las pruebas sintéticas pasaron para retención de una columna 100 % vacía, idempotencia del trim y bloqueo ante clave duplicada. Python 3.13.14; pandas 3.0.6, NumPy 2.5.3, Matplotlib 3.11.2, PyArrow 25.0.1. No se usó ni modificó el venv. Se agregó hash del código al manifiesto de esta ejecución y se incorporó generación automática del hash en las siguientes corridas. `git diff --check` pasó. No hubo publicación Flask/PostgreSQL.
