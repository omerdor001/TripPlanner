import hashlib
import json
import logging
import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


def make_key(*parts: Any) -> str:
    """Stable digest of JSON-serializable parts, safe to use as a filename."""
    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class JsonCache:
    """Two-level (memory, then disk) cache of JSON-serializable values with a TTL.

    Disk access is best-effort: if the directory can't be created or written
    (e.g. a read-only serverless filesystem) the cache silently degrades to
    memory only.
    """

    def __init__(
        self,
        directory: Optional[str],
        ttl_seconds: int,
        max_memory_entries: int = 256,
        enabled: bool = True,
    ) -> None:
        self._ttl = ttl_seconds
        self._max_memory_entries = max_memory_entries
        self._enabled = enabled
        self._memory: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()
        self._memory_lock = threading.Lock()
        self._key_locks: dict[str, threading.Lock] = {}
        self._directory: Optional[Path] = None

        if enabled and directory:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                self._directory = Path(directory)
            except OSError as error:
                logger.warning("Cache directory %s unusable, using memory only: %s", directory, error)

    def lock_for(self, key: str) -> threading.Lock:
        """Per-key lock so concurrent identical requests share one LLM call."""
        with self._memory_lock:
            return self._key_locks.setdefault(key, threading.Lock())

    def get(self, key: str) -> Optional[Any]:
        if not self._enabled:
            return None

        with self._memory_lock:
            entry = self._memory.get(key)
            if entry is not None:
                if self._is_fresh(entry[0]):
                    self._memory.move_to_end(key)
                    return entry[1]
                del self._memory[key]

        entry = self._read_disk(key)
        if entry is None:
            return None
        stored_at, value = entry
        self._remember(key, stored_at, value)
        return value

    def set(self, key: str, value: Any) -> None:
        if not self._enabled:
            return
        stored_at = time.time()
        self._remember(key, stored_at, value)
        self._write_disk(key, stored_at, value)

    def delete(self, key: str) -> None:
        with self._memory_lock:
            self._memory.pop(key, None)
        if self._directory is not None:
            try:
                self._path(key).unlink(missing_ok=True)
            except OSError:
                pass

    def _is_fresh(self, stored_at: float) -> bool:
        return time.time() - stored_at < self._ttl

    def _remember(self, key: str, stored_at: float, value: Any) -> None:
        with self._memory_lock:
            self._memory[key] = (stored_at, value)
            self._memory.move_to_end(key)
            while len(self._memory) > self._max_memory_entries:
                self._memory.popitem(last=False)

    def _path(self, key: str) -> Path:
        assert self._directory is not None
        return self._directory / f"{key}.json"

    def _read_disk(self, key: str) -> Optional[tuple[float, Any]]:
        if self._directory is None:
            return None
        path = self._path(key)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            stored_at, value = float(data["stored_at"]), data["value"]
        except FileNotFoundError:
            return None
        except (OSError, ValueError, KeyError, TypeError) as error:
            logger.warning("Ignoring unreadable cache file %s: %s", path, error)
            return None
        if not self._is_fresh(stored_at):
            return None
        return stored_at, value

    def _write_disk(self, key: str, stored_at: float, value: Any) -> None:
        if self._directory is None:
            return
        path = self._path(key)
        tmp_path = path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
        try:
            tmp_path.write_text(
                json.dumps({"stored_at": stored_at, "value": value}, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(tmp_path, path)  # atomic, so readers never see a partial file
        except OSError as error:
            logger.warning("Could not write cache file %s: %s", path, error)
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
