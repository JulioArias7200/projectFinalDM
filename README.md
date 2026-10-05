# Limpieza y bitácora JSON de `persona.csv`

Proyecto de minería de datos para preparar `data/persona.csv` mediante pipeline Python y una interfaz Flask. Por decisión del usuario, la persistencia de versiones y eventos usa JSON local; no depende de PostgreSQL. Las reglas se fundamentan en `curso/` y en el diccionario disponible. El archivo fuente es de solo lectura.

## Estado

La versión técnica validada `persona-317279aafe9023a2` conserva 39.497 filas y 275 columnas. Está publicada para uso interno mediante el catálogo JSON, con limitaciones semánticas explícitas. S-01 marcó como inválidas tres celdas con más de 168 horas semanales; S-02 normalizó 12.516 respuestas en 13 columnas abiertas definidas; la auditoría L-06 no encontró duplicados y no eliminó filas. No se imputaron datos ni se quitaron columnas por ausencia global.

La auditoría estructural y de artefactos pasó 10/10 controles; la suite tiene 11 pruebas aprobadas. Esto no certifica la semántica de las 275 columnas: `totper`, dominios, universos y discrepancias de procedencia siguen documentados como pendientes. La publicación es interna y no respalda inferencias oficiales.

- CSV publicado: `data/proprosessing/versions/persona-317279aafe9023a2/persona_clean_master.csv`
- Parquet de la misma versión: `data/proprosessing/versions/persona-317279aafe9023a2/persona_clean_master.parquet`
- Catálogo y bitácora JSON: `data/audit_log.json`
- Validación y muestreo: `docs/final-validation-sampling-persona.md`
- Dictamen semántico: `docs/semantic-cleaning-audit.md`

## Guía de Ejecución Paso a Paso (Desde Cero)

Para poner en marcha el proyecto localmente en cualquier máquina limpia (Windows, Linux o macOS), siga estos pasos:

### 1. Clonar el Repositorio

Abra su terminal y clone el repositorio desde GitHub:

```bash
git clone https://github.com/JulioArias7200/projectFinalDM.git
cd projectFinalDM
```

### 2. Crear y Activar un Entorno Virtual

Se recomienda usar Python 3.10, 3.11 o 3.12:

- **En Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(Si PowerShell restringe scripts, ejecute antes: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **En Linux o macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar las Dependencias

Instale todas las librerías necesarias especificadas en `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verificar la Suite de Pruebas Unitarias

Antes de iniciar la aplicación, valide que la integridad de las reglas, los esquemas y los contratos JSON se cumplan al 100%:

```bash
python -m pytest tests/ -v
```

*(Debe confirmar 16 pruebas aprobadas: `16 passed`)*.

### 5. Iniciar la Aplicación Web (Dashboard Flask)

Ejecute el servidor de desarrollo local:

- **Opción recomendada (directo con Python):**
  ```powershell
  python dashboard/app.py
  ```

- **O utilizando el runner de Flask:**
  ```powershell
  flask --app dashboard.app run --port 5000
  ```

Abra su navegador web e ingrese a la siguiente dirección:
👉 **[http://127.0.0.1:5000/dashboard/](http://127.0.0.1:5000/dashboard/)**

---

### 6. Ejecución del Pipeline de Limpieza desde Cero (Opcional)

Si desea regenerar el proceso de limpieza y validación censal a partir del microdato fuente de solo lectura (`data/persona.csv`):

1. **Ejecutar el pipeline de transformación y auditoría de reglas (L-01 a L-12, S-01, S-02):**
   ```powershell
   python data/proprosessing/preprocessing.py
   ```
   *Esto generará una carpeta candidata en `data/proprosessing/output/<RUN_ID>/` con los perfiles y vistas.*

2. **Publicar la versión validada en el catálogo atómico JSON:**
   ```powershell
   python data/proprosessing/publish_validated_candidate.py --candidate data/proprosessing/output/<RUN_ID>
   ```
   *La publicación valida hashes criptográficos SHA-256, genera la copia inmutable en `versions/` y actualiza atómicamente el puntero en `data/audit_log.json`.*

---

### 7. Despliegue en la Nube (Producción en Render)

El proyecto cuenta con configuración lista para despliegues en la nube:
* **Plataforma Activa:** [https://projectfinaldm.onrender.com/dashboard/](https://projectfinaldm.onrender.com/dashboard/)
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `gunicorn wsgi:app`

## Alcance semántico

El usuario confirmó `persona.csv` como el único microdato de trabajo. El diccionario F27 disponible no coincide exactamente en casos/columnas con esta copia; `totper` es una extensión local y no tiene definición confirmada. Las observaciones sin decisión concluyente se preservan. Ver [metodología](docs/cleaning-methodology.md), [contrato](docs/data-contract.md), [progreso](docs/progress.md) y [arquitectura JSON](docs/architecture.md).

## Documentación

| Documento | Contenido |
|---|---|
| [Requisitos](docs/requirements.md) | Comportamiento esperado y reglas de datos |
| [Criterios de aceptación](docs/acceptance-criteria.md) | Verificaciones y estado |
| [Trazabilidad](docs/versioning-and-audit.md) | Versiones y eventos persistidos en JSON |
| [Análisis exploratorio](docs/exploratory-analysis-persona.md) | Perfiles y análisis por variable/universo |
| [Escenarios de prueba](docs/test-scenarios.md) | Casos sintéticos y reales documentados |

La próxima etapa del dashboard está especificada en [la propuesta de análisis por universos](docs/dashboard-universe-plan.md). Es una decisión documentada, todavía no implementada como cálculos estadísticos dinámicos.

## Límites de operación

El catálogo JSON está pensado para uso local y una instancia de aplicación. Es una escritura atómica de un archivo, no una base transaccional distribuida. Protege eventos contra edición/borrado desde el servicio, pero permisos del sistema operativo y copias de seguridad del directorio `data/` siguen siendo responsabilidad del entorno. El dashboard no cuenta todavía con autenticación completa ni aprobación multiusuario de cambios.
