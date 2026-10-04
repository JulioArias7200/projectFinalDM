# Revisión estadística del trabajo de conciliación y universos

**Fecha:** 4 de octubre de 2026  
**Alcance:** revisión del informe `source-reconciliation-persona.md` y de los hallazgos de fecundidad que lo preceden; no es certificación total de calidad de las 275 columnas.

## Veredicto

El trabajo anterior es **parcialmente correcto y prudente en su decisión principal**: el conteo y esquema locales se compararon correctamente con los metadatos F27 disponibles; se conservó `persona.csv`; y se dejó la procedencia sin atribuir. Sin embargo, algunos resultados se interpretaron con más certeza de la permitida y dos observaciones de fecundidad fueron descritas erróneamente como discrepancias del DDI local. La revisión estructural no basta para afirmar que el dataset está estadísticamente validado, que el cuestionario corresponde a F27 o que el candidato previo está limpio.

## Comprobaciones que sí quedan respaldadas

| Aspecto | Evaluación |
| --- | --- |
| Estructura física | Correcta para el parser probado: 39.497 registros locales, 275 campos por registro, sin encabezados repetidos ni registro truncado por comillas abiertas. El decodificador UTF-8 estricto pudo leer el flujo completo. Esto valida legibilidad, no significado. |
| Huella y preservación | SHA-256 y tamaño coinciden con el manifiesto de la corrida histórica. No se modificó `data/persona.csv`. |
| Comparación de nombres | Correcta según el JSON local: 273 nombres compartidos, tres en el DDI F27 que no están en el CSV (`s01b_10a`, `s05c_09be`, `s05c_09aa`) y dos locales no listados como variables F27 (`s05c_09e`, `totper`). |
| Diferencia de casos | Correcto informar una diferencia aritmética de 12 entre 39.497 registros locales y los 39.485 casos que declara ANDA. No se puede llamar a esos 12 “registros sobrantes” comparables sin tener prueba de que ambas cifras describen la misma versión y unidad. |
| Procedencia | Correcto dejarla como no confirmada. La diferencia estructural respalda una alerta, pero no identifica quién entregó el archivo ni la causa del cambio. |
| Clave candidata | Control adicional: `(folio,nro)` no tiene valores vacíos/`NA` ni duplicados exactos como texto en la copia analizada; `folio` tiene 12.718 valores distintos. Esto apoya la unicidad técnica de la clave candidata en este archivo, pero no certifica que sea la clave institucional para otros archivos o versiones. |

ANDA publica 39.485 casos y 276 variables para EH2025_Persona/F27. Su ficha de `nro` declara rango 1–14; en el CSV local los valores observados abarcan 1–15 y hay un registro con `nro=15`. Esto debe quedar como **una excepción de dominio para investigar**, no cambiarse ni rechazarse automáticamente. [Diccionario oficial](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona), [ficha de `nro`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V1957?name=nro).

## Correcciones a conclusiones anteriores

### Codec `utf-8-sig`

El informe anterior decía que el manifiesto había “sobrestimado” el BOM por registrar `utf-8-sig`. Esa frase es incorrecta: el codec `utf-8-sig` puede leer archivos UTF-8 con BOM y sin él. Los bytes locales indican que este archivo no tiene BOM y su contenido se decodifica como UTF-8 estricto. Esto no desacredita la corrida ni es una falla de codificación; solo se registra el hecho físico del BOM ausente.

### `s02b_11` y `s02b_14a`

Se había descrito que sus textos `pre_question_text` podían estar asociados a columnas equivocadas. La ficha oficial F27 de `s02b_11` sí presenta la pregunta del conteo de nacidos vivos como pre-pregunta; la ficha oficial de `s02b_14a` también presenta la pregunta del Subsidio Prenatal del último embarazo. Por tanto, esos textos **no son por sí mismos evidencia de desalineación del JSON local**. Las fichas oficiales documentan `s02b_11` y `s02b_14a` con esas pre-preguntas. [Ficha de `s02b_11`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2015?name=s02b_11), [ficha de `s02b_14a`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2021?name=s02b_14a).

