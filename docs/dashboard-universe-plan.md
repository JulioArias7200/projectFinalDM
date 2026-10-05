# Propuesta de análisis por universos para el dashboard

## Propósito y estado

Este documento fija la propuesta aprobada y el alcance de su implementación parcial en el dashboard Flask. La unidad de trabajo sigue siendo exclusivamente `data/persona.csv` y su versión publicada internamente `persona-317279aafe9023a2` (39.497 filas y 275 columnas). El estado funcional se registra en [progress.md](progress.md); no se debe interpretar una gráfica descriptiva de códigos como un KPI semántico validado.

La fuente conserva limitaciones semánticas: la copia local difiere en filas y columnas del DDI EH2025 F27; hay dominios, universos y procedencia aún por reconciliar. Por eso los filtros que siguen son diseños analíticos iniciales, no reglas aprobadas para corregir ni descartar datos. Para cada variable, el diccionario y el flujo aplicable deben confirmar elegibilidad antes de interpretar ausencia.

## Principios que deben guiar el dashboard

1. Mantener el maestro completo: los universos son vistas de análisis, no particiones destructivas ni datasets que reemplacen al maestro.
2. Mostrar junto a cada resultado el dataset, `version_id`, fecha de actualización, filtro, universo, unidad de análisis, tamaño (`N`) y método de cálculo.
3. Informar por pregunta `N total`, `N elegible`, `N respondido`, `N faltante entre elegibles` y `N fuera del universo`, cuando la regla de elegibilidad esté confirmada. No llamar “no respuesta” a un `NA` estructural.
4. Hasta confirmar el diseño de encuesta, describir los resultados como conteos y estadísticas no ponderadas de la copia observada. No presentar proyecciones poblacionales, tasas oficiales, errores estándar ni intervalos de confianza.
5. No calcular promedios de códigos categóricos. Para montos, mostrar distribución robusta (mediana y cuantiles) además de cobertura y denominador; no suprimir valores extremos plausibles por IQR.
6. Aplicar supresión configurable a celdas con menos de 10 observaciones en resultados compartibles. Proteger folio, salud, ingresos y ubicación detallada; no exponer microdatos en registros.
7. Si la regla de universo o semántica está en conflicto, dejar el indicador bloqueado o marcado como exploratorio, con la limitación visible.

## Universos propuestos

| ID | Universo/vista | Población y alcance | Análisis propuesto y cautelas |
|---|---|---|---|
| U-D01 | Demografía | Todas las personas; sección `s01`, edad, sexo y geografía según el diccionario. | Distribuciones de edad, sexo y ubicación; describir el tamaño observado. `folio` y `nro` son identificadores, no categorías de análisis. Variables de diseño se conservan como contexto, no como prueba de inferencia válida. |
| U-S01 | Salud general | Todas las personas para las preguntas generales de salud. | Cobertura/afiliación y respuestas generales; para cada pregunta reportar elegibilidad y ausencia por separado. No asumir que todas las preguntas `s02a_*` son universales sin revisar saltos. |
| U-S02 | Fecundidad y salud materna | Mujeres de 13 a 50 años para la vista marco; preguntas posteriores pueden estrechar el universo. | Describir fecundidad y ramas maternas por su propio denominador. `s02b_10` queda bloqueada para interpretación de faltantes hasta resolver el conflicto del corte temporal y la procedencia. |
| U-S03 | Salud infantil | Menores de 6 años para asistencia infantil y menores de 5 para la vista asociada al bono; cada pregunta puede tener filtro adicional. | Mantener vistas separadas por tramo y salto. `s02d_17`, `s02d_17a` y patrones no confirmados se etiquetan como hipótesis hasta cotejar el flujo del cuestionario. |
| U-E01 | Educación | Vista marco de personas de 4 años o más; alfabetismo y otras preguntas pueden tener edad mínima distinta. | Describir alfabetismo, asistencia y trayectoria con denominadores específicos. Resolver la máscara candidata de `s03b_12`, pues hay respuestas observadas fuera de ella. |
| U-T01 | Empleo y actividad económica | Vista marco de personas de 7 años o más; módulos ocupacionales y remuneración exigen filtros adicionales. | Separar condición de actividad, ocupación y características del trabajo. No generalizar la ausencia global a irrelevancia. `s04b_13` y `s04c_17a` tienen filtros candidatos conocidos, aún sujetos a conciliación del esquema local con F27. |
| U-T02 | Ocupación secundaria | Casos con respuesta afirmativa a `s04e_25`; la vista existente retiene además un código reportado fuera del filtro para revisión. | Analizar características del segundo trabajo solo entre elegibles confirmados. Mostrar la excepción como control de calidad, sin corregirla ni ocultarla. `s04e_26_cod` no debe descartarse por ausencia global alta. |
| U-I01 | Ingresos personales | Personas elegibles por fuente laboral/no laboral, condición de actividad y filtros propios. | Resumir montos mediante mediana, cuantiles y distribución; no convertir ausencias fuera del universo en cero. Resolver unidades, periodos y dominios antes de publicar indicadores concluyentes. |
| U-I02 | Ingresos y pobreza del hogar | Unidad hogar, una observación analítica por `folio`, para agregados como `yhog`, `yhogpc` y medidas de pobreza. | No contar copias persona como hogares ni promediar valores repetidos por persona. Confirmar el universo de miembros, ponderación y significado de `totper`; no usar `totper` como denominador hasta resolver su discrepancia. |
| U-X01 | Extensiones y semántica pendiente | Campos locales/derivados sin contrato oficial confirmado, incluido `s05c_09e` y otras variables marcadas en la matriz. | Conservar en el maestro y mostrar en un inventario de revisión; excluirlos de KPI semánticos hasta confirmar definición, universo y dominio. No heredar filtros por similitud de nombre. |

