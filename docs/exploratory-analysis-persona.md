# Análisis exploratorio descriptivo de `persona.csv`

## Objetivo y estado

La siguiente etapa tras construir vistas por universo es caracterizar las variables y observar distribuciones dentro del universo válido de cada módulo. Se añadió `data/proprosessing/exploratory_analysis.py` para generar un informe reproducible desde la versión candidata vigente y sus 11 vistas temáticas. La implementación está escrita, pero **todavía no se ha ejecutado ni verificado** en este entorno: `py -3.12` informa que no hay una instalación global de Python disponible. No se utilizó `venv`, que está reservado a otro trabajo. Por ello aún no existen resultados exploratorios atribuibles a esta etapa.

## Fuente y límites

- Fuente única: maestro candidato `data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f/` y sus CSV temáticos, derivados exclusivamente de `data/persona.csv`.
- Antes de leer una vista, el programa compara su SHA-256 y sus dimensiones con `views_manifest.json`; también comprueba el hash del maestro.
- El diccionario JSON que acompaña la corrida proporciona etiquetas y tipo semántico. Los códigos se tratan como categorías. Estadísticos de magnitud se calculan únicamente cuando el tipo del diccionario indica una variable cuantitativa o monetaria.
- El análisis reporta conteos no ponderados. `factor`, `estrato` y `upm` no se interpretan como diseño certificado; no hay estimaciones poblacionales, intervalos ni pruebas de hipótesis.
- Ausencia/vacío/`NA` se describen en cada vista; el porcentaje no se llama tasa de no respuesta porque algunos faltantes son saltos estructurales.
- Los gráficos y tablas de frecuencia agregadas aplican umbral mínimo de 10 observaciones. Las categorías inferiores se agrupan en gráficos o se omiten de la exportación. Aun así, los artefactos son microanálisis internos y requieren control de acceso antes de compartirse.
- La vista `empleo_secundario_casos` retiene una excepción de filtro; su análisis es diagnóstico y no una estimación del subuniverso.
- La vista `hogar_resumen_persona_candidato` cuenta hogares, no personas; no se calculará una media ni tasa de hogares ponderada sin confirmar el ponderador y `totper`.

## Productos que generará una ejecución

Cada corrida crea una carpeta nueva `exploratory_analysis/<UTC>/` dentro de la corrida candidata, sin sobrescribir resultados anteriores:

- `README.md`: versión, hash, universos, método, advertencias y listado de vistas.
- `analysis_manifest.json`: linaje, ficheros examinados y política de cálculo.
- `column_descriptives.csv`: cobertura, observaciones, vacíos, token literal `NA`, token exacto `0`, cardinalidad, categoría más frecuente y estadísticos permitidos por tipo semántico, una fila por variable y vista.
- `view_universes.csv`: unidad de análisis, filtro, tamaño y cautelas de cada vista.
- `plots/`: gráficos de distribución seleccionados por tema, titulados con nombre del diccionario, universo y tamaño no ponderado.
- `frequency__*.csv`: frecuencias agregadas de variables no clasificadas como sensibles, con celdas pequeñas omitidas.

## Ejecución pendiente

Desde la raíz y con Python 3.11+ y dependencias declaradas en `requirements.txt` disponibles globalmente:

```powershell
python data/proprosessing/exploratory_analysis.py
```

Para otra corrida candidata se admite `--candidate <ruta>`. La ejecución requiere revisar luego las distribuciones y dominios con el cuestionario/diccionario aplicable; generar estadísticas descriptivas no confirma errores ni autoriza correcciones. `data/persona.csv` permanece de solo lectura. La reconciliación de esquema con F27, el significado local de `totper` y el diseño muestral siguen pendientes antes de inferencia o publicación.

## Siguiente decisión analítica

Tras obtener las salidas, priorizar revisión por tema y registrar hipótesis descriptivas, excepciones y variables de interés. Para salud, educación y trabajo respetar los filtros de sus vistas; para ingresos reportar también el número observado y no observado. Solo después de validar procedencia, universos, ponderadores y diseño se considerarán estimaciones o análisis de relaciones.
