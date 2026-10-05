# Criterios de aceptación

Estos criterios indican cómo evaluar una futura implementación. **Ninguno se considera cumplido por la documentación sola.** Para cada entrega registrar evidencia, fecha y versión de código en `progress.md`.

| ID | Criterio verificable | Evidencia mínima |
| --- | --- | --- |
| CA-01 | Una carga conserva el CSV original byte a byte y registra SHA-256, tamaño, actor, fecha y procedencia | Comparación de hash y consulta de metadatos |
| CA-02 | La repetición de la misma solicitud de carga con clave de idempotencia no crea dos versiones | Prueba de repetición y conteo de versiones |
| CA-03 | El perfil informa filas, columnas, nulos, tipos, duplicados y errores de parseo; distingue `NA`, vacío y cero según contrato | Reporte y casos de prueba sintéticos |
| CA-04 | Cada regla de limpieza tiene versión, orden, parámetros, fundamento de `curso/`, universo y conteo de filas afectadas | Manifiesto JSON, bitácora JSON y reporte antes/después |
| CA-05 | Una fila o valor inválido queda en cuarentena o bloquea publicación de acuerdo con política | Prueba con entrada inválida y estado de trabajo |
| CA-06 | Una versión fallida o incompleta no sustituye la publicada | Inyección de fallo antes de publicación |
| CA-07 | Una versión publicada se puede reproducir desde raw, contrato, reglas, parches y código identificados | Reejecución y comparación de hash lógico/conteos |
| CA-08 | Una corrección exige clave estable, versión base, valor anterior, valor nuevo y motivo; queda aprobada/rechazada con actor y fecha | Flujo completo en UI y registros de auditoría |
| CA-09 | Un conflicto por cambio de versión o valor anterior no sobreescribe datos | Dos solicitudes concurrentes sobre la misma celda |
| CA-10 | Comparar o restaurar versiones no borra el historial; restaurar crea una versión nueva | Linaje y auditoría antes/después |
| CA-11 | Dashboard y exportación muestran versión, filtros, universo, método y fecha; números reconciliados con la versión limpia | Comparación de una métrica con cálculo independiente |
| CA-12 | Estadísticas de encuesta usan ponderador y diseño solo cuando el contrato está confirmado; si falta, no se presenta inferencia poblacional como válida | Casos con/sin configuración de encuesta |
| CA-13 | Un lector no recibe microdatos restringidos ni celdas pequeñas suprimidas mediante API, tabla, gráfico o exportación | Pruebas de autorización y reconstrucción básica |
| CA-14 | Los trabajos largos informan estado, errores y reintentos sin bloquear la API | Ejecución y fallo controlado |
| CA-15 | Copia de seguridad y restauración recuperan metadatos y artefactos de una versión publicada | Ensayo de restauración documentado |
| CA-16 | La instalación desde cero usa configuración de entorno, migraciones y comandos documentados | Despliegue limpio reproducido por otra persona |
| CA-17 | El sistema web Flask usa persistencia JSON local con rutas configurables y esquema versionado | Prueba de rutas Flask, escritura atómica, bloqueo concurrente y lectura del catálogo |
| CA-18 | La bitácora JSON registra cargas, reglas, fallos, cambios, decisiones y publicación; persiste tras reiniciar y el servicio solo agrega eventos | Flujo completo, reinicio, consulta filtrada y prueba de ausencia de operaciones de edición/borrado en el servicio |
| CA-19 | La limpieza de `persona.csv` produce reporte por columna/universo antes/después, distingue faltantes legítimos y conserva excepciones | Reglas L-01 a L-12 aplicables, pruebas sintéticas y reporte técnico real sin microdatos expuestos |

| CA-20 | Cada universo visible tiene población/unidad/filtro/denominador declarados; los agregados se reconcilian con la versión publicada; cifras no verificadas quedan bloqueadas o etiquetadas; las celdas pequeñas se suprimen | Pruebas de denominadores y supresión, recálculo independiente de KPI, metadatos visibles y manejo seguro de universo pendiente |
| CA-21 | Los gráficos usan la tipografía/tokens visuales compartidos, indican versión, universo/filtro, unidad, N y método, preservan estados de ausencia distintos y no revelan celdas <10 | Revisión en tema claro/oscuro, pruebas sintéticas de estados y supresión, verificación de checksum de la fuente publicada y lectura visual accesible |

## Entrega mínima útil

La primera versión utilizable debe cumplir CA-01 a CA-09, CA-11, CA-13 y CA-17 a CA-19, con análisis descriptivo y dashboard Flask básico. CA-19 no exige imputación ni transformaciones que no estén justificadas; una regla opcional se documenta como deshabilitada y se verifica que no modifique datos. Ninguna variable sin definición confirmada se utiliza en indicadores semánticos. La publicación externa de resultados requiere resolver las condiciones pendientes de `data-contract.md` y CA-12. Restauración, programación y ampliación inferencial pueden seguir en etapas posteriores sin presentarse como terminadas.
