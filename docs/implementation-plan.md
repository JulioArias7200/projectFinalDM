# Plan de implementación de `persona.csv`

## Estado actual

La persistencia acordada es JSON local; no se utiliza PostgreSQL. Está implementado y ejecutado un pipeline conservador, la validación completa de la candidata y la publicación interna de `persona-317279aafe9023a2`. El CSV fuente sigue intacto. La versión conserva 39.497 filas y 275 columnas; se aplicaron S-01 y S-02 y se verificaron 300 hashes de artefactos.

La publicación no equivale a limpieza semántica integral. Se conservan alertas sin evidencia concluyente, entre ellas `totper`, dominios/rangos y universos. La versión está etiquetada para uso interno con limitaciones semánticas y no respalda por sí sola inferencia oficial. Estado detallado en [progreso](progress.md), [dictamen semántico](semantic-cleaning-audit.md) y [validación/publicación](final-validation-sampling-persona.md).

## Etapas cerradas

1. **Diagnóstico y reglas conservadoras:** perfiles por columna, gráficos antes/después, diccionario JSON, advertencias de faltantes/atípicos, retención de las 275 columnas, control de clave `(folio,nro)`, S-01 y S-02.
2. **Validación:** comparación raw/candidata, 39.497 × 275, secuencia de claves, cero duplicados exactos o de clave, bitácora de 12.519 cambios, reconciliación de todas las diferencias y hashes de 300 artefactos; 10/10 controles PASS.
3. **Muestreo de QA:** 381 hogares estratificados por departamento × área, 1.216 filas persona, asignación reproducible. Es una muestra de control, no de inferencia.
4. **Publicación JSON interna:** copia inmutable de la corrida completa, validación de hashes poscopia, manifiesto con limitaciones y actualización atómica del puntero/evento en `data/audit_log.json`. Flask lee la versión indicada por ese puntero.

## Pendientes que permanecen abiertos

### Siguiente etapa: análisis descriptivo por universos en Flask

La especificación aprobada está en [dashboard-universe-plan.md](dashboard-universe-plan.md). La implementación inicial ya sustituye el resumen estático por gráficos agregados de la versión JSON publicada, añade demografía y revisión semántica, y bloquea los indicadores económicos y geográficos que aún no se pueden respaldar. Falta ejecutar pruebas y reconciliar/validar los universos antes de habilitar indicadores con interpretación semántica.

Orden sugerido: demografía; salud general y módulos de fecundidad/niñez; educación; empleo y ocupación secundaria; ingresos personales; e ingresos/pobreza a nivel hogar. Para cada indicador se fijarán variable(s), unidad, universo, numerador, denominador, tratamiento de ausencias y método. Se mostrarán conteos no ponderados hasta validar el diseño muestral; no se publicarán tasas oficiales ni inferencia. `s02b_10`, máscaras hipotéticas, `totper` y extensiones sin contrato permanecen bloqueados o como alertas.

Esta etapa requiere cálculos desde vistas verificadas, metadatos visibles en interfaz, supresión de celdas pequeñas y pruebas con datos sintéticos más reconciliación independiente de cualquier KPI. Las gráficas implementadas hasta ahora son conteos exploratorios no ponderados; no habilitan inferencia ni certifican elegibilidad. No se deben agregar al alcance vivienda, alimentación, gastos, equipamiento ni discriminación, ausentes de `persona.csv`.

### Especificación de gráficos para el dashboard

Antes de cambiar plantillas o JavaScript, cada gráfico debe quedar ligado a una pregunta, variable(s), universo, unidad, filtro, estados de ausencia incluidos, denominador, estadístico, escala y regla de supresión. La matriz detallada y las cautelas por gráfico están en [dashboard-universe-plan.md](dashboard-universe-plan.md). Orden visual propuesto:

1. **Resumen general:** tarjetas de identidad/tamaño de versión y perfil estructural de faltantes; no usar KPI temáticos estáticos.
2. **Demografía:** histograma de edad y barras horizontales de categorías y geografía; conteos observados, sin expansión poblacional.
3. **Salud:** barras categóricas y cobertura de elegibles/respondidos/faltantes, separadas entre salud general, fecundidad/materna e infantil; solo con saltos confirmados.
4. **Educación:** barras categóricas y distribución de nivel/años según tipo semántico; denominador propio por pregunta.
5. **Empleo:** actividad y ocupación en barras; distribución de horas si unidad confirmada; módulo secundario separado con control de excepciones.
6. **Ingresos:** histogramas y cuantiles/boxplots para montos con periodo/unidad; hogar contado una vez por `folio`; cualquier pobreza requiere contrato confirmado.
7. **Revisión pendiente:** matriz de estados semánticos y recuentos de variables por estado. Mapa regional únicamente como complemento cuando la métrica geográfica se valide.

Todos deben usar la tipografía `Inter` y los tokens de tema ya definidos en `dashboard/static/css/base.css` y `dashboard/static/css/theme.css`, incluidos fondos, textos, rejilla y ejes para los modos claro/oscuro. `font-mono` se reserva para metadatos técnicos y códigos. Evitar paletas independientes, pastel con muchas categorías y porcentajes sin denominador. Incluir título/pregunta, unidad, `N`, filtro, leyenda, tooltip accesible, estado vacío/bloqueado y nota metodológica. La implementación debe incluir pruebas sintéticas de métricas, supresión y estados sin datos, además de revisión de contraste/responsividad y reconciliación contra tabla agregada.

- La auditoría semántica integral por dominio/universo no puede cerrarse con el esquema local sin reconciliar diferencias de F27 y las extensiones locales.
- `totper` difiere del roster observado en 10.285 de 12.718 hogares y no tiene definición confirmada; queda preservada y fuera de denominadores.
- La aplicación carece de autenticación/autorización completa y flujo web de propuestas/aprobaciones; esas funciones no se deben anunciar como disponibles.
- El almacenamiento JSON local es de instancia única; requiere respaldo de `data/audit_log.json` y del directorio `data/proprosessing/versions/`.

## Comandos reproducibles

Desde la raíz, con Python 3.11+ y dependencias instaladas:

```powershell
python -m unittest discover -s tests -v
python data/proprosessing/preprocessing.py
python data/proprosessing/publish_validated_candidate.py --candidate data/proprosessing/output/<run_id>
python dashboard/app.py
```

El comando de publicación vuelve a validar antes de copiar y activar una versión. Una candidata fallida no cambia el puntero JSON vigente. Las pruebas usan solo fixtures sintéticas; los datos reales se validan con reportes agregados sin imprimir filas.
