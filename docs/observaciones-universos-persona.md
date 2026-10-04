# Observaciones de ausencia y universos en `persona.csv`

## Propósito y alcance

Este documento revisa las columnas excluidas por la regla L-80 en la ejecución local `20261004T171822Z_568e82e3039d_d3abfb0b5f`. La fuente de registros fue únicamente `data/persona.csv` (39.497 filas, 275 columnas); `data_dictionary.json` se consultó como metadatos. El perfil técnico cubrió las 275 columnas, pero la corrida **no hizo una auditoría semántica completa de universos y saltos antes de excluir**. Por eso las cifras que siguen describen la regla ejecutada, no determinan por sí mismas qué variable se debe quitar de un análisis.

Los porcentajes de ausencia son globales: se calcularon sobre las 39.497 filas. La etiqueta de universo citada proviene del DDI asociado a F27; como el esquema de la copia local no coincide exactamente con F27, esas definiciones sirven como indicios para revisar, no prueban que todo salto o dominio sea aplicable a esta copia. En especial, «ausencia técnica» no significa necesariamente error, no respuesta ni ausencia de actividad económica.

## Qué se revisó y qué no

Para cada columna se calcularon vacíos/tokens reconocidos, formato mal registrado cuando existía una comprobación documentada, porcentaje combinado, perfil y decisión L-80. Un dominio no confirmado no se contó como mal registro. La regla excluyó columnas con porcentaje combinado **estrictamente mayor a 80 %** sobre el archivo completo, sin filtrar por universo. Por ello sí se hizo evaluación técnica columna por columna; **no se determinó para todas las columnas si sus faltantes son saltos válidos**.

En las 125 exclusiones, 47 entradas del DDI tienen texto no vacío en `pre_question_text`, que puede contener condiciones explícitas; 78 no tienen precondición explícita en ese campo. La presencia de texto no equivale automáticamente a una regla ejecutable: algunas instrucciones describen saltos en lenguaje natural, mencionan preguntas cuyo esquema no coincide o requieren interpretar categorías. Además, el CSV local no contiene exactamente el esquema F27. Las condiciones se deben mapear y verificar antes de programar filtros.

Se creó la [matriz de auditoría de las 125 variables](universe-matrix-persona.csv), con porcentaje global, universo DDI, precondición textual, estado de revisión, siguiente acción, disposición del candidato anterior y conteos elegibles/respondidos para algunas máscaras. Tras la revisión estadística, contiene 71 universos pendientes, 38 precondiciones por mapear, 13 reglas cotejadas localmente (nueve de fecundidad y cuatro laborales), 1 conflicto confirmado de contrato (`s02b_10`), 1 hipótesis laboral pendiente y 1 extensión local sin contrato oficial. Estos conteos describen el estado de auditoría, no una aprobación definitiva de reglas: la procedencia de la copia sigue sin conciliarse con F27.

### Registro de cambios en los datos

En esta fase **no se modificó ninguna celda ni columna de `data/persona.csv`** y no se generó otro CSV limpio. La corrida previa excluyó 125 columnas solo de su candidato de 150 columnas mediante ausencia global; no cambió el raw ni eliminó filas. Con la evidencia nueva se reconsidera la exclusión para cuatro variables: `s04b_13`, `s04c_17a`, `s04e_26_cod` y `s04e_28` deben conservarse en el maestro y evaluarse en sus universos indicados. Sus valores no se cambiaron. `s04f_31a` queda en revisión, sin filtro aplicado. El hash de origen sigue siendo `568e82e3039d991a1ee0d8e2056448f8c465c03ffa838330c4f1522dd77bddc8`.

La salida completa por columna está en [`comparison_all_columns.csv`](../data/proprosessing/output/20261004T171822Z_568e82e3039d_d3abfb0b5f/comparison_all_columns.csv), junto con [`profile_before.csv`](../data/proprosessing/output/20261004T171822Z_568e82e3039d_d3abfb0b5f/profile_before.csv), [`rule_execution_log.csv`](../data/proprosessing/output/20261004T171822Z_568e82e3039d_d3abfb0b5f/rule_execution_log.csv) y el [`diccionario de esa ejecución`](../data/proprosessing/output/20261004T171822Z_568e82e3039d_d3abfb0b5f/data_dictionary.md). Esos artefactos son evidencia del perfil, no una publicación de datos limpia.

