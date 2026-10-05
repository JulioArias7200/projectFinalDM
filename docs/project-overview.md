# Visión general del proyecto

El proyecto limpia y describe exclusivamente `data/persona.csv`, conservando el archivo de origen como solo lectura. El proceso se basa en minería de datos, reglas justificadas con `curso/` y definiciones disponibles en el diccionario JSON. No se deben convertir las técnicas del curso en reglas universales ni borrar observaciones solo por ser extremas o faltantes.

## Estado de entrega

Existe una versión interna publicada, `persona-317279aafe9023a2`, con 39.497 filas y 275 columnas. Conserva todas las filas/columnas, aplica las correcciones conservadoras S-01 y S-02 y tiene validación estructural, trazabilidad y hashes comprobados. El catálogo JSON en `data/audit_log.json` registra el puntero de publicación y los eventos; Flask consume esa versión en vez de seleccionar candidatas por fecha.

La publicación está limitada a uso interno: quedan dominios y universos por confirmar debido a diferencias entre el CSV local y F27. No afirmar limpieza semántica completa ni usar variables pendientes en indicadores concluyentes. La alerta `totper` permanece sin cambio y no sirve como conteo confirmado de miembros del hogar.

## Arquitectura vigente

- Flask y plantillas Jinja para dashboard y bitácora.
- Pipeline Python separado para perfilar, transformar y validar.
- JSON local para catálogo/versions/eventos, con lock de archivo y sustitución atómica.
- CSV y Parquet versionados e inmutables en `data/proprosessing/versions/`.
- Corridas de trabajo no publicadas en `data/proprosessing/output/`.

No se usa PostgreSQL. JSON es adecuado para este uso local de una instancia, pero no sustituye una base transaccional multiusuario o distribuida. El sistema todavía no implementa autenticación completa ni aprobaciones multiusuario.

## Evidencia y documentación

- Propuesta aprobada para el dashboard por universos: [dashboard-universe-plan.md](dashboard-universe-plan.md).
- Estado y límites del dashboard: [analytics-and-dashboard.md](analytics-and-dashboard.md).

- Reglas y fundamentos: [metodología](cleaning-methodology.md) y [auditoría semántica](semantic-cleaning-audit.md).
- Linaje, validación y publicación: [validación final](final-validation-sampling-persona.md) y [versionado/bitácora](versioning-and-audit.md).
- Criterios de aceptación: [acceptance-criteria.md](acceptance-criteria.md).
- Estado real: [progress.md](progress.md).