Una pre-pregunta tampoco demuestra por sí sola el filtro operativo. Hay que distinguir texto contextual, condición de universo y salto efectivo según cuestionario/manual. La matriz se corrigió: `s02b_11` y `s02b_14a` pasan a requerir mapeo e interpretación; `s02b_13` y `s02b_14` quedan pendientes de universo; ya no se cuentan entre cinco conflictos confirmados. En la matriz actual solo `s02b_10` conserva el estado de conflicto de contrato.

Para `s02b_14a`, la copia local tiene 2.077 casos bajo el filtro candidato `s02b_13=1`, con 382 valores de meses y 1.695 vacíos. Pero la distribución local de `s02b_14` es 382 sí y 1.695 no, y los 382 con `s02b_14=1` tienen valor de meses. Esto **sugiere** que los 1.695 vacíos de `s02b_14a` podrían ser saltos válidos tras responder no a `s02b_14`. No se debe reportar el 81,6081 % como no respuesta confirmada hasta validar la ruta y el cruce fila a fila. La matriz deja ambos denominadores explícitos y bloquea una regla productiva.

### `s02b_10`: sensibilidad calculada bajo ambos cortes

El conflicto de corte se mantiene: el DDI local indica desde 2017, y la ficha F27 de `s02b_09b` dice continuar si el nacimiento fue después de 2020. Aplicados a la copia solo como sensibilidad: con año `>=2017` hay 3.452 casos, 2.711 respuestas y 741 ausencias; con año `>2020` hay 1.856 casos, 1.716 respuestas y 140 ausencias (7,5431 %). Estos denominadores describen patrones locales; no validan el corte ni el origen. [Ficha F27 de `s02b_09b`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2012?name=s02b_09b).

## Límites del trabajo anterior

- El informe de procedencia no prueba licencia, versión de cuestionario, productor ni transformación de origen; requiere documentación del archivo local.
- La comparación del número de columnas y registros no establece cuál de los dos archivos es “correcto”.
- Los encabezados comunes se pueden seguir cotejando variable por variable con DDI, cuestionario y patrones; la diferencia global no invalida automáticamente cada etiqueta o regla. Sí exige no atribuir resultados al F27 ni automatizar reglas sin mapeo probado.
- No se verificó aquí duplicación exacta de filas, todos los dominios, rangos por columna, ausencias según universo para las 125 exclusiones, valores fuera de filtro en cada módulo, pesos ni diseño muestral.
- No se ejecutaron pipeline ni pruebas del proyecto. Los conteos de esta revisión son auditoría exploratoria agregada, no una versión publicada ni datos corregidos.

## Registro de cambios realizados durante la revisión

- Corregida en `source-reconciliation-persona.md` la interpretación del codec `utf-8-sig`.
- Añadidos el control de unicidad técnica `(folio,nro)` y la alerta `nro=15` frente al rango oficial 1–14.
- Corregidas las conclusiones sobre pre-preguntas de `s02b_11` y `s02b_14a` en `observaciones-universos-persona.md`.
- Incorporada sensibilidad local para ambos cortes de `s02b_10`.
- Actualizados estados, próximos pasos y denominadores de esas variables en `universe-matrix-persona.csv`.
- `persona.csv` no se modificó; no se corrigió, eliminó ni imputó ningún valor.

## Dictamen de uso

El diagnóstico de procedencia es válido como advertencia estructural, pero el análisis previo de fecundidad requiere estas correcciones antes de usar sus porcentajes para decidir limpieza. El CSV puede seguirse perfilando técnicamente; la publicación de resultados oficiales, la exclusión L-80 y la edición de valores deben esperar la conciliación del instrumento, la revisión de dominios y la validación completa de reglas.
