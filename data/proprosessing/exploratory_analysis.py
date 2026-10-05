"""Generate conservative, reproducible descriptive analysis for persona.csv views.

Reads only a previously generated candidate master and its thematic views.
It does not modify source data, infer survey estimates, impute, or remove rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUN = ROOT / "data/proprosessing/output/20261004T215218Z_568e82e3039d_d3abfb0b5f"
MIN_CELL = 10
IDENTIFIER_COLUMNS = {"folio", "nro", "upm", "estrato", "factor"}
SENSITIVE_PREFIXES = ("s02", "s04", "s05", "y", "z", "p")
PLOT_VARS = {
    "demografia_persona": ["s01a_02", "s01a_03", "area", "depto"],
    "salud_general_persona": ["s02a_01a", "s02b_01", "s02c_01"],
    "educacion_personas_4_mas": ["s03a_01", "s03b_05", "s03c_10"],
    "empleo_personas_7_mas": ["condact", "s04a_01", "s04e_25"],
    "empleo_secundario_casos": ["s04e_25", "s04e_26_cod"],
    "ingresos_no_laborales_persona": ["ynolab"],
    "ingresos_pobreza_persona": ["yper", "yhogpc", "p0", "p1", "p2"],
    "salud_fecundidad_mujeres_13_50": ["s02d_01"],
    "salud_asistencia_infantil_menores_6": ["s02b_01"],
    "salud_bono_menores_5": ["s02c_01"],
    "hogar_resumen_persona_candidato": ["totper", "yhogpc", "p0", "p1", "p2"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def present(series: pd.Series) -> pd.Series:
    text = series.astype("string").str.strip()
    return text.notna() & text.ne("") & text.str.upper().ne("NA")


def label_for(column: str, dictionary: dict[str, Any]) -> tuple[str, str, str]:
    item = dictionary.get("variables", {}).get(column)
    if item is None:
        item = dictionary.get("local_extensions", {}).get(column, {})
    return (
        str(item.get("display_name") or item.get("description") or column),
        str(item.get("section") or "Sección por confirmar"),
        str(item.get("semantic_type") or "pendiente de confirmar"),
    )


def column_summary(df: pd.DataFrame, view_id: str, dictionary: dict[str, Any]) -> pd.DataFrame:
    rows = []
    n = len(df)
    for col in df.columns:
        text = df[col].astype("string").str.strip()
        mask = present(df[col])
        values = df.loc[mask, col].astype("string").str.strip()
        numeric = pd.to_numeric(values.str.replace(",", ".", regex=False), errors="coerce")
        name, section, semantic_type = label_for(col, dictionary)
        item = dictionary.get("variables", {}).get(col) or dictionary.get("local_extensions", {}).get(col, {})
        is_sensitive = (
            col.casefold() in IDENTIFIER_COLUMNS
            or col.casefold().startswith(SENSITIVE_PREFIXES)
            or bool(item.get("sensitive", False))
            or str(item.get("sensitivity") or "").casefold() in {"sensitive", "high", "alta", "alto"}
        )
        category_counts = values.value_counts()
        top_count = int(category_counts.iloc[0]) if not category_counts.empty else 0
        publish_top_category = not is_sensitive and top_count >= MIN_CELL
        confirmed_quant = any(token in semantic_type.casefold() for token in ("cuantitativa", "monetaria", "numérica continua", "numerica continua"))
        valid_numeric = numeric.dropna()
        quantiles = valid_numeric.quantile([.25, .5, .75]) if confirmed_quant and not valid_numeric.empty else pd.Series(dtype=float)
        rows.append({
            "view_id": view_id, "column": col, "display_name": name, "section": section,
            "semantic_type": semantic_type, "universe_n": n, "observed_n": int(mask.sum()),
            "empty_n": int((text.isna() | text.eq("")).sum()),
            "literal_NA_n": int(text.str.upper().eq("NA").fillna(False).sum()),
            "missing_empty_or_literal_NA_pct": round(100 * (n - mask.sum()) / n, 4) if n else None,
            "exact_zero_token_n": int(text.eq("0").fillna(False).sum()),
            "distinct_observed": int(values.nunique()),
            "top_category": str(category_counts.index[0]) if publish_top_category else None,
            "top_category_n": top_count if publish_top_category else None,
            "top_category_status": "reported" if publish_top_category else "suppressed: sensitive/identifier or below minimum cell size",
            "numeric_descriptives_status": "eligible by dictionary type" if confirmed_quant else "not computed: categorical, identifier, or type pending",
            "numeric_n": int(len(valid_numeric)) if confirmed_quant else None,
            "minimum": float(valid_numeric.min()) if confirmed_quant and len(valid_numeric) else None,
            "q1": float(quantiles.get(.25)) if .25 in quantiles else None,
            "median": float(quantiles.get(.5)) if .5 in quantiles else None,
            "q3": float(quantiles.get(.75)) if .75 in quantiles else None,
            "maximum": float(valid_numeric.max()) if confirmed_quant and len(valid_numeric) else None,
            "mean_unweighted": float(valid_numeric.mean()) if confirmed_quant and len(valid_numeric) else None,
        })
    return pd.DataFrame(rows)


def plot_variable(df: pd.DataFrame, column: str, title: str, target: Path) -> None:
    if column not in df.columns:
        return
    values = df.loc[present(df[column]), column].astype("string").str.strip()
    if values.empty:
        return
    counts = values.value_counts()
    # Suppress small cells before plotting; combine suppressed categories.
    shown = counts[counts >= MIN_CELL].head(20)
    suppressed_n = int(counts[counts < MIN_CELL].sum())
    if len(counts) > len(shown) and suppressed_n:
        shown.loc[f"Supresión (<{MIN_CELL})"] = suppressed_n
    if shown.empty:
        return
    fig, ax = plt.subplots(figsize=(9, max(3.5, .38 * len(shown))))
    shown.sort_values().plot(kind="barh", ax=ax, color="#3b82a0")
    ax.set_title(title, loc="left", fontsize=10, wrap=True)
    ax.set_xlabel("Personas observadas (conteo no ponderado)")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(target, dpi=140)
    plt.close(fig)


def run(candidate: Path) -> Path:
    candidate = candidate.resolve()
    views_dir = candidate / "thematic_views"
    manifest_path = views_dir / "views_manifest.json"
    master_path = candidate / "persona_clean_master.csv"
    dictionary_path = candidate / "data_dictionary.json"
    for required in (manifest_path, master_path, dictionary_path):
        if not required.is_file():
            raise FileNotFoundError(f"Falta artefacto requerido: {required}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    dictionary = json.loads(dictionary_path.read_text(encoding="utf-8-sig"))
    if sha256(master_path) != manifest.get("source_master_sha256"):
        raise ValueError("Hash del maestro no coincide con el manifiesto de vistas.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result_dir = candidate / "exploratory_analysis" / stamp
    result_dir.mkdir(parents=True, exist_ok=False)
    (result_dir / "plots").mkdir()
    all_summaries = []
    coverage = []
    for item in manifest["views"]:
        view_path = views_dir / item["file"]
        if sha256(view_path) != item["sha256"]:
            raise ValueError(f"Hash de vista no coincide: {item['file']}")
        df = pd.read_csv(view_path, dtype="string", keep_default_na=False, encoding="utf-8-sig")
        if len(df) != item["rows"] or len(df.columns) != item["columns"]:
            raise ValueError(f"Dimensiones inesperadas: {item['file']}")
        summary = column_summary(df, item["view_id"], dictionary)
        all_summaries.append(summary)
        coverage.append({"view_id": item["view_id"], "file": item["file"], "unit": item["analysis_unit"],
                         "n": len(df), "filter": item.get("filter", ""), "caveat": item.get("caveat", ""),
                         "inferential_status": item.get("inferential_status", "not certified")})
        for col in PLOT_VARS.get(item["view_id"], []):
            display, section, _ = label_for(col, dictionary)
            plot_variable(df, col, f"{display}\n{item['view_id']} | n={len(df):,} | {item.get('filter', '')}",
                          result_dir / "plots" / f"{item['view_id']}__{col}.png")
        # Frequency tables are aggregated; identifiers and sensitive fields are omitted.
        for col in df.columns:
            if col.casefold() in IDENTIFIER_COLUMNS or col.casefold().startswith(SENSITIVE_PREFIXES):
                continue
            vals = df.loc[present(df[col]), col].astype("string").str.strip().value_counts()
            safe = vals[vals >= MIN_CELL].head(30)
            if not safe.empty:
                safe.rename_axis("category").rename("n").reset_index().assign(column=col, view_id=item["view_id"]).to_csv(
                    result_dir / f"frequency__{item['view_id']}__{col}.csv", index=False, encoding="utf-8-sig")
    profile = pd.concat(all_summaries, ignore_index=True)
    profile.to_csv(result_dir / "column_descriptives.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(coverage).to_csv(result_dir / "view_universes.csv", index=False, encoding="utf-8-sig")
    lines = ["# Análisis exploratorio descriptivo de `persona.csv`", "",
             f"- Ejecución UTC: {stamp}", f"- Versión candidata: {manifest.get('source_version_id')}",
             f"- Run de origen: {manifest.get('source_run_id')}", f"- Hash maestro: `{manifest['source_master_sha256']}`",
             "- Unidad: personas, salvo la vista hogar candidata.",
             "- Método: conteos y distribuciones no ponderados; cuantiles/media solo para tipos cuantitativos confirmados por el diccionario.",
             f"- Celdas pequeñas en gráficos y frecuencias exportadas: categorías con n < {MIN_CELL} se agrupan/omiten.",
             "- No son estimaciones poblacionales ni resultados oficiales; el diseño muestral aún no está certificado.",
             "- Las ausencias se describen dentro del universo de cada vista; no equivalen automáticamente a no respuesta.", "",
             "## Universos examinados", ""]
    for row in coverage:
        lines.append(f"- **{row['view_id']}**: n={row['n']:,}; filtro: {row['filter']}. {row['caveat']}")
    lines += ["", "## Archivos", "", "`column_descriptives.csv` contiene una fila por columna y vista. `plots/` contiene gráficos de variables seleccionadas por tema. Las frecuencias se guardan agregadas y con umbral de supresión.",
              "", "## Lectura estadística", "", "No comparar porcentajes entre vistas con universos distintos sin recalcular un denominador común. Los códigos categóricos se reportan como categorías, nunca como magnitudes. Los ingresos y medidas candidatas llevan sus valores observados sin ponderar y requieren confirmar unidad, periodo, universo y edición del diccionario antes de interpretarse. La vista secundaria conserva una excepción al filtro; no utilizarla como muestra depurada.", ""]
    (result_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")
    run_meta = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "source_candidate": str(candidate.relative_to(ROOT)),
                "source_master_sha256": manifest["source_master_sha256"], "source_version_id": manifest.get("source_version_id"),
                "source_run_id": manifest.get("source_run_id"), "minimum_cell_size": MIN_CELL,
                "weighted_estimation": False, "inferential_status": "not certified", "input_files": [x["file"] for x in manifest["views"]]}
    (result_dir / "analysis_manifest.json").write_text(json.dumps(run_meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return result_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_RUN)
    args = parser.parse_args()
    print(run(args.candidate))
