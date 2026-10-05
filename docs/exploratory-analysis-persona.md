# Análisis exploratorio descriptivo de `persona.csv`

## Estado y alcance

El análisis exploratorio descriptivo fue ejecutado el 4 de octubre de 2026 sobre la corrida candidata `data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f/`, en `exploratory_analysis/20261004T225208Z/`. Se examinaron las 11 vistas temáticas derivadas del maestro candidato. El análisis es local y no ponderado; no utiliza otros archivos de microdatos ni realiza análisis del cuestionario. El JSON del diccionario se usa para nombres y tipos declarados, no para inventar reglas o universos no presentes en los datos.

Esta etapa describe los datos y señala patrones para revisión. No constituye certificación de limpieza semántica completa, estimación poblacional, inferencia estadística ni publicación de una versión limpia. Se conservan como objetivo las 39.497 filas y las 275 columnas del maestro `persona.csv`; las vistas temáticas son subconjuntos analíticos y no reemplazan ese maestro.

## Linaje y validaciones

- El programa lee el maestro candidato, `views_manifest.json`, las 11 vistas verificadas por hash y el diccionario JSON que acompaña la corrida.
- Hash SHA-256 del maestro examinado: `1dbf937c73972a78746b1106d2e591dc46ea487b943112afb406887801bf8fee`.
- Comprueba el hash del maestro y de cada vista antes de analizarlos, además de las dimensiones de las vistas declaradas en el manifiesto.
- La corrida de origen documenta la fuente raw `data/persona.csv` con SHA-256 `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`; el archivo fuente no se modifica.
- Resultado verificado: 11 universos, 410 filas de resumen columna-vista, 21 gráficos y 112 archivos de frecuencias agregadas.

## Método

- Registra por columna y universo: número observado, vacíos, token literal `NA`, token exacto `0`, porcentaje no observado y cardinalidad. Esas ausencias se describen dentro de cada vista y no se interpretan automáticamente como no respuesta.
- Calcula mínimo, cuartiles, mediana, máximo y media sin ponderar solo para variables cuyo tipo en el diccionario está declarado cuantitativo/monetario. No calcula medias de códigos categóricos.
- Produce gráficos seleccionados por tema con títulos legibles del diccionario, universo y tamaño de muestra no ponderado. Las categorías con menos de 10 casos se agrupan en gráficos.
- Las frecuencias exportadas excluyen identificadores, variables de diseño y columnas sensibles por nombre/prefijo; se omiten categorías con menos de 10 casos.
- El perfil descriptivo suprime `top_category` y `top_category_n` de identificadores y columnas sensibles, así como de cualquier categoría cuya frecuencia sea inferior a 10. Se verificó esta condición en el resultado nuevo.
- No se estiman resultados ponderados, errores estándar, intervalos de confianza, relaciones causales ni significancia estadística. El diseño muestral no está certificado para esta corrida.

## Artefactos

En `data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f/exploratory_analysis/20261004T225208Z/`:

- `README.md`: universos, método y cautelas de interpretación.
- `analysis_manifest.json`: versión de origen, hash del maestro, parámetros y lista de vistas.
- `column_descriptives.csv`: diagnóstico agregado de cada columna dentro de cada vista.
- `view_universes.csv`: unidad, tamaño, filtro y cautelas de las 11 vistas.
- `plots/`: 21 imágenes por tema, no gráficos de todas las 275 columnas; los gráficos individuales del perfil global se conservan en la corrida de origen.
- `frequency__*.csv`: 112 tablas de frecuencias permitidas con supresión de celdas pequeñas.

## Ejecución y revisión

Desde la raíz del proyecto, usando Python global 3.12.9 y las dependencias ya disponibles:

```powershell
& 'C:\Users\julio\AppData\Local\Programs\Python\Python312\python.exe' data/proprosessing/exploratory_analysis.py
```

La validación local confirmó 410 resúmenes, 11 universos, 21 gráficos, 112 tablas y supresión de categorías identificadoras/sensibles. No se afirma que se haya ejecutado una suite de pruebas automatizadas para esta etapa.

Hay una carpeta de una ejecución exploratoria anterior, `exploratory_analysis/20261004T224908Z/`, que debe considerarse restringida y no compartirse: se generó antes de aplicar la supresión de identificadores al perfil descriptivo. Se conservó como artefacto histórico inmutable; la carpeta `20261004T225208Z/` es el resultado corregido.

## Limitaciones y pasos siguientes

Los conteos describen la copia local y no prueban por sí solos que un valor sea erróneo, extremo o semánticamente inválido. No se ejecutó depuración adicional a partir de estos gráficos. La versión técnica se publicó después mediante catálogo JSON para uso interno; la limpieza semántica integral de las 275 columnas, la resolución de conflictos entre procedencia/metadatos y la validación del diseño de encuesta siguen pendientes. Si no se dispone de cuestionario, diccionario validado u otra fuente autorizada, los resultados deben registrarse como patrones empíricos o hipótesis; no se deben convertir en correcciones automáticas.

No comparar porcentajes entre vistas con denominadores diferentes. Las vistas de hogar y de personas tienen unidades distintas, y cualquier análisis inferencial requeriría verificar ponderador y diseño muestral. Las vistas temáticas no alteran el requisito del proyecto de preservar todas las filas y columnas en el maestro.
