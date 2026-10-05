"""
JSON Storage service: Safe and atomic read/write utilities for JSON documents.
"""
import json
import os
import tempfile
import time
from typing import Any, Dict, List, Optional
from contextlib import contextmanager


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


@contextmanager
def json_file_lock(file_path: str, timeout_seconds: float = 30.0):
    """Acquire a cross-process exclusive lock next to a JSON document."""
    lock_path = f"{os.path.abspath(file_path)}.lock"
    os.makedirs(os.path.dirname(lock_path), exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    descriptor = None
    while descriptor is None:
        try:
            descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(descriptor, str(os.getpid()).encode("ascii"))
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timeout esperando bloqueo JSON: {lock_path}")
            time.sleep(0.05)
    try:
        yield
    finally:
        os.close(descriptor)
        try:
            os.unlink(lock_path)
        except FileNotFoundError:
            pass


def update_json_file(file_path: str, updater, default: Optional[Any] = None) -> Any:
    """Read-modify-write under a process lock; never masks corrupt JSON."""
    with json_file_lock(file_path):
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as stream:
                data = json.load(stream)
        else:
            data = {} if default is None else default
        updated = updater(data)
        if not write_json_file(file_path, updated):
            raise OSError(f"No se pudo guardar el documento JSON: {file_path}")
        return updated
