"""Thread-safe append-only audit events stored in a local JSON catalog."""
from datetime import datetime, timezone
import os
import uuid
from typing import Any, Dict, List

from .json_store import read_json_file, update_json_file

DEFAULT_AUDIT_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "audit_log.json",
)


class AuditService:
    def __init__(self, storage_path: str = DEFAULT_AUDIT_FILE):
        self.storage_path = storage_path
        if not os.path.exists(self.storage_path):
            update_json_file(
                self.storage_path,
                lambda value: value,
                default={"schema_version": 1, "events": [], "versions": [], "published_version_id": None},
            )

    def log_event(self, actor: str, action: str, entity: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Atomically append one event; malformed storage fails closed."""
        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actor": actor,
            "action": action,
            "entity": entity,
            "details": details,
        }

        def append(data: Dict[str, Any]) -> Dict[str, Any]:
            events = data.setdefault("events", [])
            if not isinstance(events, list):
                raise ValueError("El registro JSON está dañado: 'events' no es una lista.")
            events.append(event)
            data.setdefault("versions", [])
            data.setdefault("published_version_id", None)
            data.setdefault("schema_version", 1)
            return data

        update_json_file(self.storage_path, append, default={"events": [], "versions": []})
        return event

    def get_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return most recent events without mutating stored order."""
        data = read_json_file(self.storage_path, default={"events": []})
        events = data.get("events", [])
        return sorted(events, key=lambda item: item.get("timestamp", ""), reverse=True)[:limit]


audit_service = AuditService()
