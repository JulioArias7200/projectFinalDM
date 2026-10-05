# Auditoría y limpieza semántica de `persona.csv`

## Alcance y estado

La limpieza semántica verifica que cada valor tenga sentido según la definición, unidad, universo y relaciones del cuestionario. No equivale a borrar outliers estadísticos: un valor extremo plausible se conserva. La fuente `data/persona.csv` permanece inmutable; los cambios se producen solo en una nueva salida candidata con bitácora de celdas.

Se implementa S-01 para `phrs`, `shrs` y `tothrs`: el DDI oficial EH2025 define estas variables como horas promedio trabajadas por semana. Un valor superior a 168 excede las horas disponibles en una semana y es imposible. En la salida candidata se convierte a `NA` (dato inválido, no imputado); la fila permanece. `semantic_cell_changes_restricted.csv` registra número de fila CSV (incluye encabezado), variable, valor fuente, valor de salida, regla, razón y referencia. El número de fila permite localizar el dato en el raw inmutable y se considera información restringida. El manifiesto incluye el hash del artefacto.

El umbral de 168 es un límite físico, no un límite observado del DDI ni una regla estadística. No se recortan valores al máximo ni se sustituyen por una estimación. Las horas iguales a 168 se conservan.

## Reglas ejecutables

| ID | Variables | Prueba | Acción | Estado |
|---|---|---|---|---|
| S-01 | `phrs`, `shrs`, `tothrs` | Horas semanales numéricas >168 | Marcar únicamente esa celda `NA`; preservar fila y auditar valor anterior | Aplicada; verificar conteos y trazabilidad en la nueva ejecución |
| S-02 | 13 campos explícitos de respuesta abierta `*_e` / “Especifique” | Texto alfabético no faltante | Pasar a minúsculas solo la respuesta, preservar `NA`, código, identificador y raw; bitácora de cada celda | Aplicada en candidata `persona-317279aafe9023a2` |
| L-80 | Todas | Ausencia/error técnico global >80 % | Solo alerta; no eliminar columnas porque incluye no elegibles de saltos | Aplicada como diagnóstico |
| L-03 | Campos permitidos por diccionario | Espacios periféricos | Recorte tipado si existe; no modificar IDs, texto libre ni tokens de ausencia | Aplicada cuando corresponde |
| L-06 | Todas; clave candidata `(folio,nro)` | Filas idénticas, claves repetidas y componentes vacíos | Auditar y bloquear si hay conflictos; no eliminar filas automáticamente | 0 filas idénticas, 0 duplicados de clave, 0 claves incompletas en las 39.497 filas |

S-02 usa una lista explícita en `LOWERCASE_TEXT_RESPONSE_COLUMNS` porque convertir a minúsculas las 275 columnas cambiaría identificadores y códigos. Las 13 columnas son `s01b_12e`, `s02a_01e`, `s02a_02he`, `s02b_10e`, `s03a_05e`, `s03b_11e`, `s03c_17e`, `s04a_06e`, `s04a_07e`, `s05a_02ce`, `s05b_06ae`, `s05b_06be` y `s05b_06ce`. Se registraron 12.516 celdas de respuestas abiertas normalizadas; no se imprime su contenido en reportes públicos. Los detalles antes/después quedan en `semantic_cell_changes_restricted.csv`, artefacto de acceso restringido. El fundamento está descrito en `docs/cleaning-methodology.md`.

## Validación de la candidata actual — 4 de octubre de 2026

La corrida `data/proprosessing/output/20261004T231539Z_568e82e3039d_d3abfb0b5f/` produjo la versión candidata `persona-317279aafe9023a2`. Conserva 39.497 filas y 275 columnas, la secuencia de `(folio,nro)` y el SHA-256 del raw (`568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`). La comparación independiente raw→candidata encontró 12.519 celdas diferentes: 12.516 por S-02 y 3 por S-01 (`phrs`: 1, `tothrs`: 2). No cambió ninguna otra columna. Hay 275 gráficos y 300 artefactos con hashes registrados. L-03 no halló espacios exteriores que modificar. La candidata no se publica como versión oficial.

