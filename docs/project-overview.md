# Plan de implementación

El proyecto cuenta con especificación y un prototipo local de preprocesamiento ejecutado para `persona.csv`. La primera entrega sigue siendo un sistema Flask con bitácora PostgreSQL, aplicando [la metodología basada en `curso/`](cleaning-methodology.md); esa aplicación aún no está implementada. El comando operativo disponible ejecuta solo el pipeline local, no arranca el sistema web. Cada etapa termina con demostración, pruebas y actualización de `progress.md`.

Actualización de alcance: el análisis cubre **columna por columna**, con diagnóstico de atípicos y comparación antes/después. El script y notebook equivalentes ya se ejecutaron el 4 de octubre de 2026. La corrida `20261004T171822Z_568e82e3039d_d3abfb0b5f` generó un candidato de 39.497 filas y 150 columnas desde las 275 de origen; el candidato no está publicado y la regla L-80 debe revisarse frente a universos condicionales. La aplicación Flask, PostgreSQL, pruebas automáticas y publicación siguen pendientes.

## Etapa 0. Definiciones y base del repositorio

- Confirmar origen, año, licencia y diccionario oficial del CSV de ejemplo; decidir si puede incorporarse al repositorio o debe mantenerse fuera de Git.
- Definir clave de persona y reglas para columnas sensibles. Aprobar política de roles, supresión, retención y doble control.
- Convertir la teoría de tipos, descriptiva y preparación de `curso/` en definiciones de reglas L-01 a L-12 por columna y universo; la imputación queda deshabilitada salvo justificación.
- Crear la estructura Flask con factoría, blueprints, templates Jinja y recursos estáticos; configurar `DATABASE_URL`, `SECRET_KEY` y almacenamiento, sin secretos en Git.
- Crear contrato versionado de personas y datos sintéticos. El contrato puede habilitar un subconjunto semántico confirmado; marcar explícitamente columnas pendientes.
- Planificar el diccionario Markdown con una entrada por cada columna real del CSV, separando significado confirmado, descripción provisional y definición pendiente. No excluir columnas del diagnóstico por falta de semántica.
- Entregable: alcance de limpieza delimitado, contrato revisado y base de entorno local Flask/PostgreSQL.

## Etapa 1. Ingesta y catálogo

- Implementar conexión SQLAlchemy, modelos y migraciones Alembic de PostgreSQL, incluyendo usuarios, permisos, trabajos, versiones, eventos y resultados por regla.
- Implementar autenticación, autorización y bitácora append-only desde las primeras rutas Flask. Probar persistencia tras reinicio y denegación de UPDATE/DELETE de eventos.
- Implementar almacenamiento raw inmutable, rutas de importación y worker separado con cola persistente en PostgreSQL.
- Calcular hashes y metadatos, controlar idempotencia y capturar errores de parser. Generar perfil por las 275 columnas y cuarentena restringida, sin convertir automáticamente los tokens a nulos.
- Construir el perfil inicial por columna descrito en el subplan de preprocesamiento: ninguna columna puede quedar fuera del inventario o del informe técnico.
- Entregable: cargar el archivo, consultar trabajo, perfil y bitácora sin modificar el original. Verificar CA-01 a CA-03, CA-17 y controles iniciales de CA-13/CA-18.

## Etapa 2. Limpieza y publicación

El prototipo local ya implementa y ejecuta el perfilado por columna, gráficos, comparación y candidato con L-80 global. La revisión posterior demostró que ese denominador excluyó variables laborales casi completas entre sus elegibles; por ello las 125 exclusiones del candidato actual son provisionales. La etapa debe reemplazar L-80 por medición sobre universos confirmados, retener en el conjunto maestro variables aún no resueltas y producir vistas analíticas filtradas. Luego se integrarán reglas y bitácora a Flask/PostgreSQL, pruebas y publicación inmutable. El candidato actual no cumple todavía como conjunto limpio útil.

- Implementar motor de reglas versionadas de personas, reporte de impacto, validaciones, manifiesto, Parquet y publicación atómica.
- Registrar en PostgreSQL referencia del curso, condición, acción, universo, parámetros, conteos y métricas antes/después por regla. Revisar duplicados, faltantes, tipos, dominios y atípicos según contrato.
- Añadir comparación raw/clean y descarga autorizada. Evitar transformaciones semánticas en columnas pendientes y no borrar extremos ni imputar por defecto.
- Mantener el JSON como diccionario canónico y el notebook sincronizado con el script ya existente. La etapa pendiente es integrar estas reglas con el contrato versionado, la aplicación y la bitácora persistente, además de verificar su semántica y cobertura con pruebas.
- Generar una ficha antes/después para cada columna, con controles de atípicos apropiados a su tipo, decisiones y cambios verificables; incluir explícitamente las columnas sin cambios o con definición pendiente.
- Entregable: versión preparada reproducible, informe de limpieza y fallos seguros. Verificar CA-04 a CA-07 y controles de CA-18/CA-19.