## Estructura y orden de navegación propuestos

El dashboard debe presentar los universos en el siguiente orden, de población general a módulos cada vez más condicionados:

1. **Resumen general:** identidad de dataset/versión, fecha, tamaño del maestro, estado semántico y enlaces a los módulos. Mostrar solo métricas de cobertura estructural ya verificadas; no colocar KPI temáticos estáticos como si fueran hallazgos.
2. **Demografía:** perfil de todas las personas y contexto geográfico. Esta página sirve como punto de partida y explica que conteos son observaciones de la copia, no población expandida.
3. **Salud:** una sección con tres subsecciones ordenadas: salud general (todas las personas, variable por variable), fecundidad/salud materna (mujeres 13–50 como marco) y salud infantil (menores de 6 y menores de 5 en vistas separadas). Cada indicador debe especificar sus filtros internos.
4. **Educación:** vista marco desde los 4 años, con denominadores propios para alfabetismo, asistencia y trayectoria educativa.
5. **Empleo:** primero actividad/ocupación principal en la vista marco desde los 7 años; después ocupación secundaria en una subsección condicionada por `s04e_25` afirmativa y con la excepción reportada visible para revisión.
6. **Ingresos:** primero ingresos personales por fuente y elegibilidad; luego ingreso/pobreza a nivel hogar, con una fila analítica por `folio` y advertencias explícitas sobre `totper` y ponderación.
7. **Revisión pendiente:** listado de extensiones locales, universos sin mapa y conflictos semánticos. Esta sección funciona como tablero de trabajo/calidad, no como página de indicadores.

La navegación regional debe aplicar estas mismas definiciones a agregados por departamento únicamente cuando la geografía, el universo y el cálculo estén validados. No debe presentar proyecciones ni tasas oficiales mientras el diseño de encuesta no esté confirmado. Toda página comparte la franja de metadatos (dataset, versión, fecha, universo/filtro, unidad, N y método) y las reglas de supresión.

## Propuesta de gráficos por sección

Los gráficos se seleccionarán para responder preguntas concretas del análisis de `persona.csv`; no se agregarán solo por decoración. Son especificaciones para la futura implementación, no evidencia de que esos resultados ya estén calculados. Cada gráfico debe construirse con el mismo `version_id` publicado que alimenta sus tablas y tarjetas.

