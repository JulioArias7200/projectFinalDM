"""Independent full-file validation and reproducible household QA sample.

Uses only data/persona.csv and one immutable pipeline candidate. The sample
artifacts contain source row numbers, not respondent values or household IDs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from data.proprosessing import preprocessing as pipeline


DEFAULT_CANDIDATE = ROOT / "data/proprosessing/output/20261004T231539Z_568e82e3039d_d3abfb0b5f"
SAMPLE_HOUSEHOLDS = 381
MIN_PER_STRATUM = 15
HOUSEHOLD_CONSTANT_FIELDS = (
    "depto", "area", "upm", "estrato", "totper", "yhog", "yhogpc", "z", "zext",
    "p0", "p1", "p2", "pext0", "pext1", "pext2", "tipohogar",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype="string", keep_default_na=False, na_filter=False,
                       encoding="utf-8-sig", low_memory=False)


def allocate_strata(populations: dict[str, int], target: int,
                    minimum: int = MIN_PER_STRATUM) -> dict[str, int]:
    """Allocate proportionally with a minimum, census small strata, total exact."""
    populations = {key: int(value) for key, value in populations.items() if int(value) > 0}
    total = sum(populations.values())
    target = min(int(target), total)
    if target <= 0:
        return {key: 0 for key in populations}
    allocation = {key: min(size, minimum) for key, size in populations.items()}
    if sum(allocation.values()) > target:
        quotas = {key: target * size / total for key, size in populations.items()}
        allocation = {key: min(populations[key], int(quotas[key])) for key in populations}
        remaining = target - sum(allocation.values())
        for key in sorted(populations, key=lambda value: (-(quotas[value] - int(quotas[value])), value))[:remaining]:
            allocation[key] += 1
        return allocation
    remaining = target - sum(allocation.values())
    while remaining > 0:
        available = {key: populations[key] - allocation[key] for key in populations
                     if allocation[key] < populations[key]}
        if not available:
            break
        denominator = sum(available.values())
        quotas = {key: remaining * size / denominator for key, size in available.items()}
        floors = {key: min(available[key], int(quota)) for key, quota in quotas.items()}
        assigned = sum(floors.values())
        for key, value in floors.items():
            allocation[key] += value
        remaining -= assigned
        if remaining <= 0:
            break
        order = sorted(
            (key for key in available if allocation[key] < populations[key]),
            key=lambda key: (-(quotas[key] - int(quotas[key])), key),
        )
        if not order:
            break
        step = min(remaining, len(order))
        for key in order[:step]:
            allocation[key] += 1
        remaining -= step
    if sum(allocation.values()) != target:
        raise AssertionError("La asignación estratificada no suma el tamaño de muestra objetivo.")
    return allocation


def stable_stratum_value(series: pd.Series) -> tuple[str, bool]:
    text = series.astype("string").str.strip()
    missing = pipeline.missing_mask(text)
    normalized = text.mask(missing, "__MISSING__")
    unique = sorted(normalized.unique().tolist())
    if len(unique) == 1:
        return str(unique[0]), False
    return "__WITHIN_HOUSEHOLD_CONFLICT__", True


def household_frame(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    groups: dict[str, np.ndarray] = {}
    records = []
    for folio, positions in raw.groupby("folio", sort=True, dropna=False).indices.items():
        positions = np.asarray(positions, dtype=np.int64)
        groups[str(folio)] = positions
        indexes = pd.Index(positions)
        depto, depto_conflict = stable_stratum_value(raw.loc[indexes, "depto"])
        area, area_conflict = stable_stratum_value(raw.loc[indexes, "area"])
        if depto_conflict or area_conflict:
            stratum = "INTRA_HOUSEHOLD_STRATUM_CONFLICT"
        else:
            stratum = f"depto={depto}|area={area}"
        records.append({"folio": str(folio), "stratum": stratum, "person_count": len(positions),
                        "source_positions": positions})
    return pd.DataFrame(records), groups


def select_households(raw: pd.DataFrame, source_sha256: str,
                      target: int = SAMPLE_HOUSEHOLDS) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    frame, _ = household_frame(raw)
    populations = frame.groupby("stratum", sort=True).size().astype(int).to_dict()
    target = min(target, len(frame))
    allocation = allocate_strata(populations, target)
    seed = int(source_sha256[:16], 16)
    rng = np.random.default_rng(seed)
    selected_parts = []
    design = []
    for index, (stratum, n_h) in enumerate(sorted(allocation.items()), start=1):
        members = frame.index[frame["stratum"].eq(stratum)].to_numpy()
        chosen = np.sort(rng.choice(members, size=n_h, replace=False)) if n_h else np.array([], dtype=int)
        stratum_id = f"S{index:02d}"
        N_h = int(populations[stratum])
        design.append({"stratum_id": stratum_id, "households_in_frame_N_h": N_h,
                       "households_selected_n_h": int(n_h),
                       "inclusion_probability": float(n_h / N_h) if N_h else None,
                       "audit_expansion_weight_N_over_n": float(N_h / n_h) if n_h else None,
                       "person_records_in_selected_households": int(frame.loc[chosen, "person_count"].sum())})
        part = frame.loc[chosen, ["folio", "person_count", "source_positions"]].copy()
        part["stratum_id"] = stratum_id
        part["N_h"] = N_h
        part["n_h"] = int(n_h)
        part["weight"] = float(N_h / n_h) if n_h else None
        selected_parts.append(part)
    selected = pd.concat(selected_parts, ignore_index=True) if selected_parts else pd.DataFrame()
    rows = []
    for cluster_number, item in enumerate(selected.itertuples(index=False), start=1):
        for position in item.source_positions:
            rows.append({"sample_household_id": f"QA{cluster_number:04d}",
                         "stratum_id": item.stratum_id,
                         "source_csv_row_number_1based": int(position + 2),
                         "household_weight_N_h_over_n_h": item.weight})
    row_sample = pd.DataFrame(rows)
    design_frame = pd.DataFrame(design)
    return row_sample, design_frame, seed


def audit_household_consistency(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in HOUSEHOLD_CONSTANT_FIELDS:
        if column not in frame.columns:
            continue
        checked = 0
        conflicts = 0
        for _, group in frame.groupby("folio", sort=False, dropna=False):
            text = group[column].astype("string").str.strip()
            observed = text.mask(pipeline.missing_mask(text)).dropna()
            if observed.empty:
                continue
            checked += 1
            if observed.nunique() > 1:
                conflicts += 1
        rows.append({"check": "within-household nonmissing value constancy", "column": column,
                     "households_with_observed_value": checked, "households_with_multiple_values": conflicts,
                     "interpretation": "review-only; no values changed"})
    if "totper" in frame.columns:
        checked = matches = mismatches = ambiguous = 0
        for _, group in frame.groupby("folio", sort=False, dropna=False):
            vals = group["totper"].astype("string").str.strip()
            vals = vals.mask(pipeline.missing_mask(vals)).dropna().unique()
            if len(vals) == 0:
                continue
            if len(vals) != 1:
                ambiguous += 1
                continue
            try:
                declared = float(vals[0])
            except (TypeError, ValueError):
                ambiguous += 1
                continue
            checked += 1
            if declared == len(group):
                matches += 1
            else:
                mismatches += 1
        rows.append({"check": "totper versus observed persona rows per household", "column": "totper",
                     "households_with_observed_value": checked, "households_with_multiple_values": mismatches,
                     "interpretation": f"{matches} match, {mismatches} differ, {ambiguous} unavailable/ambiguous; review-only, definition unconfirmed"})
    return pd.DataFrame(rows)


def verify_transformation(raw: pd.DataFrame, candidate: pd.DataFrame) -> dict[str, Any]:
    if list(raw.columns) != list(candidate.columns) or raw.shape != candidate.shape:
        return {"passed": False, "reason": "candidate schema/dimensions differ from raw"}
    expected = raw.copy(deep=True)
    text_changes = 0
    for column in pipeline.LOWERCASE_TEXT_RESPONSE_COLUMNS:
        if column not in expected:
            continue
        original = expected[column].astype("string")
        missing = pipeline.missing_mask(original)
        normalized = original.str.lower()
        text_changes += int((~missing & original.ne(normalized)).sum())
        expected[column] = original.mask(~missing, normalized)
    hour_changes = 0
    for column in ("phrs", "shrs", "tothrs"):
        if column not in expected:
            continue
        numeric = pd.to_numeric(expected[column], errors="coerce")
        impossible = numeric.gt(168) & expected[column].notna()
        hour_changes += int(impossible.sum())
        expected.loc[impossible, column] = "NA"
    different = expected.ne(candidate)
    changed_columns = {column: int(different[column].sum()) for column in different if different[column].any()}
    return {"passed": expected.equals(candidate), "expected_s02_cells": text_changes,
            "expected_s01_cells": hour_changes, "total_differences": int(different.sum().sum()),
            "changed_columns": changed_columns}


def verify_cell_audit(raw: pd.DataFrame, candidate: pd.DataFrame, audit_path: Path) -> dict[str, Any]:
    audit = load_csv(audit_path)
    seen: set[tuple[int, str]] = set()
    matches = True
    for record in audit.itertuples(index=False):
        row = int(record.row_number_1based)
        column = str(record.column)
        key = (row, column)
        if key in seen:
            matches = False
            continue
        seen.add(key)
        index = row - 2
        if not (0 <= index < len(raw) and column in raw.columns):
            matches = False
            continue
        if (str(raw.iloc[index][column]) != str(record.old_value)
                or str(candidate.iloc[index][column]) != str(record.new_value)):
            matches = False
    return {"passed": matches, "entries": len(audit),
            "entries_by_rule": {str(key): int(value) for key, value in audit.groupby("rule_id").size().items()}}


def validate(candidate_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    manifest_path = candidate_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    source_path = ROOT / manifest["source_relpath"]
    raw = load_csv(source_path)
    candidate = load_csv(candidate_dir / "persona_clean_master.csv")
    source_hash = sha256_file(source_path)
    raw_exact_duplicate_extras = int(raw.duplicated(keep="first").sum())
    candidate_exact_duplicate_extras = int(candidate.duplicated(keep="first").sum())
    key_columns = ["folio", "nro"]
    raw_key_duplicates = int(raw.duplicated(key_columns, keep="first").sum())
    candidate_key_duplicates = int(candidate.duplicated(key_columns, keep="first").sum())
    raw_blank_keys = int(sum(pipeline.missing_mask(raw[column]).sum() for column in key_columns))
    candidate_blank_keys = int(sum(pipeline.missing_mask(candidate[column]).sum() for column in key_columns))
    source_metadata = {
        "source_sha256_matches_manifest": source_hash == manifest.get("sha256"),
        "raw_rows": len(raw), "raw_columns": len(raw.columns),
        "candidate_rows": len(candidate), "candidate_columns": len(candidate.columns),
        "same_schema_and_dimensions": list(raw.columns) == list(candidate.columns) and raw.shape == candidate.shape,
        "same_key_sequence": raw[key_columns].equals(candidate[key_columns]),
        "raw_exact_duplicate_extras": raw_exact_duplicate_extras,
        "candidate_exact_duplicate_extras": candidate_exact_duplicate_extras,
        "raw_duplicate_key_extras": raw_key_duplicates,
        "candidate_duplicate_key_extras": candidate_key_duplicates,
        "raw_blank_key_cells": raw_blank_keys,
        "candidate_blank_key_cells": candidate_blank_keys,
        "raw_sha256": source_hash,
        "candidate_csv_sha256": sha256_file(candidate_dir / "persona_clean_master.csv"),
        "candidate_version_id": manifest.get("version_id"),
    }
    transform = verify_transformation(raw, candidate)
    cell_audit = verify_cell_audit(raw, candidate, candidate_dir / "semantic_cell_changes_restricted.csv")
    artifact_checks = []
    for relative, expected_hash in manifest.get("artifact_sha256", {}).items():
        path = candidate_dir / relative
        artifact_checks.append(path.is_file() and sha256_file(path) == expected_hash)
    source_metadata["artifact_hashes_passed"] = int(sum(artifact_checks))
    source_metadata["artifact_hashes_expected"] = len(artifact_checks)
    source_metadata["all_artifact_hashes_match"] = bool(artifact_checks) and all(artifact_checks)
    source_metadata["transformation_reconciliation"] = transform
    source_metadata["cell_audit_reconciliation"] = cell_audit
    checks = {
        "source hash matches manifest": source_metadata["source_sha256_matches_manifest"],
        "candidate preserves 39,497 rows × 275 columns": source_metadata["candidate_rows"] == 39497 and source_metadata["candidate_columns"] == 275,
        "schema and dimensions match raw": source_metadata["same_schema_and_dimensions"],
        "(folio,nro) sequence preserved": source_metadata["same_key_sequence"],
        "no exact duplicate rows in source": raw_exact_duplicate_extras == 0,
        "no duplicate candidate person keys": candidate_key_duplicates == 0,
        "no blank candidate key components": candidate_blank_keys == 0,
        "only declared S-01/S-02 transformations exist": bool(transform["passed"]),
        "restricted cell audit matches raw and candidate": bool(cell_audit["passed"]),
        "all candidate artifact hashes match": bool(source_metadata["all_artifact_hashes_match"]),
    }
    source_metadata["checks"] = checks
    source_metadata["validation_status"] = "passed" if all(checks.values()) else "failed"
    return raw, candidate, manifest, source_metadata, checks


def run(candidate_dir: Path, sample_size: int = SAMPLE_HOUSEHOLDS) -> Path:
    candidate_dir = candidate_dir.resolve()
    raw, candidate, manifest, validation, checks = validate(candidate_dir)
    row_sample, sample_design, seed = select_households(raw, validation["raw_sha256"], sample_size)
    selected_positions = row_sample["source_csv_row_number_1based"].astype(int).to_numpy() - 2
    sampled_raw = raw.iloc[selected_positions].copy()
    sampled_clean = candidate.iloc[selected_positions].copy()
    sample_consistency = audit_household_consistency(sampled_clean)
    sample_metrics = {
        "sampled_households": int(sample_design["households_selected_n_h"].sum()),
        "population_households": int(sample_design["households_in_frame_N_h"].sum()),
        "sampled_person_records": int(len(row_sample)),
        "populated_strata": int(len(sample_design)),
        "sample_key_duplicates": int(sampled_clean.duplicated(["folio", "nro"], keep="first").sum()),
        "sample_raw_candidate_key_sequence_matches": bool(sampled_raw[["folio", "nro"]].reset_index(drop=True).equals(sampled_clean[["folio", "nro"]].reset_index(drop=True))),
        "sample_frame_selection_reproducible_seed": seed,
        "sample_unit": "household; all person rows from each selected household are included",
        "sampling_scope": "quality audit only; not an analytical or model-training subset",
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / "data/proprosessing/validation" / f"{stamp}_{manifest.get('run_id', 'candidate')}"
    output.mkdir(parents=True, exist_ok=False)
    # Restricted map contains row positions only, not folio/nro or responses.
    row_sample.to_csv(output / "sampled_source_rows_RESTRICTED.csv", index=False, encoding="utf-8-sig")
    sample_design.to_csv(output / "sample_design_RESTRICTED.csv", index=False, encoding="utf-8-sig")
    sample_consistency.to_csv(output / "sample_internal_checks.csv", index=False, encoding="utf-8-sig")
    (output / "validation_results.json").write_text(
        json.dumps({"candidate_run_id": manifest.get("run_id"), "candidate_version_id": manifest.get("version_id"),
                    "candidate_path": candidate_dir.relative_to(ROOT).as_posix(),
                    "validation": validation, "sample": sample_metrics}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = [
        "# Validación final y muestra de auditoría de `persona.csv`", "",
        f"- Fecha UTC: {stamp}",
        f"- Candidata examinada: `{candidate_dir.relative_to(ROOT).as_posix()}`",
        f"- Versión candidata: `{manifest.get('version_id')}`",
        f"- Estado de controles automáticos: **{validation['validation_status'].upper()}**",
        f"- Filas/columnas: {validation['raw_rows']:,} × {validation['raw_columns']:,} (raw) y {validation['candidate_rows']:,} × {validation['candidate_columns']:,} (candidata).",
        f"- Hash SHA-256 raw: `{validation['raw_sha256']}`", "",
        "## Validación censal del archivo", "",
    ]
    report.extend(f"- {'PASS' if result else 'FAIL'} — {name}." for name, result in checks.items())
    report += [
        f"- Celdas reconciliadas: {validation['transformation_reconciliation'].get('total_differences', 'N/D'):,};",
        f"  S-01: {validation['transformation_reconciliation'].get('expected_s01_cells', 'N/D')};",
        f"  S-02: {validation['transformation_reconciliation'].get('expected_s02_cells', 'N/D')}.",
        f"- Bitácora restringida: {validation['cell_audit_reconciliation']['entries']:,} entradas y coincidencia antes/después: {validation['cell_audit_reconciliation']['passed']}.",
        f"- Artefactos verificados por hash: {validation['artifact_hashes_passed']}/{validation['artifact_hashes_expected']}.", "",
        "## Muestra estratificada de control", "",
        f"Se seleccionaron {sample_metrics['sampled_households']:,} hogares de {sample_metrics['population_households']:,}, estratificados por las combinaciones observadas de departamento y área; se incluyen todas las filas de persona de cada hogar seleccionado ({sample_metrics['sampled_person_records']:,} filas). La asignación usa mínimo de {MIN_PER_STRATUM} hogares por estrato poblado cuando el tamaño lo permite, y distribuye el resto proporcionalmente.",
        f"Semilla reproducible derivada del hash SHA-256: `{seed}`. La muestra es para QA; no reemplaza ni reduce el maestro. El diseño se estratifica y agrupa por hogar, por lo que no se atribuye automáticamente el margen de error de una muestra aleatoria simple. Las probabilidades y pesos por estrato están en `sample_design_RESTRICTED.csv`.",
        "El archivo `sampled_source_rows_RESTRICTED.csv` contiene números de fila del raw para inspección, sin claves ni respuestas. `sample_internal_checks.csv` informa consistencia intrahogar y la comparación exploratoria de `totper` con el roster observado; estos resultados son alertas, no reglas correctivas.", "",
        "## Interpretación y límites", "",
        "Los controles censales comprueban estructura, unicidad, preservación de claves, transformaciones declaradas, bitácora y hashes. La muestra permite revisar coherencia interna en hogares seleccionados. Como solo está disponible `persona.csv`, no es posible verificar que las respuestas coincidan con formularios originales ni confirmar todos los universos, dominios o valores verdaderos. Los problemas no decidibles se conservan como pendientes; no se eliminaron filas, columnas ni valores atípicos adicionales.",
        "La candidata sigue sin publicarse. Un estado PASS certifica que se cumplieron los controles declarados aquí, no que cada respuesta observada sea verdadera o que el instrumento coincida con F27.", "",
        "## Archivos", "",
        "- `validation_results.json`: controles censales, linaje y tamaño de la muestra.",
        "- `sample_design_RESTRICTED.csv`: asignación, probabilidades y pesos por estrato.",
        "- `sampled_source_rows_RESTRICTED.csv`: filas seleccionadas del CSV fuente; tratar como restringido.",
        "- `sample_internal_checks.csv`: conteos agregados de consistencia interna en la muestra.",
    ]
    (output / "README.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    output_hashes = {path.name: sha256_file(path) for path in sorted(output.iterdir()) if path.is_file()}
    (output / "artifact_hashes.json").write_text(json.dumps(output_hashes, indent=2, sort_keys=True), encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    parser.add_argument("--sample-households", type=int, default=SAMPLE_HOUSEHOLDS)
    arguments = parser.parse_args()
    print(run(arguments.candidate, arguments.sample_households))
