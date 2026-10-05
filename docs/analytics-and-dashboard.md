# Análisis estadístico y dashboard

## Estado funcional vigente — 4 de octubre de 2026

El dashboard Flask consume microdatos solo desde la versión indicada por `data/audit_log.json` y verifica el SHA-256 registrado antes de calcular los gráficos. La página principal y `/demografia` muestran distribuciones observadas de edad y códigos de sexo/departamento/área. Salud, educación y empleo muestran conteos de códigos de respuesta agregados; no aplican filtros de elegibilidad ni asignan equivalencias interpretativas no verificadas. Ingresos permanece bloqueado para visualizaciones sustantivas. `/region` informa que la visualización regional está pendiente y ya no presenta los valores de demostración anteriores. `/revision-pendiente` resume los estados de la matriz documental.

Los gráficos son barras HTML responsivas que heredan `Inter`, `theme.css`, `base.css` y los tokens de fondo, texto y color; códigos/metadata usan `font-mono`. Muestran versión, fecha, universo/filtro, unidad, `N` y método. Categorías con menos de 10 casos se agrupan y se aplica supresión complementaria para impedir deducir el total oculto por resta. Las vistas maternas, infantiles y secundarias siguen siendo filtros registrados en manifiesto, todavía no certificados para interpretación. No se presentan porcentajes oficiales, proyecciones, ponderaciones o inferencia. Se ejecutaron 14 pruebas sintéticas y las 8 rutas del resumen/universos/revisión/región respondieron HTTP 200; la comprobación automatizada de render no sustituye una inspección visual manual en ambos temas.

La descripción histórica del prototipo en las secciones siguientes debe leerse subordinada a este estado funcional: sus KPI y capas regionales estáticas no son resultados válidos ni se sirven en las páginas actuales.

## Alcance del sistema Flask y Arquitectura Frontend

El frontend del sistema está construido como una aplicación web analítica de alto rendimiento servida mediante Flask (`dashboard_bp` montado en `/dashboard/`), utilizando renderizado del lado del servidor con plantillas Jinja2, diseño modular de componentes, hojas de estilo CSS modernas con variables de diseño (tokens de tema oscuro/claro) y JavaScript interactivo para visualización cartográfica SVG, gráficos estadísticos y modales dinámicos.

La arquitectura frontend se alinea estrictamente con los principios de minería de datos del [compendio académico](../CURSO_DATA_MINING.md), mostrando en tiempo real los resultados del pipeline de limpieza sobre `data/persona.csv` (**39.497 registros**, **12.718 hogares**, **275 columnas master 100% preservadas** y **11 vistas temáticas especializadas**).

```mermaid
flowchart TD
  subgraph Client [Navegador del Usuario]
    HTML[HTML5 Semántico + Jinja2]
    CSS[Vanilla CSS Tokens / Tailwind]
    JS[theme.js / regional-map.js / data-explorer.js / comparative-chart.js]
  end

  subgraph Flask [Servidor Flask - dashboard_bp]
    Router[dashboard/routes.py]
    DService[DatasetService: In-Memory Caching]
    AService[AuditService: JSON Event Logging]
  end

  subgraph DataLayer [Pipeline & Artefactos Inmutables]
    Master[master_persona_clean.parquet / csv (275 cols)]
    ThematicViews[thematic_views/: 11 archivos CSV/Parquet]
    Manifests[views_manifest.json / manifest.json / comparison_all_columns.csv]
  end

  Client <-->|HTTP /dashboard/*| Flask
  Flask <--> DService
  DService <--> DataLayer
```

---

## Estructura de Páginas y Rutas Implementadas

El frontend expone 7 rutas principales con respuesta HTTP 200 verificada y navegación fluida:

| Ruta | Nombre de Página | Finalidad Analítica y Componentes Clave |
| --- | --- | --- |
| `/dashboard/` | **ML Lab / Resumen General** | Vista ejecutiva principal. Contiene tarjetas KPI de volumen (39.497 personas, 12.718 hogares, 275 variables master, 11 vistas temáticas), gráfico comparativo de perfiles antes/después, tarjetas de acceso rápido a los 4 universos y la matriz interactiva de reglas de limpieza. |
| `/dashboard/procedimiento` | **Metodología y Procedimiento** | Documentación paso a paso de las 7 fases del pipeline de limpieza (CRISP-DM/KDD). Incluye el **Diagrama de Flujo Dimensional SVG (Sankey Flow)** que ilustra la preservación del 100% de columnas master y derivación de 11 vistas temáticas, además del detalle de las reglas L-01 a L-12, S-01 (horas semanales) y H-01 (coalescencia de hogar). |
| `/dashboard/region` | **Distribución Regional & Universos** | **Mapa interactivo SVG de Bolivia con contornos oficiales de los 9 departamentos**. Soporta selector de capas temáticas (Demografía general, Salud, Educación, Empleo e Ingresos/Pobreza), paleta cromática diferenciada por universo e inspector dinámico de métricas por departamento. |
| `/dashboard/salud` | **Universo Salud (Sección s02)** | Análisis de cobertura médica, afiliación al SUS/Cajas y salud materno-infantil. Muestra tarjetas de sus **4 vistas temáticas derivadas** (General, Fecundidad 13–50 años, Asistencia Infantil <6 años y Bono Juana Azurduy <5 años), aviso de saltos metodológicos y tabla dinámica de variables con filtro en tiempo real. |
| `/dashboard/educacion` | **Universo Educación (Sección s03)** | Análisis de alfabetismo, asistencia escolar y años de escolaridad formal. Muestra tarjeta de la vista derivada **Educación Formal (≥4 años, 37.354 personas)**, KPIs y tabla interactiva de variables. |
| `/dashboard/empleo` | **Universo Empleo (Sección s04)** | Análisis del mercado laboral, condición de actividad (PEA/PET), ocupación principal y secundaria. Muestra tarjetas de sus **2 vistas temáticas** (**PET ≥7 años con 121 columnas** y **Ocupación Secundaria con 1.357 casos**), métricas de jornada y tabla interactiva de variables. |
| `/dashboard/ingresos` | **Universo Ingresos (Sección s05)** | Análisis de ingresos laborales, no laborales, transferencias y líneas de pobreza (p0). Muestra tarjetas de sus **3 vistas derivadas** (**Ingresos No Laborales 48 cols**, **Pobreza 25 cols** y **Resumen Hogar Folio con 12.718 folios únicos**), KPIs y tabla interactiva. |

---

## Componentes UI y Experiencia de Usuario (UX)

### 1. Navegación y Sidebars Sticky Transparentes
- **Barra Lateral Izquierda (`sidebar_nav.html`)**: Permite la navegación entre el Resumen, Procedimiento, Geografía Regional y los 4 Universos temáticos. Utiliza posicionamiento fijo/adherente (`lg:sticky lg:top-4`) con fondo transparente (`bg-transparent`) para acompañar el desplazamiento vertical del usuario sin generar bloques opacos ni desalineaciones visuales.
- **Barra Lateral Derecha (`sidebar_right.html`)**: Panel contextual sticky con resumen de estado del sistema (Dataset SHA-256, motor de minería, estado inmutable, accesos rápidos a la bitácora y especificaciones de diseño muestral).

### 2. Inspección Modal de Reglas de Limpieza (Sin Botones Invasivos)
- En la matriz de reglas de limpieza (`cleaning_rules_table.html`), **cada fila de la tabla es directamente interactiva (`cursor-pointer hover:bg-...`)**.
- Al hacer clic en cualquier regla (ej. `L-01`, `S-01`, `L-07`, `V-11`), se despliega una **modal dinámica** con diseño de cristal (*glassmorphism*) que muestra:
  - **Identificador y Nombre de Regla**.
  - **Categoría y Fundamento Teórico** (referencia exacta a los capítulos de `curso/`).
  - **Columnas Afectadas y Universo Elegible**.
  - **Condición Lógica / Restricción Matemática**.
  - **Acción Ejecutada y Evidencia Antes/Después** (métricas numéricas exactas).
  - **Barra de Estado de Validación** con brillo (*glow effect*) temático.

### 3. Cartografía SVG Oficial de Bolivia y Selector de Capas
- La página `/dashboard/region` integra el mapa vectorial oficial de Bolivia dividido en sus 9 departamentos: Chuquisaca (CH), La Paz (LP), Cochabamba (CB), Oruro (OR), Potosí (PT), Tarija (TJ), Santa Cruz (SC), Beni (BN) y Pando (PD).
- **Selector de Universos**: Permite alternar entre 5 capas de indicadores:
  1. *Político & Demografía*: Muestra tamaño muestral ($n$) y población proyectada.
  2. *Salud*: Cobertura de seguros médicos (SUS / Cajas).
  3. *Educación*: Tasa de alfabetismo en población $\ge 15$ años.
  4. *Empleo*: Tasa de ocupación efectiva en población $\ge 14$ años.
  5. *Ingresos*: Incidencia de pobreza moderada oficial ($p0$).
