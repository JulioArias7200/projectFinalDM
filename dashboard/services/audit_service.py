"""
Audit service: Append-only event logger and timeline querier using pure JSON persistence.
"""
from datetime import datetime, timezone
import os
import uuid
from typing import Any, Dict, List
from .json_store import read_json_file, write_json_file

DEFAULT_AUDIT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "audit_log.json"
)


class AuditService:
    def __init__(self, storage_path: str = DEFAULT_AUDIT_FILE):
        self.storage_path = storage_path
        self._ensure_init()

    def _ensure_init(self) -> None:
        if not os.path.exists(self.storage_path):
            initial_events = [
                {
                    "event_id": str(uuid.uuid4())[:8],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": "system",
                    "action": "INIT_SYSTEM",
                    "entity": "persona_dataset",
                    "details": {
                        "message": "Inicialización del sistema de bitácora y catálogo de personas",
                        "status": "success"
                    }
                },
                {
                    "event_id": str(uuid.uuid4())[:8],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "actor": "pipeline_worker",
                    "action": "PREPROCESSING_RUN",
                    "entity": "20261004T171822Z_568e82e3039d_d3abfb0b5f",
                    "details": {
                        "rules_applied": ["L-01", "L-02", "L-03", "L-04", "L-05", "L-06", "L-07", "L-08", "L-09", "L-10", "L-11", "L-12", "L-80"],
                        "initial_rows": 39497,
                        "initial_columns": 275,
                        "retained_columns": 150,
                        "status": "candidate_generated"
                    }
                }
            ]
            write_json_file(self.storage_path, {"events": initial_events})

    def log_event(self, actor: str, action: str, entity: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Appends an event to the JSON audit log."""
        data = read_json_file(self.storage_path, default={"events": []})
        events = data.get("events", [])
        
        event = {
            "event_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "entity": entity,
            "details": details
        }
        events.append(event)
        data["events"] = events
        write_json_file(self.storage_path, data)
        return event

    def get_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent events in reverse chronological order."""
        data = read_json_file(self.storage_path, default={"events": []})
        events = data.get("events", [])
        events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return events[:limit]


audit_service = AuditService()
