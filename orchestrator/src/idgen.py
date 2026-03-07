from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_ID_LOCK = Lock()
_ID_COUNTERS: dict[tuple[str, str, str], int] = {}


def _scan_max_seq(path: Path, prefix: str, date: str) -> int:
    if not path.exists() or not path.is_file():
        return 0

    max_seq = 0
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if i == 1 and '"_schema"' in line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        rec_id = str(obj.get("id", ""))
        if not rec_id.startswith(f"{prefix}_{date}_"):
            continue
        tail = rec_id.rsplit("_", 1)[-1]
        if tail.isdigit():
            max_seq = max(max_seq, int(tail))
    return max_seq


def next_id_for_path(path: Path, prefix: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    path_key = str(path.resolve())
    key = (path_key, prefix, date)

    with _ID_LOCK:
        file_max = _scan_max_seq(path, prefix, date)
        current = _ID_COUNTERS.get(key, 0)
        seq = max(current, file_max) + 1
        _ID_COUNTERS[key] = seq

    return f"{prefix}_{date}_{seq:03d}"


def next_id_for_rel_path(root: Path, prefix: str, log_rel_path: str) -> str:
    return next_id_for_path(root / log_rel_path, prefix)