- **Inspector Interactivo**: Al hacer hover o clic sobre cualquier departamento, el panel lateral actualiza inmediatamente los datos sociodemográficos, porcentaje respecto al total nacional y valor del indicador seleccionado con su correspondiente universo de procedencia.

### 4. Diagrama de Flujo Dimensional (Sankey Flow)
- Ubicado en `/dashboard/procedimiento`, visualiza de forma intuitiva el paradigma del pipeline moderno:
  $$\text{Raw } persona.csv \ (275\text{ cols}) \longrightarrow \text{Master Limpio } (275\text{ cols 100\% preservadas}) \longrightarrow 11\text{ Vistas Temáticas}$$
- Explica visualmente la coalescencia de 12.718 hogares sin conflictos y el tratamiento trazable de la regla S-01 ($\le 168\text{ h/sem}$).

### 5. Tarjetas de Vistas Temáticas en Universos
- En cada página de universo (`/salud`, `/educacion`, `/empleo`, `/ingresos`), se renderizan tarjetas modulares que detallan las vistas derivadas generadas en `thematic_views/`, mostrando nombre del archivo, población elegible ($N$), cantidad de columnas y condición de filtro estricto según el cuestionario.

---

## Estilos, Tokens y Temas (Dark / Light)

El sistema visual está construido sobre variables CSS estándar definidas en `dashboard/static/css/base.css`:
- `--bg-body`, `--bg-card`, `--bg-card-subtle`: Fondos con soporte para modo oscuro profundo (Dark Modern) y modo claro de alto contraste.
- `--text-main`, `--text-secondary`, `--text-muted`: Jerarquía tipográfica accesible.
- `--border-card`, `--card-shadow`: Separación limpia de componentes con bordes sutiles y sombras de profundidad.
- `--accent-cyan` (`#00d2ff`), `--accent-purple` (`#8a5cf6`), `--accent-blue` (`#3b82f6`), `--accent-red` (`#ff2453`), `--accent-emerald` (`#10b981`): Paleta de colores semántica unificada para los universos y reglas de minería de datos.
- `theme.js`: Manejo persistente del cambio de tema (Dark/Light) en `localStorage`.

---

## Rendimiento y Capa de Datos en Memoria

### Decisión vigente: análisis por universos

La propuesta aprobada para la siguiente etapa se especifica en [dashboard-universe-plan.md](dashboard-universe-plan.md), que define además el orden de navegación: resumen general, demografía, salud (general, fecundidad/materna e infantil), educación, empleo (principal y secundario), ingresos (personales y hogar/pobreza) y revisión pendiente. Estas vistas no reemplazan ni reducen el maestro `persona.csv`.

Las rutas Flask temáticas ya existen, y el servicio resuelve la versión indicada por el catálogo JSON. Esto no significa que todos los indicadores visibles sean cálculos reproducibles: `UNIVERSE_CONFIGS` contiene KPI y descripciones/conteos estáticos de presentación. Hasta calcularlos desde los artefactos verificados de la versión publicada, sus cifras deben tratarse como demostrativas, no como resultados analíticos certificados.

La implementación futura debe mostrar versión, fecha, filtro, universo, unidad y denominador junto a cada resultado; evaluar elegibilidad por pregunta; suprimir celdas pequeñas; y bloquear indicadores cuyo contrato semántico o diseño muestral no esté resuelto. Vivienda, equipamiento, gastos, alimentación y discriminación quedan fuera de `persona.csv` y no se deben simular ni importar en esta etapa.

Para garantizar tiempos de respuesta instantáneos en la interfaz web:
- `DatasetService` (`dashboard/services/dataset_service.py`): Lee y almacena en memoria los metadatos desde `manifest.json`, `views_manifest.json`, `comparison_all_columns.csv` y `view_coverage.csv`.
- `AuditService` (`dashboard/services/audit_service.py`): Gestiona la bitácora de eventos en formato JSON append-only con recuperación ante caídas.
- Sin dependencias de motores SQL pesados en tiempo de renderizado: las métricas de perfiles, conteos y esquemas se sirven en $<15\text{ ms}$.\n