## Etapa 3. Ediciones y auditoría

- Ampliar los permisos ya implementados con propuestas, aprobación, control de conflictos y versiones derivadas.
- Crear vistas Flask/Jinja de bitácora, solicitudes y comparación de versiones con protección de valores sensibles.
- Entregable: ciclo de corrección y seguimiento persistente. Verificar CA-08, CA-09, CA-13 y CA-18. La restauración CA-10 queda para la etapa 5.

## Etapa 4. Estadística y dashboard

- Crear métricas descriptivas con pandas sobre Parquet publicado, filtros, denominadores y caché por versión y permisos, siguiendo `curso/03_estadistica_descriptiva.md`.
- Construir vistas Flask/Jinja de resumen, exploración, calidad antes/después y bitácora; usar Plotly para gráficos y añadir exportaciones con metadatos.
- Mantener inferencia no disponible mientras no se confirme el diseño; validar cualquier descriptiva ponderada habilitada con cálculo independiente.
- Entregable: primera entrega utilizable con dashboard coherente con versión limpia. Verificar CA-11, CA-13 y CA-19, y bloqueo de inferencia de CA-12.

## Etapa 5. Operación

- Restauración de versiones como nuevas versiones; programación recurrente, observabilidad, límites de recursos, copias de seguridad y ensayo de restauración. Los reintentos básicos del worker ya deben existir desde la etapa 1.
- Incorporar métodos inferenciales solo tras confirmar diseño muestral y supuestos, tomando `curso/04_estadistica_inferencial.md` como fundamento complementario.
- Pruebas de integración, permisos, rendimiento con volumen real y despliegue limpio.
- Entregable: operación documentada y verificable. Verificar CA-10, CA-12 y CA-14 a CA-16.

## Subplan detallado de análisis y preprocesamiento por columna

Este subplan desarrolla las etapas 0 a 2 y sus resultados alimentan la etapa 4. El prototipo local descrito en `progress.md` ya se implementó y ejecutó; las tareas restantes de contrato formal, integración, validación y publicación siguen pendientes. Las rutas propuestas no implican que exista la aplicación Flask. Se conserva el nombre de carpeta `proprosessing` solicitado por el usuario.

### P-01. Preparar configuración, identidad y lectura conservadora

- Definir rutas relativas, configuración de contrato, reglas habilitadas, codificación y política de resultados. Registrar versiones de dependencias y código.
- Conservar `data/persona.csv` sin modificación, registrar bytes y SHA-256 y separar identificadores de archivo, ejecución y versión.
- Leer inicialmente como texto, sin transformar automáticamente vacío, `NA` o códigos especiales en un único nulo. Inspeccionar encabezados originales antes de que una biblioteca pueda renombrar duplicados.
- Verificar delimitador, comillas, registros multilínea, número de campos y errores de parseo. Capturar las excepciones sin omitir registros silenciosamente ni imprimir filas personales.
- Entregable: manifiesto inicial y control estructural del archivo.

### P-02. Inventariar y documentar todas las columnas

- Recorrer los nombres reales del encabezado, no una lista reducida de variables seleccionadas. Para la copia revisada se esperan 275 entradas; si cambia el esquema, informar la diferencia y validar el contrato antes de continuar.
- Agrupar variables por identificación/diseño, demografía, salud, educación, empleo, ingresos y derivadas, conservando una entrada individual para cada una.
- Clasificar identificadores, categorías nominales/ordinales, magnitudes discretas/continuas, fechas y texto libre según `curso/02_tipos_de_datos.md`. Separar tipo físico observado de tipo semántico confirmado.
- Documentar nivel persona/hogar, unidad, universo elegible, sensibilidad, códigos, tokens de origen y fuente de definición. El diccionario local es referencia provisional hasta cotejar la edición exacta.
- Entregable: inventario completo y estructura de `data/proprosessing/data_dictionary.json` y su vista legible Markdown.

### P-03. Elaborar el análisis inicial columna por columna

