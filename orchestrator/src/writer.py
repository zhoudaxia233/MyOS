from __future__ import annotations

from pathlib import Path

from validators import append_jsonl, ensure_parent

RUNS_SCHEMA = {
    "_schema": {
        "name": "runs",
        "version": "1.0",
        "fields": ["id", "created_at", "status", "task", "module", "provider", "result_path"],
        "notes": "append-only",
    }
}

RETRIEVAL_QUERY_SCHEMA = {
    "_schema": {
        "name": "retrieval_queries",
        "version": "1.0",
        "fields": ["id", "created_at", "status", "query", "module", "top_k", "result_count"],
        "notes": "append-only",
    }
}

SCHEDULE_RUN_SCHEMA = {
    "_schema": {
        "name": "schedule_runs",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "cycle",
            "routine_id",
            "module",
            "skill",
            "provider",
            "result_path",
        ],
        "notes": "append-only",
    }
}


def write_output(repo_root: Path, output_rel: str, content: str) -> Path:
    p = repo_root / output_rel
    ensure_parent(p)
    p.write_text(content, encoding="utf-8")
    return p


def log_run(repo_root: Path, record: dict) -> None:
    runs = repo_root / "orchestrator" / "logs" / "runs.jsonl"
    append_jsonl(runs, record, schema_header=RUNS_SCHEMA)


def log_retrieval_query(repo_root: Path, record: dict, rel_log_path: str) -> None:
    path = repo_root / rel_log_path
    append_jsonl(path, record, schema_header=RETRIEVAL_QUERY_SCHEMA)


def log_schedule_run(repo_root: Path, record: dict) -> None:
    path = repo_root / "orchestrator" / "logs" / "schedule_runs.jsonl"
    append_jsonl(path, record, schema_header=SCHEDULE_RUN_SCHEMA)