## Hallazgos semánticos que siguen en revisión

Estos casos se identificaron mediante reglas y relaciones del DDI/dataset. No se alteran porque falta resolver versión, universo o convención de captura:

| Hallazgo | Evidencia agregada | Tratamiento actual y decisión requerida |
|---|---|---|
| `totper` frente al tamaño de roster | 12.718 hogares; el campo es constante dentro de cada hogar, pero coincide con las filas-persona del hogar en solo 2.433 hogares. | No usarlo como denominador o conteo de miembros hasta confirmar definición y versión del archivo. `yhogpc` sí concuerda con `yhog / filas del hogar` en 12.701 hogares comparables, sin discrepancias. |
| Edad (`s01a_03`) frente a año de nacimiento | Usando 2024 como referencia, 36.176 casos coinciden con `2024 - año_nacimiento`; 3.321 difieren por un año. | No recalcular edad: falta fecha de referencia exacta y regla de cumpleaños/periodo de encuesta. |
| Integrantes de referencia (`s01a_05a/b/c`) | 4 de 45.483 referencias comprobadas no apuntan a un `nro` presente en el roster del hogar. | No remapear ni borrar; cotejar códigos, roster y edición del cuestionario. |
| Casos fuera de máximos/rangos publicados en DDI | Se detectaron diferencias en horas, ingresos y montos. Algunos rangos publicados son extremos observados y hay al menos una contradicción entre el campo rango y categorías (`s05b_06ba` incluye códigos 2250/2500 pese a rango indicado hasta 2000; `s04c_18b` declara 0–0 pese a describir monto anual). | Los rangos del catálogo no se usan automáticamente como dominios válidos. Confirmar cuestionario y metadatos de la versión local antes de clasificar cada caso. |
| Códigos aparentemente fuera de listas | El DDI puede listar valores observados para respuestas abiertas “otro, especifique”; algunas variables y conteos locales no coinciden con F27. | No aplicar listas cerradas indiscriminadamente. Separar categorías codificadas, texto abierto, especiales y saltos por variable. |
| Ingresos, pobreza y horas con IQR alto | IQR marca observaciones distantes, sin distinguir error de extremo económico real. | Conservar. Revisar con unidades, periodo de referencia, componentes y relaciones derivadas. No winsorizar ni eliminar por IQR. |

## Consistencias cruzadas comprobadas

- `p0`, `p1`, `p2` concuerdan con las fórmulas FGT estándar a partir de `yhogpc` y `z` en 39.477 filas comparables, con tolerancias numéricas documentadas en el análisis.
- `yper` concuerda con `ylab + ynolab` en 16.709 filas completas (tolerancia de 0,02), sin casos discrepantes.
- `yhogpc` concuerda con el ingreso del hogar dividido por el roster observado en 12.701 hogares comparables. Esto no valida `totper` como variable.
- Estas verificaciones no validan ponderadores, errores de diseño muestral ni equivalencia exacta entre el CSV local y la edición F27 consultada.

## Dictamen de revisión semántica y disposición — 4 de octubre de 2026

Se revisaron los hallazgos de esta auditoría junto con el diccionario local y las reglas metodológicas de `curso/02_tipos_de_datos.md`, `curso/03_estadistica_descriptiva.md`, `curso/05_preparacion_de_datos.md` y `curso/11_calidad_y_ciclo_de_vida.md`. El principio aplicado es no convertir una alerta estadística en una corrección sin semántica/universo confirmado; IQR y frecuencia no prueban error. Las disposiciones son:

| Hallazgo | Disposición de esta revisión | Motivo |
|---|---|---|
| S-01: `phrs`, `shrs`, `tothrs` >168 horas semanales | Aplicar a las tres celdas afectadas, con valor inválido marcado como `NA` y traza | Límite físico de una semana, unidad definida como horas semanales; no se eliminan filas ni se imputan valores. |
| S-02: respuestas abiertas identificadas como “Especifique” | Normalizar a minúsculas solo las 13 columnas autorizadas; guardar diff restringido | Transformación textual explícita y reversible desde el raw; no se extiende a códigos o identificadores. |
| L-06: duplicados y clave `(folio,nro)` | Validar y bloquear ante conflicto; no borrar registros | No se encontraron duplicados ni claves incompletas; la deduplicación no es necesaria en esta copia. |
| `totper` frente a filas persona por `folio` | **Conservar y bloquear su uso como conteo/denominador** | Extensión local fuera del esquema F27; definición de miembro y procedencia no confirmadas. 10.285/12.718 hogares no coinciden en el control censal. |
| Edad frente a año de nacimiento | Conservar ambos valores | No se conoce fecha de referencia exacta ni regla de cumpleaños; la diferencia de un año no basta para recalcular. |
| Referencias a integrantes del roster | Conservar y reportar las cuatro excepciones | Es necesario confirmar semántica/códigos de referencia y equivalencia de esquema antes de remapear. |
| Rangos, categorías y valores extremos | Solo alertas; no recortar, winsorizar ni eliminar | Hay máximos contradictorios o posiblemente observados en el DDI; IQR identifica distancia estadística, no invalidez. |
| Faltantes por columnas con universos incompletamente mapeados | Conservar campos y estados originales; no imputar ni eliminar por L-80 global | La ausencia fuera del universo puede ser estructural; no se conocen todos los saltos aplicables a la copia local. |

**Resultado de la etapa:** no se encontró una tercera transformación segura que pueda aplicarse al maestro con evidencia disponible. Por tanto, el cambio semántico adicional en esta etapa es cero celdas. La candidata existente ya refleja las dos reglas transformadoras respaldadas; las alertas pendientes quedan intactas y documentadas. Esta decisión no significa que las 275 columnas hayan superado una validación semántica integral: 162 se revisaron solo en formato numérico sin dominio confirmado y 111 siguen con dominio no evaluado, según el perfil documentado.

La validación independiente y la publicación JSON constan en [validación final y muestra de auditoría](final-validation-sampling-persona.md). La versión supera sus diez controles estructurales y está **publicada para uso interno con limitaciones semánticas explícitas**. No se declara “dataset semánticamente limpio” en todas sus columnas: CA-19 sigue parcial. El CSV de origen no cambia.

### Cierre condicionado

El cierre semántico completo requiere resolver definiciones, universos y procedencia con metadatos compatibles con la copia local. El catálogo JSON apunta a la versión técnica publicada. JSON se eligió para persistencia local y no ofrece transacciones distribuidas ni alta disponibilidad; la publicación actual es interna. No se deben usar columnas pendientes para indicadores semánticos concluyentes.

## Siguiente trabajo necesario

La ejecución actual ya incluye los controles de duplicados y S-02. La matriz de universos cubre las 125 columnas que superaban el umbral técnico global en la corrida histórica, pero su revisión semántica sigue parcial; consultar sus estados y pendientes en [observaciones de universos](observaciones-universos-persona.md). Sin análisis del cuestionario ni otra fuente semántica confirmada, dominios, unidades, periodos, universos y rangos no confirmados quedan como limitaciones; no se inventan correcciones a partir de la distribución observada. Cada regla nueva requiere evidencia permitida, prueba sintética, conteos antes/después, bitácora y revisión de impacto. La discrepancia local frente a F27 (39.497 × 275 frente a 39.485 × 276) impide tratar el catálogo como contrato automáticamente idéntico.

La salida permanece candidata, no publicada. Este documento no declara terminada la limpieza semántica integral.
