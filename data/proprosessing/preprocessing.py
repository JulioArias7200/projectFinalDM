# %% [markdown]
# The only input is `data/persona.csv`; no supplementary input files are loaded.
# # Preprocesamiento de `persona.csv`
#
# Este pipeline implementa un diagnóstico y una limpieza conservadora basados en
# `curso/02_tipos_de_datos.md`, `curso/03_estadistica_descriptiva.md`,
# `curso/05_preparacion_de_datos.md`, `curso/10_metodologias.md` y las reglas
# de `docs/cleaning-methodology.md`.
#
# Cada regla registra su justificación y su efecto. El raw se lee sin sobrescribirlo.
# Las alertas IQR describen candidatos a atípicos; no eliminan observaciones.
# Las definiciones que no están confirmadas en el diccionario se marcan como pendientes.

# %% [markdown]
# ## 1. Imports y configuración
#
# Requisitos previstos: Python 3.11+, pandas, NumPy, Matplotlib y PyArrow.
# Ejecuta este archivo desde la raíz del proyecto o desde su directorio.
# The >80% threshold is an audit flag only: the master candidate retains all
# source columns because global absence conflates questionnaire skips and nonresponse.

# %%
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import re
import sys
import warnings
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def find_project_root(start: Path | None = None) -> Path:
    """Find the repository root without embedding a machine-specific path."""
    candidates: list[Path] = []
    if start is not None:
        candidates.append(start.resolve())
    if "__file__" in globals():
        candidates.append(Path(__file__).resolve().parent)
    candidates.append(Path.cwd().resolve())
    for candidate in candidates:
        for parent in (candidate, *candidate.parents):
            if (parent / "README.md").is_file() and (parent / "curso").is_dir():
                return parent
    raise FileNotFoundError(
        "No encontré la raíz del proyecto. Ejecuta desde la carpeta del proyecto."
    )


@dataclass(frozen=True)
class PipelineConfig:
    dataset_id: str = "EH2025_Persona"
    source_relpath: str = "data/persona.csv"
    output_relpath: str = "data/proprosessing/output"
    encoding: str = "utf-8-sig"
    delimiter: str = ","
    iqr_multiplier: float = 1.5
    minimum_numeric_values: int = 5
    maximum_categories_in_plot: int = 100
    minimum_display_count: int = 10
    # Drop non-key variables only when >80% of rows are missing or malformed.
    incomplete_or_malformed_drop_pct: float = 80.0
    # Whitespace normalization is syntactic and is excluded from person keys.
    normalize_outer_whitespace: bool = True
    id_columns: tuple[str, ...] = ("folio", "nro", "upm")
    key_columns: tuple[str, ...] = ("folio", "nro")
    # No domain-dependent, imputation, or survey-weight rule is enabled.
    apply_domain_rules: bool = False
    apply_imputation: bool = False


CONFIG = PipelineConfig()
PROJECT_ROOT = find_project_root()
SOURCE_PATH = PROJECT_ROOT / CONFIG.source_relpath
OUTPUT_ROOT = PROJECT_ROOT / CONFIG.output_relpath


# %% [markdown]
# ## 2. Catálogo semántico provisional
#
# El diccionario vecino resume grupos de preguntas y describe algunas columnas.
# Este mapa registra solo definiciones puntuales disponibles allí. No completa
# códigos ni universos ausentes: esos detalles deben cotejarse con el cuestionario
# de la edición exacta. Las demás variables reciben una descripción pendiente.

# %%
KNOWN_VARIABLES: dict[str, dict[str, str]] = {
    "folio": {"description": "Identificador de vivienda/hogar.", "level": "Hogar", "kind": "Identificador"},
    "area": {"description": "Área geográfica (1 urbana, 2 rural, según diccionario local).", "level": "Persona/hogar", "kind": "Categórica nominal codificada"},
    "depto": {"description": "Código de departamento según diccionario local.", "level": "Persona/hogar", "kind": "Categórica nominal codificada"},
    "nro": {"description": "Número de orden del integrante del hogar.", "level": "Persona", "kind": "Identificador"},
    "upm": {"description": "Unidad Primaria de Muestreo.", "level": "Diseño muestral", "kind": "Identificador/diseño"},
    "estrato": {"description": "Estrato de diseño muestral.", "level": "Diseño muestral", "kind": "Categórica/diseño"},
    "factor": {"description": "Factor de expansión de la persona, según diccionario local.", "level": "Persona", "kind": "Cuantitativa ponderador candidato"},
    "s01a_02": {"description": "Sexo registrado del individuo.", "level": "Persona", "kind": "Categórica; códigos pendientes"},
    "s01a_03": {"description": "Edad cumplida en años.", "level": "Persona", "kind": "Cuantitativa discreta; unidad años"},
    "s01a_04a": {"description": "Día de nacimiento.", "level": "Persona", "kind": "Fecha/campo discreto"},
    "s01a_04b": {"description": "Mes de nacimiento.", "level": "Persona", "kind": "Fecha/campo discreto"},
    "s01a_04c": {"description": "Año de nacimiento.", "level": "Persona", "kind": "Fecha/campo discreto"},
    "condact": {"description": "Condición de actividad (1 ocupado, 2 desocupado, 3 inactivo, según diccionario local).", "level": "Persona", "kind": "Categórica nominal codificada"},
    "phrs": {"description": "Horas semanales de la ocupación principal.", "level": "Persona", "kind": "Cuantitativa; unidad por confirmar"},
    "shrs": {"description": "Horas semanales de la ocupación secundaria.", "level": "Persona", "kind": "Cuantitativa; unidad por confirmar"},
    "tothrs": {"description": "Total de horas trabajadas por semana, según diccionario local.", "level": "Persona", "kind": "Cuantitativa; unidad por confirmar"},
    "totper": {"description": "Total de personas que habitan en el hogar.", "level": "Hogar", "kind": "Conteo"},
    "yprilab": {"description": "Ingreso laboral neto de ocupación principal.", "level": "Persona", "kind": "Monetaria; unidad/periodo pendientes"},
    "yseclab": {"description": "Ingreso laboral neto de ocupación secundaria.", "level": "Persona", "kind": "Monetaria; unidad/periodo pendientes"},
    "ylab": {"description": "Ingreso laboral individual.", "level": "Persona", "kind": "Monetaria; unidad/periodo pendientes"},
    "ynolab": {"description": "Ingreso no laboral individual.", "level": "Persona", "kind": "Monetaria; unidad/periodo pendientes"},
    "yper": {"description": "Ingreso total personal; relación exacta pendiente de verificar.", "level": "Persona", "kind": "Monetaria; unidad/periodo pendientes"},
    "yhog": {"description": "Ingreso total del hogar.", "level": "Hogar", "kind": "Monetaria; unidad/periodo pendientes"},
    "yhogpc": {"description": "Ingreso per cápita del hogar, según diccionario local.", "level": "Hogar", "kind": "Monetaria; unidad/periodo pendientes"},
    "z": {"description": "Línea monetaria de pobreza moderada.", "level": "Hogar; confirmar", "kind": "Monetaria; unidad/periodo pendientes"},
    "zext": {"description": "Línea monetaria de pobreza extrema.", "level": "Hogar; confirmar", "kind": "Monetaria; unidad/periodo pendientes"},
    "p0": {"description": "Indicador FGT de incidencia de pobreza moderada.", "level": "Hogar; confirmar", "kind": "Cuantitativa derivada; fórmula/edición pendientes"},
    "p1": {"description": "Indicador FGT de brecha de pobreza moderada.", "level": "Hogar; confirmar", "kind": "Cuantitativa derivada; fórmula/edición pendientes"},
    "p2": {"description": "Indicador FGT de severidad de pobreza moderada.", "level": "Hogar; confirmar", "kind": "Cuantitativa derivada; fórmula/edición pendientes"},
    "pext0": {"description": "Indicador FGT de incidencia de pobreza extrema.", "level": "Hogar; confirmar", "kind": "Cuantitativa derivada; fórmula/edición pendientes"},
    "pext1": {"description": "Indicador FGT de brecha de pobreza extrema.", "level": "Hogar; confirmar", "kind": "Cuantitativa derivada; fórmula/edición pendientes"},
    "pext2": {"description": "Indicador FGT de severidad de pobreza extrema.", "level": "Hogar; confirmar", "kind": "Cuantitativa derivada; fórmula/edición pendientes"},
    "niv_ed": {"description": "Nivel educativo alcanzado; códigos por cotejar.", "level": "Persona", "kind": "Categórica ordinal codificada"},
    "niv_ed_g": {"description": "Nivel educativo alcanzado agrupado; códigos por cotejar.", "level": "Persona", "kind": "Categórica ordinal codificada"},
    "aestudio": {"description": "Años efectivos de estudio acumulados.", "level": "Persona", "kind": "Cuantitativa discreta"},
    "cmasi": {"description": "Condición de asistencia escolar actual.", "level": "Persona elegible; confirmar", "kind": "Categórica; códigos pendientes"},
}

