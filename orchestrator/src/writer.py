from __future__ import annotations

from pathlib import Path

from validators import append_jsonl, ensure_parent

RUNS_SCHEMA = {
    "_schema": {
        "name": "runs",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "task",
            "module",
            "provider",
            "skill",
            "route_reason",
            "matched_keywords",
            "loaded_files",
            "result_path",
            "output_hash",
        ],
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

METRICS_SNAPSHOT_SCHEMA = {
    "_schema": {
        "name": "metrics_snapshots",
        "version": "1.0",
        "fields": ["id", "created_at", "status", "window_days", "summary", "report_path"],
        "notes": "append-only",
    }
}

GUARDRAIL_OVERRIDE_SCHEMA = {
    "_schema": {
        "name": "guardrail_overrides",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "domain",
            "decision_ref",
            "violations",
            "override_reason",
            "owner_confirmation",
            "provider",
            "notes",
        ],
        "notes": "append-only",
    }
}

OWNER_REPORT_SCHEMA = {
    "_schema": {
        "name": "owner_reports",
        "version": "1.0",
        "fields": ["id", "created_at", "status", "window_days", "summary", "report_path", "source_artifacts"],
        "notes": "append-only",
    }
}


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    root = repo_root.resolve()
    target = (repo_root / rel_path).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Path escapes repository root: {rel_path}")
    return target


def write_output(repo_root: Path, output_rel: str, content: str) -> Path:
    p = _safe_repo_path(repo_root, output_rel)
    ensure_parent(p)
    p.write_text(content, encoding="utf-8")
    return p


def log_run(repo_root: Path, record: dict) -> None:
    runs = _safe_repo_path(repo_root, "orchestrator/logs/runs.jsonl")
    append_jsonl(runs, record, schema_header=RUNS_SCHEMA)


def log_retrieval_query(repo_root: Path, record: dict, rel_log_path: str) -> None:
    path = _safe_repo_path(repo_root, rel_log_path)
    append_jsonl(path, record, schema_header=RETRIEVAL_QUERY_SCHEMA)


def log_schedule_run(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/schedule_runs.jsonl")
    append_jsonl(path, record, schema_header=SCHEDULE_RUN_SCHEMA)


def log_metrics_snapshot(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/metrics_snapshots.jsonl")
    append_jsonl(path, record, schema_header=METRICS_SNAPSHOT_SCHEMA)


def log_guardrail_override(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "modules/decision/logs/guardrail_overrides.jsonl")
    append_jsonl(path, record, schema_header=GUARDRAIL_OVERRIDE_SCHEMA)


def log_owner_report(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/owner_reports.jsonl")
    append_jsonl(path, record, schema_header=OWNER_REPORT_SCHEMA)
