from __future__ import annotations

import argparse
import hashlib
import json
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from cognition import (
    build_cognitive_timeline,
    detect_disequilibrium,
    render_cognitive_timeline,
    render_disequilibrium_report,
)
from config import load_runtime_config
from idgen import next_id_for_rel_path
from learning_console import (
    apply_learning_candidate_verdict,
    build_learning_handoff_packet,
    ingest_learning_handoff_response,
    list_recent_learning_candidates,
    promote_learning_candidate,
    summarize_learning_pipeline,
    summarize_learning_pipeline_trend,
)
from loader import load_context_bundle
from learning_ingest import ingest_learning_text
from manifests import discover_module_manifests
from metrics import compute_cognition_trend, compute_drift_metrics, render_metrics_report
from owner_report import (
    build_owner_snapshot,
    list_open_owner_todos,
    render_owner_report,
    render_owner_todos,
    resolve_owner_todo,
    summarize_suggestion_review_trend,
    summarize_suggestion_reviews,
    sync_owner_todos,
)
from planner import plan_task
from plugin_contract import validate_repo
from prompting import schema_debugger_output_sections, schema_debugger_questions
from retrieval import build_index, load_retrieval_config, search_index
from route_selector import select_route
from runner import run_with_provider
from schedulers.manual import get_cycle
from scheduling import task_from_routine
from settings import (
    apply_provider_api_key_env,
    get_deepseek_api_key,
    get_openai_api_key,
    load_settings,
    redact_settings,
    save_settings,
)
from token_count import count_text_tokens
from writer import (
    log_metrics_snapshot,
    log_owner_correction,
    log_owner_report,
    log_owner_verdict,
    log_retrieval_query,
    log_run,
    log_schedule_run,
    log_suggestion,
    write_output,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _root_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        try:
            return str(path.resolve().relative_to(root.resolve()))
        except ValueError:
            return str(path)


def _coerce_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, ivalue))