SECTION_PREFIXES = (
    ("s01", "Sección 1: características sociodemográficas"),
    ("s02", "Sección 2: salud y discapacidad"),
    ("s03", "Sección 3: educación"),
    ("s04", "Sección 4: empleo y mercado laboral"),
    ("s05", "Sección 5: ingresos no laborales"),
)
SENSITIVE_PREFIXES = ("s02", "s04", "s05", "y", "z", "p", "folio")


DATA_DICTIONARY_PATH = PROJECT_ROOT / "data" / "proprosessing" / "data_dictionary.json"


def load_data_dictionary(path: Path) -> dict[str, dict[str, str]]:
    """Load the canonical JSON dictionary used by reports and graph labels."""
    if not path.is_file():
        raise FileNotFoundError(f"No se encontro el diccionario JSON: {path}")
    document = json.loads(path.read_text(encoding="utf-8-sig"))
    # `variables` mirrors the official INE F27 dictionary. Local CSV columns
    # absent from that release are kept separately and merged only for labels.
    variables = {
        **document.get("variables", {}),
        **document.get("local_extensions", {}),
    }
    if not isinstance(variables, dict) or not variables:
        raise ValueError(f"El diccionario JSON no contiene un objeto 'variables': {path}")
    entries: dict[str, dict[str, str]] = {}
    for name, definition in variables.items():
        if not isinstance(definition, dict) or not definition.get("description"):
            raise ValueError(f"La definicion JSON de {name} no contiene una descripcion.")
        description = str(definition["description"])
        entries[str(name)] = {
            "column": str(name),
            "description": description,
            "display_name": str(definition.get("display_name") or f"{description} ({name})"),
            "section": str(definition.get("section", "Pendiente de confirmar")),
            "level": str(definition.get("level", "Pendiente de confirmar")),
            "kind": str(definition.get("semantic_type", "Pendiente de confirmar")),
            "sensitivity": str(definition.get("sensitivity", "Clasificar antes de compartir")),
            "definition_status": str(definition.get("definition_status", "pendiente de confirmar")),
            "universe": str((definition.get("official") or {}).get("universe", "No especificado en el diccionario")),
            "valid_ranges": (definition.get("official") or {}).get("valid_ranges", {}),
            "categories": (definition.get("official") or {}).get("categories", []),
        }
    return entries


DATA_DICTIONARY = load_data_dictionary(DATA_DICTIONARY_PATH)

def column_metadata(column: str) -> dict[str, str]:
    if column in DATA_DICTIONARY:
        entry = DATA_DICTIONARY[column].copy()
    elif column in KNOWN_VARIABLES:
        entry = KNOWN_VARIABLES[column].copy()
        entry["definition_status"] = "provisional: cotejar con cuestionario de la edición"
    else:
        section = next((name for prefix, name in SECTION_PREFIXES if column.startswith(prefix)), None)
        entry = {
            "description": (
                f"Campo de cuestionario de {section.lower()}; verificar la pregunta exacta "
                "en el cuestionario de la edición antes de interpretar o transformar."
                if section else
                "Descripción y dominio pendientes de confirmar con el diccionario/cuestionario de la edición."
            ),
            "level": "Pendiente de confirmar",
            "kind": "Tipo semántico pendiente; se informa el formato observado",
            "definition_status": "pendiente de confirmar",
            "universe": "No especificado; confirmar con cuestionario",
            "valid_ranges": {},
            "categories": [],
        }
    entry.setdefault("definition_status", "provisional: cotejar con cuestionario de la edición")
    entry.setdefault("level", "Pendiente de confirmar")
    entry.setdefault("kind", "Pendiente de confirmar")
    entry.setdefault("section", "Pendiente de confirmar")
    entry.setdefault("universe", "No especificado; confirmar con cuestionario")
    entry.setdefault("valid_ranges", {})
    entry.setdefault("categories", [])
    entry.setdefault("display_name", f"{entry['description']} ({column})")
    if "sensitivity" not in entry:
        entry["sensitivity"] = (
            "restringida o potencialmente sensible" if column.startswith(SENSITIVE_PREFIXES)
            else "revisar clasificación antes de compartir"
        )
    if column in {"area", "depto", "upm", "estrato"} and column not in DATA_DICTIONARY:
        entry["sensitivity"] = "geográfica o de diseño muestral; restringir detalle"
    entry["column"] = column
    return entry


def has_confirmed_numeric_semantics(column: str) -> bool:
    """Do not calculate means or IQR for numeric category codes or unknown fields."""
    kind = column_metadata(column)["kind"]
    return kind.startswith(("Cuantitativa", "Monetaria", "Conteo"))


def allows_outer_whitespace_normalization(column: str) -> bool:
    """Trim documented coded/numeric fields, not open-text answers."""
    kind = column_metadata(column)["kind"].casefold()
    markers = (
        "categórica", "categorica", "ordinal", "cuantitativa", "monetaria",
        "conteo", "identificador / diseño", "identificador/diseño",
    )
    return any(marker in kind for marker in markers)


def dictionary_schema_reconciliation(header: list[str]) -> dict[str, Any]:
    """Compare local CSV columns with official F27 variables and extensions."""
    document = json.loads(DATA_DICTIONARY_PATH.read_text(encoding="utf-8-sig"))
    official = set(document.get("variables", {}))
    local = set(header)
    extensions = set(document.get("local_extensions", {}))
    return {
        "dataset_id": document.get("dataset", {}).get("dataset_id"),
        "official_file_id": document.get("dataset", {}).get("official_file_id"),
        "official_case_count": document.get("dataset", {}).get("official_case_count"),
        "official_variable_count": len(official),
        "csv_variable_count": len(local),
        "official_only_columns": sorted(official - local),
        "csv_only_columns": sorted(local - official),
        "dictionary_local_extensions": sorted(extensions),
        "exact_schema_match": official == local,
        "merge_status": "not merged; person-level CSV only",
    }


# %% [markdown]
# ## 3. Conservar y leer el original
#
# Comprobamos la estructura antes de que pandas pueda renombrar encabezados
# duplicados. `NA`, vacío y cero se conservan como texto durante la lectura.

# %%
def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_csv_structure(path: Path, encoding: str, delimiter: str) -> tuple[list[str], int]:
    with path.open("r", encoding=encoding, newline="") as stream:
        reader = csv.reader(stream, delimiter=delimiter, strict=True)
        try:
            header = next(reader)
        except StopIteration as error:
            raise ValueError("El archivo CSV está vacío.") from error
        duplicates = [name for name, count in Counter(header).items() if count > 1]
        if duplicates:
            raise ValueError(f"Encabezados repetidos: {len(duplicates)}. Revisar el contrato antes de continuar.")
        if any(name == "" for name in header):
            raise ValueError("El CSV contiene encabezados vacíos; no se asignarán nombres automáticamente.")
        expected_width = len(header)
        record_count = 0
        for line_number, row in enumerate(reader, start=2):
            if len(row) != expected_width:
                raise ValueError(
                    f"Registro CSV con {len(row)} campos; se esperaban {expected_width}. "
                    f"Número aproximado de línea física: {line_number}."
                )
            record_count += 1
    return header, record_count


def read_raw_csv(path: Path, config: PipelineConfig) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {path}")
    header, expected_rows = inspect_csv_structure(path, config.encoding, config.delimiter)
    frame = pd.read_csv(
        path,
        sep=config.delimiter,
        encoding=config.encoding,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
        skip_blank_lines=False,
        on_bad_lines="error",
        low_memory=False,
    )
    if list(frame.columns) != header or len(frame) != expected_rows:
        raise ValueError("El conteo o encabezado pandas no coincide con el recorrido estructural del CSV.")
    metadata = {
        "original_name": path.name,
        "source_relpath": path.relative_to(PROJECT_ROOT).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "encoding": config.encoding,
        "encoding_status": "configuración solicitada; pendiente cotejo de procedencia",
        "delimiter": config.delimiter,
        "rows": int(frame.shape[0]),
        "columns": int(frame.shape[1]),
        "header": header,
    }
    return frame, metadata


# %% [markdown]
# ## 4. Herramientas de perfil por columna
#
# Se informan los tokens por separado. No se convierten en nulos ni se imputan.
# Los valores se analizan como magnitudes solo si todos los valores no vacíos
# se convierten sin pérdida a números finitos y la columna no es identificadora.

