# Análisis estadístico y dashboard

## Alcance del sistema Flask

Las vistas se sirven con Flask y Jinja; JavaScript y Plotly ofrecen interacción y gráficos. La primera entrega prioriza calidad y limpieza de `persona.csv`, descriptiva de variables confirmadas y consulta de bitácora PostgreSQL. Los resúmenes y gráficos siguen [tipos de datos](../curso/02_tipos_de_datos.md), [descriptiva](../curso/03_estadistica_descriptiva.md) y [preparación](../curso/05_preparacion_de_datos.md). Los análisis inferenciales del catálogo son ampliaciones condicionadas, no funciones de la primera entrega.

## Contrato de un resultado

Todo resultado almacena y muestra: `dataset_id`, `version_id`, fecha de cálculo, universo, filtros, variable, unidad, tratamiento de nulos, ponderador, método, parámetros, tamaño de muestra no ponderado y advertencias. Las consultas de contenido y gráficos consumen únicamente la versión limpia publicada. La revisión de perfiles raw/clean es un flujo de calidad restringido, separado de los indicadores publicados. Al cambiar versión o filtros se recalculan las métricas y se invalida la caché correspondiente.

## Catálogo inicial de análisis

| Tipo | Métodos disponibles | Condición de uso |
| --- | --- | --- |
| Calidad | Nulos, valores inválidos, duplicados, distribución y cambios entre versiones | Cualquier columna declarada |
| Descriptiva numérica | Conteo, mínimo, máximo, media, mediana, cuantiles, desviación, histogramas | Tipo y unidad confirmados |
| Descriptiva categórica | Frecuencias, proporciones, barras, cruces | Códigos interpretados mediante diccionario |
| Relaciones | Correlación, dispersión, tablas cruzadas | Tipos compatibles; informar nulos y tamaño efectivo |
| Comparación | Diferencia de grupos, intervalos y pruebas apropiadas | Hipótesis, supuestos y control de múltiples pruebas definidos |
| Temporal | Series y cambios por periodo | Fecha real o periodo confirmado en el contrato |
| Encuestas | Totales, medias y tasas ponderadas; intervalos de confianza | Ponderador, estratos, conglomerados y universo confirmados |

Las técnicas inferenciales no se aplican automáticamente a todas las variables. El sistema debe advertir sobre muestras pequeñas, selección de grupos posterior a mirar resultados, valores extremos, distribución no adecuada o ausencia de diseño muestral. Un valor `p` no sustituye tamaño de efecto ni intervalo de confianza.

### Reglas para el caso `persona.csv`

- `factor` es candidato a ponderador. Antes de usarlo, confirmar que corresponde a la persona y a la edición exacta del archivo.
- `folio` representa hogar según el diccionario disponible; `nro` indica integrante. Comprobar la unicidad de `(folio, nro)` y evitar contar `yhog` una vez por cada persona cuando se quiere un total por hogar.
- Para proporciones de personas, mostrar `n` de registros válidos y suma de pesos. Una estimación ponderada simple de una categoría es `Σ(wᵢ · Iᵢ) / Σ(wᵢ)` sobre el universo definido. No aplicar pesos a un subconjunto diferente en numerador y denominador.
- `estrato` y `upm` son candidatos para estimar varianza de diseño. Confirmar estratificación, conglomerados, ajuste de pesos y tratamiento de estratos con una sola UPM antes de producir errores estándar e intervalos.
- `p0`, `p1`, `p2`, `pext0` y derivados de ingreso requieren definición de la edición concreta. No recalcular ni rotular índices de pobreza sin documentar línea, unidad, población y fórmula.
- Las variables de salud, educación, empleo e ingresos pueden tener saltos del cuestionario; filtrar el universo elegible antes de mostrar porcentajes.

### Vistas reproducibles ya generadas

