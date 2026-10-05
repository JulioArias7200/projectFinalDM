# Requisitos del sistema

## Convenciones

`RF` designa una función, `RD` una regla de datos y `RNF` una condición operativa. El alcance es el sistema Flask de limpieza de `data/persona.csv`; por decisión del usuario, catálogo, versiones y bitácora persisten en JSON local, sin PostgreSQL. Su contrato define columnas, tipos, claves, universos y métricas; las reglas se justifican con `curso/` y el diccionario aplicable.

## Requisitos funcionales

| ID | Requisito | Resultado observable |
| --- | --- | --- |
| RF-01 | Registrar el dataset de personas, propietario, fuente, licencia/permiso y contrato | Ficha de personas con historial persistido en catálogo JSON |
| RF-02 | Importar CSV sin alterar el original | Archivo raw con hash, fecha, usuario y trabajo asociado |
| RF-03 | Detectar estructura y perfilar datos antes de limpiar | Informe de tipos, faltantes, duplicados, rangos y errores de parseo |
| RF-04 | Configurar y ejecutar reglas de limpieza de persona con orden, versión y fundamento de `curso/` | Salida preparada y reporte por regla con registros afectados y comparación antes/después |
| RF-05 | Separar registros que no cumplen reglas críticas | Cuarentena con clave/línea, motivo y opción de revisión |
| RF-06 | Validar y publicar una nueva versión | Versión inmutable con linaje y puntero de publicación |
| RF-07 | Permitir propuestas de corrección de celdas o filas | Diff, motivo, autor, fecha, estado y conflicto detectable |
| RF-08 | Aprobar/rechazar cambios según rol | Decisión registrada; una aprobación válida genera nueva versión |
| RF-09 | Consultar versiones, comparar dos versiones y restaurar una anterior | Resumen de diferencias y nueva versión de restauración |
| RF-10 | Calcular análisis descriptivos sobre versión y filtros explícitos | Conteos, frecuencias, distribución, dispersión y datos faltantes |
| RF-11 | Ejecutar análisis inferenciales solo con supuestos cumplidos | Método, tamaño de muestra, intervalo/estadístico, supuestos y advertencias |
| RF-12 | Mostrar dashboard y calidad antes/después mediante vistas Flask/Jinja | Filtros, indicadores, gráficos, linaje, reglas y definiciones visibles |
| RF-13 | Exportar datos limpios, cuarentena y resultados según permisos | Archivo con versión, filtros, fecha y método en metadatos |
| RF-14 | Programar importaciones y reejecuciones | Trabajo recurrente con estado, reintentos y alertas de fallos |
| RF-15 | Registrar eventos de lectura/exportación sensible y cambios de configuración | Bitácora consultable por administradores |
| RF-16 | Consultar bitácora JSON desde Flask con filtros y paginación | Cargas, reglas, impactos, fallos, cambios, decisiones y versiones conservados tras reiniciar la aplicación |
| RF-17 | Evaluar y documentar la limpieza según la teoría del curso | Informe por columna y universo, decisiones justificadas y limitaciones pendientes |

## Reglas de datos

| ID | Regla |
| --- | --- |
| RD-01 | El raw es inmutable. Cada salida limpia referencia el hash del raw, contrato, conjunto de reglas, parámetros y versión de código. |
| RD-02 | La lectura inicial conserva texto y diferencia entre vacío, token `NA`, cero y no aplica. La clasificación depende de columna y universo; la imputación está deshabilitada por defecto. |
| RD-03 | La clave candidata `(folio, nro)` se valida en cada carga y tras normalización; `folio` solo no identifica una persona. Si no existe clave estable, se exige una estrategia documentada antes de editar. |
| RD-04 | No se elimina una fila ni se imputa un valor automáticamente sin regla y política de publicación explícitas. |
| RD-05 | Tipos, dominios, invariantes y relaciones se validan antes de publicar. Un error crítico bloquea publicación. |
| RD-06 | La ejecución repetida con mismo raw, contrato, reglas y código produce la misma salida lógica o informa por qué no puede garantizarse. |
| RD-07 | Toda corrección aprobada se aplica con control de concurrencia de la versión base y valor anterior. |
| RD-08 | Cada métrica especifica población, unidad, filtros, ponderador, tratamiento de faltantes y, si aplica, diseño muestral. |
| RD-09 | Cada regla declara referencia de `curso/`, evidencia del diccionario, universo, condición, acción y métricas antes/después. Los ejemplos didácticos no autorizan tratamientos indiscriminados. |

## Requisitos no funcionales

| ID | Requisito | Criterio de diseño inicial |
| --- | --- | --- |
| RNF-01 | Seguridad | Autenticación, permisos por rol y dataset, TLS en despliegue, secretos fuera del repositorio |
| RNF-02 | Privacidad | Datos de identificación minimizados, agregación, supresión de celdas pequeñas y trazas sin filas completas |
| RNF-03 | Integridad | Hashes, artefactos de versión inmutables, catálogo JSON reemplazado atómicamente, eventos append-only desde el servicio y copias de seguridad verificadas |
| RNF-04 | Reproducibilidad | Parámetros, dependencia de código, contrato y versión visibles en cada ejecución |
| RNF-05 | Rendimiento | Cargas asíncronas, paginación, análisis con límites, caché por versión/filtros |
| RNF-06 | Observabilidad | Logs estructurados con `job_id`, métricas, alertas y estado accesible |
| RNF-07 | Portabilidad | Configuración por entorno y rutas relativas; esquema JSON versionado |
| RNF-08 | Accesibilidad | Tablas navegables, contraste y textos alternativos para gráficos principales |
| RNF-09 | Arquitectura requerida | Flask con vistas Jinja, persistencia JSON local con escrituras atómicas y pipeline Python independiente; rutas configurables y portables |

La primera entrega prioriza carga, perfil, limpieza, publicación, correcciones auditadas y análisis descriptivo de personas. RF-09 (restauración), RF-11 (inferencia) y RF-14 (programación) son ampliaciones posteriores. Los permisos y la bitácora se implementan desde la primera carga, no después del dashboard.

Los objetivos cuantitativos de latencia, concurrencia, volumen máximo, retención y disponibilidad se fijarán tras probar un prototipo con el volumen real y acordar el entorno de despliegue. No son promesas implícitas de esta especificación.

## Permisos mínimos

| Acción | Administrador | Responsable | Analista | Lector |
| --- | --- | --- | --- | --- |
| Ver agregados autorizados | Sí | Sí | Sí | Sí |
| Ver microdatos autorizados | Sí | Según concesión | Según concesión | No |
| Registrar fuente/contrato | Sí | Proponer | No | No |
| Definir reglas | Sí | Sí | Proponer | No |
| Proponer corrección | Sí | Sí | Sí | No |
| Aprobar corrección | Sí | Sí | No | No |
| Publicar versión | Sí | Sí | No | No |
| Exportar microdatos | Según política | Según política | Según política | No |

La autorización efectiva también depende del dataset, clasificación de campos y política de supresión. Las cuentas de servicio no reciben permisos de lectura interactiva o aprobación.
