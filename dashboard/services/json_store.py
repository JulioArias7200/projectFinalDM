"""
JSON Storage service: Safe and atomic read/write utilities for JSON documents.
"""
import json
import os
import tempfile
from typing import Any, Dict, List, Optional


def read_json_file(file_path: str, default: Optional[Any] = None) -> Any:
    """Reads a JSON file safely. Returns default value if not found or corrupted."""
    if not os.path.exists(file_path):
        return default if default is not None else {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[JSON_STORE] Error reading {file_path}: {e}")
        return default if default is not None else {}


def write_json_file(file_path: str, data: Any, indent: int = 2) -> bool:
    """Atomically writes data to a JSON file using a temp file."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    temp_dir = os.path.dirname(os.path.abspath(file_path))
    temp_fd, temp_path = tempfile.mkstemp(dir=temp_dir, prefix="tmp_json_", suffix=".tmp")
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        # Atomic rename
        if os.path.exists(file_path):
            os.replace(temp_path, file_path)
        else:
            os.rename(temp_path, file_path)
        return True
    except Exception as e:
        print(f"[JSON_STORE] Error writing {file_path}: {e}")
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False
