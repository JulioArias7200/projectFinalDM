# Conciliación de procedencia y esquema de `persona.csv`

**Fecha de revisión:** 4 de octubre de 2026  
**Estado:** discrepancia estructural confirmada; procedencia exacta pendiente  
**Alcance:** `data/persona.csv`, metadatos locales `data/proprosessing/data_dictionary.json` y manifiesto del candidato anterior. El DDI público se consultó como referencia de metadatos; no se incorporó otro archivo de microdatos.

## Resultado

El contenido local **no coincide exactamente en conteo ni esquema** con el archivo que el diccionario identifica como EH2025 Persona, archivo ANDA F27. No hay evidencia suficiente en el repositorio para probar de dónde se obtuvo `persona.csv`, qué versión/cuestionario lo produjo, ni bajo qué permiso/licencia fue entregado. El nombre genérico `persona.csv` y los metadatos locales que lo asocian a EH2025 no prueban identidad de origen. Por consiguiente, se adopta el estado `SCHEMA_MISMATCH_PROVENANCE_UNRESOLVED`; no se deben aplicar automáticamente dominios y saltos F27 al CSV local.

## Pasos ejecutados y evidencia

| Paso | Comprobación | Resultado | Qué permite concluir |
| --- | --- | --- | --- |
| 1 | Fijar alcance de entrada | Se revisó solo `data/persona.csv`; se usó el JSON y el manifiesto como metadatos/evidencia técnica. | No se combinaron otros microdatos ni se alteró el origen. |
| 2 | Identificar bytes y huella | 34.568.646 bytes; SHA-256 `568E82E3039D991A1EE0D8E2056448F8C465C03FFA838330C4F1522DD77BDDC8`. Primeros bytes `22-66-6F-6C`; el archivo comienza con comilla, no con BOM UTF-8. | Se decodifica como UTF-8 estricto y no se observó BOM. El codec `utf-8-sig` del manifiesto admite UTF-8 con o sin BOM; su uso no implica que el archivo contuviera uno y no constituye un error del manifiesto. |
| 3 | Parsear estructura CSV | Separador coma y comillas dobles; 39.497 registros de datos; 275 encabezados; cada registro tiene 275 campos; cero nombres de encabezado duplicados; cero filas con comillas sin cerrar. El flujo se leyó en modo UTF-8 estricto. | El archivo es estructuralmente legible bajo esta convención. No certifica que los valores respeten el cuestionario o sean semánticamente correctos. |
| 4 | Comparar encabezados con JSON DDI F27 | DDI: 276 nombres oficiales. Intersección exacta: 273 nombres. Solo DDI: `s01b_10a`, `s05c_09be`, `s05c_09aa`. Solo CSV: `s05c_09e`, `totper`. | No renombrar ni equiparar extensiones por similitud. Investigar si hubo transformación/versión distinta y documentar origen de las extensiones. |
| 5 | Comparar conteo local con catálogo | CSV local: 39.497 filas. F27 en ANDA/JSON: 39.485 casos. Diferencia: 12 filas adicionales localmente. | La diferencia podría tener varias causas, pero no se infiere cuál. Debe reconciliarse con quien entregó el archivo o con documentación de exportación; no se eliminarán 12 filas para forzar igualdad. |
| 6 | Revisar manifiesto del candidato previo | `20261004T171822Z_568e82e3039d_d3abfb0b5f` registra la misma huella, tamaño, encabezado y 39.497 filas; declara `pipeline_status: candidate; not published`, esquema no coincidente y “pending” respecto a procedencia. | Confirma qué archivo procesó esa ejecución. No aporta procedencia primaria. Su CSV reducido a 150 columnas sigue siendo candidato técnico histórico, no maestro ni entrega limpia. |
| 7 | Comprobar clave local candidata y un valor de diseño | `(folio, nro)` no tiene claves vacías/`NA` ni repeticiones exactas como texto en las 39.497 filas; hay 12.718 `folio` distintos. `nro` recorre 1–15 y aparece el valor 15 una vez. | La clave es técnicamente única en esta copia, no prueba que sea la clave oficial para todo uso. ANDA publica rango 1–14 para `nro`; el único `15` es una alerta de dominio que requiere cotejo, no corrección automática. [Ficha oficial de `nro`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V1957?name=nro). |

El catálogo oficial ANDA identifica EH2025 Persona como archivo F27 y declara 39.485 casos y 276 variables; también describe las secciones y universos de la encuesta. [Diccionario oficial EH2025_Persona](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona). El enlace verifica los metadatos publicados, pero no prueba que la copia local provenga de esa descarga.

## Identidad de variables y decisión

Las 273 columnas compartidas coinciden por nombre exacto. La coincidencia de nombre permite usar la etiqueta oficial como **referencia provisional**; no permite asumir que un dominio o salto aplica a esta copia si cambió la edición del formulario, el orden, las reglas de exportación u otra parte del contrato. La diferencia de esquema/conteo tampoco demuestra por sí sola que todos los metadatos para las columnas compartidas sean inválidos: se pueden cotejar regla por regla contra la ficha/cuestionario y los patrones locales, manteniéndolas provisionales hasta resolver la procedencia. Las cinco diferencias se registran así:

| Grupo | Variables | Acción actual |
| --- | --- | --- |
| En F27, ausentes localmente | `s01b_10a`, `s05c_09be`, `s05c_09aa` | No crear columnas ni inferir valores. Determinar si fueron omitidas, renombradas o no incluidas en la versión recibida. |
| En CSV, no listadas en F27 | `s05c_09e`, `totper` | Conservar en raw y marcar como extensión local. Identificar productor, definición, unidad, derivación y versión antes de usarlas. |

**Variables modificadas en esta revisión:** ninguna. No se renombró ninguna columna, no se cambió tipo o valor, no se retiraron filas ni columnas. Se actualizó únicamente el registro de conciliación y el estado de procedencia. En particular, los 12 casos extra no se consideran duplicados ni se eliminan; hace falta una regla y evidencia que lo justifique.

## Metadatos que faltan para cerrar la procedencia

Se necesita registrar, de fuente documental del archivo local: institución/productor y URL o medio de entrega; nombre y edición exactos del archivo de origen; fecha de descarga/exportación y filtros aplicados; cuestionario/DDI que acompañó esa versión; licencia o permiso; transformaciones antes de llegar al proyecto; razón de la diferencia de 12 casos; explicación del trío de columnas oficiales ausentes; definición y origen de `s05c_09e` y `totper`. La fecha de modificación del archivo en Windows no se toma como fecha de descarga ni evidencia de origen.

Hasta recibir o localizar esa evidencia, el JSON local mantiene los metadatos públicos F27 como referencias y los campos locales separados, pero el dataset queda marcado como no conciliado. Las reglas de universo previamente cotejadas siguen siendo diagnósticos candidatos; no se promoverán a reglas de limpieza productiva sobre la copia local.

## Instrumento oficial disponible para cotejo — 4 de octubre de 2026

La página de [materiales relacionados de EH 2025 en ANDA](https://anda.ine.gob.bo/index.php/catalog/256/related-materials) ofrece el cuestionario EH 2025 (fecha 2025-10-08), el Manual del/la Encuestador/a, el Manual del/la Supervisor/a y el Manual Técnico de Monitoreo. La descripción oficial indica que el cuestionario contiene flujos/saltos y cortes por grupos poblacionales; esos documentos son las referencias para terminar la matriz de universos y revisar dominios.

Disponibilidad documental no equivale a conciliación de `persona.csv`: el CSV local sigue teniendo 12 filas más, 3 variables F27 ausentes y 2 extensiones propias. El cuestionario servirá como fuente externa para cotejar las 273 columnas coincidentes, pero cada regla propuesta debe contrastarse con los códigos y patrones locales. No se importó ningún otro microdato, no se alteró el CSV y ninguna regla nueva se habilita solo por encontrar estos enlaces.

Referencias: [cuestionario EH 2025 (PDF)](https://anda.ine.gob.bo/index.php/catalog/256/download/1859), [Manual del/la Encuestador/a](https://anda.ine.gob.bo/index.php/catalog/256/download/1860), [Manual del/la Supervisor/a](https://anda.ine.gob.bo/index.php/catalog/256/download/1861) y [Manual Técnico de Monitoreo](https://anda.ine.gob.bo/index.php/catalog/256/download/1862). La página relacionada confirma autor INE, fecha y alcance general. El cotejo pregunta por pregunta y la correspondencia con la copia local siguen pendientes.

## Registro de cambios del proyecto

- Añadido este informe con los pasos, métricas, diferencias y decisión de procedencia.
- Actualizado `docs/data-contract.md` para enlazar el estado de esquema/procedencia.
- Actualizado `docs/progress.md` con las comprobaciones realizadas, comandos y limitaciones.
- `data/persona.csv` permanece de solo lectura y conserva su SHA-256.
- No se ejecutó el pipeline ni se generó/publicó un candidato nuevo. La ejecución automatizada completa queda pendiente; la auditoría de estructura aquí descrita se realizó con un lector CSV de streaming compatible con comillas y UTF-8 estricto.
- La revisión posterior de calidad detectó dos sobreinterpretaciones en la auditoría de ausencias de fecundidad (`s02b_11`, `s02b_14a`) y corrigió el sentido del codec `utf-8-sig`; los detalles están en `docs/review-statistical-quality-persona.md`.

## Próximo paso técnico

Usar primero el cuestionario y los manuales oficiales enlazados arriba para construir el mapa de preguntas, filtros y dominios de las 273 variables coincidentes; contrastar cada regla con los códigos observados en `persona.csv`, sin alterar filas/columnas ni corregir excepciones por inferencia. En paralelo, solicitar/localizar constancia de entrega, licencia y versión exacta del microdato. Si no se obtiene, declarar explícitamente una versión local derivada y producir un DDI de trabajo validado para las 275 columnas del CSV, manteniendo separado lo publicado por INE de las conclusiones locales. La falta de procedencia no impide el perfilado local, pero sí mantiene las reglas F27 como candidatas hasta comprobarlas.