def _coerce_bool(value: Any, *, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        norm = value.strip().lower()
        if norm in {"1", "true", "yes", "y", "on"}:
            return True
        if norm in {"0", "false", "no", "n", "off"}:
            return False
    if value is None:
        return default
    return bool(value)


def _normalize_optional_str(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None


def _default_task_model(settings: dict, cfg: dict, provider: str) -> str:
    normalized = str(provider or "").strip().lower()
    if normalized == "deepseek":
        return str(settings.get("deepseek_model", "deepseek-chat")) or "deepseek-chat"
    openai_model = str(settings.get("openai_model", "")).strip() or str(settings.get("task_model", "")).strip()
    return openai_model or str(cfg.get("default_openai_model", "gpt-4.1-mini"))


def _module_override_provider(settings: dict, module: str) -> str | None:
    key = f"{module}_provider"
    provider = str(settings.get(key, "")).strip().lower()
    if provider in {"dry-run", "handoff", "openai", "deepseek"}:
        return provider
    return None


def _module_override_model(settings: dict, module: str) -> str | None:
    key = f"{module}_model"
    model = str(settings.get(key, "")).strip()
    return model or None


def _resolve_provider_model(
    settings: dict,
    cfg: dict,
    module: str,
    *,
    provider_hint: str | None,
    model_hint: str | None,
) -> tuple[str, str]:
    provider = _normalize_optional_str(provider_hint)
    if provider and provider.lower() == "auto":
        provider = None
    if provider:
        provider = provider.lower()
    else:
        provider = _module_override_provider(settings, module)
    if not provider:
        provider = str(settings.get("default_provider", "")).strip() or str(cfg.get("default_provider", "handoff"))

    model = _normalize_optional_str(model_hint)
    if not model:
        model = _module_override_model(settings, module)
    if not model:
        model = _default_task_model(settings, cfg, provider)
    return provider, model


def _route_reason_for_log(route: dict) -> str:
    base_reason = str(route.get("reason", "fallback_default"))
    scoring = route.get("scoring")
    if not isinstance(scoring, dict):
        return base_reason

    candidates: list[dict] = []
    manifest_candidates = scoring.get("manifest_candidates")
    routes_candidates = scoring.get("routes_candidates")
    if isinstance(manifest_candidates, list) and manifest_candidates:
        candidates = [c for c in manifest_candidates if isinstance(c, dict)]
    elif isinstance(routes_candidates, list) and routes_candidates:
        candidates = [c for c in routes_candidates if isinstance(c, dict)]

    if not candidates:
        return base_reason

    module = str(route.get("module", ""))
    selected = next((c for c in candidates if str(c.get("module", "")) == module), candidates[0])

    score = int(selected.get("score", 0))
    positive = int(selected.get("positive_hits", 0))
    negative = int(selected.get("negative_hits", 0))
    return f"{base_reason}|s={score}|p={positive}|n={negative}"


def _coerce_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if "," in text:
            return [part.strip() for part in text.split(",") if part.strip()]
        return [text]
    text = str(value).strip()
    return [text] if text else []


def _retrieval_hits(root: Path, query: str, module: str | None, top_k: int) -> list[dict]:
    try:
        return search_index(root, query=query, module=module, top_k=top_k)
    except FileNotFoundError:
        build_index(root)
        return search_index(root, query=query, module=module, top_k=top_k)


def _bundle_with_hits(bundle: dict, hits: list[dict]) -> dict:
    if not hits:
        return bundle
    lines = ["# Retrieval Hits", ""]
    for hit in hits:
        lines.append(f"- {hit['path']}:{hit['line']} score={hit['score']}")
        if hit.get("record_id"):
            lines.append(f"  record_id: {hit['record_id']}")
        lines.append(f"  text: {hit['text']}")
    bundle["files"].append({"path": "retrieval://top_hits", "content": "\n".join(lines)})
    return bundle


def _log_retrieval(root: Path, query: str, module: str | None, top_k: int, result_count: int) -> None:
    cfg = load_retrieval_config(root)
    rec = {
        "id": next_id_for_rel_path(root, "rq", cfg["query_log_path"]),
        "created_at": _utc_now(),
        "status": "active",
        "query": query,
        "module": module,
        "top_k": top_k,
        "result_count": result_count,
    }
    log_retrieval_query(root, rec, cfg["query_log_path"])


def _suggestion_tensions(route: dict, with_retrieval: bool, hits: list[dict]) -> list[str]:
    tensions: list[str] = []
    reason = str(route.get("reason", ""))
    if reason.startswith("fallback_default"):
        tensions.append("routing_low_signal")
    if with_retrieval and not hits:
        tensions.append("retrieval_no_hits")
    return tensions


def _preview_text(text: str, max_chars: int = 8000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n...[truncated]"


def _pct(value: float) -> str:
    return f"{(value * 100):.1f}%"


def _cognition_cards(root: Path) -> list[dict]:
    trend = compute_cognition_trend(root)
    comparisons = {
        str(item.get("key", "")): item for item in trend.get("comparisons", []) if isinstance(item, dict)
    }
    snapshot_7d = trend.get("windows", {}).get("7d", {})
    metrics_7d = snapshot_7d.get("metrics", {}) if isinstance(snapshot_7d, dict) else {}

    config = [
        ("unresolved_disequilibrium_rate", "Unresolved Disequilibrium", "<="),
        ("equilibration_quality_rate", "Equilibration Quality", ">="),
        ("schema_explicitness_rate", "Schema Explicitness", ">="),
    ]

    cards: list[dict] = []
    for key, label, operator in config:
        metric = metrics_7d.get(key, {})
        if not isinstance(metric, dict):
            continue
        cmp = comparisons.get(key, {})
        cards.append(
            {
                "key": key,
                "label": label,
                "status": str(metric.get("status", "warn")),
                "value": _pct(float(metric.get("value", 0.0))),
                "threshold": _pct(float(metric.get("threshold", 0.0))),
                "target_operator": operator,
                "trend": str(cmp.get("trend", "stable")),
                "delta_pp": round(float(cmp.get("delta", 0.0)) * 100.0, 1),
            }
        )
    return cards


def _safe_output_file(root: Path, rel_path: str) -> Path:
    rel = str(rel_path).strip()
    if not rel:
        raise ValueError("path is required")

    root_abs = root.resolve()
    target = (root / rel).resolve()
    if not target.is_relative_to(root_abs):
        raise ValueError("path escapes repository root")

    rel_target = target.relative_to(root_abs)
    parts = rel_target.parts
    if len(parts) < 4 or parts[0] != "modules" or parts[2] != "outputs":
        raise ValueError("path must point to an outputs file")

    if not target.exists() or not target.is_file():
        raise ValueError("output file not found")
    return target


def api_output(root: Path, rel_path: str) -> dict:
    path = _safe_output_file(root, rel_path)
    content = path.read_text(encoding="utf-8")
    return {
        "ok": True,
        "path": _root_relative(path, root),
        "content": content,
    }


def api_output_meta(root: Path, rel_path: str, model: str | None = None) -> dict:
    path = _safe_output_file(root, rel_path)
    content = path.read_text(encoding="utf-8")
    stats = count_text_tokens(content, model=model)
    return {
        "ok": True,
        "path": _root_relative(path, root),
        **stats,
    }


def _read_jsonl_records(path: Path) -> list[dict]:
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict] = []
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
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _find_jsonl_record_by_id(path: Path, record_id: str) -> dict | None:
    rid = str(record_id).strip()
    if not rid:
        return None
    for row in reversed(_read_jsonl_records(path)):
        if str(row.get("id", "")).strip() == rid:
            return row
    return None


def _find_latest_jsonl_record_by_field(path: Path, *, key: str, value: str) -> dict | None:
    match_value = str(value).strip()
    if not match_value:
        return None
    for row in reversed(_read_jsonl_records(path)):
        if str(row.get(key, "")).strip() == match_value and str(row.get("status", "active")).strip().lower() == "active":
            return row
    return None


def _suggestion_owner_review(root: Path, suggestion_id: str) -> dict:
    verdict_path = root / "orchestrator" / "logs" / "owner_verdicts.jsonl"
    correction_path = root / "orchestrator" / "logs" / "owner_corrections.jsonl"

    verdict = _find_latest_jsonl_record_by_field(verdict_path, key="suggestion_ref", value=suggestion_id)
    correction: dict[str, Any] | None = None
    if verdict is not None:
        verdict_id = str(verdict.get("id", "")).strip()
        if verdict_id:
            correction = _find_latest_jsonl_record_by_field(correction_path, key="verdict_ref", value=verdict_id)
        if correction is None:
            correction = _find_latest_jsonl_record_by_field(correction_path, key="suggestion_ref", value=suggestion_id)

    return {
        "verdict": verdict,
        "correction": correction,
    }


def api_suggestion(root: Path, suggestion_id: str) -> dict:
    sid = str(suggestion_id).strip()
    if not sid:
        raise ValueError("id is required")

    suggestions_path = root / "orchestrator" / "logs" / "suggestions.jsonl"
    suggestion = _find_jsonl_record_by_id(suggestions_path, sid)
    if suggestion is None:
        raise ValueError(f"suggestion not found: {sid}")

    run_ref = str(suggestion.get("run_ref", "")).strip()
    run_record: dict[str, Any] | None = None
    if run_ref:
        run_record = _find_jsonl_record_by_id(root / "orchestrator" / "logs" / "runs.jsonl", run_ref)

    output_preview = None
    output_path = _normalize_optional_str(suggestion.get("recommendation_path"))
    if output_path:
        try:
            path = _safe_output_file(root, output_path)
            output_preview = _preview_text(path.read_text(encoding="utf-8"), max_chars=4000)
        except ValueError:
            output_preview = None

    return {
        "ok": True,
        "suggestion": suggestion,
        "run": run_record,
        "owner_review": _suggestion_owner_review(root, sid),
        "output_path": output_path,
        "output_preview": output_preview,
    }


def _inspect_task(
    *,
    root: Path,
    task: str,
    forced_module: str | None,
    with_retrieval: bool,
    retrieval_top_k: int,
) -> dict:
    cfg = load_runtime_config(root)
    route = select_route(task, forced_module=forced_module, repo_root=root)
    module = route["module"]
    plan = plan_task(task, module, repo_root=root)
    bundle = load_context_bundle(
        root,
        module,
        cfg["max_context_chars"],
        skill_path=plan["skill"],
        intent_text=task,
    )

    hits: list[dict] = []
    if with_retrieval:
        hits = _retrieval_hits(root, task, module, retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    return {
        "module": module,
        "route": route,
        "plan": plan,
        "retrieval_hits": len(hits),
        "loaded_files": [f["path"] for f in bundle["files"]],
        "debug_prompts": schema_debugger_questions(module, task),
        "debug_sections": schema_debugger_output_sections(module, task),
    }


def _execute_task(
    *,
    root: Path,
    task: str,
    forced_module: str | None,
    provider_hint: str | None,
    model_hint: str | None,
    with_retrieval: bool,
    retrieval_top_k: int,
    skill_hint: str | None = None,
    routine_id: str | None = None,
) -> dict:
    cfg = load_runtime_config(root)
    route = select_route(task, forced_module=forced_module, repo_root=root)
    module = route["module"]
    settings = load_settings(root)
    provider, model = _resolve_provider_model(
        settings,
        cfg,
        module,
        provider_hint=provider_hint,
        model_hint=model_hint,
    )
    plan = plan_task(task, module, skill_hint=skill_hint, routine_id=routine_id, repo_root=root)
    bundle = load_context_bundle(
        root,
        module,
        cfg["max_context_chars"],
        skill_path=plan["skill"],
        intent_text=task,
    )

    hits: list[dict] = []
    if with_retrieval:
        hits = _retrieval_hits(root, task, module, retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    apply_provider_api_key_env(root, provider)
    content = run_with_provider(provider, task, module, plan, bundle, model)
    out = write_output(root, plan["output_path"], content)
    output_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    run_record = {
        "id": next_id_for_rel_path(root, "run", "orchestrator/logs/runs.jsonl"),
        "created_at": _utc_now(),
        "status": "active",
        "task": task,
        "module": module,
        "provider": provider,
        "skill": plan["skill"],
        "route_reason": _route_reason_for_log(route),
        "matched_keywords": route["matched_keywords"],
        "loaded_files": [f["path"] for f in bundle["files"]],
        "result_path": _root_relative(out, root),
        "output_hash": output_hash,
    }
    log_run(root, run_record)

    if with_retrieval:
        _log_retrieval(root, task, module, retrieval_top_k, len(hits))

    debug_prompts = schema_debugger_questions(module, task)
    debug_sections = schema_debugger_output_sections(module, task)
    suggestion_id = next_id_for_rel_path(root, "sg", "orchestrator/logs/suggestions.jsonl")
    suggestion_record = {
        "id": suggestion_id,
        "created_at": _utc_now(),
        "status": "active",
        "task_raw": task,
        "interpreted_task": task,
        "module": module,
        "skill": plan["skill"],
        "route_reason": run_record["route_reason"],
        "matched_keywords": route["matched_keywords"],
        "loaded_files": [f["path"] for f in bundle["files"]],
        "retrieval_hit_ids": [str(hit.get("record_id", "")).strip() for hit in hits if str(hit.get("record_id", "")).strip()],
        "retrieval_hit_count": len(hits),
        "invoked_artifacts": [f["path"] for f in bundle["files"]],
        "tensions": _suggestion_tensions(route, with_retrieval, hits),
        "uncertainties": [],
        "recommendation_path": _root_relative(out, root),
        "audit_focus_points": debug_sections,
        "run_ref": run_record["id"],
        "output_hash": output_hash,
    }
    log_suggestion(root, suggestion_record)

    return {
        "module": module,
        "provider": provider,
        "route": route,
        "plan": plan,
        "suggestion_id": suggestion_id,
        "output_path": _root_relative(out, root),
        "output_hash": output_hash,
        "output_preview": _preview_text(content),
        "retrieval_hits": len(hits),
        "loaded_files": [f["path"] for f in bundle["files"]],
        "debug_prompts": debug_prompts,
        "debug_sections": debug_sections,
    }


def _run_metrics(root: Path, window_days: int, output_rel: str | None) -> dict:
    snapshot = compute_drift_metrics(root, window_days)
    trend = compute_cognition_trend(root)
    snapshot["cognitive_trend"] = trend
    report = render_metrics_report(snapshot)

    if output_rel:
        output_path = output_rel
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = f"modules/decision/outputs/metrics_{stamp}.md"

    out = write_output(root, output_path, report)
    report_path = _root_relative(out, root)

    summary = {k: v["status"] for k, v in snapshot["metrics"].items()}
    record = {
        "id": next_id_for_rel_path(root, "mt", "orchestrator/logs/metrics_snapshots.jsonl"),
        "created_at": _utc_now(),
        "status": "active",
        "window_days": window_days,
        "summary": summary,
        "report_path": report_path,
    }
    log_metrics_snapshot(root, record)

    return {
        "window_days": window_days,
        "summary": summary,
        "output_path": report_path,
        "output_preview": _preview_text(report),
        "cognitive_trend": trend,
    }


def _run_owner_report(root: Path, window_days: int, output_rel: str | None) -> dict:
    snapshot = build_owner_snapshot(root, window_days=window_days)
    report = render_owner_report(snapshot)

    if output_rel:
        output_path = output_rel
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = f"modules/decision/outputs/owner_report_{stamp}.md"

    out = write_output(root, output_path, report)
    report_path = _root_relative(out, root)

    todos_path = None
    if snapshot.get("escalation_todos"):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        todos_rel = f"modules/decision/outputs/owner_todos_{stamp}.md"
        todos_out = write_output(root, todos_rel, render_owner_todos(snapshot))
        todos_path = _root_relative(todos_out, root)
        snapshot["source_artifacts"]["owner_todos"] = todos_path

    summary = {k: v["status"] for k, v in snapshot["metrics"]["metrics"].items()}
    owner_report_id = next_id_for_rel_path(root, "or", "orchestrator/logs/owner_reports.jsonl")
    record = {
        "id": owner_report_id,
        "created_at": _utc_now(),
        "status": "active",
        "window_days": window_days,
        "summary": summary,
        "report_path": report_path,
        "source_artifacts": snapshot["source_artifacts"],
    }
    log_owner_report(root, record)
    queue_sync = sync_owner_todos(root, snapshot, owner_report_ref=owner_report_id)

    return {
        "window_days": window_days,
        "summary": summary,
        "output_path": report_path,
        "output_preview": _preview_text(report),
        "source_artifacts": snapshot["source_artifacts"],
        "candidate_pipeline_summary": snapshot.get("candidate_pipeline_summary", {}),
        "candidate_pipeline_trend": snapshot.get("candidate_pipeline_trend", {}),
        "suggestion_review_summary": snapshot.get("suggestion_review_summary", {}),
        "suggestion_review_trend": snapshot.get("suggestion_review_trend", {}),
        "owner_todos_path": todos_path,
        "owner_todo_queue": queue_sync,
    }


def _run_disequilibrium(
    root: Path,
    *,
    topic: str,
    window_days: int,
    schema_version_id: str | None,
    tags: list[str],
    output_rel: str | None,
) -> dict:
    result = detect_disequilibrium(
        root,
        topic=topic,
        window_days=window_days,
        schema_version_id=schema_version_id,
        tags=tags,
    )
    report = render_disequilibrium_report(result)

    if output_rel:
        output_path = output_rel
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = f"modules/cognition/outputs/disequilibrium_{stamp}.md"

    out = write_output(root, output_path, report)
    record = result["record"]
    return {
        "topic": topic,
        "window_days": window_days,
        "event_id": record["id"],
        "tension_score": record["tension_score"],
        "signal_count": len(result.get("signals", [])),
        "output_path": _root_relative(out, root),
        "output_preview": _preview_text(report),
    }


def _run_cognition_timeline(
    root: Path,
    *,
    topic: str | None,
    window_days: int,
    output_rel: str | None,
) -> dict:
    snapshot = build_cognitive_timeline(root, topic=topic, window_days=window_days)
    report = render_cognitive_timeline(snapshot)

    if output_rel:
        output_path = output_rel
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_path = f"modules/cognition/outputs/cognitive_timeline_{stamp}.md"

    out = write_output(root, output_path, report)
    return {
        "topic": topic,
        "window_days": window_days,
        "event_count": snapshot["counts"]["events"],
        "output_path": _root_relative(out, root),
        "output_preview": _preview_text(report),
    }


def _run_schedule_cycle(
    *,
    root: Path,
    cycle: str,
    provider_hint: str | None,
    model_hint: str | None,
    with_retrieval: bool,
    retrieval_top_k: int,
    limit: int | None,
    owner_window: int,
    no_owner_report: bool,
) -> dict:
    routines = get_cycle(root, cycle)
    settings = load_settings(root)
    cfg = load_runtime_config(root)
    if limit is not None:
        routines = routines[:limit]

    run_items: list[dict] = []
    for routine in routines:
        task = task_from_routine(cycle, routine)
        result = _execute_task(
            root=root,
            task=task,
            forced_module=routine["module"],
            provider_hint=provider_hint,
            model_hint=model_hint,
            with_retrieval=with_retrieval,
            retrieval_top_k=retrieval_top_k,
            skill_hint=routine["skill"],
            routine_id=routine["id"],
        )

        schedule_record = {
            "id": next_id_for_rel_path(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "cycle": cycle,
            "routine_id": routine["id"],
            "module": routine["module"],
            "skill": routine["skill"],
            "provider": result["provider"],
            "result_path": result["output_path"],
        }
        log_schedule_run(root, schedule_record)

        run_items.append(
            {
                "routine_id": routine["id"],
                "module": routine["module"],
                "skill": routine["skill"],
                "output_path": result["output_path"],
                "output_preview": result["output_preview"],
            }
        )

    owner_output: dict[str, Any] | None = None
    if cycle == "weekly" and not no_owner_report:
        owner_provider, _ = _resolve_provider_model(
            settings,
            cfg,
            "decision",
            provider_hint=provider_hint,
            model_hint=model_hint,
        )
        owner_output = _run_owner_report(root, window_days=owner_window, output_rel=None)
        schedule_record = {
            "id": next_id_for_rel_path(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "cycle": cycle,
            "routine_id": "rt_weekly_owner_report_auto",
            "module": "decision",
            "skill": "owner_report",
            "provider": owner_provider,
            "result_path": owner_output["output_path"],
        }
        log_schedule_run(root, schedule_record)
        if owner_output.get("owner_todos_path"):
            todos_record = {
                "id": next_id_for_rel_path(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
                "created_at": _utc_now(),
                "status": "active",
                "cycle": cycle,
                "routine_id": "rt_weekly_owner_todos_auto",
                "module": "decision",
                "skill": "owner_todos",
                "provider": owner_provider,
                "result_path": owner_output["owner_todos_path"],
            }
            log_schedule_run(root, todos_record)

    return {
        "cycle": cycle,
        "routine_count": len(run_items),
        "runs": run_items,
        "owner_report": owner_output,
    }


def api_status(root: Path) -> dict:
    cfg = load_runtime_config(root)
    settings = load_settings(root)
    manifests = discover_module_manifests(root)
    modules = [m for m in sorted(manifests.keys()) if m != "_template"]
    cognition_cards = _cognition_cards(root)
    return {
        "ok": True,
        "repo_root": str(root),
        "default_provider": settings["default_provider"] or cfg["default_provider"],
        "default_model": _default_task_model(settings, cfg, settings["default_provider"] or cfg["default_provider"]),
        "openai_model": settings.get("openai_model", settings.get("task_model", "gpt-4.1-mini")),
        "openai_base_url": settings.get("openai_base_url", "https://api.openai.com/v1"),
        "routing_model": settings["routing_model"],
        "deepseek_model": settings.get("deepseek_model", "deepseek-chat"),
        "ui_language": settings.get("ui_language", "zh"),
        "has_openai_api_key": bool(get_openai_api_key(root)),
        "has_deepseek_api_key": bool(get_deepseek_api_key(root)),
        "modules": modules,
        "cognition_cards": cognition_cards,
        "owner_todos": list_open_owner_todos(root),
        "learning_candidates": list_recent_learning_candidates(root, limit=12, include_resolved=True),
        "candidate_pipeline_summary": summarize_learning_pipeline(root, window_days=30),
        "candidate_pipeline_trend": summarize_learning_pipeline_trend(root),
        "suggestion_review_summary": summarize_suggestion_reviews(root, window_days=30, limit=12),
        "suggestion_review_trend": summarize_suggestion_review_trend(root),
    }


def api_get_settings(root: Path) -> dict:
    settings = load_settings(root)
    payload = redact_settings(settings)
    payload["has_openai_api_key"] = bool(get_openai_api_key(root))
    payload["has_deepseek_api_key"] = bool(get_deepseek_api_key(root))
    return {"ok": True, **payload}


def api_update_settings(root: Path, payload: dict[str, Any]) -> dict:
    updates: dict[str, str] = {}
    if "default_provider" in payload:
        updates["default_provider"] = str(payload.get("default_provider", ""))
    if "openai_model" in payload:
        updates["openai_model"] = str(payload.get("openai_model", ""))
    elif "task_model" in payload:
        updates["openai_model"] = str(payload.get("task_model", ""))
    if "deepseek_model" in payload:
        updates["deepseek_model"] = str(payload.get("deepseek_model", ""))
    if "routing_model" in payload:
        updates["routing_model"] = str(payload.get("routing_model", ""))
    if "openai_base_url" in payload:
        updates["openai_base_url"] = str(payload.get("openai_base_url", ""))
    if "deepseek_base_url" in payload:
        updates["deepseek_base_url"] = str(payload.get("deepseek_base_url", ""))
    for module_name in ("decision", "content", "cognition"):
        provider_key = f"{module_name}_provider"
        model_key = f"{module_name}_model"
        if provider_key in payload:
            updates[provider_key] = str(payload.get(provider_key, ""))
        if model_key in payload:
            updates[model_key] = str(payload.get(model_key, ""))
    if "ui_language" in payload:
        updates["ui_language"] = str(payload.get("ui_language", ""))

    if "openai_api_key" in payload:
        key = str(payload.get("openai_api_key", "")).strip()
        if key:
            updates["openai_api_key"] = key
    elif _coerce_bool(payload.get("clear_openai_api_key"), default=False):
        updates["openai_api_key"] = ""

    if "deepseek_api_key" in payload:
        key = str(payload.get("deepseek_api_key", "")).strip()
        if key:
            updates["deepseek_api_key"] = key
    elif _coerce_bool(payload.get("clear_deepseek_api_key"), default=False):
        updates["deepseek_api_key"] = ""

    settings = save_settings(root, updates)
    data = redact_settings(settings)
    data["has_openai_api_key"] = bool(get_openai_api_key(root))
    data["has_deepseek_api_key"] = bool(get_deepseek_api_key(root))
    return {"ok": True, **data}


def api_inspect(root: Path, payload: dict[str, Any]) -> dict:
    task = str(payload.get("task", "")).strip()
    if not task:
        raise ValueError("task is required")

    module = _normalize_optional_str(payload.get("module"))
    with_retrieval = _coerce_bool(payload.get("with_retrieval"), default=False)
    retrieval_top_k = _coerce_int(payload.get("retrieval_top_k"), default=6, minimum=1, maximum=32)

    result = _inspect_task(
        root=root,
        task=task,
        forced_module=module,
        with_retrieval=with_retrieval,
        retrieval_top_k=retrieval_top_k,
    )
    return {"ok": True, **result}


def api_run(root: Path, payload: dict[str, Any]) -> dict:
    task = str(payload.get("task", "")).strip()
    if not task:
        raise ValueError("task is required")

    module = _normalize_optional_str(payload.get("module"))
    provider_hint = _normalize_optional_str(payload.get("provider"))
    model_hint = _normalize_optional_str(payload.get("model"))
    with_retrieval = _coerce_bool(payload.get("with_retrieval"), default=False)
    retrieval_top_k = _coerce_int(payload.get("retrieval_top_k"), default=6, minimum=1, maximum=32)

    result = _execute_task(
        root=root,
        task=task,
        forced_module=module,
        provider_hint=provider_hint,
        model_hint=model_hint,
        with_retrieval=with_retrieval,
        retrieval_top_k=retrieval_top_k,
    )
    return {"ok": True, **result}


def api_action(root: Path, payload: dict[str, Any]) -> dict:
    action = str(payload.get("action", "")).strip().lower()
    if not action:
        raise ValueError("action is required")

    if action == "validate":
        strict = _coerce_bool(payload.get("strict"), default=True)
        result = validate_repo(root)
        status = "pass"
        if result["errors"]:
            status = "fail"
        elif strict and result["warnings"]:
            status = "fail"
        elif result["warnings"]:
            status = "warn"
        return {
            "ok": status != "fail",
            "action": action,
            "status": status,
            "strict": strict,
            "checked": result["checked"],
            "warnings": result["warnings"],
            "errors": result["errors"],
        }

    if action == "metrics":
        window_days = _coerce_int(payload.get("window_days"), default=7, minimum=1, maximum=365)
        output_rel = _normalize_optional_str(payload.get("output"))
        result = _run_metrics(root, window_days, output_rel)
        return {"ok": True, "action": action, **result, "cognition_cards": _cognition_cards(root)}

    if action == "owner_report":
        window_days = _coerce_int(payload.get("window_days"), default=7, minimum=1, maximum=365)
        output_rel = _normalize_optional_str(payload.get("output"))
        result = _run_owner_report(root, window_days, output_rel)
        return {"ok": True, "action": action, **result, "owner_todos": list_open_owner_todos(root)}

    if action == "suggestion_review_summary":
        window_days = _coerce_int(payload.get("window_days"), default=30, minimum=1, maximum=365)
        verdict_filter = _normalize_optional_str(payload.get("verdict_filter"))
        summary = summarize_suggestion_reviews(
            root,
            window_days=window_days,
            verdict_filter=verdict_filter,
            limit=12,
        )
        trend = summarize_suggestion_review_trend(root)
        return {
            "ok": True,
            "action": action,
            "suggestion_review_summary": summary,
            "suggestion_review_trend": trend,
        }

    if action == "resolve_owner_todo":
        todo_id = str(payload.get("todo_id", "")).strip()
        note = str(payload.get("note", "")).strip()
        if not todo_id:
            raise ValueError("todo_id is required for resolve_owner_todo")
        if not note:
            raise ValueError("note is required for resolve_owner_todo")
        record = resolve_owner_todo(
            root,
            todo_id=todo_id,
            note=note,
            owner_report_ref=_normalize_optional_str(payload.get("owner_report_ref")),
        )
        return {
            "ok": True,
            "action": action,
            "resolution_record_id": record["id"],
            "resolved_todo": record["resolution_of"],
            "owner_todos": list_open_owner_todos(root),
        }

    if action == "schedule_cycle":
        cycle = str(payload.get("cycle", "weekly")).strip().lower()
        if cycle not in {"daily", "weekly", "monthly"}:
            raise ValueError("cycle must be one of: daily, weekly, monthly")

        provider_hint = _normalize_optional_str(payload.get("provider"))
        model_hint = _normalize_optional_str(payload.get("model"))
        with_retrieval = _coerce_bool(payload.get("with_retrieval"), default=False)
        retrieval_top_k = _coerce_int(payload.get("retrieval_top_k"), default=6, minimum=1, maximum=32)
        limit_raw = payload.get("limit")
        limit = _coerce_int(limit_raw, default=0, minimum=0, maximum=100) if limit_raw is not None else None
        owner_window = _coerce_int(payload.get("owner_window"), default=7, minimum=1, maximum=365)
        no_owner_report = _coerce_bool(payload.get("no_owner_report"), default=False)

        result = _run_schedule_cycle(
            root=root,
            cycle=cycle,
            provider_hint=provider_hint,
            model_hint=model_hint,
            with_retrieval=with_retrieval,
            retrieval_top_k=retrieval_top_k,
            limit=limit,
            owner_window=owner_window,
            no_owner_report=no_owner_report,
        )
        return {"ok": True, "action": action, **result}

    if action == "detect_disequilibrium":
        topic = str(payload.get("task", "")).strip()
        if not topic:
            raise ValueError("task is required for detect_disequilibrium")
        window_days = _coerce_int(payload.get("window_days"), default=30, minimum=1, maximum=365)
        schema_version_id = _normalize_optional_str(payload.get("schema_version_id"))
        tags = _coerce_tags(payload.get("tags"))
        output_rel = _normalize_optional_str(payload.get("output"))
        result = _run_disequilibrium(
            root,
            topic=topic,
            window_days=window_days,
            schema_version_id=schema_version_id,
            tags=tags,
            output_rel=output_rel,
        )
        return {"ok": True, "action": action, **result}

    if action == "cognition_timeline":
        topic = _normalize_optional_str(payload.get("task"))
        window_days = _coerce_int(payload.get("window_days"), default=90, minimum=1, maximum=3650)
        output_rel = _normalize_optional_str(payload.get("output"))
        result = _run_cognition_timeline(
            root,
            topic=topic,
            window_days=window_days,
            output_rel=output_rel,
        )
        return {"ok": True, "action": action, **result}

    if action == "build_index":
        payload_out = build_index(root)
        return {
            "ok": True,
            "action": action,
            "built_at": payload_out["built_at"],
            "doc_count": payload_out["doc_count"],
            "source_count": len(payload_out["sources"]),
        }

    if action == "review_suggestion":
        suggestion_id = str(payload.get("suggestion_id", "")).strip()
        if not suggestion_id:
            raise ValueError("suggestion_id is required for review_suggestion")

        verdict = str(payload.get("verdict", "")).strip().lower()
        if verdict not in {"accept", "modify", "reject"}:
            raise ValueError("verdict must be one of: accept, modify, reject")

        owner_note = str(payload.get("owner_note", "")).strip()
        if not owner_note:
            raise ValueError("owner_note is required for review_suggestion")

        suggestion_payload = api_suggestion(root, suggestion_id)
        suggestion = suggestion_payload.get("suggestion", {})
        run_ref = str(suggestion.get("run_ref", "")).strip()
        source_refs: list[str] = [suggestion_id]
        if run_ref:
            source_refs.append(run_ref)

        verdict_id = next_id_for_rel_path(root, "ov", "orchestrator/logs/owner_verdicts.jsonl")
        correction_ref = None

        correction_target_layer = _normalize_optional_str(payload.get("correction_target_layer"))
        replacement_judgment = _normalize_optional_str(payload.get("replacement_judgment"))
        unlike_me_reason = _normalize_optional_str(payload.get("unlike_me_reason"))

        if verdict == "modify":
            if not replacement_judgment:
                raise ValueError("replacement_judgment is required for modify verdict")
            if not unlike_me_reason:
                raise ValueError("unlike_me_reason is required for modify verdict")
            correction_ref = next_id_for_rel_path(root, "oc", "orchestrator/logs/owner_corrections.jsonl")
            correction_record = {
                "id": correction_ref,
                "created_at": _utc_now(),
                "status": "active",
                "suggestion_ref": suggestion_id,
                "verdict_ref": verdict_id,
                "target_layer": correction_target_layer or str(suggestion.get("module", "")).strip() or "decision",
                "replacement_judgment": replacement_judgment,
                "unlike_me_reason": unlike_me_reason,
                "source_refs": source_refs + [verdict_id],
            }
            log_owner_correction(root, correction_record)

        verdict_record = {
            "id": verdict_id,
            "created_at": _utc_now(),
            "status": "active",
            "suggestion_ref": suggestion_id,
            "verdict": verdict,
            "owner_note": owner_note,
            "correction_ref": correction_ref,
            "source_refs": source_refs,
        }
        log_owner_verdict(root, verdict_record)

        return {
            "ok": True,
            "action": action,
            "suggestion_id": suggestion_id,
            "verdict": verdict,
            "verdict_record_id": verdict_id,
            "correction_record_id": correction_ref,
            "suggestion_detail": api_suggestion(root, suggestion_id),
        }

    if action == "ingest_learning":
        learning_text = str(payload.get("task", "")).strip()
        if not learning_text:
            raise ValueError("task is required for ingest_learning")

        result = ingest_learning_text(
            root,
            learning_text,
            title=_normalize_optional_str(payload.get("title")),
            source_type=_normalize_optional_str(payload.get("source_type")) or "video",
            max_points=_coerce_int(payload.get("max_points"), default=6, minimum=1, maximum=20),
            confidence=_coerce_int(payload.get("confidence"), default=7, minimum=1, maximum=10),
            dry_run=_coerce_bool(payload.get("dry_run"), default=False),
            extra_tags=_coerce_tags(payload.get("tags")),
        )
        return {"ok": True, "action": action, **result}

    if action == "learning_handoff_packet":
        source_ref = str(payload.get("source_ref", "")).strip()
        if not source_ref:
            raise ValueError("source_ref is required for learning_handoff_packet")
        result = build_learning_handoff_packet(
            source_ref=source_ref,
            title=_normalize_optional_str(payload.get("title")),
            source_type=_normalize_optional_str(payload.get("source_type")),
            owner_goal=_normalize_optional_str(payload.get("owner_goal")),
            max_candidates_per_type=_coerce_int(
                payload.get("max_candidates_per_type"),
                default=3,
                minimum=1,
                maximum=8,
            ),
        )
        return {"ok": True, "action": action, **result}

    if action == "learning_handoff_import":
        response_text = str(payload.get("response_text", "")).strip()
        if not response_text:
            raise ValueError("response_text is required for learning_handoff_import")
        result = ingest_learning_handoff_response(
            root,
            response_text,
            source_ref=_normalize_optional_str(payload.get("source_ref")),
            title=_normalize_optional_str(payload.get("title")),
            source_type=_normalize_optional_str(payload.get("source_type")),
            confidence=_coerce_int(payload.get("confidence"), default=7, minimum=1, maximum=10),
            dry_run=_coerce_bool(payload.get("dry_run"), default=False),
            tags=_coerce_tags(payload.get("tags")),
        )
        return {
            "ok": True,
            "action": action,
            **result,
            "learning_candidates": list_recent_learning_candidates(root, limit=12, include_resolved=True),
            "candidate_pipeline_summary": summarize_learning_pipeline(root, window_days=30),
            "candidate_pipeline_trend": summarize_learning_pipeline_trend(root),
        }

    if action == "review_learning_candidate":
        candidate_id = str(payload.get("candidate_id", "")).strip()
        verdict = str(payload.get("verdict", "")).strip().lower()
        owner_note = str(payload.get("owner_note", "")).strip()
        modified_statement = _normalize_optional_str(payload.get("modified_statement"))
        result = apply_learning_candidate_verdict(
            root,
            candidate_id=candidate_id,
            verdict=verdict,
            owner_note=owner_note,
            modified_statement=modified_statement,
        )
        return {
            "ok": True,
            "action": action,
            **result,
            "learning_candidates": list_recent_learning_candidates(root, limit=12, include_resolved=True),
            "candidate_pipeline_summary": summarize_learning_pipeline(root, window_days=30),
            "candidate_pipeline_trend": summarize_learning_pipeline_trend(root),
        }

    if action == "promote_learning_candidate":
        candidate_id = str(payload.get("candidate_id", "")).strip()
        approval_note = str(payload.get("approval_note", "")).strip()
        result = promote_learning_candidate(
            root,
            candidate_id=candidate_id,
            approval_note=approval_note,
        )
        return {
            "ok": True,
            "action": action,
            **result,
            "learning_candidates": list_recent_learning_candidates(root, limit=12, include_resolved=True),
            "candidate_pipeline_summary": summarize_learning_pipeline(root, window_days=30),
            "candidate_pipeline_trend": summarize_learning_pipeline_trend(root),
        }

    raise ValueError(f"unsupported action: {action}")


def _make_handler(root: Path, static_root: Path) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "PersonalCoreOSWeb/1.0"

        def _send_json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_file(self, path: Path, content_type: str) -> None:
            if not path.exists() or not path.is_file():
                self._send_json(404, {"ok": False, "error": "not found"})
                return
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _read_json_body(self) -> dict[str, Any]:
            length_header = self.headers.get("Content-Length", "0")
            try:
                length = int(length_header)
            except ValueError as exc:
                raise ValueError("invalid Content-Length") from exc
            if length <= 0:
                return {}
            if length > 1_000_000:
                raise ValueError("request body too large")
            raw = self.rfile.read(length)
            if not raw:
                return {}
            try:
                data = json.loads(raw.decode("utf-8"))
            except json.JSONDecodeError as exc:
                raise ValueError("invalid JSON body") from exc
            if not isinstance(data, dict):
                raise ValueError("JSON body must be an object")
            return data

        def do_GET(self) -> None:  # noqa: N802
            try:
                parsed = urlparse(self.path)
                path = parsed.path

                if path in {"/", "/index.html"}:
                    self._send_file(static_root / "index.html", "text/html; charset=utf-8")
                    return
                if path in {"/audit", "/audit.html"}:
                    self._send_file(static_root / "audit.html", "text/html; charset=utf-8")
                    return
                if path == "/styles.css":
                    self._send_file(static_root / "styles.css", "text/css; charset=utf-8")
                    return
                if path == "/app.js":
                    self._send_file(static_root / "app.js", "application/javascript; charset=utf-8")
                    return
                if path == "/workspace.js":
                    self._send_file(static_root / "workspace.js", "application/javascript; charset=utf-8")
                    return
                if path == "/api/status":
                    self._send_json(200, api_status(root))
                    return
                if path == "/api/settings":
                    self._send_json(200, api_get_settings(root))
                    return
                if path == "/api/output":
                    query = parse_qs(parsed.query)
                    rel_path = query.get("path", [""])[0]
                    self._send_json(200, api_output(root, rel_path))
                    return
                if path == "/api/output-meta":
                    query = parse_qs(parsed.query)
                    rel_path = query.get("path", [""])[0]
                    model = _normalize_optional_str(query.get("model", [""])[0])
                    self._send_json(200, api_output_meta(root, rel_path, model))
                    return
                if path == "/api/suggestion":
                    query = parse_qs(parsed.query)
                    suggestion_id = query.get("id", [""])[0]
                    self._send_json(200, api_suggestion(root, suggestion_id))
                    return

                self._send_json(404, {"ok": False, "error": "not found"})
            except ValueError as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._send_json(500, {"ok": False, "error": str(exc)})

        def do_POST(self) -> None:  # noqa: N802
            path = self.path.split("?", 1)[0]
            try:
                payload = self._read_json_body()
                if path == "/api/inspect":
                    self._send_json(200, api_inspect(root, payload))
                    return
                if path == "/api/run":
                    self._send_json(200, api_run(root, payload))
                    return
                if path == "/api/settings":
                    self._send_json(200, api_update_settings(root, payload))
                    return
                if path == "/api/action":
                    self._send_json(200, api_action(root, payload))
                    return
                self._send_json(404, {"ok": False, "error": "not found"})
            except ValueError as exc:
                self._send_json(400, {"ok": False, "error": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._send_json(500, {"ok": False, "error": str(exc)})

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            return

    return Handler


def start_web_ui(
    *,
    root: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = False,
) -> None:
    resolved_root = root or repo_root()
    static_root = resolved_root / "orchestrator" / "web"
    if not static_root.exists() or not static_root.is_dir():
        raise FileNotFoundError(f"Web static directory not found: {static_root}")

    server = ThreadingHTTPServer((host, port), _make_handler(resolved_root, static_root))
    url = f"http://{host}:{port}"

    print(f"Personal Core OS UI running at: {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Personal Core OS Web UI")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--open-browser", action="store_true")
    return p


def main() -> int:
    args = _build_parser().parse_args()
    start_web_ui(host=args.host, port=args.port, open_browser=args.open_browser)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