| Sección / pregunta | Gráfico propuesto | Variables y universo necesarios | Lectura y cautelas |
|---|---|---|---|
| Resumen general: ¿qué versión y qué tan completa es la copia? | Tarjetas de filas, columnas, versión y fecha; barra horizontal de completitud estructural global y distribución del porcentaje de faltantes por variable (vista resumida, con acceso al explorador). | Metadatos del manifiesto y perfil de columnas de la versión publicada. | Distinguir cobertura técnica global de faltantes entre elegibles. No usar tarjetas de pobreza, salud o empleo hasta verificar denominadores. |
| Demografía: ¿cómo se distribuyen edad y categorías demográficas? | Histograma de edad con bins explícitos; barras horizontales ordenadas para sexo, área y departamento; barras de conteo observado al comparar tamaños departamentales. | Edad, sexo y ubicación con definiciones cotejadas en el diccionario; personas como unidad. | Mostrar conteos observados y `N` válido por variable. No usar promedio de códigos ni interpretar el tamaño de muestra como población del departamento. Evitar pirámide por sexo/edad hasta resolver edades y categorías válidas. |
| Salud general: ¿qué respuestas y ausencias se observan? | Barras horizontales de categorías por pregunta; barra apilada de elegibles respondidos/faltantes/fuera del universo solo si el salto está confirmado. | Variable de respuesta y máscara de elegibilidad por pregunta. | Denominador explícito; los estados de ausencia deben seguir diferenciados. No combinar preguntas de respuesta múltiple como si fueran categorías excluyentes. |
| Fecundidad y salud materna: ¿cómo se distribuyen respuestas entre las elegibles? | Barras de categorías para respuestas discretas; distribución de edad en el marco elegible si resulta útil; barras de cobertura por pregunta con elegibles/respondidos/faltantes. | Mujeres 13–50 como marco inicial, más filtro confirmado de cada variable. | Subtítulos muestran filtro interno. Bloquear la lectura de `s02b_10` hasta resolver corte/procedencia; no tratar NA de no elegibles como no respuesta. |
| Salud infantil: ¿qué respuestas se observan por tramo? | Barras por categoría separadas para menores de 6 y menores de 5, más barras de cobertura por pregunta. | Edad y variables infantiles con filtros propios confirmados. | No fusionar tramos de edad ni afirmar que `s02d_17`/`s02d_17a` tienen universo confirmado antes de reconciliar el flujo. Aplicar supresión a celdas pequeñas. |
| Educación: ¿cómo se distribuyen alfabetismo, asistencia y trayectoria? | Barras para variables categóricas; histograma o barras ordenadas para años/nivel educativo, según escala y diccionario; cobertura elegible por pregunta. | Personas desde 4 años como marco de vista; edad mínima específica para cada indicador. | No promediar códigos de nivel. Resolver respuestas fuera de máscara en `s03b_12` antes de publicar su denominador. |
| Empleo principal: ¿qué condición/ocupación se reporta? | Barras categóricas para condición de actividad y categoría ocupacional; histograma para horas trabajadas solo con magnitud/unidad confirmadas; cobertura por salto. | Personas desde 7 años como marco; filtros particulares de ocupación/remuneración. | No interpretar NAs del módulo como irrelevancia. En horas, incluir límites/unidades y no eliminar extremos plausibles automáticamente. |
| Ocupación secundaria: ¿cuántos casos entran al módulo y qué reportan? | Tarjeta de conteo elegible y barras de categorías entre elegibles; barra de control separada para casos observados fuera de `s04e_25`. | Respuesta de `s04e_25` y campos secundarios; elegibilidad confirmada. | La excepción fuera de filtro se presenta como control de calidad, sin mezclarla con el universo analítico ni corregirla automáticamente. |
| Ingresos personales: ¿cómo se comportan los montos y su cobertura? | Histograma con escala/unidad visibles; boxplot o banda de cuantiles (mediana, P25, P75 y cuantiles adicionales acordados); barras de elegibilidad y respuesta por fuente. | Variables monetarias con periodo, moneda, unidad y universo confirmados. | Evitar escalas que oculten colas; cualquier escala logarítmica debe rotularse. Mostrar faltantes por elegibles; no convertir ausencia o no aplica en cero ni eliminar valores extremos plausibles por IQR. |
| Ingresos/pobreza del hogar: ¿qué distribución se observa por hogar? | Histograma y cuantiles para montos; barras de categorías para estado de pobreza solo si definición oficial, línea y denominador están confirmados. | Una fila analítica por `folio`; variables de ingreso/pobreza reconciliadas. | Excluir `totper` de denominadores hasta resolver discrepancia. Reportar hogares observados (`N hogares`) por separado de personas; sin afirmaciones inferenciales/estimaciones oficiales. |
| Revisión pendiente: ¿qué definiciones impiden análisis? | Tabla/matriz de estado semántico y barra horizontal de conteos de variables por estado de revisión. | Matriz de universos, diccionario y auditorías documentales versionadas. | Es visualización de calidad del conocimiento, no de prevalencia poblacional; identificar estados provisionales, conflictos y extensiones locales. |
| Vista regional | Mapa coroplético solo como complemento de barras por departamento, con métrica y rango completos en leyenda. | Geografía, elegibilidad, agregación y métrica regional validadas. | Deshabilitado hasta validar cálculo/universo. No usar población proyectada ni porcentaje oficial con los valores demo actuales. |

### Tipografía y estilo visual

