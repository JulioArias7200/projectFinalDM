"""Immutable local version publication backed by an atomic JSON catalog."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dashboard.services.json_store import read_json_file, update_json_file


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "data" / "audit_log.json"
VERSIONS_ROOT = ROOT / "data" / "proprosessing" / "versions"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _append_publication(registry_path: Path, record: dict[str, Any]) -> None:
    def append(data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValueError("El registro JSON debe ser un objeto.")
        events = data.setdefault("events", [])
        versions = data.setdefault("versions", [])
        if not isinstance(events, list) or not isinstance(versions, list):
            raise ValueError("El registro JSON tiene una estructura incompatible.")
        previous = data.get("published_version_id")
        if previous == record["version_id"]:
            return data  # Idempotent retry: same version already published.
        for item in versions:
            if item.get("version_id") == record["version_id"]:
                raise ValueError("La versión ya está registrada con otro estado.")
        if previous:
            for item in versions:
                if item.get("version_id") == previous:
                    item["status"] = "superseded"
        versions.append(record)
        data["schema_version"] = max(int(data.get("schema_version", 0)), 1)
        data["published_version_id"] = record["version_id"]
        data["published_version_path"] = record["relative_path"]
        events.append({
            "event_id": record["publication_event_id"],
            "timestamp": record["published_at"],
            "actor": record["actor"],
            "action": "PUBLISH_VERSION",
            "entity": record["version_id"],
            "details": {
                "dataset_id": record["dataset_id"],
                "source_run_id": record["source_run_id"],
                "sha256": record["csv_sha256"],
                "rows": record["rows"],
                "columns": record["columns"],
                "semantic_status": record["semantic_status"],
                "validation_status": record["validation_status"],
            },
        })
        return data

    update_json_file(str(registry_path), append, default={"events": [], "versions": []})


def publish_validated_candidate(
    candidate_dir: Path,
    validation: dict[str, Any],
    *,
    versions_root: Path = VERSIONS_ROOT,
    registry_path: Path = REGISTRY_PATH,
    actor: str = "project_owner",
) -> Path:
    """Copy a fully validated run, then atomically activate it in the JSON catalog."""
    candidate_dir = candidate_dir.resolve()
    if validation.get("validation_status") != "passed":
        raise ValueError("Se rechaza publicar: la validación censal no pasó.")
    checks = validation.get("checks", {})
    if not checks or not all(checks.values()):
        raise ValueError("Se rechaza publicar: falta evidencia de todos los controles PASS.")
    manifest_path = candidate_dir / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"No existe manifiesto de candidata: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    version_id = str(manifest["version_id"])
    csv_name = "persona_clean_master.csv"
    csv_path = candidate_dir / csv_name
    expected_hash = validation.get("candidate_csv_sha256")
    if not csv_path.is_file() or not expected_hash or sha256_file(csv_path) != expected_hash:
        raise ValueError("El CSV candidato no coincide con el hash validado.")

    versions_root = versions_root.resolve()
    versions_root.mkdir(parents=True, exist_ok=True)
    destination = versions_root / version_id
    staging = versions_root / f".{version_id}.{uuid.uuid4().hex}.staging"
    current_registry = read_json_file(str(registry_path), default={"events": [], "versions": []})
    if current_registry.get("published_version_id") == version_id:
        current_record = next((v for v in current_registry.get("versions", [])
                               if v.get("version_id") == version_id), {})
        if current_record.get("csv_sha256") == expected_hash and destination.is_dir():
            return destination
        raise ValueError("El catálogo apunta a una versión cuyo artefacto no coincide.")
    try:
        if not destination.exists():
            shutil.copytree(candidate_dir, staging)
            work_dir = staging
        else:
            # Recover safely from a prior interrupted commit only if its CSV is identical.
            if not (destination / csv_name).is_file() or sha256_file(destination / csv_name) != expected_hash:
                raise FileExistsError(f"La versión inmutable ya existe con otro contenido: {destination}")
            work_dir = destination
        copied_manifest = json.loads((work_dir / "manifest.json").read_text(encoding="utf-8-sig"))
        expected_artifacts = copied_manifest.get("artifact_sha256", {})
        verified_artifacts = 0
        for relative, digest in expected_artifacts.items():
            copied = work_dir / relative
            if not copied.is_file() or sha256_file(copied) != digest:
                raise ValueError(f"Artefacto no coincide tras copiar: {relative}")
            verified_artifacts += 1
        if verified_artifacts != validation.get("artifact_hashes_expected"):
            raise ValueError("La cantidad de artefactos verificados no concuerda con la validación.")

        now = datetime.now(timezone.utc).isoformat()
        publication = {
            "status": "published_internal_with_semantic_limitations",
            "published_at": now,
            "actor": actor,
            "validation_status": "passed",
            "semantic_status": "pending_domains_and_universes; internal use only",
            "validation_checks_passed": len(checks),
            "artifact_hashes_verified": verified_artifacts,
            "csv_sha256": expected_hash,
        }
        if work_dir == staging:
            copied_manifest["pipeline_status"] = publication["status"]
            copied_manifest["publication"] = publication
            (staging / "manifest.json").write_text(
                json.dumps(copied_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            (staging / "publication_validation.json").write_text(
                json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            # Same-volume directory rename: the complete version becomes visible at once.
            os.replace(staging, destination)

        record = {
            "version_id": version_id,
            "dataset_id": manifest.get("dataset_id", "EH2025_Persona"),
            "status": publication["status"],
            "published_at": now,
            "actor": actor,
            "source_run_id": manifest.get("run_id"),
            "relative_path": os.path.relpath(destination, ROOT).replace(os.sep, "/"),
            "csv_file": csv_name,
            "csv_sha256": expected_hash,
            "rows": int(validation["candidate_rows"]),
            "columns": int(validation["candidate_columns"]),
            "semantic_status": publication["semantic_status"],
            "validation_status": "passed",
            "validation_checks_passed": len(checks),
            "artifact_hashes_verified": verified_artifacts,
            "publication_event_id": uuid.uuid4().hex,
        }
        _append_publication(registry_path, record)
        return destination
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