Cada columna tendrá una ficha técnica identificada por nombre y sección. La ficha se producirá también para columnas constantes, totalmente vacías, identificadores y variables sin definición confirmada.

| Dimensión | Contenido obligatorio del perfil antes de limpiar |
| --- | --- |
| Cobertura | Registros totales, elegibles, válidos y estado de confirmación del universo |
| Ausencias | Conteos y porcentajes de vacío, `NA`, espacios, códigos especiales, no respuesta y no aplica cuando estén clasificados |
| Formato | Tipo observado/candidato, patrones, errores de conversión y espacios inconsistentes |
| Cardinalidad | Valores distintos, constancia y categorías frecuentes; no publicar valores de identificadores |
| Numéricas confirmadas | Mínimo, máximo, media, mediana, desviación, cuartiles, IQR y percentiles con método declarado |
| Categorías confirmadas | Frecuencias, proporciones, códigos fuera de dominio y orden cuando proceda; no calcular medias de códigos |
| Fechas/texto | Validez de fechas o formatos y, en texto libre pertinente, longitudes y anomalías de formato; no tokenizar identificadores |
| Calidad | Errores confirmados, alertas, atípicos candidatos, severidad y pendientes de definición |

Los porcentajes indicarán su denominador. Si el universo no está confirmado, se informará cobertura técnica sobre registros observados sin llamar error a una ausencia. Las distribuciones de códigos sin etiquetas se describirán como códigos, sin inventar categorías.

### P-04. Detectar y evaluar atípicos por columna

- Para magnitudes numéricas confirmadas, calcular alertas mediante cuantiles, histogramas, boxplots e IQR. Como regla exploratoria inicial configurable, examinar valores fuera de `Q1 - 1.5 × IQR` y `Q3 + 1.5 × IQR`; no convertir esa alerta en una eliminación automática.
- Especificar universo/grupo, método, límites y conteos para cada variable. Manejar muestras insuficientes, columnas constantes e IQR cero con un estado explícito; no forzar una clasificación engañosa.
- Separar extremos estadísticos de valores imposibles, códigos especiales y extremos plausibles. Evaluar ingresos y horas según unidad, elegibilidad y distribución, sin imponer normalidad ni prohibir ceros/negativos sin definición.
- Para categorías, evaluar códigos fuera de dominio y categorías raras; rareza no equivale a error ni se trata como atípico numérico.
- Para identificadores, revisar formato, ausencia y unicidad; el tamaño numérico no es un criterio de atipicidad. Para fechas, validar calendario y restricciones confirmadas.
- Cada ficha tendrá estado de revisión: sin alertas detectadas por el método, alertas presentes, método no aplicable o semántica pendiente. No dejar columnas sin respuesta a esta revisión.
- Entregable: diagnóstico de atípicos por columna y decisión justificada de conservar, corregir, cuarentenar o dejar pendiente.

### P-05. Definir y ejecutar reglas justificadas cuando se autorice

- Aplicar el catálogo L-01 a L-12 de `cleaning-methodology.md`: esquema, clave, formatos, estados de ausencia, tipos/códigos, duplicados, rangos, relaciones, pesos, imputación opcional, derivaciones y parches.
- Declarar por regla ID, versión, orden, columna(s), universo, condición, acción, referencia de `curso/`, evidencia del diccionario, severidad y política de rechazo.
- Revisar `(folio, nro)` y duplicados exactos separadamente; comprobar nuevamente la clave tras normalizar. No deduplicar por `folio` ni eliminar registros incompletos de forma general.
- Conservar máscaras/estados de origen para distinguir valores observados, convertidos, corregidos e imputados. Mantener trazabilidad restringida por registro/celda cuando exista cambio; los informes compartidos serán agregados.
- Mantener la imputación deshabilitada por defecto. Si se justifica para una variable, documentar método, población de ajuste, evaluación, parámetros, semilla y máscara. No sustituir saltos legítimos por valores inventados.
- Conservar columnas derivadas separadas y su fórmula. Las columnas sin definición confirmada solo reciben controles técnicos seguros; no se alteran semánticamente.
- Entregable: versión candidata y reporte de reglas, sin publicación automática.

### P-06. Comparar antes y después de cada columna

La comparación es obligatoria para **todas las columnas originales**. Cada columna derivada se documenta aparte con su origen y fórmula. Una columna sin cambios debe mostrar la evidencia de conservación y el motivo, no desaparecer del informe.