La futura interfaz y los gráficos deben reutilizar el sistema que ya existe en `dashboard/static/css/base.css` y `theme.css`: tipografía general `Inter` con fallbacks del sistema; `font-mono` solo para identificadores, códigos de variable, versión, conteos técnicos y etiquetas de ejes compactas. Títulos, leyendas y tooltips deben heredar la tipografía de interfaz. Los colores deben venir de tokens CSS —por ejemplo `--text-main`, `--text-secondary`, `--text-muted`, `--svg-grid`, `--svg-axis`, `--bg-card`, `--border-card` y `--tooltip-*`— para que el tema claro/oscuro siga funcionando; usar colores semánticos existentes para distinguir universos, manteniendo contraste suficiente y sin codificar el significado solo por color.

Los gráficos deben adaptarse al ancho disponible, incluir título con pregunta, unidad, denominador y nota metodológica, ejes con unidades/formato, leyenda comprensible, tooltip accesible y estado sin datos/bloqueado. Preferir barras ordenadas para categorías; evitar pastel/donut cuando haya muchas categorías o se necesite comparar valores cercanos. Las barras de proporciones deben señalar denominador y no comenzar en un eje truncado sin advertencia. Para gráficos SVG/Canvas, las fuentes y colores se inyectarán desde estilos/tokens del dashboard, no se mantendrán paletas o tipografías paralelas en JavaScript.

### Secuencia para especificar y validar visualizaciones

Antes de programar cada visualización, registrar: nombre de pregunta, tipo de variable según diccionario, universo/filtro, unidad de análisis, estados de datos incluidos, denominador, métrica, escala, regla de supresión y limitaciones. Luego probar con datos sintéticos los cálculos y estados vacíos; verificar contraste en ambos temas, tamaños de pantalla, tooltips/etiquetas, supresión (<10) y reconciliación visual con tabla de conteos. Si no existe un contrato semántico suficiente, mostrar el estado pendiente en vez de dibujar una cifra provisional.

## Secuencia de trabajo para llevarlo al dashboard

1. Reconciliar el manifiesto de vistas temáticas con la versión publicada en el puntero JSON; los conteos y nombres mostrados deben proceder de esos artefactos, no de constantes aisladas.
2. Completar el mapa de elegibilidad para cada variable que alimente un KPI, resolviendo cuestionario/procedencia y las filas pertinentes de `docs/universe-matrix-persona.csv`.
3. Definir, por KPI, pregunta analítica, unidad, numerador, denominador, valores válidos, tratamiento de ausencia y estado de ponderación. Bloquear KPI sin contrato suficiente.
4. Calcular resultados agregados reproducibles desde la versión publicada y las vistas verificadas por hash. Mantener salidas exploratorias separadas de estadísticas inferenciales.
5. Reemplazar en el dashboard valores de demostración por resultados calculados; mostrar método, filtro, `N` y avisos de limitación en pantalla y exportación.
6. Añadir pruebas sintéticas de máscaras/denominadores, reconciliación independiente de KPI, supresión de celdas pequeñas, versión/filtro expuestos y fallo seguro ante universos no resueltos.
7. Documentar la revisión de interfaz y resultados agregados en `docs/progress.md`; solo entonces marcar los criterios de aceptación asociados como cumplidos.
8. Implementar los gráficos descritos arriba siguiendo la guía tipográfica/visual existente, empezando por resumen estructural y demografía, y continuar en orden de navegación solo cuando sus variables y denominadores estén confirmados. La visualización regional se deja al final y bloqueada por validación semántica.

## Estado de las vistas de base y decisiones pendientes

El documento [vistas temáticas](thematic-views-persona.md) registra once vistas derivadas: demografía; salud general, fecundidad, asistencia infantil y bono; educación; PET y ocupación secundaria; ingresos no laborales, ingresos/pobreza por persona y resumen por hogar. Los conteos publicados allí son tamaños observados de esta copia, no estimaciones poblacionales ni prueba de elegibilidad de cada pregunta.

La matriz [universe-matrix-persona.csv](universe-matrix-persona.csv) y las [observaciones de universos](observaciones-universos-persona.md) son la fuente de seguimiento variable por variable. La auditoría allí es parcial: hay reglas cotejadas provisionalmente, condiciones sin mapear, una discrepancia confirmada (`s02b_10`), patrones hipotéticos y una extensión local sin contrato. No convertir esos estados en KPI ni limpieza automática.

Quedan fuera de alcance las secciones de vivienda, equipamiento, gastos, alimentación y discriminación, porque no están en `persona.csv`; no deben importarse ni simularse para completar el dashboard de persona.

## Criterio de cierre de esta etapa futura

La documentación queda preparada. La etapa de dashboard por universos solo podrá declararse implementada cuando cada indicador visible derive de la versión JSON publicada, sus denominadores se reconcilien con un cálculo independiente, las cautelas aparezcan en la interfaz y las pruebas correspondientes pasen. La existencia de una ruta Flask o una tarjeta visual por sí sola no satisface ese criterio.
