"""Synthetic tests for JSON audit persistence and immutable publication."""
import hashlib
import json
import tempfile
import threading
import unittest
from pathlib import Path

from dashboard.services.audit_service import AuditService
from data.proprosessing.version_registry import publish_validated_candidate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class JsonPublicationTests(unittest.TestCase):
    def make_candidate(self, root: Path) -> tuple[Path, dict]:
        candidate = root / "candidate"
        candidate.mkdir()
        payload = b"folio,nro,value\nh1,1,ok\n"
        (candidate / "persona_clean_master.csv").write_bytes(payload)
        csv_hash = digest(candidate / "persona_clean_master.csv")
        manifest = {
            "dataset_id": "persona_test",
            "run_id": "synthetic-run",
            "version_id": "persona-synthetic1",
            "artifact_sha256": {"persona_clean_master.csv": csv_hash},
        }
        (candidate / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        validation = {
            "validation_status": "passed",
            "checks": {"dimensions": True, "hash": True},
            "candidate_csv_sha256": csv_hash,
            "candidate_rows": 1,
            "candidate_columns": 3,
            "artifact_hashes_expected": 1,
        }
        return candidate, validation

    def test_publishes_immutable_copy_and_switches_json_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, validation = self.make_candidate(root)
            versions = root / "versions"
            registry = root / "audit.json"
            destination = publish_validated_candidate(
                candidate, validation, versions_root=versions, registry_path=registry,
                actor="test_actor",
            )
            stored = json.loads(registry.read_text(encoding="utf-8"))
            self.assertEqual(destination.name, "persona-synthetic1")
            self.assertEqual(digest(destination / "persona_clean_master.csv"), validation["candidate_csv_sha256"])
            self.assertEqual(stored["published_version_id"], "persona-synthetic1")
            self.assertEqual(stored["versions"][0]["status"], "published_internal_with_semantic_limitations")
            self.assertEqual(stored["events"][-1]["action"], "PUBLISH_VERSION")
            self.assertTrue((destination / "publication_validation.json").is_file())
            self.assertEqual(
                publish_validated_candidate(candidate, validation, versions_root=versions,
                                             registry_path=registry), destination
            )
            self.assertEqual(len(json.loads(registry.read_text(encoding="utf-8"))["events"]), 1)

    def test_failed_validation_does_not_publish_or_switch_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate, validation = self.make_candidate(root)
            validation["validation_status"] = "failed"
            with self.assertRaises(ValueError):
                publish_validated_candidate(candidate, validation, versions_root=root / "versions",
                                            registry_path=root / "audit.json")
            self.assertFalse((root / "versions").exists())
            self.assertFalse((root / "audit.json").exists())

    def test_audit_events_are_persisted_without_lost_thread_updates(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = str(Path(temp) / "audit.json")
            service = AuditService(path)
            threads = [threading.Thread(target=lambda n=n: service.log_event(
                "synthetic", "TEST", str(n), {"sequence": n}
            )) for n in range(12)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            stored = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(len(stored["events"]), 12)
            self.assertEqual(len({event["event_id"] for event in stored["events"]}), 12)


if __name__ == "__main__":
    unittest.main()
