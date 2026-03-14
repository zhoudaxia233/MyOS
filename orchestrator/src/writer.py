from __future__ import annotations

from pathlib import Path

from validators import append_jsonl, ensure_parent

RUNS_SCHEMA = {
    "_schema": {
        "name": "runs",
        "version": "1.3",
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
            "runtime_influences",
            "result_path",
            "output_hash",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

RETRIEVAL_QUERY_SCHEMA = {
    "_schema": {
        "name": "retrieval_queries",
        "version": "1.1",
        "fields": ["id", "created_at", "status", "query", "module", "top_k", "result_count", "object_type", "proposal_target"],
        "notes": "append-only",
    }
}

SCHEDULE_RUN_SCHEMA = {
    "_schema": {
        "name": "schedule_runs",
        "version": "1.1",
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
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

METRICS_SNAPSHOT_SCHEMA = {
    "_schema": {
        "name": "metrics_snapshots",
        "version": "1.1",
        "fields": ["id", "created_at", "status", "window_days", "summary", "report_path", "object_type", "proposal_target"],
        "notes": "append-only",
    }
}

GUARDRAIL_OVERRIDE_SCHEMA = {
    "_schema": {
        "name": "guardrail_overrides",
        "version": "1.1",
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
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

OWNER_REPORT_SCHEMA = {
    "_schema": {
        "name": "owner_reports",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "window_days",
            "summary",
            "report_path",
            "source_artifacts",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

OWNER_VERDICTS_SCHEMA = {
    "_schema": {
        "name": "owner_verdicts",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "suggestion_ref",
            "verdict",
            "owner_note",
            "correction_ref",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

OWNER_CORRECTIONS_SCHEMA = {
    "_schema": {
        "name": "owner_corrections",
        "version": "1.0",
        "fields": [
            "id",
            "created_at",
            "status",
            "suggestion_ref",
            "verdict_ref",
            "target_layer",
            "replacement_judgment",
            "unlike_me_reason",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

DECISIONS_SCHEMA = {
    "_schema": {
        "name": "decisions",
        "version": "1.2",
        "fields": [
            "id",
            "created_at",
            "status",
            "domain",
            "decision",
            "options",
            "reasoning",
            "risks",
            "expected_outcome",
            "time_horizon",
            "confidence",
            "guardrail_check_id",
            "follow_up_date",
            "outcome",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

DECISION_GATE_CHECKS_SCHEMA = {
    "_schema": {
        "name": "decision_gate_checks",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "domain",
            "decision",
            "guardrail_check_id",
            "precommit_required",
            "precommit_status",
            "guardrail_status",
            "gate_status",
            "violations",
            "missing_override_fields",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

DECISION_CONSTITUTION_CHECKS_SCHEMA = {
    "_schema": {
        "name": "decision_constitution_checks",
        "version": "1.1",
        "fields": [
            "id",
            "created_at",
            "status",
            "decision_gate_check_id",
            "decision_ref",
            "domain",
            "decision",
            "principle_refs",
            "exception_ref",
            "context_status",
            "violations",
            "source_refs",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}

SUGGESTIONS_SCHEMA = {
    "_schema": {
        "name": "suggestions",
        "version": "1.2",
        "fields": [
            "id",
            "created_at",
            "status",
            "task_raw",
            "interpreted_task",
            "module",
            "skill",
            "route_reason",
            "matched_keywords",
            "loaded_files",
            "runtime_influences",
            "retrieval_hit_ids",
            "retrieval_hit_count",
            "invoked_artifacts",
            "invoked_rules",
            "invoked_traits",
            "tensions",
            "uncertainties",
            "recommendation_path",
            "audit_focus_points",
            "run_ref",
            "output_hash",
            "object_type",
            "proposal_target",
        ],
        "notes": "append-only",
    }
}


def _safe_repo_path(repo_root: Path, rel_path: str) -> Path:
    root = repo_root.resolve()
    target = (repo_root / rel_path).resolve()
    if not target.is_relative_to(root):
        raise ValueError(f"Path escapes repository root: {rel_path}")
    return target


def _validate_output_rel(repo_root: Path, output_rel: str) -> None:
    rel = str(output_rel).replace("\\", "/").strip()
    if not rel:
        raise ValueError("Output path is required.")

    parts = Path(rel).parts
    if len(parts) < 4 or parts[0] != "modules" or parts[2] != "outputs":
        raise ValueError(f"Output path must be under modules/<name>/outputs/: {output_rel}")
    if any(p in {"", ".", ".."} for p in parts):
        raise ValueError(f"Invalid output path segments: {output_rel}")

    module_name = parts[1]
    module_dir = repo_root / "modules" / module_name
    output_dir = module_dir / "outputs"
    if not module_dir.exists() or not module_dir.is_dir():
        raise ValueError(f"Unknown module for output path: {module_name}")
    if not output_dir.exists() or not output_dir.is_dir():
        raise ValueError(f"Missing outputs directory for module: {module_name}")


def _with_classification(record: dict, *, object_type: str, proposal_target: str | None = None) -> dict:
    out = dict(record)
    out.setdefault("object_type", object_type)
    out.setdefault("proposal_target", proposal_target)
    return out


def _as_list_of_text(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    out: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)
    return out


def _ordered_unique(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in values:
        text = str(raw).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    return out


def _skill_label(skill_path: str) -> str | None:
    text = str(skill_path).strip()
    if not text:
        return None
    if text.endswith("/MODULE.md"):
        return "MODULE"
    name = Path(text).name
    if name.lower().endswith(".md"):
        name = name[:-3]
    return name or None


def _derive_invoked_rules(record: dict) -> list[str]:
    rules: list[str] = []

    route_reason = str(record.get("route_reason", "")).strip()
    if route_reason:
        rules.append(f"route_reason:{route_reason.split('|', 1)[0]}")

    for keyword in _as_list_of_text(record.get("matched_keywords"))[:5]:
        rules.append(f"route_keyword:{keyword}")

    skill = _skill_label(str(record.get("skill", "")))
    if skill:
        rules.append(f"plan_skill:{skill}")

    retrieval_hit_count = int(record.get("retrieval_hit_count", 0) or 0)
    if retrieval_hit_count > 0:
        rules.append("retrieval:context_hits")

    return _ordered_unique(rules)


def _derive_invoked_traits(record: dict) -> list[str]:
    traits: list[str] = []
    files = _as_list_of_text(record.get("loaded_files")) + _as_list_of_text(record.get("invoked_artifacts"))

    for rel in _ordered_unique(files):
        text = rel.replace("\\", "/")
        if text.startswith("modules/profile/data/"):
            stem = Path(text).stem
            if stem:
                traits.append(f"profile_data:{stem}")
        elif text.startswith("modules/profile/logs/"):
            stem = Path(text).stem
            if stem:
                traits.append(f"profile_signal:{stem}")
        elif text.startswith("modules/profile/skills/"):
            stem = Path(text).stem
            if stem:
                traits.append(f"profile_skill:{stem}")

    return _ordered_unique(traits)


def write_output(repo_root: Path, output_rel: str, content: str) -> Path:
    _validate_output_rel(repo_root, output_rel)
    p = _safe_repo_path(repo_root, output_rel)
    ensure_parent(p)
    p.write_text(content, encoding="utf-8")
    return p


def log_run(repo_root: Path, record: dict) -> None:
    runs = _safe_repo_path(repo_root, "orchestrator/logs/runs.jsonl")
    append_jsonl(runs, _with_classification(record, object_type="system"), schema_header=RUNS_SCHEMA)


def log_retrieval_query(repo_root: Path, record: dict, rel_log_path: str) -> None:
    path = _safe_repo_path(repo_root, rel_log_path)
    append_jsonl(path, _with_classification(record, object_type="system"), schema_header=RETRIEVAL_QUERY_SCHEMA)


def log_schedule_run(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/schedule_runs.jsonl")
    append_jsonl(path, _with_classification(record, object_type="system"), schema_header=SCHEDULE_RUN_SCHEMA)


def log_metrics_snapshot(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/metrics_snapshots.jsonl")
    append_jsonl(path, _with_classification(record, object_type="system"), schema_header=METRICS_SNAPSHOT_SCHEMA)


def log_guardrail_override(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "modules/decision/logs/guardrail_overrides.jsonl")
    append_jsonl(path, _with_classification(record, object_type="decision"), schema_header=GUARDRAIL_OVERRIDE_SCHEMA)


def log_owner_report(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/owner_reports.jsonl")
    append_jsonl(path, _with_classification(record, object_type="system"), schema_header=OWNER_REPORT_SCHEMA)


def log_owner_verdict(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/owner_verdicts.jsonl")
    append_jsonl(path, _with_classification(record, object_type="decision"), schema_header=OWNER_VERDICTS_SCHEMA)


def log_owner_correction(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/owner_corrections.jsonl")
    append_jsonl(path, _with_classification(record, object_type="decision"), schema_header=OWNER_CORRECTIONS_SCHEMA)


def log_decision(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "modules/decision/logs/decisions.jsonl")
    append_jsonl(path, _with_classification(record, object_type="decision"), schema_header=DECISIONS_SCHEMA)


def log_decision_gate_check(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "modules/decision/logs/decision_gate_checks.jsonl")
    append_jsonl(path, _with_classification(record, object_type="decision"), schema_header=DECISION_GATE_CHECKS_SCHEMA)


def log_decision_constitution_check(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "modules/decision/logs/decision_constitution_checks.jsonl")
    append_jsonl(path, _with_classification(record, object_type="decision"), schema_header=DECISION_CONSTITUTION_CHECKS_SCHEMA)


def log_suggestion(repo_root: Path, record: dict) -> None:
    path = _safe_repo_path(repo_root, "orchestrator/logs/suggestions.jsonl")
    enriched = _with_classification(record, object_type="system")
    enriched.setdefault("invoked_rules", _derive_invoked_rules(enriched))
    enriched.setdefault("invoked_traits", _derive_invoked_traits(enriched))
    append_jsonl(path, enriched, schema_header=SUGGESTIONS_SCHEMA)
