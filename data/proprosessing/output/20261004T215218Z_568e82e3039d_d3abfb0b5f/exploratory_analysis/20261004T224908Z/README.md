# Análisis exploratorio descriptivo de `persona.csv`

- Ejecución UTC: 20261004T224908Z
- Versión candidata: persona-1dbf937c73972a78
- Run de origen: 20261004T215218Z_568e82e3039d_d3abfb0b5f
- Hash maestro: `1dbf937c73972a78746b1106d2e591dc46ea487b943112afb406887801bf8fee`
- Unidad: personas, salvo la vista hogar candidata.
- Método: conteos y distribuciones no ponderados; cuantiles/media solo para tipos cuantitativos confirmados por el diccionario.
- Celdas pequeñas en gráficos y frecuencias exportadas: categorías con n < 10 se agrupan/omiten.
- No son estimaciones poblacionales ni resultados oficiales; el diseño muestral aún no está certificado.
- Las ausencias se describen dentro del universo de cada vista; no equivalen automáticamente a no respuesta.

## Universos examinados

- **demografia_persona**: n=39,497; filtro: Todos los registros persona. Todas las 39.497 personas; claves y diseño muestral se retienen como contexto, no se certifica inferencia.
- **salud_general_persona**: n=39,497; filtro: Todos los registros persona. Conserva el universo general; los submódulos S02B/C/D tienen universos distintos y sus ausencias no son equivalentes.
- **salud_fecundidad_mujeres_13_50**: n=11,328; filtro: s01a_02=2 y edad s01a_03 entre 13 y 50, ambos inclusive. Filtro documentado en DDI; el resto no pertenece al denominador de fecundidad.
- **salud_asistencia_infantil_menores_6**: n=3,434; filtro: Edad s01a_03 < 6. Universo DDI de asistencia a centro infantil; no interpretar ausencias fuera del corte como falta de respuesta.
- **salud_bono_menores_5**: n=2,781; filtro: Edad s01a_03 < 5. Vista del submódulo infantil según corte DDI; revisar cortes por pregunta dentro de la sección.
- **educacion_personas_4_mas**: n=37,354; filtro: Edad s01a_03 >= 4. Universo general de educación según DDI; Parte B/C puede imponer cortes más específicos.
- **empleo_personas_7_mas**: n=35,366; filtro: Edad s01a_03 >= 7. Universo general de empleo; cada pregunta de ocupación/ingresos puede imponer filtros adicionales.
- **empleo_secundario_casos**: n=1,357; filtro: s04e_25=1 OR any nonmissing s04e/s04f field; retain exceptions for review. Not a clean eligible-only sample: contains all affirmative cases and any reported secondary-work data, including filter conflicts. Use only rows with confirmed eligibility for estimates.
- **ingresos_no_laborales_persona**: n=39,497; filtro: Todos los registros persona. Row-level extract only; item-level questionnaire universes differ. No household aggregation or estimate is implied.
- **ingresos_pobreza_persona**: n=39,497; filtro: Todos los registros persona. Incluye variables personales y de hogar repetidas por persona. No calcular promedios ni intervalos sin definir unidad, ponderador y diseño.
- **hogar_resumen_persona_candidato**: n=12,718; filtro: Una fila por folio; solo campos invariantes dentro del folio. If copies have missing markers but one unique observed value, the household view uses that value and audits the coalescing; person-level master is unchanged. person_records_in_source counts source rows and does not substitute totper, whose local definition/provenance still requires confirmation.

## Archivos

`column_descriptives.csv` contiene una fila por columna y vista. `plots/` contiene gráficos de variables seleccionadas por tema. Las frecuencias se guardan agregadas y con umbral de supresión.

## Lectura estadística

No comparar porcentajes entre vistas con universos distintos sin recalcular un denominador común. Los códigos categóricos se reportan como categorías, nunca como magnitudes. Los ingresos y medidas candidatas llevan sus valores observados sin ponderar y requieren confirmar unidad, periodo, universo y edición del diccionario antes de interpretarse. La vista secundaria conserva una excepción al filtro; no utilizarla como muestra depurada.