## Observaciones del resultado L-80

La corrida conservó las 39.497 filas y retuvo 150 columnas; excluyó 125. La distribución de exclusiones fue:

| Grupo en el reporte | Columnas excluidas | Ausencia combinada global observada | Observación para interpretar |
| --- | ---: | ---: | --- |
| Sección 1: características del hogar y sus miembros | 9 | 95,5743–99,9544 % | El DDI indica «todos los miembros del hogar» para estas variables. La ausencia alta no se explica solo con ese rótulo; revisar filtros, estructura de roster, subpreguntas y codificación. |
| Sección 2: salud | 22 | 83,6545–99,9949 % | El grupo mezcla preguntas generales con preguntas para mujeres de 13–50 años, menores de 6 o menores de 5. El denominador global incluye personas fuera de varios universos. |
| Sección 3: educación | 7 | 92,8045–99,9063 % | Los universos del DDI incluyen personas desde 4 o 5 años. El total incluye niñas y niños por debajo de esas edades; revisar completitud en la población elegible. |
| Sección 4: empleo | 65 | 80,2871–99,9924 % | El DDI indica en general personas de 7 años o más, pero el acceso a detalles suele depender además de actividad/ocupación. Las subpreguntas pueden ser estructuralmente no aplicables. |
| Sección 5 y extensión local | 17 (16 F27 + 1 local) | 86,9155–99,9823 % | Hay universos por edad o «todos los miembros». `s05c_09e` es extensión local sin universo confirmado; no debe heredarse automáticamente el universo de campos similares. |
| Variables derivadas/geográficas asociadas | 5 | 93,1362–97,6555 % | Mezcla variables con universos de edad/sexo y medidas derivadas de empleo. No asumir que se calculan para toda persona ni que las ausencias son errores. |

Las tasas no deben compararse entre variables sin su denominador elegible. Un 95 % de ausencia global podría significar poca cobertura real, una pregunta para una subpoblación, un salto correcto o un problema de carga; el perfil por sí solo no distingue esas causas.

## Casos que requieren atención prioritaria

### `s04e_26_cod` — actividad de una ocupación secundaria