# %%
MISSING_LITERALS = {"NA", "N/A", "NULL", "null", "NaN", "nan"}


def missing_mask(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return text.isna() | text.eq("") | text.isin(MISSING_LITERALS)


def malformed_registration_mask(column: str, series: pd.Series) -> tuple[pd.Series, str]:
    """Count only format/domain errors supported by declared column semantics."""
    missing = missing_mask(series)
    text = series.astype("string").str.strip()
    if column == "area":
        return (~missing & ~text.isin({"1", "2"})), "domain confirmed by local dictionary"
    if column == "depto":
        return (~missing & ~text.isin({str(value) for value in range(1, 10)})), "domain confirmed by local dictionary"
    if has_confirmed_numeric_semantics(column):
        parsed = pd.to_numeric(text.mask(missing), errors="coerce")
        finite = pd.Series(
            np.isfinite(parsed.to_numpy(dtype="float64", na_value=np.nan)), index=series.index
        )
        malformed = ~missing & (parsed.isna() | ~finite)
        return malformed, "numeric format checked; range/domain not confirmed"
    return pd.Series(False, index=series.index), "not evaluated: variable domain is not confirmed"


def token_counts(series: pd.Series) -> dict[str, int]:
    text = series.astype("string")
    blank = text.eq("").fillna(False)
    stripped = text.str.strip()
    whitespace_only = (~blank & stripped.eq("")).fillna(False)
    literal_na = stripped.isin(MISSING_LITERALS) & ~blank & ~whitespace_only
    exact_zero = stripped.isin({"0", "+0", "-0"})
    return {
        "empty_count": int(blank.sum()),
        "whitespace_only_count": int(whitespace_only.sum()),
        "literal_missing_token_count": int(literal_na.sum()),
        "exact_zero_count": int(exact_zero.sum()),
    }


def numeric_view(series: pd.Series, minimum_values: int, identifier: bool) -> pd.Series | None:
    if identifier:
        return None
    text = series.astype("string").str.strip()
    present = text.notna() & text.ne("") & ~text.isin(MISSING_LITERALS)
    values = text[present]
    if len(values) < minimum_values:
        return None
    parsed = pd.to_numeric(values, errors="coerce")
    if parsed.isna().any():
        return None
    finite = np.isfinite(parsed.to_numpy(dtype="float64", na_value=np.nan))
    if not finite.all():
        return None
    result = pd.Series(np.nan, index=series.index, dtype="float64")
    result.loc[values.index] = parsed.astype("float64")
    return result


def iqr_summary(values: pd.Series, multiplier: float) -> dict[str, Any]:
    clean = values.dropna().astype("float64")
    if clean.empty:
        return {"outlier_method": "IQR", "outlier_status": "sin valores numéricos", "outlier_count": 0,
                "outlier_pct_valid": np.nan, "lower_fence": np.nan, "upper_fence": np.nan}
    q1, median, q3 = (float(clean.quantile(q)) for q in (0.25, 0.5, 0.75))
    iqr = q3 - q1
    if len(clean) < 5:
        return {"outlier_method": f"IQR exploratorio × {multiplier:g}", "outlier_status": "muy pocos valores para evaluar",
                "outlier_count": 0, "outlier_pct_valid": np.nan, "lower_fence": np.nan, "upper_fence": np.nan,
                "q1": q1, "median": median, "q3": q3, "iqr": iqr}
    if math.isclose(iqr, 0.0):
        return {"outlier_method": f"IQR exploratorio × {multiplier:g}", "outlier_status": "IQR cero; alertas no clasificadas automáticamente",
                "outlier_count": 0, "outlier_pct_valid": np.nan, "lower_fence": np.nan, "upper_fence": np.nan,
                "q1": q1, "median": median, "q3": q3, "iqr": iqr}
    lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
    outliers = (clean < lower) | (clean > upper)
    return {"outlier_method": f"IQR exploratorio × {multiplier:g}", "outlier_status": "alerta estadística; requiere revisión semántica",
            "outlier_count": int(outliers.sum()), "outlier_pct_valid": float(outliers.mean() * 100),
            "lower_fence": lower, "upper_fence": upper, "q1": q1, "median": median, "q3": q3, "iqr": iqr}


def profile_column(name: str, series: pd.Series, config: PipelineConfig) -> dict[str, Any]:
    n = len(series)
    metadata = column_metadata(name)
    tokens = token_counts(series)
    missing = missing_mask(series)
    malformed, malformed_check_status = malformed_registration_mask(name, series)
    malformed_count = int(malformed.sum())
    bad_count = int(missing.sum()) + malformed_count
    bad_pct = (bad_count / n * 100) if n else np.nan
    identifier = name in config.id_columns
    text = series.astype("string")
    present = text.ne("") & ~text.str.strip().isin(MISSING_LITERALS) & text.str.strip().ne("")
    values = text[present]
    unique = int(values.nunique(dropna=True))
    semantic = metadata["kind"].casefold()
    high_cardinality_categorical = unique > 30 and ("categórica" in semantic or "categorica" in semantic)
    quality_alert = (
        f"REVISAR: {unique} valores distintos en una variable categórica; cotejar códigos y alineación con el cuestionario."
        if high_cardinality_categorical else "Sin alerta heurística de cardinalidad."
    )
    numeric_candidate = numeric_view(series, config.minimum_numeric_values, identifier)
    numeric = numeric_candidate if has_confirmed_numeric_semantics(name) else None
    result: dict[str, Any] = {
        "column": name,
        "display_name": metadata["display_name"],
        "description": metadata["description"],
        "section": metadata["section"],
        "universe": metadata["universe"],
        "rows": n,
        "valid_non_missing_candidates": int(len(values)),
        "missing_pct_of_rows": round((n - len(values)) / n * 100, 4) if n else np.nan,
        "missing_count": int(missing.sum()),
        "malformed_count": malformed_count,
        "malformed_pct_of_rows": round(malformed_count / n * 100, 4) if n else np.nan,
        "malformed_check_status": malformed_check_status,
        "incomplete_or_malformed_count": bad_count,
        "incomplete_or_malformed_pct": round(bad_pct, 4) if n else np.nan,
        "drop_threshold_pct": config.incomplete_or_malformed_drop_pct,
        "processing_action": (
            "RETAIN IN MASTER; >80% global absence is an audit flag, not a deletion rule"
            if bad_pct > config.incomplete_or_malformed_drop_pct
            else "Retain in master; profile and review documented format/domain and outlier alerts"
        ),
        **tokens,
        "distinct_non_missing": unique,
        "distinct_ratio": round(unique / len(values), 6) if len(values) else np.nan,
        "observed_type": (
            "numeric-like; semantic quantitative type provisionally documented" if numeric is not None
            else "numeric-like candidate; no numeric summary until semantics are confirmed" if numeric_candidate is not None
            else "text/categorical or mixed"
        ),
        "semantic_type": metadata["kind"],
        "quality_alert": quality_alert,
        "definition_status": metadata["definition_status"],
        "sensitive": name.startswith(SENSITIVE_PREFIXES),
    }
    if numeric is not None:
        numeric_valid = numeric.dropna()
        result.update({
            "numeric_valid_count": int(len(numeric_valid)),
            "minimum": float(numeric_valid.min()) if len(numeric_valid) else np.nan,
            "maximum": float(numeric_valid.max()) if len(numeric_valid) else np.nan,
            "mean": float(numeric_valid.mean()) if len(numeric_valid) else np.nan,
            "std": float(numeric_valid.std(ddof=1)) if len(numeric_valid) > 1 else np.nan,
            "q1": float(numeric_valid.quantile(.25)) if len(numeric_valid) else np.nan,
            "median": float(numeric_valid.median()) if len(numeric_valid) else np.nan,
            "q3": float(numeric_valid.quantile(.75)) if len(numeric_valid) else np.nan,
            **iqr_summary(numeric_valid, config.iqr_multiplier),
        })
    else:
        result.update({"numeric_valid_count": 0, "outlier_method": "No aplicable: no es magnitud numérica confirmada",
                       "outlier_status": "revisar códigos/categorías con el diccionario", "outlier_count": 0,
                       "outlier_pct_valid": np.nan, "lower_fence": np.nan, "upper_fence": np.nan})
    return result


def profile_frame(frame: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
    return pd.DataFrame([profile_column(column, frame[column], config) for column in frame.columns])


# %% [markdown]
# ## 5. Limpieza conservadora y perfil inicial/final
#
# Se conserva el esquema completo. El porcentaje global >80% se reporta como
# alerta, nunca como criterio para borrar una variable de la tabla maestra.
# La única transformación automática es quitar espacios exteriores de campos
# categóricos/magnitudes tipados por el diccionario; IDs, texto libre, tokens
# de ausencia, filas y extremos se preservan. La clave se valida y un fallo
# detiene la generación de la versión derivada.
# %%
def clean_frame(
    raw: pd.DataFrame, config: PipelineConfig
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Apply declared rules and return cell-level semantic edits separately."""
    cleaned = raw.copy(deep=True)
    changes: list[dict[str, Any]] = []
    semantic_changes: list[dict[str, Any]] = []
    if config.normalize_outer_whitespace:
        for column in cleaned.columns:
            if column in config.id_columns or not allows_outer_whitespace_normalization(column):
                continue
            original = cleaned[column].astype("string")
            normalized = original.str.strip()
            changed = (original != normalized).fillna(False)
            count = int(changed.sum())
            if count:
                cleaned[column] = normalized
            changes.append({
                "rule_id": "L-03",
                "rule_version": "2",
                "column": column,
                "rule": "Trim outer whitespace only in dictionary-typed coded/numeric fields; preserve identifiers, free text, missing tokens, and internal content",
                "theory_ref": "curso/02_tipos_de_datos.md + curso/05_preparacion_de_datos.md: type-aware transformation",
                "rows_examined": int(len(raw)),
                "cells_changed": count,
                "status": "applied" if count else "no changes",
            })
    # The official DDI describes these fields as average work hours per week.
    # More than 168 hours in one week is physically impossible. Preserve the
    # source row and mark only the invalid measurement missing, with cell audit.
    for column in ("phrs", "shrs", "tothrs"):
        if column not in cleaned.columns:
            continue
        numeric = pd.to_numeric(cleaned[column], errors="coerce")
        impossible = numeric.gt(168) & cleaned[column].notna()
        positions = np.flatnonzero(impossible.to_numpy())
        for position in positions:
            semantic_changes.append({
                "row_number_1based": int(position + 2),  # CSV row includes header
                "column": column,
                "old_value": str(cleaned.iloc[position][column]),
                "new_value": "NA",
                "rule_id": "S-01",
                "rule_version": "1",
                "reason": "Impossible value: reported hours per week exceed the physical maximum of 168.",
                "theory_ref": "curso/05_preparacion_de_datos.md: validación de dominio y tratamiento trazable de errores; DDI oficial EH2025 F27: horas promedio semanales",
            })
        if len(positions):
            cleaned.loc[cleaned.index[positions], column] = "NA"
        changes.append({
            "rule_id": "S-01", "rule_version": "1", "column": column,
            "rule": "Mark weekly hours above 168 as invalid-as-missing; preserve rows and original in restricted cell audit",
            "theory_ref": "curso/05_preparacion_de_datos.md: validación de dominio y tratamiento trazable de errores; DDI oficial EH2025 F27",
            "rows_examined": int(len(cleaned)), "cells_changed": int(len(positions)),
            "status": "applied" if len(positions) else "no changes",
        })
    for column in cleaned.columns:
        missing = missing_mask(cleaned[column])
        malformed, check_status = malformed_registration_mask(column, cleaned[column])
        bad_count = int(missing.sum()) + int(malformed.sum())
        bad_pct = bad_count / len(cleaned) * 100 if len(cleaned) else 0.0
        changes.append({
            "rule_id": "L-80", "rule_version": "2", "column": column,
            "rule": "Audit global incomplete/malformed percentage; never delete a master column using an all-person denominator",
            "theory_ref": "curso/05_preparacion_de_datos.md: profile, validate and document transformations; docs/cleaning-methodology.md: universe-aware completeness",
            "rows_examined": int(len(cleaned)), "missing_count": int(missing.sum()),
            "malformed_count": int(malformed.sum()), "malformed_check_status": check_status,
            "incomplete_or_malformed_pct": round(bad_pct, 4),
            "threshold_pct": config.incomplete_or_malformed_drop_pct,
            "status": "audit flag > threshold; retained in master" if bad_pct > config.incomplete_or_malformed_drop_pct else "retained in master",
        })
    for key in config.key_columns:
        if key not in raw.columns:
            raise ValueError(f"Falta columna de clave declarada: {key}")
    duplicated = cleaned.duplicated(list(config.key_columns), keep=False)
    blank_key = pd.Series(False, index=cleaned.index)
    for key in config.key_columns:
        blank_key |= missing_mask(cleaned[key])
    if bool(duplicated.any()) or bool(blank_key.any()):
        raise ValueError(
            "La clave de persona no es única o tiene componentes vacíos. "
            "No se deduplicó ni se publicó una salida; revise perfil y contrato."
        )
    return cleaned, pd.DataFrame(changes), pd.DataFrame(semantic_changes)

def numeric_columns(frame: pd.DataFrame, config: PipelineConfig) -> dict[str, pd.Series]:
    result: dict[str, pd.Series] = {}
    for column in frame.columns:
        values = numeric_view(
            frame[column], config.minimum_numeric_values,
            column in config.id_columns or not has_confirmed_numeric_semantics(column),
        )
        if values is not None:
            result[column] = values
    return result


def compare_profiles(before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "column", "rows", "valid_non_missing_candidates", "missing_pct_of_rows", "empty_count",
        "missing_count", "malformed_count", "malformed_pct_of_rows", "malformed_check_status",
        "incomplete_or_malformed_count", "incomplete_or_malformed_pct", "drop_threshold_pct", "processing_action",
        "whitespace_only_count", "literal_missing_token_count", "exact_zero_count", "distinct_non_missing",
        "distinct_ratio", "observed_type", "semantic_type", "quality_alert", "definition_status", "numeric_valid_count",
        "minimum", "maximum", "mean", "std", "q1", "median", "q3", "iqr", "outlier_method",
        "outlier_status", "outlier_count", "outlier_pct_valid", "lower_fence", "upper_fence", "sensitive",
    ]
    left = before.set_index("column")
    right = after.set_index("column").reindex(left.index)
    comparison = pd.DataFrame(index=left.index)
    for label_column in ("display_name", "description", "section", "universe", "definition_status", "processing_action"):
        if label_column in left:
            comparison[label_column] = left[label_column]
    for metric in columns:
        if metric == "column":
            continue
        comparison[f"before_{metric}"] = left[metric] if metric in left else np.nan
        comparison[f"after_{metric}"] = right[metric] if metric in right else np.nan
    comparison.insert(0, "column", comparison.index)
    comparison["numeric_outlier_count_change"] = (
        pd.to_numeric(comparison["after_outlier_count"], errors="coerce")
        - pd.to_numeric(comparison["before_outlier_count"], errors="coerce")
    )
    comparison["decision"] = "Retener en el maestro; revisar perfil, universo, semántica y alertas"
    return comparison.reset_index(drop=True)


# %% [markdown]
# ## 6. Vista Markdown del diccionario JSON
#
# Se genera una fila por columna desde el JSON canonico. Las etiquetas
# provisionales quedan claramente separadas de las descripciones puntuales.

# %%
def markdown_escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def make_dictionary_markdown(
    columns: Iterable[str], source_metadata: dict[str, Any], profile: pd.DataFrame | None = None
) -> str:
    lines = [
        "# Diccionario de datos de `persona.csv`",
        "",
        "> Generado por `preprocessing.py` a partir del encabezado del archivo. Las definiciones marcadas como provisionales o pendientes requieren cotejo con el cuestionario oficial de la edición.",
        "",
        f"- Archivo: `{source_metadata['original_name']}`",
        f"- SHA-256: `{source_metadata['sha256']}`",
        f"- Filas: {source_metadata['rows']:,}; columnas: {source_metadata['columns']:,}.",
        "- `NA`, vacío, cero y no aplica conservan estado diferente hasta confirmar la regla por pregunta.",
        "- Las columnas sensibles se clasifican para restringir salidas detalladas.",
        "",
        "| Columna | Descripción para mostrar | Sección | Nivel | Tipo semántico | Estado de definición | Sensibilidad |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for column in columns:
        info = column_metadata(column)
        lines.append("| " + " | ".join(markdown_escape(info[key]) for key in (
            "column", "display_name", "section", "level", "kind", "definition_status", "sensitivity"
        )) + " |")
    if profile is not None:
        lines += [
            "", "## Análisis y proceso aplicado por columna", "",
            "Los porcentajes combinan faltantes técnicos y errores de formato/dominio que el diccionario permite comprobar. Los dominios desconocidos se marcan como no evaluados. La regla elimina del candidato columnas no clave solo cuando el porcentaje es estrictamente mayor al umbral; nunca cambia el archivo raw.",
            "", "| Columna | Descripción | Faltantes % | Mal registrados % | Comprobación | Alerta de calidad | Umbral % | Proceso/decisión |", "| --- | --- | ---: | ---: | --- | --- | ---: | --- |",
        ]
        for row in profile.to_dict(orient="records"):
            values = (
                row["column"], row["display_name"], row["missing_pct_of_rows"],
                row["malformed_pct_of_rows"], row["malformed_check_status"], row["quality_alert"],
                row["drop_threshold_pct"], row["processing_action"],
            )
            lines.append("| " + " | ".join(markdown_escape(value) for value in values) + " |")
    lines += [
        "",
        "## Reglas generales",
        "",
        "El perfil y el informe antes/después contienen los estadísticos observados para esta carga; este diccionario describe semántica y contrato. Ningún código categórico se interpreta como magnitud sin definición. La detección IQR es una alerta estadística, no una instrucción de eliminación.",
        "",
        "Las columnas derivadas y sus fórmulas deben documentarse en una sección versionada adicional cuando se habiliten reglas confirmadas.",
        "",
    ]
    return "\n".join(lines)


# %% [markdown]
# ## 7. Gráficos comparables antes y después
#
# Una imagen legible se produce por cada columna y compara raw con candidato.
# Las magnitudes confirmadas usan histogramas superpuestos con los mismos bins;
# códigos/categorías usan barras horizontales; identificadores solo muestran
# completitud. La vista general enfoca las columnas con mayor ausencia técnica.
# Celdas pequeñas se agrupan o suprimen según el umbral configurado.

# %%
def safe_plot_filename(column: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", column).strip("_.") or "column"


def suppress_counts(counts: pd.Series, threshold: int) -> pd.Series:
    return counts.where(counts >= threshold, np.nan)


def category_counts(series: pd.Series, top_n: int, minimum_count: int) -> pd.Series:
    """Frequency table with explicit missingness and small-cell suppression."""
    text = series.astype("string").str.strip()
    missing = text.isna() | text.eq("") | text.isin(MISSING_LITERALS)
    counts = text[~missing].value_counts(dropna=False)
    common = counts[counts >= minimum_count]
    selected = common.iloc[:top_n]
    result = selected.copy()
    other_common = int(common.iloc[top_n:].sum())
    if other_common >= minimum_count:
        result.loc["Otros (categorías agrupadas)"] = other_common
    small_count = int(counts[counts < minimum_count].sum())
    empty_count = int((text.isna() | text.eq("")).sum())
    token_count = int(text.isin(MISSING_LITERALS).sum())
    if empty_count >= minimum_count:
        result.loc["Vacío o solo espacios"] = empty_count
    else:
        small_count += empty_count
    if token_count >= minimum_count:
        result.loc["Token NA/N/A/NULL"] = token_count
    else:
        small_count += token_count
    if small_count >= minimum_count:
        result.loc[f"Suprimidos/agrupados (<{minimum_count} por categoría)"] = small_count
    return result


def numeric_plot_bounds(before: pd.Series, after: pd.Series) -> tuple[float, float]:
    combined = pd.concat([before.dropna(), after.dropna()]).astype(float)
    if combined.empty:
        return 0.0, 1.0
    lo, hi = float(combined.min()), float(combined.max())
    if math.isclose(lo, hi):
        pad = max(abs(lo) * 0.05, 0.5)
        return lo - pad, hi + pad
    return lo, hi


def plot_column_pair(
    column: str,
    before_frame: pd.DataFrame,
    after_frame: pd.DataFrame,
    config: PipelineConfig,
    out_dir: Path,
) -> Path | None:
    metadata = column_metadata(column)
    label = metadata["display_name"]
    figure, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    figure.suptitle(label, fontsize=14, wrap=True)
    if column not in after_frame.columns:
        ax.set_title(f"Valores del campo en el maestro derivado (umbral de alerta >{config.incomplete_or_malformed_drop_pct:g}%)")
        if column in config.id_columns:
            missing_count = int(missing_mask(before_frame[column]).sum())
            valid_count = len(before_frame) - missing_count
            bars = ax.bar(["Con valor", "Vacío / token NA"], [valid_count, missing_count], color=["#4C78A8", "#E15759"])
            ax.set_ylabel("Número de filas")
            labels = [f"{value:,.0f}" if value >= config.minimum_display_count else "" for value in bars.datavalues]
            ax.bar_label(bars, labels=labels, padding=2)
            ax.text(.5, -.16, "Esta columna se conserva en el maestro; los identificadores no se muestran como categorías.",
                    transform=ax.transAxes, ha="center", fontsize=9)
        elif has_confirmed_numeric_semantics(column):
            values = numeric_view(before_frame[column], config.minimum_numeric_values, False)
            if values is not None and values.notna().any():
                lower, upper = numeric_plot_bounds(values, pd.Series(dtype=float))
                bins = min(35, max(8, int(np.sqrt(max(int(values.notna().sum()), 1)))))
                edges = np.histogram_bin_edges(values.dropna(), bins=bins, range=(lower, upper))
                heights, _ = np.histogram(values.dropna(), bins=edges)
                heights = np.where(heights >= config.minimum_display_count, heights, np.nan)
                bars = ax.bar(edges[:-1], heights, width=np.diff(edges), align="edge", color="#4C78A8", alpha=.75)
                ax.set_xlim(lower, upper)
                ax.set_xlabel(f"Valor observado · {metadata['description']}")
                ax.set_ylabel("Número de filas")
                ax.set_title("Distribución numérica antes/después; variable retenida en el maestro")
                ax.text(.5, -.16, "El histograma solo facilita la inspección; no elimina ni recorta valores del CSV.",
                        transform=ax.transAxes, ha="center", fontsize=9)
                ax.grid(axis="y", alpha=.2)
            else:
                ax.text(.5, .5, "No hay suficientes valores numéricos válidos para graficar", ha="center", va="center")
                ax.set_axis_off()
        else:
            counts = category_counts(before_frame[column], config.maximum_categories_in_plot, config.minimum_display_count)
            counts = counts.sort_values(ascending=True)
            bars = ax.barh(counts.index.astype(str), counts.values, color="#4C78A8")
            ax.set_xlabel("Número de filas")
            ax.bar_label(bars, fmt="{:,.0f}", padding=3, fontsize=8)
            ax.text(0, -.16, "La variable se conserva en el maestro; el umbral global solo prioriza revisión.",
                    transform=ax.transAxes, fontsize=9)
        ax.grid(axis="x" if column not in config.id_columns else "y", alpha=.2)
    elif column in {"folio", "upm"}:
        phases = (before_frame, after_frame)
        valid_counts = [int((~missing_mask(frame[column])).sum()) for frame in phases]
        missing_counts = [int(missing_mask(frame[column]).sum()) for frame in phases]
        x = np.arange(2)
        width = .36
        ax.bar(x - width / 2, valid_counts, width, label="Con valor", color="#4C78A8")
        ax.bar(x + width / 2, missing_counts, width, label="Vacío / token NA", color="#E15759")
        ax.set_xticks(x, ["Antes · raw", "Después · maestro derivado"])
        ax.set_ylabel("Número de filas")
        ax.set_title("Control de completitud de identificador; no se grafica su distribución")
        ax.legend(title="Estado del campo")
        ax.grid(axis="y", alpha=.2)
        for bars in ax.containers:
            labels = [f"{value:,.0f}" if value >= config.minimum_display_count else "" for value in bars.datavalues]
            ax.bar_label(bars, labels=labels, padding=2)
    elif has_confirmed_numeric_semantics(column):
        before_numeric = numeric_view(before_frame[column], config.minimum_numeric_values, False)
        after_numeric = numeric_view(after_frame[column], config.minimum_numeric_values, False)
        available = [v.dropna() for v in (before_numeric, after_numeric) if v is not None]
        if available and any(len(v) for v in available):
            lower, upper = numeric_plot_bounds(
                before_numeric if before_numeric is not None else pd.Series(dtype=float),
                after_numeric if after_numeric is not None else pd.Series(dtype=float),
            )
            bins = min(35, max(8, int(np.sqrt(max(sum(map(len, available)), 1)))))
            edges = np.histogram_bin_edges(pd.concat(available), bins=bins, range=(lower, upper))
            for values, name, color in zip((before_numeric, after_numeric), ("Antes · raw", "Después · maestro derivado"), ("#4C78A8", "#59A14F")):
                if values is not None:
                    heights, _ = np.histogram(values.dropna(), bins=edges)
                    heights = np.where(heights >= config.minimum_display_count, heights, np.nan)
                    ax.bar(edges[:-1], heights, width=np.diff(edges), align="edge", alpha=.58,
                           color=color, label=f"{name} (n={values.notna().sum():,})")
            ax.set_xlim(lower, upper)
            ax.set_xlabel(f"Valor observado · {metadata['description']}")
            ax.set_ylabel("Número de filas")
            ax.set_title("Histograma superpuesto · ambos periodos usan los mismos intervalos")
            ax.legend()
            ax.grid(axis="y", alpha=.2)
        else:
            ax.text(.5, .5, "No hay suficientes valores numéricos válidos para graficar", ha="center", va="center")
            ax.set_axis_off()
    else:
        before_counts = category_counts(before_frame[column], config.maximum_categories_in_plot, config.minimum_display_count)
        after_counts = category_counts(after_frame[column], config.maximum_categories_in_plot, config.minimum_display_count)
        labels = list(dict.fromkeys([str(x) for x in before_counts.index] + [str(x) for x in after_counts.index]))
        def category_order(item: str) -> tuple[int, float]:
            try:
                return (0, float(item))
            except ValueError:
                return (1, -float(before_counts.get(item, 0) + after_counts.get(item, 0)))

        labels.sort(key=category_order)
        figure.set_size_inches(12, max(6, min(36, 2.5 + len(labels) * .28)))
        y = np.arange(len(labels))
        width = .38
        left = np.array([int(before_counts.get(item, 0)) for item in labels], dtype=float)
        right = np.array([int(after_counts.get(item, 0)) for item in labels], dtype=float)
        ax.barh(y - width / 2, left, width, label="Antes · raw", color="#4C78A8")
        ax.barh(y + width / 2, right, width, label="Después · maestro derivado", color="#59A14F")
        ax.set_yticks(y, labels)
        ax.set_xlabel("Número de filas/personas observadas")
        semantic = metadata["kind"].casefold()
        before_values = before_frame[column].astype("string").str.strip()
        distinct_values = int(before_values[~missing_mask(before_frame[column])].nunique(dropna=True))
        high_cardinality = ("categórica" in semantic or "categorica" in semantic) and distinct_values > 30
        title = "Frecuencia por categoría o código · antes/después"
        if high_cardinality:
            title += " · ALERTA: cardinalidad inusual; verificar dominio"
        ax.set_title(title)
        ax.legend()
        ax.grid(axis="x", alpha=.2)
        ax.set_axisbelow(True)
        for bars in ax.containers:
            ax.bar_label(bars, fmt="{:,.0f}", padding=2, fontsize=8)
        ax.text(0, -.16, "Los códigos y el valor 0 se muestran tal como están en el CSV; vacíos y tokens NA se separan. Celdas pequeñas se agrupan/suprimen.",
                transform=ax.transAxes, fontsize=8, va="top", wrap=True)
    path = out_dir / f"{safe_plot_filename(column)}.png"
    out_dir.mkdir(parents=True, exist_ok=True)
    figure.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(figure)
    return path


def make_missingness_plot(before: pd.DataFrame, after: pd.DataFrame, out_path: Path) -> Path:
    def rate(frame: pd.DataFrame) -> pd.Series:
        values: dict[str, float] = {}
        for column in frame.columns:
            text = frame[column].astype("string")
            missing = text.eq("") | text.str.strip().eq("") | text.str.strip().isin(MISSING_LITERALS)
            values[column] = float(missing.mean() * 100)
        return pd.Series(values)
    left, right = rate(before), rate(after)
    right = right.reindex(left.index)
    order = (left.fillna(0) + right.fillna(0)).sort_values(ascending=True).tail(25).index
    left, right = left.reindex(order), right.reindex(order)
    labels = []
    for column in order:
        description = column_metadata(column)["description"]
        short = description if len(description) <= 52 else description[:49] + "..."

        labels.append(f"{column} — {short}")
    y = np.arange(len(order))
    height = .38
    fig, ax = plt.subplots(figsize=(14, max(8, len(order) * .38)), constrained_layout=True)
    ax.barh(y - height/2, left.to_numpy(dtype=float), height, label="Antes · raw", color="#4C78A8")
    ax.barh(y + height/2, right.to_numpy(dtype=float), height, label="Después · maestro derivado", color="#59A14F")
    ax.set_yticks(y, labels, fontsize=8)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Filas con vacío, espacios o token NA (%)")
    ax.set_title("Hasta 25 variables con mayor ausencia técnica\nPorcentaje de filas incompletas, antes y después")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=.25)
    ax.set_axisbelow(True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return out_path


# %% [markdown]
# ## 8. Guardar informes, gráficos y manifiesto
#
# Los resultados se escriben en una carpeta de ejecución nueva bajo
# `data/proprosessing/output/`. No se sobrescribe el raw ni se publica una versión
# en Flask/PostgreSQL: esta integración requiere la aplicación y una revisión
# posterior.

# %%
def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) or np.isinf(value) else float(value)
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    return value


def make_run_id(source_hash: str, config: PipelineConfig) -> str:
    config_json = json.dumps(asdict(config), sort_keys=True, default=list)
    config_hash = hashlib.sha256(config_json.encode("utf-8")).hexdigest()[:10]
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}_{source_hash[:12]}_{config_hash}"


def save_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def _present_values(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return text.notna() & text.ne("") & ~text.isin(MISSING_LITERALS)


def _thematic_columns(frame: pd.DataFrame, prefixes: tuple[str, ...], extra: Iterable[str] = ()) -> list[str]:
    context = ("folio", "nro", "area", "depto", "upm", "estrato", "factor")
    selected = [column for column in context if column in frame.columns]
    selected.extend(column for column in frame.columns if column.startswith(prefixes) and column not in selected)
    selected.extend(column for column in extra if column in frame.columns and column not in selected)
    return selected


def build_thematic_views(frame: pd.DataFrame, destination: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    """Write auditable, survey-aware extracts without changing the master frame."""
    if destination.exists():
        raise FileExistsError(f"La carpeta de vistas ya existe y es inmutable: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    age = pd.to_numeric(frame.get("s01a_03", pd.Series(index=frame.index, dtype="string")), errors="coerce")
    sex = frame.get("s01a_02", pd.Series(index=frame.index, dtype="string")).astype("string").str.strip()
    out: dict[str, tuple[pd.DataFrame, str, str, str]] = {}
    core = _thematic_columns(frame, ("s01",))
    out["demografia_persona"] = (frame[core].copy(), "persona", "Todos los registros persona", "Todas las 39.497 personas; claves y diseño muestral se retienen como contexto, no se certifica inferencia.")

    health_context = ["s01a_02", "s01a_03"]
    out["salud_general_persona"] = (
        frame[_thematic_columns(frame, ("s02a_",), health_context)].copy(), "persona", "Todos los registros persona",
        "Conserva el universo general; los submódulos S02B/C/D tienen universos distintos y sus ausencias no son equivalentes.",
    )
    fecundity_mask = age.between(13, 50, inclusive="both") & sex.eq("2")
    fecundity = frame.loc[fecundity_mask]
    out["salud_fecundidad_mujeres_13_50"] = (
        fecundity[_thematic_columns(frame, ("s02b_",), health_context)].copy(), "persona",
        "s01a_02=2 y edad s01a_03 entre 13 y 50, ambos inclusive",
        "Filtro documentado en DDI; el resto no pertenece al denominador de fecundidad.",
    )
    children6 = frame.loc[age.lt(6)]
    out["salud_asistencia_infantil_menores_6"] = (
        children6[_thematic_columns(frame, ("s02c_",), health_context)].copy(), "persona",
        "Edad s01a_03 < 6", "Universo DDI de asistencia a centro infantil; no interpretar ausencias fuera del corte como falta de respuesta.",
    )
    children5 = frame.loc[age.lt(5)]
    out["salud_bono_menores_5"] = (
        children5[_thematic_columns(frame, ("s02d_",), health_context)].copy(), "persona",
        "Edad s01a_03 < 5", "Vista del submódulo infantil según corte DDI; revisar cortes por pregunta dentro de la sección.",
    )
    education = frame.loc[age.ge(4)]
    out["educacion_personas_4_mas"] = (
        education[_thematic_columns(frame, ("s03",), [*health_context, "niv_ed", "niv_ed_g", "cmasi", "educ_prev", "aestudio"])].copy(),
        "persona", "Edad s01a_03 >= 4", "Universo general de educación según DDI; Parte B/C puede imponer cortes más específicos.",
    )
    employment = frame.loc[age.ge(7)]
    labor_extra = [*health_context, "pet", "pea", "pei", "condact", "caeb_op", "caeb_os", "phrs", "shrs", "tothrs", "yprilab", "yseclab", "ylab", "ynolab", "yper"]
    out["empleo_personas_7_mas"] = (
        employment[_thematic_columns(frame, ("s04",), labor_extra)].copy(), "persona", "Edad s01a_03 >= 7",
        "Universo general de empleo; cada pregunta de ocupación/ingresos puede imponer filtros adicionales.",
    )

    secondary_columns = _thematic_columns(frame, ("s04e_", "s04f_"), [*health_context, "pet", "pea", "pei", "condact", "caeb_os", "shrs", "tothrs", "yseclab", "ylab", "yper"])
    secondary_present_columns = ["s04e_26_cod"] if "s04e_26_cod" in frame.columns else []
    secondary_reported = pd.Series(False, index=frame.index)
    for column in secondary_present_columns:
        secondary_reported |= _present_values(frame[column])
    secondary_filter_yes = frame["s04e_25"].astype("string").str.strip().eq("1").fillna(False) if "s04e_25" in frame.columns else pd.Series(False, index=frame.index)
    # Keep affirmative filter cases and out-of-filter reports for review; never silently drop contradictions.
    secondary_mask = secondary_filter_yes | secondary_reported
    secondary = frame.loc[secondary_mask, secondary_columns].copy()
    if "s04e_25" in frame.columns:
        filter_value = frame.loc[secondary_mask, "s04e_25"].astype("string").str.strip()
        secondary["secondary_filter_status"] = np.select(
            [
                filter_value.eq("1").fillna(False).to_numpy(dtype=bool),
                filter_value.eq("2").fillna(False).to_numpy(dtype=bool),
                (filter_value.isna() | filter_value.isin(MISSING_LITERALS)).fillna(False).to_numpy(dtype=bool),
            ],
            ["affirmative_filter", "reported_data_with_negative_filter_review", "reported_data_without_filter_review"],
            default="reported_data_with_other_filter_code_review",
        )
    secondary["age_universe_status"] = np.where(age.loc[secondary_mask].ge(7), "age_7_plus", "outside_or_unknown_age_universe_review")
    out["empleo_secundario_casos"] = (
        secondary, "persona", "s04e_25=1 OR any nonmissing s04e/s04f field; retain exceptions for review",
        "Not a clean eligible-only sample: contains all affirmative cases and any reported secondary-work data, including filter conflicts. Use only rows with confirmed eligibility for estimates.",
    )
    out["ingresos_no_laborales_persona"] = (
        frame[_thematic_columns(frame, ("s05",), health_context)].copy(), "persona", "Todos los registros persona",
        "Row-level extract only; item-level questionnaire universes differ. No household aggregation or estimate is implied.",
    )
    poverty_columns = _thematic_columns(frame, (), [*health_context, "totper", "yprilab", "yseclab", "ylab", "ynolab", "yper", "yhog", "yhogpc", "z", "zext", "p0", "p1", "p2", "pext0", "pext1", "pext2"])
    out["ingresos_pobreza_persona"] = (
        frame[poverty_columns].copy(), "persona", "Todos los registros persona",
        "Incluye variables personales y de hogar repetidas por persona. No calcular promedios ni intervalos sin definir unidad, ponderador y diseño.",
    )

    # A household view is formed only for variables that are invariant within each folio.
    household_candidates = [c for c in ("area", "depto", "upm", "estrato", "totper", "tipohogar", "yhog", "yhogpc", "z", "zext", "p0", "p1", "p2", "pext0", "pext1", "pext2") if c in frame.columns]
    stable: list[str] = []
    conflicts: dict[str, int] = {}
    coalesced_missing: dict[str, int] = {}
    for column in household_candidates:
        source_values = frame[column].astype("string")
        observed_values = source_values.where(_present_values(source_values), pd.NA)
        distinct = observed_values.groupby(frame["folio"], dropna=False, sort=False).nunique(dropna=True)
        conflict_n = int(distinct.gt(1).sum())
        if conflict_n == 0:
            stable.append(column)
            observed_n = observed_values.groupby(frame["folio"], dropna=False, sort=False).count()
            group_size = frame.groupby("folio", dropna=False, sort=False).size()
            coalesced_missing[column] = int(((observed_n > 0) & (observed_n < group_size)).sum())
        else:
            conflicts[column] = conflict_n
    household = frame[["folio"]].drop_duplicates("folio", keep="first").copy()
    household_indexed = frame.assign(_group_folio=frame["folio"])
    for column in stable:
        source_values = household_indexed[column].astype("string")
        observed_values = source_values.where(_present_values(source_values), pd.NA)
        observed_first = observed_values.groupby(household_indexed["_group_folio"], dropna=False, sort=False).first()
        missing_first = source_values.groupby(household_indexed["_group_folio"], dropna=False, sort=False).first()
        household[column] = household["folio"].map(observed_first.combine_first(missing_first))
    roster_counts = frame.groupby("folio", dropna=False).size().rename("person_records_in_source").reset_index()
    household = household.merge(roster_counts, on="folio", how="left", validate="one_to_one", sort=False)
    out["hogar_resumen_persona_candidato"] = (
        household, "hogar", "Una fila por folio; solo campos invariantes dentro del folio",
        "If copies have missing markers but one unique observed value, the household view uses that value and audits the coalescing; person-level master is unchanged. person_records_in_source counts source rows and does not substitute totper, whose local definition/provenance still requires confirmation.",
    )

    conflict_report = pd.DataFrame([
        {"column": column, "households_with_multiple_values": count, "action": "excluded_from_household_summary; retained in person-level master/view"}
        for column, count in conflicts.items()
    ], columns=["column", "households_with_multiple_values", "action"])
    save_csv(conflict_report, destination / "household_field_conflicts.csv")
    coalescing_report = pd.DataFrame([
        {"column": column, "households_with_missing_and_one_observed_copy": count,
         "action": "use the sole observed value in household view; person-level source copies remain unchanged"}
        for column, count in coalesced_missing.items() if count
    ], columns=["column", "households_with_missing_and_one_observed_copy", "action"])
    save_csv(coalescing_report, destination / "household_field_coalescing.csv")

    view_rows: list[dict[str, Any]] = []
    for view_id, (view, unit, filter_description, caveat) in out.items():
        key = ["folio"] if unit == "hogar" else [c for c in ("folio", "nro") if c in view.columns]
        if view.duplicated(key).any():
            raise ValueError(f"La vista {view_id} tiene clave duplicada: {key}")
        csv_path = destination / f"{view_id}.csv"
        view.to_csv(csv_path, index=False, encoding="utf-8-sig")
        view_rows.append({
            "view_id": view_id, "file": csv_path.name, "analysis_unit": unit,
            "rows": int(len(view)), "columns": int(view.shape[1]), "key": key,
            "filter": filter_description, "survey_design_columns_retained": [c for c in ("factor", "estrato", "upm") if c in view.columns],
            "inferential_status": "not certified; confirm design/weights and use domain estimation where applicable",
            "caveat": caveat, "sha256": sha256_file(csv_path),
        })
    summary = {
        "dataset_id": metadata.get("dataset_id", metadata.get("configuration", {}).get("dataset_id", "EH2025_Persona")),
        "source_run_id": metadata["run_id"],
        "source_version_id": metadata["version_id"], "source_master_sha256": metadata["output_dataset_sha256"],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_policy": "Derived only from persona.csv through the cleaned candidate master; no other data files are read.",
        "missingness_policy": "No variable is removed by global missingness; module-specific universes remain explicit.",
        "household_field_conflicts_excluded": conflicts,
        "household_missing_copies_coalesced": {k: v for k, v in coalesced_missing.items() if v},
        "views": view_rows,
    }
    coverage = pd.DataFrame([
        {"view_id": view["view_id"], "analysis_unit": view["analysis_unit"], "input_person_rows": int(len(frame)),
         "output_rows": view["rows"], "output_columns": view["columns"], "filter": view["filter"],
         "inferential_status": view["inferential_status"]}
        for view in view_rows
    ])
    save_csv(coverage, destination / "view_coverage.csv")
    summary["supporting_files"] = [
        {"file": path.name, "sha256": sha256_file(path)}
        for path in sorted(destination.iterdir()) if path.is_file() and path.name != "views_manifest.json"
    ]
    (destination / "views_manifest.json").write_text(json.dumps(json_safe(summary), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def run_pipeline(config: PipelineConfig = CONFIG) -> dict[str, Any]:
    """Run one local candidate-cleaning job and return paths plus aggregate profiles."""
    try:
        import pyarrow  # noqa: F401
    except ImportError as error:
        raise RuntimeError("Instala PyArrow para generar la salida Parquet del candidato.") from error
    project_root = find_project_root()
    source_path = project_root / config.source_relpath
    output_root = project_root / config.output_relpath
    raw, source_metadata = read_raw_csv(source_path, config)
    before_profile = profile_frame(raw, config)
    candidate, rule_log, semantic_changes = clean_frame(raw, config)
    after_profile = profile_frame(candidate, config)
    comparison = compare_profiles(before_profile, after_profile)
    source_metadata["run_id"] = make_run_id(source_metadata["sha256"], config)
    source_metadata["created_at_utc"] = datetime.now(timezone.utc).isoformat()
    source_metadata["python_version"] = platform.python_version()
    source_metadata["pandas_version"] = pd.__version__
    source_metadata["numpy_version"] = np.__version__
    source_metadata["matplotlib_version"] = plt.matplotlib.__version__
    try:
        import pyarrow
        source_metadata["pyarrow_version"] = pyarrow.__version__
    except ImportError:
        source_metadata["pyarrow_version"] = None
    source_metadata["configuration"] = asdict(config)
    source_metadata["pipeline_code_path"] = "data/proprosessing/preprocessing.py"
    source_metadata["pipeline_code_sha256"] = sha256_file(project_root / "data/proprosessing/preprocessing.py")
    source_metadata["data_dictionary_sha256"] = sha256_file(DATA_DICTIONARY_PATH)
    source_metadata["schema_reconciliation"] = dictionary_schema_reconciliation(source_metadata["header"])
    source_metadata["dataset_scope"] = (
        "Only data/persona.csv is loaded and analyzed; no supplementary input files are used."
    )
    source_metadata["pipeline_status"] = "candidate; not published"
    source_metadata["semantic_limit"] = "S-01 applied for physically impossible weekly hours. Other suspected anomalies remain review-only pending questionnaire/version confirmation."
    run_dir = output_root / source_metadata["run_id"]
    if run_dir.exists():
        raise FileExistsError(f"El directorio de ejecución ya existe; no se sobrescribe: {run_dir}")
    plots_dir = run_dir / "plots"
    column_plots_dir = plots_dir / "columns"
    # Build nested output paths recursively so missing intermediate directories
    # (including a fresh output/ or plots/ folder) cannot raise FileNotFoundError.
    run_dir.mkdir(parents=True, exist_ok=False)
    column_plots_dir.mkdir(parents=True, exist_ok=True)
    save_csv(before_profile, run_dir / "profile_before.csv")
    save_csv(after_profile, run_dir / "profile_after.csv")
    save_csv(comparison, run_dir / "comparison_all_columns.csv")
    save_csv(rule_log, run_dir / "rule_execution_log.csv")
    if not semantic_changes.empty:
        semantic_changes.insert(0, "run_id", source_metadata["run_id"])
        semantic_changes.insert(1, "dataset_id", config.dataset_id)
        semantic_changes.insert(2, "actor", "automated_pipeline")
    save_csv(semantic_changes, run_dir / "semantic_cell_changes_restricted.csv")
    candidate.to_csv(run_dir / "persona_clean_master.csv", index=False, encoding="utf-8-sig")
    try:
        candidate.to_parquet(run_dir / "persona_clean_master.parquet", index=False, compression="zstd")
    except (ImportError, ModuleNotFoundError) as error:
        raise RuntimeError("Instala PyArrow para generar la salida Parquet del candidato.") from error
    source_metadata["source_file_id"] = source_metadata["sha256"]
    source_metadata["output_dataset_sha256"] = sha256_file(run_dir / "persona_clean_master.csv")
    source_metadata["version_id"] = f"persona-{source_metadata['output_dataset_sha256'][:16]}"
    views_summary = build_thematic_views(candidate, run_dir / "thematic_views", source_metadata)
    dictionary = make_dictionary_markdown(source_metadata["header"], source_metadata, before_profile)
    (run_dir / "data_dictionary.md").write_text(dictionary, encoding="utf-8")
    (run_dir / "data_dictionary.json").write_text(DATA_DICTIONARY_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    make_missingness_plot(raw, candidate, plots_dir / "missingness_all_columns.png")
    plot_paths = []
    for column in raw.columns:
        path = plot_column_pair(column, raw, candidate, config, column_plots_dir)
        plot_paths.append(path)
    source_metadata["column_plots"] = len(plot_paths)
    source_metadata["outputs"] = [
        "profile_before.csv", "profile_after.csv", "comparison_all_columns.csv",
        "rule_execution_log.csv", "semantic_cell_changes_restricted.csv", "persona_clean_master.csv", "persona_clean_master.parquet",
        "data_dictionary.json", "data_dictionary.md",
        "plots/missingness_all_columns.png", "plots/columns/", "thematic_views/",
    ]
    source_metadata["thematic_views"] = [
        {"view_id": view["view_id"], "rows": view["rows"], "columns": view["columns"], "file": f"thematic_views/{view['file']}"}
        for view in views_summary["views"]
    ]
    source_metadata["artifact_sha256"] = {
        path.relative_to(run_dir).as_posix(): sha256_file(path)
        for path in sorted(run_dir.rglob("*"))
        if path.is_file() and path.name != "manifest.json"
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(json_safe(source_metadata), ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    return {
        "run_dir": run_dir,
        "before_profile": before_profile,
        "after_profile": after_profile,
        "comparison": comparison,
        "rule_log": rule_log,
        "semantic_changes": semantic_changes,
        "thematic_views": views_summary,
        "plot_paths": plot_paths,
        "metadata": source_metadata,
    }


# %% [markdown]
# ## 9. Ejecutar el pipeline
#
# Esta celda crea resultados locales al ejecutarse. Revisa la configuración y las
# definiciones pendientes antes de usar esos resultados en un análisis sustantivo.

# %%
def main() -> dict[str, Any]:
    result = run_pipeline(CONFIG)
    print(f"Ejecución candidata: {result['metadata']['run_id']}")
    print(f"Carpeta de resultados: {result['run_dir']}")
    print(f"Filas: {result['metadata']['rows']:,}; columnas: {result['metadata']['columns']:,}")
    print(f"Columnas graficadas: {len(result['plot_paths']):,}")
    print("Estado: candidato local; no publicado en Flask/PostgreSQL.")
    return result


if __name__ == "__main__":
    PIPELINE_RESULT = main()


# %% [markdown]
# ## 10. Ver los gráficos producidos
#
# Cada columna tiene una imagen PNG completa. Esta celda muestra una variable
# de ejemplo por sección para que se puedan leer a tamaño normal; no son datos
# simulados. Use el código de columna indicado para abrir cualquier otra imagen.

# %%
if "get_ipython" in globals() and "PIPELINE_RESULT" in globals():
    try:
        from IPython.display import Image, display

        print("Clave visual: azul = raw/original; verde = candidato. El resumen muestra las columnas con mayor ausencia técnica. Categorías/códigos = frecuencias antes/después; magnitudes confirmadas = histogramas superpuestos; identificadores = completitud solamente. Atípicos se marcan en el perfil, no se eliminan.")
        with pd.option_context("display.max_rows", 300, "display.max_colwidth", 120):
            display(PIPELINE_RESULT["comparison"][
                ["column", "display_name", "before_missing_pct_of_rows", "before_malformed_pct_of_rows", "before_quality_alert",
                 "before_malformed_check_status", "before_incomplete_or_malformed_pct",
                 "before_drop_threshold_pct", "before_processing_action", "before_outlier_status", "decision"]
            ])
        display(Image(filename=str(PIPELINE_RESULT["run_dir"] / "plots" / "missingness_all_columns.png")))
        shown_sections = set()
        for path in PIPELINE_RESULT["plot_paths"]:
            column = path.stem
            section = next((prefix for prefix in ("s01", "s02", "s03", "s04", "s05") if column.startswith(prefix)), None)
            if section is None or section in shown_sections or column in CONFIG.id_columns:
                continue
            shown_sections.add(section)
            print(f"Ejemplo {section}: {column} — {column_metadata(column)['description']}")
            display(Image(filename=str(path)))
        print(f"Hay una imagen legible por columna en: {PIPELINE_RESULT['run_dir'] / 'plots' / 'columns'}")
        print("Para abrir otra: display(Image(filename=str(PIPELINE_RESULT['run_dir'] / 'plots' / 'columns' / 's01a_02.png')))")
    except ImportError:
        warnings.warn("Instala Jupyter/IPython para mostrar imágenes inline.", stacklevel=1)












