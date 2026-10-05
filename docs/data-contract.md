# Contrato de datos y limpieza

## Alcance de los archivos

El único archivo de datos de entrada de esta etapa es `data/persona.csv`, que se conserva de solo lectura. El JSON del diccionario se consulta únicamente para metadatos de variables, etiquetas y universos; no se cargan otras fuentes de datos ni se hacen uniones.

## Contrato específico de `persona.csv`

El contrato de personas registra: identificador, propietario, finalidad, origen, licencia/permiso, formato, codificación, delimitador, encabezado, clave de registro, versión de esquema, columnas y tipos, nivel persona/hogar, universos, tokens, dominios, reglas de calidad, política de publicación, campos sensibles y métricas permitidas. Flask y el pipeline consumen la misma configuración versionada en JSON; `data/audit_log.json` guarda linaje y eventos. Rechazar o solicitar mapeo si cambia un encabezado requerido. La generalización a otros datasets no es requisito de esta entrega.

Ejemplo ilustrativo de configuración (no ejecutable aún):

```yaml
dataset_id: encuesta_personas
schema_version: 1
source_file: data/persona.csv
format: csv
encoding: utf-8 # leído en modo estricto; sin BOM observado (no confirma procedencia)
delimiter: ','
record_key: [folio, nro] # clave técnica completa/única en copia actual; confirmar semántica y versión
origin_tokens: ['', 'NA', '0'] # estados distintos, no una lista de nulos equivalentes
missing_policy: per_column_and_universe # pendiente de diccionario y saltos
sensitive_columns: [folio, s02a_01a, yhogpc]
survey:
  weight: factor
  strata: estrato # confirmar definición oficial
  cluster: upm    # confirmar diseño oficial
  year: null       # no inferir
quality:
  max_critical_errors: 0
  quarantine_invalid_rows: true
```

Los campos sensibles de ejemplo no son una lista exhaustiva. Clasificar todas las columnas antes de permitir acceso a microdatos.

## Observaciones del archivo actual

La revisión estructural y las diferencias con F27 se registran en [conciliación de procedencia y esquema](source-reconciliation-persona.md), y su evaluación está en [revisión estadística](review-statistical-quality-persona.md). Para el alcance de este proyecto, el usuario confirma `data/persona.csv` como fuente definitiva de trabajo. Esto resuelve qué archivo se debe procesar, pero no certifica identidad con F27 ni resuelve condiciones de licencia/publicación externa. La codificación se leyó como UTF-8 estricto y no se observó BOM; esto acredita legibilidad, no procedencia. Las reglas DDI pueden contrastarse individualmente con cuestionario y patrones locales, pero no deben automatizarse como reglas productivas hasta mapear la versión y probar cada máscara.

`data/persona.csv` tiene 39.497 filas de datos, 275 encabezados y un tamaño de 34.568.646 bytes al momento de la inspección. La primera fila es el encabezado. Se identificaron columnas como `folio`, `nro`, `area`, `depto`, `factor`, `estrato`, `upm`, `condact`, `yhogpc`, `p0`, `niv_ed` y `aestudio`. Este es el único archivo de datos de entrada del alcance. `data/proprosessing/data_dictionary.json` se consulta exclusivamente como metadato para etiquetas, definiciones y universos.

El [INE publica el diccionario EH2025_Persona](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona) y su DDI oficial. El diccionario local [data_dictionary.json](../data/proprosessing/data_dictionary.json) conserva las 276 variables F27, sus etiquetas, preguntas, universos, formatos, rangos y categorías. También registra las extensiones locales por separado.

La ficha oficial declara 39.485 casos y 276 variables, mientras `data/persona.csv` contiene 39.497 registros y 275 columnas. La comparación exacta de encabezados encontró solo en F27 `s01b_10a`, `s05c_09be` y `s05c_09aa`; solo en el CSV local `s05c_09e` y `totper`. No se deben equiparar esos campos por parecido de nombre ni tratar el CSV como la misma versión sin confirmar su procedencia. El diccionario oficial puede rotular las variables coincidentes, pero las reglas semánticas y los dominios para limpieza requieren reconciliar esta diferencia, el año/licencia del archivo y el cuestionario aplicable.

La ejecución histórica `20261004T171822Z_568e82e3039d_d3abfb0b5f` conservó 39.497 filas y solo 150 columnas al aplicar L-80 global; no es el maestro recomendado. La versión vigente `persona-317279aafe9023a2` conserva 39.497 filas y 275 columnas. L-80 es una alerta y las correcciones semánticas son las tres celdas S-01; S-02 cambia solo texto abierto designado. El raw no se modifica. La revisión de universos y dominios sigue incompleta. Flask consume la versión apuntada por el catálogo JSON.

## Perfil inicial requerido

El primer trabajo de ingesta debe producir, como mínimo:

- Conteo de líneas y registros parseados; filas ilegibles y causa.
- Cantidad de columnas, nombres duplicados, campos extra/faltantes y tipos candidatos.
- Nulos por columna distinguiendo token de origen y no aplicabilidad declarada.
- Cardinalidad, categorías frecuentes, mínimos, máximos, cuantiles y posibles valores atípicos para columnas numéricas válidas.
- Unicidad y nulos de la clave candidata `(folio, nro)`; duplicados exactos por hash de fila.
- Reglas de consistencia: `factor > 0` donde aplique; `totper > 0` si está presente; no negatividad de edades u horas donde la definición lo exija; relaciones de ingreso y pobreza solo tras confirmar semántica y redondeos.
- Distribución por `area` y `depto`, con códigos desconocidos señalados, sin inferir etiquetas no confirmadas.

Estas son verificaciones del futuro pipeline. La revisión técnica de lectura del 3 de octubre de 2026 confirmó la estructura, ausencia de claves textuales repetidas o faltantes y valores de `factor` numéricos, finitos y positivos para esta copia. Los resultados y límites están en [la metodología de limpieza](cleaning-methodology.md#diagnóstico-técnico-de-referencia); no constituyen validación semántica de todas las columnas.

## Estrategia de limpieza

| Paso | Acción | Evidencia que se guarda |
| --- | --- | --- |
| Parseo | Leer CSV con comillas y codificación configurada | Fila, error y archivo original |
| Normalización | Quitar espacios de campos donde proceda; uniformar tokens faltantes | Regla, columna y cantidad afectada |
| Tipado | Convertir números/fechas con formato explícito | Valores rechazados y motivo |
| Dominios | Validar códigos, rangos y dependencias del cuestionario | Conteos por regla y excepciones |
| Duplicados | Evaluar clave y hash de fila | Grupos duplicados, decisión de conservación |
| Correcciones | Aplicar solo parches aprobados | ID de propuesta y diff |
| Imputación | Ejecutar solo método aprobado para una variable y objetivo | Método, parámetros, máscara de imputación y diagnóstico |
| Validación final | Reconciliar entradas, salidas y cuarentena | Informe y decisión de publicación |

No aplicar una misma regla universal a todas las columnas: un `NA` puede ser dato faltante o salto legítimo del cuestionario. Conservar columnas de origen y registrar columnas derivadas con nombres y fórmulas documentadas. Las reglas de limpieza pueden ser deterministas o parametrizadas; si hay aleatoriedad, guardar semilla y versión de dependencias.

Aplicar el catálogo L-01 a L-12 de [la metodología](cleaning-methodology.md), fundamentado en `curso/`. El contrato JSON registra la definición de cada regla y sus condiciones; la bitácora JSON conserva sus resultados. La lectura inicial no convierte automáticamente tokens en nulos y la salida analítica mantiene metadatos o marcas de estado para distinguir vacío, `NA`, cero y no aplicabilidad. La imputación está deshabilitada por defecto.

## Reconciliación y salida

Cada ejecución debe cumplir `registros_parseados = registros_aceptados + registros_en_cuarentena`, ajustado explícitamente por deduplicación o agregación si se autoriza. Informar los cambios de tipo, conteo y nulos por columna entre raw y clean. Publicar Parquet tipado y CSV de exportación con codificación y formato definidos. Anexar manifiesto JSON con hashes, conteos, contrato, reglas y código. El CSV exportado no reemplaza el raw.

## Condiciones pendientes antes de estadísticas públicas

Confirmar: año y versión de la Encuesta de Hogares, procedencia y derechos del archivo, clave de persona, significado de códigos, universo de cada pregunta, factor de expansión, estratos, conglomerados, tratamientos de no respuesta y umbral de supresión. Sin estas confirmaciones, el dashboard puede mostrar perfil técnico interno, pero no atribuir estimaciones oficiales a la encuesta.

La versión maestra derivada vigente conserva 39.497 filas y 275 columnas. El pipeline registra cambios por celda y valida la clave `(folio,nro)`. No realiza imputación, correcciones de dominio, deduplicación ni eliminación de outliers. La versión fue copiada como artefacto inmutable y publicada internamente tras verificar manifiesto, clave, conteos y hashes; quedan explícitas las limitaciones semánticas.

## Ejecución vigente del maestro técnico

La versión publicada internamente es `data/proprosessing/versions/persona-317279aafe9023a2/`, con 39.497 filas y 275 columnas, S-01/S-02 y 11 vistas temáticas. Los manifiestos registran procedencia, reglas, artefactos y hashes. Los métodos inferenciales de la encuesta, universos y reconciliación con F27 siguen pendientes; la publicación no habilita inferencia oficial. Ver [progreso](progress.md), [vistas temáticas](thematic-views-persona.md) y [auditoría semántica](semantic-cleaning-audit.md).
