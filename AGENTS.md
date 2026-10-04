# Instrucciones para trabajar en proyectoFinal

## Propósito y estado

Implementar el sistema Flask de limpieza de `data/persona.csv` descrito en `README.md` y `docs/`, conectado a PostgreSQL para la bitácora del dataset. Fundamentar las reglas en `curso/` y en el diccionario confirmado de la encuesta, siguiendo `docs/cleaning-methodology.md`. A fecha de esta documentación solo existen documentos y el archivo de datos; no afirmar que una función está operativa sin código y pruebas que lo demuestren. Registrar avances verificables en `docs/progress.md`.

## Fuentes de verdad

1. La solicitud vigente del usuario.
2. `docs/requirements.md` y `docs/acceptance-criteria.md` para comportamiento esperado.
3. `docs/architecture.md`, `docs/data-contract.md` y `docs/versioning-and-audit.md` para decisiones técnicas.
4. `docs/implementation-plan.md` para el orden de trabajo. Si una decisión cambia, actualizar el documento afectado junto con el código.

La arquitectura acordada usa Flask con vistas Jinja, SQLAlchemy/Alembic y PostgreSQL. Cada regla de limpieza debe declarar referencia teórica, columnas, universo, condición, acción y evidencia antes/después. La teoría orienta el método; el diccionario confirma la semántica. No extrapolar los ejemplos del curso a todo `persona.csv` ni marcar todos los `NA` como errores.

## Reglas de datos

- Tratar `data/persona.csv` como fuente de ejemplo de solo lectura. No corregirlo ni normalizarlo en el mismo archivo.
- Conservar bytes originales, hash SHA-256, nombre, tamaño, fecha de carga, codificación detectada/confirmada y procedencia declarada. Separar identificador de archivo, versión lógica y ejecución de pipeline.
- Las salidas limpias deben escribirse en una ubicación nueva e inmutable. Publicar una versión solo después de validar esquema, claves, reglas y conteos. Un fallo deja la versión anterior publicada.
- Registrar la configuración y versión de código de cada ejecución, junto con filas aceptadas, rechazadas y motivos. Una regla no debe modificar silenciosamente datos no contemplados.
- Preservar `NA`, vacío, cero y “no aplica” como estados distintos cuando el contrato lo requiera. Nunca imputar, eliminar outliers o convertir tipos sin una regla declarada y trazable.
- Para `persona.csv`, validar la posible clave `(folio, nro)` antes de adoptarla. `folio` identifica el hogar y no es una clave única de persona. No suponer que `factor`, `estrato` o `upm` bastan por sí solos para todos los cálculos inferenciales.
- Los campos potencialmente sensibles o de identificación (`folio`, salud, ingresos, ubicación detallada) requieren controles de acceso, minimización y agregación; no imprimir filas completas en logs.

## Reglas de edición y auditoría

- No ofrecer edición directa sobre raw ni UPDATE manual sobre versiones publicadas. Una propuesta de cambio incluye dataset, versión base, clave de fila, columna, valor anterior, valor nuevo, razón y actor.
- Validar permisos, tipo, dominio, reglas de negocio y conflicto de versión antes de aprobar. Guardar rechazo o aprobación y el resultado en un historial append-only. Las acciones administrativas también se auditan.
- Aplicar cambios como parches sobre una nueva versión. Restaurar significa publicar otra versión derivada de una anterior, nunca borrar el historial.
- Mantener transacciones de metadatos consistentes con la publicación del archivo; una versión incompleta no debe ser visible en el dashboard.

## Reglas de análisis y dashboard

- Mostrar siempre dataset, versión, fecha de actualización, filtros, universo, tamaño de muestra y método de cálculo junto a los resultados.
- No presentar medias de variables categóricas ni interpretar códigos numéricos como medidas sin el diccionario. Diferenciar conteos de personas observadas, estimaciones ponderadas y tasas.
- Aplicar umbrales de supresión en celdas pequeñas configurables antes de compartir vistas o exportaciones. Los intervalos de confianza para encuestas complejas requieren un método de varianza compatible con su diseño.
- Las consultas y gráficos deben consumir la versión limpia publicada, no el archivo raw ni datos editados sin aprobación.

## Calidad de implementación

- Añadir pruebas para reglas de limpieza, idempotencia de importación, conflictos de edición, publicación atómica, permisos, cálculos ponderados y contratos de API. Usar datos sintéticos en pruebas; no copiar registros reales al repositorio.
- Versionar migraciones de PostgreSQL, esquemas de API y configuración de datasets. Los secretos van en variables de entorno o gestor de secretos, nunca en Git.
- Mantener rutas relativas y configuración portable; no codificar rutas de esta computadora en el código.
- Al cerrar una etapa, documentar el comando real para ejecutarla, las pruebas realizadas y las limitaciones pendientes. No marcar como completado un criterio solo por tener documentación.
