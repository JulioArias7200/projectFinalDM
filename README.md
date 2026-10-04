# Sistema Flask de limpieza y bitácora de `persona.csv`

Proyecto de Minería de Datos centrado en limpiar `data/persona.csv` mediante un sistema web basado en Flask, conectado a PostgreSQL para conservar la bitácora del dataset. La preparación se fundamenta en la teoría de `curso/` y en el diccionario de la encuesta. Toda transformación o corrección aprobada produce una nueva versión y queda vinculada a su regla, autor, motivo y validación.

## Estado actual

**Candidata semántica y vistas temáticas generadas; aún no publicada.** La ejecución vigente `data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f/` conserva las 39.497 filas y 275 columnas del maestro, aplica una regla semántica trazable a tres horas semanales imposibles y genera 11 vistas temáticas por sección/universo. Cada vista incluye conteos, filtro, clave, advertencias estadísticas y hash. El resumen de hogar consolida copias no faltantes únicas; no se encontraron valores observados contradictorios, y la operación queda auditada sin modificar el maestro. El raw permanece intacto. La limpieza semántica integral, validación del diseño inferencial y confirmación de `totper` siguen pendientes; Flask/PostgreSQL y la bitácora persistente tampoco están implementados.

El usuario identifica el archivo como un dataset muy sucio. El sistema debe medir y clasificar sus problemas antes de corregirlos: los tokens `NA`, vacíos y valores extremos no constituyen por sí solos errores. Ver [la estrategia de limpieza](docs/cleaning-methodology.md).

El INE publica el [diccionario EH2025_Persona](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona), pero la copia local no coincide exactamente con ese archivo: tiene 39.497 filas y 275 columnas, frente a 39.485 casos y 276 variables en la ficha oficial. Por ello la edición y procedencia de `data/persona.csv` siguen pendientes de confirmar; no deben aplicarse dominios ni saltos del cuestionario como si ambas copias fueran idénticas. El diccionario local separa las definiciones oficiales de las columnas adicionales locales.

## Qué debe permitir el sistema

1. Registrar la fuente y cargar el archivo de personas con un contrato específico y versionado.
2. Conservar el archivo original y crear un perfil de calidad.
3. Aplicar reglas de limpieza versionadas y revisar las excepciones.
4. Publicar una versión limpia solo si supera las validaciones.
5. Comparar la calidad antes y después de limpiar y describir las variables de personas con tipos y universos confirmados.
6. Explorar resultados, calidad y linaje desde un dashboard.
7. Proponer correcciones, aprobarlas y consultar en la bitácora de PostgreSQL quién cambió qué, cuándo, por qué y con qué fundamento del curso.
8. Exportar datos limpios y resultados con la versión y los filtros identificados.

## Lectura recomendada

| Documento | Contenido |
| --- | --- |
| [Visión general](docs/project-overview.md) | Problema, alcance, usuarios y límites del caso de ejemplo |
| [Requisitos](docs/requirements.md) | Funciones, reglas, seguridad y requisitos operativos |
| [Arquitectura](docs/architecture.md) | Componentes, flujo de datos y decisiones técnicas |
| [Contrato de datos](docs/data-contract.md) | Esquema, clave, tokens y validaciones de `persona.csv` |
| [Metodología de limpieza](docs/cleaning-methodology.md) | Aplicación de la teoría de `curso/`, reglas y evidencia antes/después |
| [Vistas temáticas de persona](docs/thematic-views-persona.md) | Contenido, filtros, conteos, unidad de análisis y limitaciones estadísticas de las 11 vistas |
| [Análisis exploratorio descriptivo](docs/exploratory-analysis-persona.md) | Método y estado de la etapa descriptiva por variable y universo |
| [Trazabilidad](docs/versioning-and-audit.md) | Versiones, cambios, aprobaciones y modelo de base de datos |
| [Análisis y dashboard](docs/analytics-and-dashboard.md) | Métodos estadísticos, vistas y reglas de presentación |
| [Criterios de aceptación](docs/acceptance-criteria.md) | Condiciones verificables de entrega |
| [Escenarios de prueba](docs/test-scenarios.md) | Casos funcionales, de datos y de seguridad |
| [Plan de implementación](docs/implementation-plan.md) | Etapas, dependencias y entregables |
| [Progreso](docs/progress.md) | Estado real del repositorio y próximos pasos |

## Estructura prevista

```text
proyectoFinal/
  backend/       aplicación Flask, blueprints, servicios, modelos, migraciones y pruebas
    templates/   vistas Jinja de calidad, dashboard y bitácora
    static/      estilos y JavaScript para tablas y gráficos
  config/        contrato de persona y reglas de limpieza versionadas
  data/          archivo de ejemplo local; los originales productivos van a almacenamiento controlado
  docs/          especificación y decisiones de diseño
  curso/         fundamento teórico para preparar y evaluar los datos
  AGENTS.md      reglas para quienes implementen este repositorio
```

## Decisiones de diseño iniciales

- Python y Flask para el sistema web; Jinja, HTML/CSS y JavaScript con Plotly para las vistas; SQLAlchemy y Alembic para conexión y migraciones de PostgreSQL; pandas para perfilamiento y limpieza; CSV/Parquet inmutables para los datos. Un worker separado procesa las cargas. Estas decisiones aún no están implementadas.
- PostgreSQL es la base de la bitácora: cargas, ejecuciones, reglas, impactos, propuestas, decisiones, versiones y exportaciones. Los registros completos de personas permanecen en archivos controlados; no se copian a los logs generales.
- Cada importación o edición aprobada produce una versión nueva. Nunca se sobrescribe el original.
- Las estadísticas de la encuesta deben respetar el universo, el ponderador y, para intervalos de confianza, el diseño muestral cuando sus variables estén confirmadas.
- El primer alcance está dedicado a `persona.csv`. La generalización a otros datasets queda fuera de la primera entrega.
- La teoría de `curso/05_preparacion_de_datos.md` guía faltantes, duplicados, imputación y transformaciones; los capítulos de tipos, descriptiva y metodología complementan las decisiones. Los ejemplos didácticos no se convierten en reglas universales.

## Ejecución local del preprocesamiento

Desde la raíz del repositorio, con Python 3.11 o posterior y pandas, NumPy, Matplotlib y PyArrow instalados:

```powershell
python data/proprosessing/preprocessing.py
```

Cada corrida crea un directorio nuevo en `data/proprosessing/output/` con CSV/Parquet candidatos, perfiles, comparación, bitácoras, manifiesto, gráficas y `thematic_views/`. Para ejecutar con el Python global instalado en Windows, desde PowerShell: `& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" data/proprosessing/preprocessing.py`. Esto no inicia ni sustituye la aplicación Flask/PostgreSQL, que continúa pendiente. Revisar [el contrato](docs/data-contract.md), [la metodología](docs/cleaning-methodology.md), [las vistas temáticas](docs/thematic-views-persona.md) y [el progreso](docs/progress.md) antes de interpretar resultados.

El análisis descriptivo posterior se genera por separado con `python data/proprosessing/exploratory_analysis.py`; sus unidades, universos, límites y estado de ejecución están en [el documento de análisis exploratorio](docs/exploratory-analysis-persona.md).