El DDI oficial identifica `s04e_26_cod` como clasificación de actividad económica y la coloca inmediatamente después de `s04e_25`, la pregunta «Además de la actividad mencionada anteriormente, ¿realizó otro trabajo durante la semana pasada?». La respuesta afirmativa de `s04e_25` define el filtro observable para revisar esta columna. Aunque el campo de universo de `s04e_26_cod` aparece vacío en el CSV de comparación, el cuestionario/DDI ofrece evidencia del salto por pregunta precedente. [La ficha de `s04e_25`](https://fm.ine.gob.bo/index.php/catalog/256/variable/F27/V2129?name=s04e_25) documenta respuestas sí/no; [la ficha de `s04e_26_cod`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2130?name=s04e_26_cod) identifica la clasificación y reporta 1.476 casos válidos para la copia publicada por ANDA.

Se contó el archivo local secuencialmente, sin imprimir registros: 39.497 filas; `s04e_25 = 1` en 1.356 filas; `s04e_25 = 2` en 18.123; token `NA` en 20.018. `s04e_26_cod` tiene 1.357 valores no vacíos/no `NA`: los 1.356 casos con `s04e_25 = 1` tienen un código y hay un único código registrado fuera de ese filtro. Así, el 96,5643 % global de ausencia se explica casi por completo porque la pregunta secundaria no aplica a la mayoría. Entre las 1.356 respuestas afirmativas locales, la tasa de ausencia del código es 0 %; **la columna debe conservarse para análisis de ocupación secundaria y no excluirse por L-80 global**. El valor no vacío fuera del filtro es una excepción de consistencia para investigar, no motivo para cambiarlo automáticamente.

La fuente oficial reporta 1.476 válidos para esta variable, frente a 1.357 no vacíos en el CSV local. Junto con la diferencia global de casos y columnas entre F27 y la copia local, esta divergencia respalda que no debemos asumir identidad de versiones. La regla `s04e_25 = 1` es una condición analítica provisional fuerte y coherente con la secuencia del cuestionario, pero no basta para declarar que el CSV local es el microdato F27 exacto.

La revisión de la misma rama encontró un nivel de salto más específico. Para `s04e_28`, el propio DDI incluye `s04e_27` como precondición, con respuestas 1, 2 o 7. En el archivo local, de las 1.356 personas con `s04e_25 = 1`, 138 pertenecen a esos códigos de trabajador; 137 tienen respuesta en `s04e_28` y 1 no (0,7246 % de ausencia entre elegibles), en lugar de 89,8968 % global. Es un ejemplo de universo reconstruido directamente del campo `pre_question_text` del diccionario.

En el campo de salario de ocupación secundaria `s04f_31a`, el conteo local observa 133 montos entre las 1.356 personas con segundo trabajo: 132 en códigos `s04e_27` 1/2 y uno en código 8; no observa montos para las restantes categorías 3/4/6/7. El patrón sugiere un universo de trabajadores remunerados, pero el DDI local no presenta precondición explícita para esa variable. Lo registramos como **hipótesis pendiente de cotejar con cuestionario**, no como regla de elegibilidad validada. Los seis registros de categoría 7 sin salario y la diferencia por código son evidencia para revisión; no se rellenan ni corrigen automáticamente.

**Recomendación:** conservarla y analizarla en una vista derivada filtrada por `s04e_25 = 1`, con una tabla de control de excepciones para códigos presentes fuera del filtro. La vista debe incluir su criterio de selección, denominador (1.356 en esta corrida local) y distribución de códigos; no reemplaza ni parte físicamente la fuente `persona.csv`.

### `s04c_17a` — monto de salario líquido

El porcentaje global es 81,3505 % y el campo fue excluido por L-80. Aunque el `universe` del DDI repite «personas de 7 años o más», el `pre_question_text` oficial agrega la condición esencial: asalariados que respondieron 1, 2 u 8 en la pregunta 12 de la Parte B (`s04b_12`). [La ficha F27 de la variable](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2078?name=s04c_17a) confirma ese filtro.

En el archivo local hay 7.370 personas en esos tres códigos; 7.366 tienen monto y 4 no (0,0543 % de ausencia entre elegibles). Casi toda la ausencia global corresponde a personas que no pertenecen al universo asalariado. La variable debe conservarse en el maestro y en análisis salariales; los 4 faltantes entre elegibles deben revisarse como no respuesta potencial. ANDA muestra 7.387 casos válidos para F27, frente a 7.366 locales, otra discrepancia que apoya una revisión de procedencia.

### `s04b_13` — administración del lugar de trabajo

Esta variable también supera L-80 global (82,1429 %). Su `pre_question_text` limita la pregunta a códigos 1, 2 o 7 de `s04b_12`; en la copia local hay 7.054 personas elegibles, 7.053 respondidas y 1 faltante (0,0142 %). Por tanto, no debe excluirse del análisis laboral por ausencia global. La ficha oficial [s04b_13](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2073?name=s04b_13) confirma el salto. El conteo F27 publicado registra 7.108 valores válidos, 55 más que la copia local.

### Salud y educación

Ejemplos de columnas excluidas del bloque de salud son `s02b_06b`–`s02b_14a` (universo DDI: mujeres de 13–50 años), `s02c_15` (menores de 6) y `s02d_16`–`s02d_17a` (menores de 5). Para educación, `s03a_03a` presenta 94,1844 % global y universo de personas de 4 años o más. En ambos grupos debe calcularse primero la elegibilidad usando una regla confirmada y edad/sexo confiables; comparar luego faltantes entre elegibles, no tratar todo `NA` fuera del universo como error.

## Inventario de columnas excluidas

Los códigos se listan para facilitar el cruce con los reportes por columna. La lista indica exclusión mecánica del candidato en esta corrida; **no recomienda eliminar esas variables del proyecto ni de todos los análisis**.

| Grupo | Columnas excluidas por L-80 |
| --- | --- |
| Sección 1 | `s01a_07_3`, `s01b_11b`, `s01b_11c`, `s01b_11d`, `s01b_11e`, `s01b_12`, `s01b_12e`, `s01b_13a`, `s01b_13b` |
| Salud | `s02a_01b`, `s02a_01e`, `s02a_02he`, `s02a_05`, `s02b_06b`, `s02b_07`, `s02b_08`, `s02b_09a`, `s02b_09b`, `s02b_10`, `s02b_10e`, `s02b_11`, `s02b_12a1`, `s02b_12a2`, `s02b_12b`, `s02b_13`, `s02b_14`, `s02b_14a`, `s02c_15`, `s02d_16`, `s02d_17`, `s02d_17a` |
| Educación | `s03a_03a`, `s03a_03c`, `s03a_05e`, `s03b_11`, `s03b_11e`, `s03b_12`, `s03c_17e` |
| Empleo | `s04a_02a`, `s04a_06e`, `s04a_07e`, `s04b_13`, `s04c_17a`, `s04c_17b`, `s04c_18a`, `s04c_18b`, `s04c_19aa`, `s04c_19ab`, `s04c_19ba`, `s04c_19bb`, `s04c_20a1`, `s04c_20a2`, `s04c_20b`, `s04c_20a_1`, `s04c_20a_2`, `s04c_21a`, `s04c_21a1`, `s04c_21a2`, `s04c_21b`, `s04c_21b1`, `s04c_21b2`, `s04c_21c`, `s04c_21c1`, `s04c_21c2`, `s04c_21d`, `s04c_21d1`, `s04c_21d2`, `s04c_21e`, `s04c_21e1`, `s04c_21e2`, `s04d_23ab`, `s04d_23bb`, `s04d_23cb`, `s04d_23db`, `s04d_23eb`, `s04d_23fb`, `s04d_23gb`, `s04d_23hb`, `s04d_24ba`, `s04d_24bb`, `s04d_24bc`, `s04e_26_cod`, `s04e_27`, `s04e_28`, `s04e_29`, `s04e_30a`, `s04e_30b`, `s04f_31a`, `s04f_31b`, `s04f_32a`, `s04f_32a1`, `s04f_32b`, `s04f_32b1`, `s04f_32c`, `s04f_32c1`, `s04f_33a`, `s04f_33b`, `s04f_34a`, `s04f_34b`, `s04f_34ba`, `s04f_34bb`, `s04f_34bc`, `s04f_36` |
| Ingresos no laborales | `s05a_01b`, `s05a_01e`, `s05a_01e0`, `s05a_01f`, `s05a_02ce`, `s05b_05ab`, `s05b_05bb`, `s05b_05cb`, `s05b_06ab`, `s05b_06ae`, `s05b_06bb`, `s05b_06be`, `s05c_08`, `s05c_09a`, `s05c_09b`, `s05c_10` |
| Extensión local sin universo confirmado | `s05c_09e` |
| Derivadas/geográficas | `caeb_os`, `shrs`, `yseclab`, `quienatenparto`, `educ_prev` |

## Siguiente revisión recomendada

La conciliación de procedencia/esquema se ejecutó y quedó registrada en [source-reconciliation-persona.md](source-reconciliation-persona.md). Su resultado es `SCHEMA_MISMATCH_PROVENANCE_UNRESOLVED`; hasta obtener origen/licencia y resolver diferencias no se promueven las máscaras locales a limpieza productiva.

Antes de regenerar un candidato o fijar una decisión de exclusión:

1. Reconciliar la edición/procedencia del CSV con F27 y determinar qué metadatos y filtros aplican a esta copia.
2. Para cada pregunta, documentar condición de elegibilidad, código de salto, tokens observados y campo(s) necesarios para reconstruir el universo.
3. Calcular `N elegible`, `N respondido`, `N faltante entre elegibles` y porcentaje sobre elegibles; reportar aparte los no elegibles.
4. Conservar variables valiosas aunque tengan alta ausencia global. Crear vistas/subconjuntos analíticos filtrados y reproducibles, manteniendo intactos CSV raw y catálogo completo.
5. Reaplicar L-80 solo con una política explícita: por ejemplo, excluir del **producto analítico general** columnas que superen el umbral entre elegibles, pero conservarlas en el dataset maestro y poder incorporarlas en un análisis focalizado.

Las primeras reglas laborales reconstruibles con respaldo directo en el DDI son: `s04b_13` elegible por `s04b_12 ∈ {1,2,7}`; `s04c_17a` por `s04b_12 ∈ {1,2,8}`; `s04e_26_cod` por `s04e_25 = 1`; y `s04e_28` por `s04e_25 = 1` además de `s04e_27 ∈ {1,2,7}`. Antes de ejecutarlas deben quedar versionadas y probarse sus máscaras, denominadores y valores fuera del filtro. Esta lista es un inicio, no cubre todas las columnas excluidas.

## Auditoría focalizada de fecundidad y salud materna

Esta auditoría cruza únicamente agregados de `data/persona.csv` con el diccionario y la ficha DDI F27. No se imprimieron registros individuales ni se modificaron celdas. El universo general del módulo es mujeres de 13 a 50 años; el cruce local con `s01a_02` (mujer=2) y `s01a_03` (edad) contiene 11.328 personas. La publicación oficial describe explícitamente ese universo y separa la Parte B de fecundidad del resto de salud.

| Campo(s) | Condición revisada en la copia local | Elegibles | Respondidos | Ausencia elegible | Interpretación / decisión |
| --- | --- | ---: | ---: | ---: | --- |
| `s02b_06b` | `s02b_06 ∈ {1,2}` (embarazada actualmente o alguna vez) | 6.456 | 6.456 | 0 | Conteo de embarazos observado para todas las respuestas afirmativas. Mantener; el universo condicional se apoya en la secuencia de preguntas y debe cotejarse con el cuestionario de la edición local. |
| `s02b_07` | `s02b_06 ∈ {1,2}` | 6.456 | 6.456 | 0 | Nacidos vivos; mantener. El cero válido cuando no hubo hijos debe distinguirse de vacío/NA. |
| `s02b_08`, `s02b_09a`, `s02b_09b` | `s02b_07 > 0` | 6.339 | 6.339 cada campo | 0 | Número de hijos actualmente vivos y mes/año del último nacido vivo. En la ficha oficial `s02b_09b`, el año tiene 6.226 válidos; la copia local observa 6.339, señal de que el esquema/edición no está conciliado. |
| `s02b_10` | Año de `s02b_09b`; dos cortes de universo discrepan | Véase abajo | Véase abajo | No fijar | No aplicar L-80 ni imputar por este campo hasta identificar la edición del cuestionario y resolver el corte temporal. |
| `s02b_10e` | `s02b_10 = 8` (otra persona) | 2 | 2 | 0 | Campo de especificación muy raro pero completo entre elegibles observados; conservar en el maestro. |
| `s02b_12a1`, `s02b_12b` | `s02b_11 = 1` (inscrita en BJA) según precondición DDI | 3.077 | 3.077 cada campo | 0 | Mantener las variables en su vista focalizada. `s02b_12a2`, condicionado localmente a `s02b_12a1 = 1`, tiene 407/407 respuestas. No confundir el denominador condicional con la ausencia global. |
| `s02b_13` | Patrón local: 3.077 valores, igual al conteo de BJA=1; sin precondición explícita | — | 3.077 observados | — | La coincidencia es una pista, no prueba de elegibilidad. No filtrar por BJA sin respaldo del cuestionario. |
| `s02b_14` | DDI: mujeres de 13–50; no hay pre-pregunta explícita | 11.328 | 2.077 | 9.251 | Los 2.077 observados se dividen en 382 sí y 1.695 no. No extrapolar automáticamente el universo de `s02b_13`; revisar el cuestionario. |
| `s02b_14a` | DDI oficial presenta pre-pregunta `s02b_13 = 1`; la ruta podría exigir además `s02b_14 = 1` | 2.077 bajo `s02b_13=1`; 382 bajo el filtro candidato `s02b_14=1` | 382 bajo ambos filtros locales | 1.695 bajo el filtro amplio; 0 bajo `s02b_14=1` | No tratar las 1.695 ausencias como no respuesta confirmada: los márgenes locales sugieren un salto tras “no” en `s02b_14`. Validar la intersección y el cuestionario antes de establecer denominador. |

### Conflicto concreto para `s02b_10`

El DDI local expresa “si nació a partir de 2017”; la ficha oficial F27 para `s02b_09b` indica que si nació después de 2020 se continúa con las preguntas siguientes y, en caso contrario, se salta a la pregunta 11. Esa es una discrepancia de contrato, no una invitación a escoger el umbral que produzca menos faltantes. La ficha oficial reporta 6.226 valores válidos para `s02b_09b`, frente a 6.339 en la copia local. Por ello la tasa de ausencia de `s02b_10` debe quedar como **no evaluable con regla confirmada** hasta reconciliar procedencia, versión del cuestionario y correspondencia de columnas. [Ficha oficial de `s02b_09b`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2012?name=s02b_09b) y [diccionario EH2025_Persona](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona).

Como sensibilidad descriptiva, con corte local `año ≥ 2017` hay 3.452 mujeres elegibles, 2.711 respuestas y 741 ausencias en `s02b_10` (21,4658 %). Con el corte de la ficha oficial, `año > 2020`, hay 1.856 elegibles, 1.716 respuestas y 140 ausencias (7,5431 %). La diferencia muestra que la decisión de corte cambia sustancialmente el diagnóstico. Ninguna tasa debe usarse como regla productiva hasta confirmar que el campo de año y la versión del cuestionario corresponden a F27.

### Interpretación de pre-preguntas y rutas

La auditoría inicial interpretó en exceso dos textos `pre_question_text` como posibles errores de alineación. La ficha oficial de `s02b_11` también presenta como pre-pregunta el conteo de nacidos vivos; la ficha oficial de `s02b_14a` también presenta la pregunta del subsidio del último embarazo. Por ello, no es correcto decir que esas cadenas sean un desajuste propio del JSON local. La presencia de texto anterior tampoco basta por sí sola para definir una máscara de elegibilidad: hay que determinar si describe contexto, un salto o ambas cosas. [Ficha oficial de `s02b_11`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2015?name=s02b_11) y [ficha oficial de `s02b_14a`](https://anda.ine.gob.bo/index.php/catalog/256/variable/F27/V2021?name=s02b_14a).

Para `s02b_14a`, la copia local tiene 382 valores de meses; `s02b_14` presenta 382 respuestas sí y 1.695 no. Los 382 casos con `s02b_14=1` tienen respuesta en `s02b_14a`. Esto sugiere que las 1.695 ausencias corresponden al salto de respuesta “no”, y no a 1.695 no respuestas. Como la pre-pregunta oficial de `s02b_14a` apunta a `s02b_13=1`, el cuestionario completo debe resolver cuál condición constituye el filtro operativo; hasta entonces el 81,6081 % calculado con el filtro más amplio no es una tasa confirmada de falta de respuesta.

Para `s02b_11`, la copia local contiene 6.456 respuestas dentro de `s02b_06 ∈ {1,2}`, con 3.077 sí y 3.379 no. El patrón local respalda esa puerta como hipótesis, pero debe cotejarse con el cuestionario; la ficha oficial reporta 6.334 válidos. El dato de pre-pregunta sobre nacidos vivos sí coincide entre la ficha oficial y el DDI local, así que no constituye evidencia de desalineación.

### Cambios celda por celda

En esta etapa focalizada no se cambió ningún valor ni tipo de dato. `data/persona.csv` permanece byte por byte como fuente de solo lectura; no se eliminó ninguna columna del raw, no se imputaron faltantes, no se recortaron extremos y no se reescribió el candidato previo. Las diferencias son decisiones documentales: los campos de fecundidad se conservan en el maestro; se calculan solo con universos documentados cuando el mapeo de la copia esté confirmado; los campos con desajuste se marcan para conciliación. Los conteos anteriores describen la copia y no certifican una corrección de sus respuestas.

### Trabajo aún requerido para cerrar la revisión de las 125 exclusiones

La matriz `universe-matrix-persona.csv` es un inventario completo de las 125 columnas que excluyó la corrida anterior, pero su etiqueta de estado debe considerarse preliminar salvo los cuatro casos laborales cotejados en la sección anterior. Faltan, en este orden: (1) conciliar versión/procedencia y mapa de nombres con F27; (2) auditar por pregunta los 22 campos de salud, incluyendo Parte A, atención infantil y bonos de niñez; (3) revisar las 7 variables de educación contra edades y saltos de matrícula/inasistencia; (4) revisar los restantes campos de empleo en módulos principal/secundario con sus universos encadenados; (5) auditar ingresos no laborales y variables derivadas; (6) incorporar denominadores, estados NA/vacío/cero/no aplica, excepciones fuera de filtro y enlaces de fuente a cada fila de matriz; (7) aprobar reglas versionadas y probarlas con datos sintéticos antes de crear una nueva versión candidata.

Mientras falte cualquiera de esos pasos, no se reejecuta la exclusión física L-80 ni se declara listo/publicado el conjunto maestro. El candidato de 150 columnas de la corrida `20261004T171822Z_568e82e3039d_d3abfb0b5f` continúa siendo candidato técnico no publicable, por aplicar ausencia global sin un mapa semántico completo.

| Variable | Regla de elegibilidad respaldada | Elegibles locales | Respondidos | Faltantes elegibles | Acción recomendada |
| --- | --- | ---: | ---: | ---: | --- |
| `s04b_13` | `s04b_12 ∈ {1,2,7}` | 7.054 | 7.053 | 1 (0,0142 %) | Retener; revisar 1 faltante |
| `s04c_17a` | `s04b_12 ∈ {1,2,8}` | 7.370 | 7.366 | 4 (0,0543 %) | Retener; revisar 4 faltantes |
| `s04e_26_cod` | `s04e_25 = 1` | 1.356 | 1.356 | 0 (0 %) | Retener; auditar 1 código fuera del filtro |
| `s04e_28` | `s04e_25 = 1` y `s04e_27 ∈ {1,2,7}` | 138 | 137 | 1 (0,7246 %) | Retener; revisar 1 faltante |
| `s04f_31a` | Posible condición salarial por categoría `s04e_27`; no confirmada en el DDI cargado | — | 133 valores observados entre 1.356 con segundo trabajo | — | No codificar filtro todavía; cotejar manual |

Hasta realizar esa revisión, el CSV candidato de 150 columnas debe tratarse como prototipo técnico y no como dataset universalmente limpio. Ninguna de las 125 exclusiones debe interpretarse como decisión definitiva de eliminar una variable.

## Evidencia y límites

El DDI describe explícitamente que la Parte E de empleo es «Ocupación Secundaria» y la pregunta `s04e_25` indaga si la persona realizó otro trabajo durante la semana pasada; la lista oficial ubica `s04e_26_cod` y luego variables de condiciones de esa otra ocupación. Véase [diccionario EH2025_Persona](https://anda.ine.gob.bo/index.php/catalog/256/data-dictionary/F27?file_name=EH2025_Persona). Los conteos locales se obtuvieron de `data/persona.csv` con lectura CSV citada/escapada, agregando solo cantidades, sin generar una extracción con identificadores o filas personales.

El hallazgo anterior permite corregir la interpretación de esta variable, pero **no autoriza aplicar `s04e_25 = 1` a todo el bloque laboral**: preguntas de administración, tipo de trabajador, remuneración y transferencias pueden requerir filtros adicionales. Hay que reconstruir esos saltos pregunta por pregunta antes de calcular faltantes elegibles del resto de las 125 columnas. La matriz CSV es el inventario trazable para continuar; una regla no se activa automáticamente solo porque el DDI contenga texto de precondición.

## Auditoría por universo — salud general/niñez y educación — 4 de octubre de 2026

Se revisaron agregados por máscara para las columnas de salud general, niñez y educación. El conteo se hizo sobre `data/persona.csv` con lectura CSV secuencial y campos citados; no se mostraron filas, identificadores ni textos libres. Las reglas identificadas en el DDI se contrastaron con los campos locales, pero la edición exacta del CSV sigue sin conciliarse con F27. “Regla cotejada” significa que la máscara mapeada coincide con el patrón agregado local, no que la procedencia esté resuelta ni que exista aprobación para transformar datos.

| Variable | Universo/máscara examinada | Elegibles | Respondidas | Faltantes elegibles | Resultado y decisión |
| --- | --- | ---: | ---: | ---: | --- |
| `s02a_01b` | Sin máscara confirmada; segunda cobertura médica | — | — | — | 39.497 filas globales; 74 observadas y 39.423 técnicamente ausentes. No interpretar la ausencia global como calidad sin hallar el salto de la segunda ranura. |
| `s02a_01e` | `s02a_01a=4` o `s02a_01b=4` | 2 | 2 | 0 | Coincide con “otro, especifique”; conservar. |
| `s02a_02he` | `s02a_02h=1` | 6 | 6 | 0 | Coincide con especificación de respuesta afirmativa; conservar. |
| `s02a_05` | Hipótesis: alguna dificultad en `s02a_04a..d` | 4.064 | 4.064 | 0 | Coincidencia exacta de patrón, pero DDI declara todos los miembros y no explicita filtro. Estado pendiente de confirmar en cuestionario; no fijar regla todavía. |
| `s02c_15` | Edad < 6 (`s01a_03`) | 3.434 | 3.434 | 0 | Universo de edad del DDI; conservar. |
| `s02d_16` | Edad < 5 (`s01a_03`) | 2.781 | 2.781 | 0 | Universo de edad del DDI; conservar. Respuestas locales: 1.734 sí y 1.047 no. |
| `s02d_17` | Edad < 5; hipótesis de respuesta solo si `s02d_16=1` | 2.781 | 1.734 | 1.047 | Los 1.734 registros con sí en la pregunta previa tienen respuesta; filtro plausible, pendiente de confirmar en cuestionario. |
| `s02d_17a` | Edad < 5; hipótesis de respuesta si `s02d_17=1` | 2.781 | 685 | 2.096 | La rama candidata contiene 685/685 respuestas; requiere confirmar salto y dominio. |
| `s03a_03a`, `s03a_03c` | Edad ≥ 4 y `s03a_02a ∈ {71,72,77,78}` | 2.297 cada una | 2.297 cada una | 0 | Mapeo local del pretexto DDI para niveles técnicos/cursos cortos; conservar y validar dominios aparte. |
| `s03a_05e` | `s03a_05=8` | 330 | 330 | 0 | Coincide con “otro, especifique”; conservar. |
| `s03b_11` | `s03b_10=4` (no asiste actualmente) | 2.842 | 2.842 | 0 | Coincide con el filtro de motivo de inasistencia; conservar. |
| `s03b_11e` | `s03b_11=5` | 23 | 23 | 0 | Coincide con especificación de “otro motivo”; conservar. |
| `s03b_12` | Máscara candidata `s03b_10=4` y `s03b_11 ∈ {3,4,5}` | 36 | 36 | 0 | Hay 40 valores locales observados para edad ≥4; cuatro caen fuera de la máscara candidata. El mapeo queda bloqueado hasta revisar el flujo exacto. |
| `s03c_17e` | Edad ≥5 y `s03c_17aa=7` o `s03c_17ab=7` | 205 | 205 | 0 | Coincide con especificación de “otro lugar”; conservar. |

Los estados de las 125 columnas que salieron del candidato por L-80 quedaron así: 66 universos pendientes, 30 precondiciones por mapear, 19 máscaras cotejadas provisionalmente con DDI, 4 reglas cotejadas frente a la copia local, 3 patrones locales pendientes de confirmación, 1 conflicto de procedencia (`s02b_10`), 1 hipótesis laboral pendiente y 1 extensión local sin contrato oficial. Los conteos están en [la matriz de universos](universe-matrix-persona.csv); los tres estados de patrón local incluyen `s02a_05`, `s02d_17` y `s02d_17a`.

La copia local no fue corregida ni se generó candidato nuevo. Los resultados son denominadores exploratorios de esta copia (39.497 filas), no estimaciones ponderadas ni validación de contenido. Próximo trabajo: cotejar las tres ramas hipotéticas y las cuatro excepciones de `s03b_12` con el cuestionario de la misma edición local; luego continuar con las columnas pendientes de empleo/ingresos y derivadas. No ejecutar exclusión L-80 sobre estos módulos hasta resolver el universo elegible.
