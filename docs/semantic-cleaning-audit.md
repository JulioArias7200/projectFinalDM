# Auditoría y limpieza semántica de `persona.csv`

## Alcance y estado

La limpieza semántica verifica que cada valor tenga sentido según la definición, unidad, universo y relaciones del cuestionario. No equivale a borrar outliers estadísticos: un valor extremo plausible se conserva. La fuente `data/persona.csv` permanece inmutable; los cambios se producen solo en una nueva salida candidata con bitácora de celdas.

Se implementa S-01 para `phrs`, `shrs` y `tothrs`: el DDI oficial EH2025 define estas variables como horas promedio trabajadas por semana. Un valor superior a 168 excede las horas disponibles en una semana y es imposible. En la salida candidata se convierte a `NA` (dato inválido, no imputado); la fila permanece. `semantic_cell_changes_restricted.csv` registra número de fila CSV (incluye encabezado), variable, valor fuente, valor de salida, regla, razón y referencia. El número de fila permite localizar el dato en el raw inmutable y se considera información restringida. El manifiesto incluye el hash del artefacto.

El umbral de 168 es un límite físico, no un límite observado del DDI ni una regla estadística. No se recortan valores al máximo ni se sustituyen por una estimación. Las horas iguales a 168 se conservan.

## Reglas ejecutables

| ID | Variables | Prueba | Acción | Estado |
|---|---|---|---|---|
| S-01 | `phrs`, `shrs`, `tothrs` | Horas semanales numéricas >168 | Marcar únicamente esa celda `NA`; preservar fila y auditar valor anterior | Aplicada; verificar conteos y trazabilidad en la nueva ejecución |
| L-80 | Todas | Ausencia/error técnico global >80 % | Solo alerta; no eliminar columnas porque incluye no elegibles de saltos | Aplicada como diagnóstico |
| L-03 | Campos permitidos por diccionario | Espacios periféricos | Recorte tipado si existe; no modificar IDs, texto libre ni tokens de ausencia | Aplicada cuando corresponde |

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

## Siguiente trabajo necesario

La ejecución S-01 debe comprobar cantidad de celdas corregidas y que la bitácora permite reconstruir los valores fuente. Luego se requiere auditoría variable por variable de dominios codificados, unidades, periodos, edades/universos y saltos, apoyada en el cuestionario/manual exactos del archivo. Cada nueva regla necesita evidencia, prueba sintética, conteos antes/después, bitácora y revisión de impacto. La discrepancia local vs. F27 (39.497×275 frente a 39.485×276) impide tratar la edición del catálogo como contrato automáticamente idéntico.

La salida permanece candidata, no publicada. Este documento no declara terminada la limpieza semántica integral.