El prototipo genera [11 CSV temáticos](thematic-views-persona.md) junto con cada versión candidata. El dashboard futuro puede usar sus columnas y filtros como puntos de partida, pero debe seguir mostrando versión, unidad, denominador y método. `empleo_secundario_casos.csv` incluye una excepción con filtro contradictorio marcada para revisión; no equivale a un universo depurado para inferencia. `hogar_resumen_persona_candidato.csv` reduce copias concordantes a una fila por `folio`, y no debe usarse para estimaciones de pobreza hasta confirmar `totper`, las definiciones de hogar y el ponderador de hogar. La coalescencia solo resuelve representaciones ausentes cuando queda un único valor observado; las celdas del maestro no se modifican.

Estas vistas no certifican inferencia. Si el dashboard calcula estimaciones, debe conservar el diseño muestral y emplear procedimientos de dominio/subpoblación para los filtros, no tratar cada archivo filtrado como una muestra aleatoria independiente.

## Vistas del dashboard

### 1. Resumen

Encabezado fijo con dataset de personas, versión publicada, fecha de actualización, origen, alcance de validación y filtros activos. Indicadores: filas aceptadas, rechazadas, columnas, completitud definida por universo, reglas fallidas y última ejecución. Las métricas pueden incluir composición por área/departamento, educación, actividad e ingresos únicamente cuando sus definiciones estén confirmadas. Las columnas pendientes se muestran como pendientes y no se utilizan en indicadores semánticos.

### 2. Exploración

Selector de columna y tipo de gráfico sugerido por tipo de dato. Tabla paginada o virtualizada con búsqueda, orden, filtros y metadatos de variable. Histogramas y boxplots para numéricas; barras para categóricas; dispersión para pares numéricos; cruces para categorías. Mostrar porcentaje de faltantes y denominador del gráfico. No exponer filas sensibles a usuarios sin permiso.

### 3. Calidad

Matriz de estados de ausencia por variable y universo, alertas de dominios, duplicados, valores extremos, cuarentena y comparación antes/después. Cada alerta enlaza con regla, referencia del curso, conteo y decisión. Mostrar vacíos, `NA`, no respuesta y no aplicabilidad por separado cuando estén clasificados; los estados pendientes no se rotulan como errores confirmados. La completitud no debe tratar saltos legítimos como errores. Las distribuciones antes/después deben usar universos comparables y explicar diferencias de composición.

### 4. Análisis

Constructor de análisis con variable, universo, filtros, ponderación y método. Mostrar tabla de resultados y gráfico, supuestos y advertencias. Permitir guardar una configuración reproducible. Los análisis largos son trabajos en segundo plano; el panel muestra progreso y error específico.

### 5. Cambios y versiones

Línea temporal de versiones, linaje, estado de publicación, diff de columnas y registros, solicitudes pendientes y decisiones. La bitácora PostgreSQL muestra fecha, actor, acción, regla, ejecución, versión, motivo, conteos y resultado con filtros y paginación. Los usuarios autorizados pueden proponer un parche; un responsable revisa diff y validaciones antes de decidir. El lector solo ve metadatos agregados sin valores sensibles; no recibe valores restringidos de auditoría en el HTML ni en respuestas JSON.

## Interacción y presentación

- Filtros globales aplican a todos los indicadores de la vista y aparecen como chips o resumen textual exportable. Cada tarjeta indica unidad y denominador.
- Toda comparación muestra las dos versiones o grupos y el cambio absoluto/relativo cuando matemáticamente procede.
- Para celdas pequeñas, aplicar supresión según política antes de entregar datos al frontend. La ocultación solo visual es insuficiente; evitar que totales o filtros permitan reconstrucción trivial.
- Usar colores consistentes para categorías y estados; ofrecer tabla de datos, etiquetas accesibles y estados de carga/error/vacío.
- Exportaciones de gráficos y tablas incluyen versión, filtros, fecha, método y nota de que una muestra no ponderada no equivale a estimación poblacional.

## Rendimiento y reproducibilidad

Preagregar métricas frecuentes por versión cuando su definición sea estable. Cachear por `version_id + filtros normalizados + método + permisos`; invalidar tras publicar. Limitar cardinalidad de filtros y cantidad de filas devueltas. Guardar parámetros de análisis y versión de biblioteca para reproducir resultados. La misma consulta no debe cambiar de cifras al actualizar el navegador sin una nueva versión o cambio explícito de parámetros.
