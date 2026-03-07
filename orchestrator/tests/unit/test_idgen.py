from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from idgen import next_id_for_rel_path


def _write_runs_log(path: Path) -> None:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    schema = {
        "_schema": {
            "name": "runs",
            "version": "1.0",
            "fields": ["id", "created_at", "status"],
            "notes": "append-only",
        }
    }
    existing = {
        "id": f"run_{date}_005",
        "created_at": "2026-03-07T00:00:00Z",
        "status": "active",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        f.write(json.dumps(existing) + "\n")


def test_next_id_for_rel_path_is_thread_safe() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        runs_log = root / "orchestrator/logs/runs.jsonl"
        _write_runs_log(runs_log)

        ids: list[str] = []
        ids_lock = threading.Lock()
        workers = 20
        barrier = threading.Barrier(workers)

        def _worker() -> None:
            barrier.wait()
            rid = next_id_for_rel_path(root, "run", "orchestrator/logs/runs.jsonl")
            with ids_lock:
                ids.append(rid)

        threads = [threading.Thread(target=_worker) for _ in range(workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(ids) == workers
        assert len(set(ids)) == workers