| Componente | Comparación requerida |
| --- | --- |
| Esquema | Tipo físico/semántico antes y después, conversiones autorizadas y fallos |
| Cobertura | Registros totales, elegibles, válidos y cuarentenados; exclusiones con motivo |
| Ausencias | Conteos por estado antes/después, variación absoluta y en puntos porcentuales cuando corresponda |
| Cardinalidad/categorías | Valores distintos, categorías y frecuencias; cambios de códigos autorizados |
| Distribución numérica | Mismos estadísticos, unidades y método de cuantiles antes/después |
| Atípicos | Método, límites, conteos y estado antes/después; qué se conservó, corrigió o rechazó |
| Cambios | Celdas examinadas/modificadas/imputadas, regla aplicada, justificación y pendientes |
| Visualización | Histograma/boxplot comparable para magnitudes; barras para categorías; diagnóstico de formato para identificadores/texto |

Comparar primero sobre registros alineados por clave y universo, y mostrar aparte el efecto de quitar registros de la población aceptada. No atribuir toda diferencia estadística a una corrección de valores si cambió la composición.

Para atípicos, presentar el conteo posterior usando los límites iniciales como referencia y, por separado, los límites recalculados cuando sea pertinente. Explicar que una reducción de alertas no demuestra por sí sola mayor calidad. Mantener iguales intervalos/ejes de gráficos cuando se compare visualmente.

Aplicar permisos y supresión antes de compartir informes, incluidos gráficos y extremos numéricos que puedan revelar información sensible. Los detalles individuales quedan en artefactos restringidos; no se muestran filas completas en las salidas del notebook.

### P-07. Mantener JSON canónico y generar el diccionario Markdown

La fuente canónica es `data/proprosessing/data_dictionary.json`, con metadatos del dataset y un objeto `variables` indexado por el nombre exacto de cada columna. El pipeline lee este JSON para perfiles y etiquetas, y genera `data/proprosessing/data_dictionary.md` como vista legible con análisis antes/después. No mantener definiciones de variables duplicadas manualmente entre ambos formatos.

Cada entrada incluirá:

- Nombre exacto, sección y descripción.
- Fuente de definición y estado: confirmado, provisional o pendiente.
- Nivel persona/hogar, tipo físico antes/después, tipo semántico, escala y unidad.
- Universo, códigos/etiquetas confirmados y tratamiento de vacío, `NA`, cero y no aplica.
- Sensibilidad y restricciones de uso/visualización.
- Reglas de validación/limpieza y referencias del curso.
- Resumen técnico antes/después, alertas de atípicos, decisión y limitaciones.
- Si es derivada, fórmula, variables de origen y parámetros.

El encabezado identificará dataset, hash de origen, contrato, reglas y versión de resultado. No incluir ejemplos con personas reales ni etiquetas inferidas sin respaldo. Una definición pendiente no impide documentar la columna ni su perfil técnico, pero sí restringe su interpretación.

### P-08. Mantener código idéntico en notebook y script

- Usar `data/proprosessing/preprocessing.py` como fuente principal, organizado en bloques `# %%`, y generar las celdas ejecutables de `preprocessing.ipynb` a partir de esos bloques.
- El notebook añade explicaciones Markdown y muestra las fichas de todas las columnas; las celdas de código contienen las mismas funciones, configuración, análisis y ejecución del script. No basta con importar el script como sustituto de incluir el mismo código solicitado.
- Evitar comandos mágicos, instalaciones en celdas y dependencias del orden manual. Usar funciones y un punto de entrada que también pueda ser invocado desde Flask sin ejecutar el pipeline al importar.
- Ejecutar el notebook con kernel limpio y el script en proceso limpio. Comparar código concatenado descontando solo separadores de celda, datos, perfiles, decisiones y hash lógico; no exigir igualdad de timestamps o del JSON completo del notebook.
- Permitir consultar el informe completo por columna sin depender de tablas truncadas ni mostrar únicamente las primeras variables.

### P-09. Validar resultados y preparar artefactos auditables

