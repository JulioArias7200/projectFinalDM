# Escenarios de prueba

Usar fixtures sintéticas con nombres de columnas y estructura pertinente a `persona.csv`, sin copiar registros reales. Incluir identificadores, estados de ausencia, comillas y codificaciones problemáticas. Las rutas se prueban con el cliente de Flask y la persistencia JSON con archivos temporales aislados. Los escenarios marcados como ejecutados tienen evidencia; los demás siguen planeados.

| ID | Entrada y acción | Resultado esperado | Criterio |
| --- | --- | --- | --- |
| T-01 | Cargar CSV válido con encabezados y clave única | Raw intacto, perfil completo, versión validable | CA-01, CA-03 |
| T-02 | Reenviar misma solicitud con misma clave de idempotencia | Se devuelve el trabajo original; no hay versión duplicada | CA-02 |
| T-03 | Cargar CSV con comas entre comillas y salto de línea dentro de un campo | Parser conserva el campo; conteo correcto de registros | CA-03 |
| T-04 | Cargar encabezado duplicado, columna requerida ausente o valor numérico inválido | Error o cuarentena específica; no publicación silenciosa | CA-03, CA-05 |
| T-05 | Cargar registros con `NA`, vacío, cero y no aplica | Estados diferenciados según contrato | CA-03 |
| T-06 | Ejecutar dos veces misma regla determinista sobre el mismo raw | Mismo resultado lógico y reporte reproducible | CA-04, CA-07 |
| T-07 | Fallar después de escribir artefacto temporal y antes de moverlo | Versión publicada anterior permanece visible | CA-06 |
| T-08 | Fallar al cambiar el puntero de publicación | API sigue leyendo la versión anterior; artefacto huérfano controlado | CA-06 |
| T-09 | Proponer cambio válido, aprobar y publicar | Nueva versión y diff con actor, motivo y fecha | CA-08 |
| T-10 | Aprobar cambio propio con doble control activado | Rechazo por autorización | CA-08, CA-13 |
| T-11 | Dos propuestas cambian la misma celda desde la misma base | Segunda queda en conflicto; ninguna sobrescribe silenciosamente | CA-09 |
| T-12 | Restaurar una versión previa | Nueva versión con padre y evento de restauración; historial completo | CA-10 |
| T-13 | Filtrar dashboard y exportar | Indicadores y archivo usan mismos filtros, versión y denominadores | CA-11 |
| T-14 | Solicitar intervalo para encuesta sin diseño confirmado | Resultado bloqueado o marcado como no disponible con motivo | CA-12 |
| T-15 | Calcular proporción ponderada en fixture con pesos conocidos | Resultado coincide con cálculo independiente; `n` y suma de pesos visibles | CA-12 |
| T-16 | Acceder como lector a fila sensible o exportación de microdatos | API deniega, incluso si se modifica la URL manualmente | CA-13 |
| T-17 | Filtrar grupos pequeños o combinar filtros que revelen un valor suprimido | Respuesta mantiene supresión y evita recuperación obvia | CA-13 |
| T-18 | Reiniciar worker durante trabajo y reintentarlo | Estado consistente; no publicación duplicada | CA-02, CA-14 |
| T-19 | Restaurar copia de seguridad en entorno limpio | Hashes, versión publicada y referencias de auditoría recuperados | CA-15 |
| T-20 | Instalar con instrucciones del README en entorno limpio | Flask, templates, pipeline y persistencia JSON arrancan con configuración documentada | CA-16, CA-17 |
| T-21 | Cargar, limpiar, corregir y publicar; reiniciar Flask y consultar bitácora | Eventos, actores, motivos, reglas y versiones persisten con filtros y paginación | CA-18 |
| T-22 | Intentar editar/borrar eventos usando el servicio de bitácora | La interfaz de servicio solo agrega eventos; el historial existente se conserva | CA-18 |
| T-23 | Interrumpir conexión/escritura de bitácora durante aprobación o publicación | No se confirma el cambio ni se sustituye versión publicada; reintento no duplica eventos lógicos | CA-06, CA-18 |
| T-24 | Reusar clave de idempotencia con contenido distinto; luego ejecutar mismo raw con reglas nuevas y clave nueva | Primera solicitud queda en conflicto; segunda reutiliza raw y registra nueva ejecución | CA-02, CA-07 |
| T-25 | Fixture con pregunta no aplicable, no respuesta, vacío, `NA` y cero válido | Estados y universos conservados; ninguna imputación por defecto | CA-03, CA-19 |
| T-26 | Fixture con extremos válidos y errores de dominio confirmados | Atípicos se señalan sin borrar; errores siguen cuarentena/bloqueo; antes/después reconciliado | CA-05, CA-19 |
| T-27 | Duplicado exacto, clave repetida y personas distintas en un hogar | Se distingue cada caso; `folio` no elimina integrantes; toda deduplicación exige política | CA-03, CA-19 |
| T-28 | Ejecutar regla declarada sin fundamento/universo; ejecutar regla válida | Primera configuración se rechaza; segunda persiste referencia de curso, parámetros e impacto | CA-04, CA-19 |
| T-29 | Normalizar claves con espacios que quedarían iguales | Se detecta colisión y se bloquea publicación; nunca se fusionan personas silenciosamente | CA-05, CA-19 |
| T-30 | Fixture con categoría numérica y columna sin definición confirmada | No se calcula media categórica ni indicador semántico sobre columna pendiente | CA-11, CA-19 |
| T-31 | Activar imputación justificada en fixture y repetir con misma configuración | Máscara distingue observado/imputado; método, parámetros, evaluación y semilla se registran; resultado reproducible | CA-04, CA-07, CA-19 |
| T-32 | Consultar perfil raw, cuarentena o diff sensible sin permiso; enviar cambio web sin CSRF | Flask deniega acceso/cambio; no filtra valores restringidos en JSON, HTML ni bitácora visible | CA-13, CA-17 |
| T-33 | Construir vistas con fixture sintético que combine universos, filtro secundario discordante y copias de hogar faltantes/concordantes | Filtros dan denominadores esperados; excepción secundaria se conserva marcada; una observación única se consolida solo en vista hogar; valores observados contradictorios se excluyen y auditan; fuente no cambia y destino existente no se sobrescribe | CA-03, CA-05, CA-19 |

T-33 se implementó en `tests/test_thematic_views.py`. Las pruebas de publicación JSON, reintento, fallo de validación y concurrencia de bitácora se implementaron en `tests/test_json_publication.py`; ambas suites pasan. El resto de escenarios de esta tabla continúa planificado y no se considera ejecutado.

Para el caso real, añadir el reporte del pipeline de `persona.csv`: 39.497 registros y 275 encabezados son controles de esta copia, no restricciones para todas las cargas futuras. La [revisión técnica inicial](cleaning-methodology.md#diagnóstico-técnico-de-referencia) ya midió estructura, clave textual y algunos tokens; no sustituye estas pruebas ni el perfil por columna/universo. Validar dominios y coherencia tras confirmar el contrato; documentar diferencias explicadas sin exponer personas.