- Escribir resultados en una ubicación nueva e inmutable por ejecución: dataset candidato, perfiles inicial/final, comparación por columna, reglas, excepciones, gráficos y manifiesto. El diccionario acompaña cada versión de resultados; la copia de consulta en `data/proprosessing/` identifica explícitamente la versión que describe.
- Persistir en PostgreSQL los eventos e impactos mediante la integración prevista en la arquitectura. Un informe local o notebook ejecutado no sustituye la bitácora ni confirma publicación.
- Validar esquema, clave, dominios confirmados, conteos y reconciliación. Comprobar que el hash del raw no cambia y que ninguna regla modifica columnas fuera de su alcance.
- Publicar únicamente mediante permisos y transacción de metadatos del sistema Flask, después de validar. Un fallo mantiene la versión publicada anterior.
- Probar con datos sintéticos faltantes diferenciados, claves repetidas, colisiones, errores de tipo, atípicos plausibles, categorías raras, columnas constantes, IQR cero, ausencia total, universos y fallos de escritura. Verificar determinismo y equivalencia notebook/script.

### Condiciones de cierre del subplan

| Condición | Evidencia requerida |
| --- | --- |
| Cobertura total | Igualdad entre columnas del CSV, entradas del diccionario y fichas antes/después; para esta copia, 275 |
| Revisión de atípicos total | Cada columna tiene método y resultado o motivo explícito de no aplicabilidad/definición pendiente |
| Comparación completa | Métricas comparables y decisión para todas las columnas, incluidas las conservadas sin cambios |
| Limpieza explicable | Toda modificación vincula regla, fundamento, universo, conteos y trazabilidad |
| Diccionario Markdown | Entradas completas, fuentes y pendientes explícitos; derivadas documentadas aparte |
| Igualdad de código | Verificación de las celdas de código frente al script y ejecución limpia de ambos |
| Equivalencia de resultados | Mismo dataset lógico, perfiles y decisiones con igual entrada/configuración/código |
| Protección del original | SHA-256 sin cambios; salidas separadas y acceso controlado |
| Publicación segura | Pruebas de fallo y bitácora persistente antes de declarar resultados publicados |

Estos controles complementan CA-03, CA-04, CA-07, CA-11, CA-13, CA-18 y CA-19. No se consideran cumplidos por redactar este plan. No se exige reducir todos los atípicos o faltantes a cero: se exige clasificarlos, decidir su tratamiento y demostrar el efecto.

## Riesgos y decisiones pendientes

| Tema | Riesgo | Resolución necesaria |
| --- | --- | --- |
| Procedencia del CSV | Uso o publicación sin permiso claro | Confirmar origen y licencia antes de compartir datos |
| Clave de registro | Duplicados o edición de la persona equivocada | Perfil de `(folio, nro)` y alternativa si no es única |
| Diseño de encuesta | Intervalos y tasas incorrectos | Documentación de ponderación, estratos y UPM |
| Sensibilidad | Exposición de ingresos, salud e identificadores | Clasificación de columnas, permisos y supresión |
| Limpieza indiscriminada | Eliminar `NA`, imputar o borrar atípicos sin significado confirmado | Reglas por columna/universo con referencia de `curso/` y diccionario |
| Bitácora incompleta | Cambios sin historial por fallo de conexión | Metadatos y eventos en la misma transacción PostgreSQL |
| Publicación | Lectura de versión parcial | Publicación atómica y recuperación tras fallos |

No fijar fechas ni estimaciones de esfuerzo hasta decidir equipo, despliegue y alcance del primer piloto.

## Decisión vigente: dataset maestro completo — 4 de octubre de 2026

`data/persona.csv` es la fuente definitiva del proyecto por confirmación del usuario. El candidato histórico de 150 columnas no cumple como maestro por exclusiones con denominador global. La implementación vigente debe generar una versión derivada con las 39.497 filas y 275 columnas, perfil por variable y bandera L-80 de revisión; no excluirá columnas por ausencia global. Solo se aplicará recorte sintáctico de espacios exteriores en campos permitidos por el diccionario y se bloqueará ante clave `(folio,nro)` incompleta o duplicada. Imputación, eliminación de extremos, deduplicación y correcciones semánticas permanecen deshabilitadas. Pendiente: ejecutar el código con Python en un entorno disponible y verificar el manifiesto, conteos, hash y comparación antes/después; Flask/PostgreSQL queda para etapa posterior.

## Ejecución vigente del maestro técnico

El candidato verificado `data/proprosessing/output/20261004T200928Z_568e82e3039d_d3abfb0b5f/` conserva todas las 39.497 filas y 275 columnas. El CSV y Parquet fueron validados con dimensiones iguales; la clave se mantuvo completa, única y en el mismo orden. Ninguna celda cambió valor porque no hubo whitespace elegible para normalización. La salida se identifica como master técnico candidato, aún no publicada ni validada semánticamente. Ver el detalle de pruebas y hallazgos en `progress.md`.
