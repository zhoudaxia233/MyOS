from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from cognition import (
    detect_disequilibrium,
    log_accommodation_revision,
    log_assimilation_event,
    log_equilibration_cycle,
    log_schema_version,
    render_disequilibrium_report,
)
from decision_gate import evaluate_decision_entry_gate
from config import load_runtime_config
from chat_ingest import ingest_chat_export
from guardrails import evaluate_guardrail, load_domain_guardrails
from idgen import next_id_for_rel_path
from learning_ingest import ingest_learning_asset
from loader import load_context_bundle
from metrics import compute_drift_metrics, render_metrics_report
from owner_report import build_owner_snapshot, render_owner_report
from planner import plan_task
from plugin_contract import validate_repo
from retrieval import build_index, format_hits, load_retrieval_config, search_index
from route_selector import select_route
from runner import run_with_provider
from scheduling import task_from_routine
from schedulers.cron import cron_hint
from schedulers.manual import get_cycle
from settings import apply_openai_api_key_env, load_settings
from writer import (
    log_decision,
    log_decision_gate_check,
    log_guardrail_override,
    log_metrics_snapshot,
    log_owner_report,
    log_retrieval_query,
    log_run,
    log_schedule_run,
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


def _normalize_optional_str(value: str | None) -> str | None:
    text = str(value or "").strip()
    return text or None


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


def _print_route_scoring(route: dict) -> None:
    scoring = route.get("scoring")
    if not isinstance(scoring, dict):
        return

    manifest_candidates = scoring.get("manifest_candidates")
    if isinstance(manifest_candidates, list) and manifest_candidates:
        print("Route scoring (manifest):")
        for candidate in manifest_candidates[:3]:
            module = str(candidate.get("module", ""))
            score = candidate.get("score", 0)
            positive = candidate.get("positive_hits", 0)
            negative = candidate.get("negative_hits", 0)
            matched = candidate.get("matched_keywords", [])
            print(f"- {module}: score={score} (+{positive}/-{negative}) matched={matched}")
        return

    route_candidates = scoring.get("routes_candidates")
    if isinstance(route_candidates, list) and route_candidates:
        print("Route scoring (routes):")
        for candidate in route_candidates[:3]:
            module = str(candidate.get("module", ""))
            score = candidate.get("score", 0)
            positive = candidate.get("positive_hits", 0)
            negative = candidate.get("negative_hits", 0)
            matched = candidate.get("matched_keywords", [])
            print(f"- {module}: score={score} (+{positive}/-{negative}) matched={matched}")


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


def execute_task(
    *,
    root: Path,
    task: str,
    forced_module: str | None,
    provider: str,
    model: str,
    with_retrieval: bool,
    retrieval_top_k: int,
    skill_hint: str | None = None,
    routine_id: str | None = None,
) -> dict:
    cfg = load_runtime_config(root)
    route = select_route(task, forced_module=forced_module, repo_root=root)
    module = route["module"]
    plan = plan_task(task, module, skill_hint=skill_hint, routine_id=routine_id, repo_root=root)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"], skill_path=plan["skill"])

    hits: list[dict] = []
    if with_retrieval:
        hits = _retrieval_hits(root, task, module, retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    apply_openai_api_key_env(root)
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

    return {
        "module": module,
        "provider": provider,
        "route": route,
        "plan": plan,
        "output_path": _root_relative(out, root),
        "output_hash": output_hash,
        "retrieval_hits": len(hits),
        "loaded_files": [f["path"] for f in bundle["files"]],
    }


def cmd_inspect(args: argparse.Namespace) -> int:
    root = repo_root()
    cfg = load_runtime_config(root)
    route = select_route(args.task, forced_module=args.module, repo_root=root)
    module = route["module"]
    plan = plan_task(args.task, module, repo_root=root)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"], skill_path=plan["skill"])

    if args.with_retrieval:
        hits = _retrieval_hits(root, args.task, module, args.retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    print(f"Route: modules/{module}")
    print(f"Route reason: {route['reason']}")
    if route["matched_keywords"]:
        print(f"Matched keywords: {route['matched_keywords']}")
    _print_route_scoring(route)
    print(f"Skill: {plan['skill']}")
    print(f"Output path: {plan['output_path']}")
    print("Files:")
    for f in bundle["files"]:
        print(f"- {f['path']}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    root = repo_root()
    cfg = load_runtime_config(root)
    settings = load_settings(root)
    provider = args.provider or settings["default_provider"] or cfg["default_provider"]
    model = args.model or settings["task_model"] or cfg["default_openai_model"]

    result = execute_task(
        root=root,
        task=args.task,
        forced_module=args.module,
        provider=provider,
        model=model,
        with_retrieval=args.with_retrieval,
        retrieval_top_k=args.retrieval_top_k,
    )

    print(f"Route: modules/{result['module']}")
    print(f"Route reason: {result['route']['reason']}")
    if result["route"]["matched_keywords"]:
        print(f"Matched keywords: {result['route']['matched_keywords']}")
    _print_route_scoring(result["route"])
    print("Loaded files:")
    for path in result["loaded_files"]:
        print(f"- {path}")
    print(f"Wrote: {root / result['output_path']}")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    root = repo_root()
    payload = build_index(root, source_globs=args.source_glob if args.source_glob else None)
    print("Index built")
    print(f"- built_at: {payload['built_at']}")
    print(f"- doc_count: {payload['doc_count']}")
    print(f"- source_count: {len(payload['sources'])}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    root = repo_root()
    hits = _retrieval_hits(root, args.query, args.module, args.top_k)
    _log_retrieval(root, args.query, args.module, args.top_k, len(hits))

    if not hits:
        print("No retrieval hits")
        return 0

    print(format_hits(hits))
    return 0


def cmd_ingest_chat(args: argparse.Namespace) -> int:
    root = repo_root()
    input_path = Path(args.input).expanduser()
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()

    result = ingest_chat_export(
        root,
        input_path,
        max_events=args.max_events,
        dry_run=args.dry_run,
        extra_tags=args.tag,
    )

    print(f"Input: {result['input_path']}")
    print(f"Messages parsed: {result['message_count']}")
    print(f"Normalized events: {result['event_count']}")
    print(f"Appended: {result['appended_count']}")
    if result["dry_run"]:
        print("Mode: dry-run")
    if result["record_ids"]:
        print("Record IDs:")
        for rid in result["record_ids"]:
            print(f"- {rid}")
    return 0


def cmd_ingest_learning(args: argparse.Namespace) -> int:
    root = repo_root()
    input_path = Path(args.input).expanduser()
    if not input_path.is_absolute():
        input_path = (Path.cwd() / input_path).resolve()

    result = ingest_learning_asset(
        root,
        input_path,
        title=args.title,
        source_type=args.source_type,
        max_points=args.max_points,
        confidence=args.confidence,
        dry_run=args.dry_run,
        extra_tags=args.tag,
    )

    print(f"Input: {result['input_path']}")
    print(f"Title: {result['title']}")
    print(f"Source type: {result['source_type']}")
    print(f"Core points: {result['core_points_count']}")
    print(f"Appended events: {result['appended_events']}")
    print(f"Appended insights: {result['appended_insights']}")
    if result["dry_run"]:
        print("Mode: dry-run")
    if result["record_ids"]:
        print("Record IDs:")
        for rid in result["record_ids"]:
            print(f"- {rid}")
    return 0


def cmd_log_schema(args: argparse.Namespace) -> int:
    root = repo_root()
    record = log_schema_version(
        root,
        topic=args.topic,
        schema_name=args.schema_name,
        summary=args.summary,
        assumptions=args.assumption,
        predictions=args.prediction,
        boundaries=args.boundary,
        schema_id=_normalize_optional_str(args.schema_id),
        parent_schema_version_id=_normalize_optional_str(args.parent_schema_version_id),
        source_refs=args.source_ref,
        tags=args.tag,
    )
    print(f"Schema version ID: {record['id']}")
    print(f"Schema ID: {record['schema_id']}")
    print(f"Version: {record['version']}")
    return 0


def cmd_log_assimilation(args: argparse.Namespace) -> int:
    root = repo_root()
    record = log_assimilation_event(
        root,
        topic=args.topic,
        schema_version_id=args.schema_version_id,
        input_summary=args.input_summary,
        interpreted_as=args.interpreted_as,
        fit_score=int(args.fit_score),
        stretch_points=args.stretch_point,
        source_refs=args.source_ref,
        tags=args.tag,
    )
    print(f"Assimilation event ID: {record['id']}")
    print(f"Fit score: {record['fit_score']}")
    return 0


def cmd_detect_disequilibrium(args: argparse.Namespace) -> int:
    root = repo_root()
    result = detect_disequilibrium(
        root,
        topic=args.topic,
        window_days=int(args.window),
        schema_version_id=_normalize_optional_str(args.schema_version_id),
        source_refs=args.source_ref,
        tags=args.tag,
    )
    report = render_disequilibrium_report(result)

    if args.output:
        output_rel = args.output
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_rel = f"modules/cognition/outputs/disequilibrium_{stamp}.md"
    out = write_output(root, output_rel, report)

    record = result["record"]
    print(f"Disequilibrium event ID: {record['id']}")
    print(f"Tension score: {record['tension_score']}")
    print(f"Signals: {len(result.get('signals', []))}")
    print(f"Wrote: {out}")
    return 0


def cmd_log_accommodation(args: argparse.Namespace) -> int:
    root = repo_root()
    result = log_accommodation_revision(
        root,
        topic=args.topic,
        previous_schema_version_id=args.previous_schema_version_id,
        revision_type=args.revision_type,
        failed_assumptions=args.failed_assumption,
        revision_summary=args.revision_summary,
        new_schema_hypothesis=args.new_schema_hypothesis,
        create_schema_version=not bool(args.no_schema_version),
        schema_id=_normalize_optional_str(args.schema_id),
        schema_name=_normalize_optional_str(args.schema_name),
        schema_summary=_normalize_optional_str(args.schema_summary),
        assumptions=args.assumption,
        predictions=args.prediction,
        boundaries=args.boundary,
        source_refs=args.source_ref,
        tags=args.tag,
    )
    revision = result["revision"]
    new_schema = result.get("new_schema")

    print(f"Accommodation revision ID: {revision['id']}")
    print(f"Revision type: {revision['revision_type']}")
    if new_schema:
        print(f"New schema version ID: {new_schema['id']}")
        print(f"New schema version: {new_schema['version']}")
    else:
        print("New schema version: skipped")
    return 0


def cmd_log_equilibration(args: argparse.Namespace) -> int:
    root = repo_root()
    record = log_equilibration_cycle(
        root,
        topic=args.topic,
        from_schema_version_id=args.from_schema_version_id,
        to_schema_version_id=args.to_schema_version_id,
        stabilizing_tests=args.stabilizing_test,
        residual_tensions=args.residual_tension,
        coherence_score=int(args.coherence_score),
        source_refs=args.source_ref,
        tags=args.tag,
    )
    print(f"Equilibration cycle ID: {record['id']}")
    print(f"Coherence score: {record['coherence_score']}")
    return 0


def cmd_guardrail_check(args: argparse.Namespace) -> int:
    root = repo_root()
    policy = load_domain_guardrails(root)
    payload = {
        "guardrail_check_id": args.guardrail_check_id,
        "downside": args.downside,
        "invalidation_condition": args.invalidation_condition,
        "max_loss": args.max_loss,
        "disconfirming_signal": args.disconfirming_signal,
        "emotional_weight": args.emotional_weight,
        "cooldown_applied": args.cooldown_applied,
        "cooldown_hours": args.cooldown_hours,
        "override_requested": args.override_requested,
        "override_reason": args.override_reason,
        "owner_confirmation": args.owner_confirmation,
    }

    result = evaluate_guardrail(policy, args.domain, payload)

    if result["status"] == "override_accepted":
        record = {
            "id": next_id_for_rel_path(root, "go", "modules/decision/logs/guardrail_overrides.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "domain": args.domain.lower(),
            "decision_ref": args.decision_ref,
            "violations": result["violations"],
            "override_reason": args.override_reason,
            "owner_confirmation": args.owner_confirmation,
            "provider": args.provider,
            "notes": args.notes,
        }
        log_guardrail_override(root, record)

    print(f"Status: {result['status']}")
    print(f"Violations: {result['violations']}")
    print(f"Cooldown required: {result['cooldown_required']}")
    if result["cooldown_required"]:
        print(f"Required cooldown hours: {result['required_cooldown_hours']}")
    if result["missing_override_fields"]:
        print(f"Missing override fields: {result['missing_override_fields']}")
    return 0


def cmd_log_decision(args: argparse.Namespace) -> int:
    root = repo_root()
    domain = str(args.domain).strip().lower()
    decision_text = str(args.decision).strip()
    options = [str(item).strip() for item in (args.option or []) if str(item).strip()]
    confidence = int(args.confidence)

    if not domain:
        raise ValueError("domain is required")
    if not decision_text:
        raise ValueError("decision is required")
    if not options:
        raise ValueError("at least one --option is required")
    if confidence < 1 or confidence > 10:
        raise ValueError("confidence must be in range 1..10")

    guardrail_check_id = _normalize_optional_str(args.guardrail_check_id)
    gate = evaluate_decision_entry_gate(
        root,
        domain=domain,
        guardrail_check_id=guardrail_check_id,
        downside=_normalize_optional_str(args.downside),
        invalidation_condition=_normalize_optional_str(args.invalidation_condition),
        max_loss=_normalize_optional_str(args.max_loss),
        disconfirming_signal=_normalize_optional_str(args.disconfirming_signal),
        emotional_weight=int(args.emotional_weight),
        cooldown_applied=bool(args.cooldown_applied),
        cooldown_hours=int(args.cooldown_hours),
        override_requested=bool(args.override_requested),
        override_reason=_normalize_optional_str(args.override_reason),
        owner_confirmation=_normalize_optional_str(args.owner_confirmation),
    )

    gate_record = {
        "id": next_id_for_rel_path(root, "dgc", "modules/decision/logs/decision_gate_checks.jsonl"),
        "created_at": _utc_now(),
        "status": "active",
        "domain": gate["domain"],
        "decision": decision_text,
        "guardrail_check_id": guardrail_check_id,
        "precommit_required": gate["precommit_required"],
        "precommit_status": gate["precommit_status"],
        "guardrail_status": gate["guardrail_status"],
        "gate_status": gate["gate_status"],
        "violations": gate["violations"],
        "missing_override_fields": gate["missing_override_fields"],
        "source_refs": gate["source_refs"],
    }
    log_decision_gate_check(root, gate_record)

    if gate["gate_status"] == "blocked":
        details = ", ".join(gate["violations"]) if gate["violations"] else "unspecified"
        raise RuntimeError(f"Decision gate blocked; no decision was logged. Violations: {details}")

    decision_id = next_id_for_rel_path(root, "dc", "modules/decision/logs/decisions.jsonl")
    decision_record = {
        "id": decision_id,
        "created_at": _utc_now(),
        "status": "active",
        "domain": gate["domain"],
        "decision": decision_text,
        "options": options,
        "reasoning": _normalize_optional_str(args.reasoning),
        "risks": [str(item).strip() for item in (args.risk or []) if str(item).strip()],
        "expected_outcome": _normalize_optional_str(args.expected_outcome),
        "time_horizon": _normalize_optional_str(args.time_horizon),
        "confidence": confidence,
        "guardrail_check_id": guardrail_check_id,
        "follow_up_date": _normalize_optional_str(args.follow_up_date),
        "outcome": _normalize_optional_str(args.outcome),
    }
    log_decision(root, decision_record)

    if gate["gate_status"] == "override_accepted":
        override_record = {
            "id": next_id_for_rel_path(root, "go", "modules/decision/logs/guardrail_overrides.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "domain": gate["domain"],
            "decision_ref": decision_id,
            "violations": gate["violations"],
            "override_reason": _normalize_optional_str(args.override_reason),
            "owner_confirmation": _normalize_optional_str(args.owner_confirmation),
            "provider": args.provider,
            "notes": _normalize_optional_str(args.notes),
        }
        log_guardrail_override(root, override_record)

    print(f"Decision ID: {decision_id}")
    print(f"Gate status: {gate['gate_status']}")
    print(f"Precommit status: {gate['precommit_status']}")
    print(f"Guardrail status: {gate['guardrail_status']}")
    return 0


def cmd_metrics(args: argparse.Namespace) -> int:
    root = repo_root()
    snapshot = compute_drift_metrics(root, args.window)
    report = render_metrics_report(snapshot)

    if args.output:
        output_rel = args.output
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_rel = f"modules/decision/outputs/metrics_{stamp}.md"

    out = write_output(root, output_rel, report)
    report_path = _root_relative(out, root)

    summary = {k: v["status"] for k, v in snapshot["metrics"].items()}
    record = {
        "id": next_id_for_rel_path(root, "mt", "orchestrator/logs/metrics_snapshots.jsonl"),
        "created_at": _utc_now(),
        "status": "active",
        "window_days": args.window,
        "summary": summary,
        "report_path": report_path,
    }
    log_metrics_snapshot(root, record)

    print(f"Wrote: {out}")
    print(f"Summary: {summary}")
    return 0


def cmd_owner_report(args: argparse.Namespace) -> int:
    root = repo_root()
    snapshot = build_owner_snapshot(root, window_days=args.window)
    report = render_owner_report(snapshot)

    if args.output:
        output_rel = args.output
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        output_rel = f"modules/decision/outputs/owner_report_{stamp}.md"

    out = write_output(root, output_rel, report)
    report_path = _root_relative(out, root)

    summary = {k: v["status"] for k, v in snapshot["metrics"]["metrics"].items()}
    record = {
        "id": next_id_for_rel_path(root, "or", "orchestrator/logs/owner_reports.jsonl"),
        "created_at": _utc_now(),
        "status": "active",
        "window_days": args.window,
        "summary": summary,
        "report_path": report_path,
        "source_artifacts": snapshot["source_artifacts"],
    }
    log_owner_report(root, record)

    print(f"Wrote: {out}")
    print(f"Summary: {summary}")
    return 0


def cmd_schedule_run(args: argparse.Namespace) -> int:
    root = repo_root()
    cfg = load_runtime_config(root)
    settings = load_settings(root)
    provider = args.provider or settings["default_provider"] or cfg["default_provider"]
    model = args.model or settings["task_model"] or cfg["default_openai_model"]

    if args.scheduler == "cron":
        print(cron_hint(root, args.cycle))
        return 0

    routines = get_cycle(root, args.cycle)
    if args.limit is not None:
        routines = routines[: args.limit]

    if not routines:
        print(f"No routines for cycle: {args.cycle}")
        return 0

    print(f"Running cycle: {args.cycle} ({len(routines)} routines)")

    for routine in routines:
        task = task_from_routine(args.cycle, routine)
        result = execute_task(
            root=root,
            task=task,
            forced_module=routine["module"],
            provider=provider,
            model=model,
            with_retrieval=args.with_retrieval,
            retrieval_top_k=args.retrieval_top_k,
            skill_hint=routine["skill"],
            routine_id=routine["id"],
        )

        schedule_record = {
            "id": next_id_for_rel_path(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "cycle": args.cycle,
            "routine_id": routine["id"],
            "module": routine["module"],
            "skill": routine["skill"],
            "provider": provider,
            "result_path": result["output_path"],
        }
        log_schedule_run(root, schedule_record)

        print(f"- {routine['id']} -> {result['output_path']}")

    if args.cycle == "weekly" and not args.no_owner_report:
        owner_snapshot = build_owner_snapshot(root, window_days=args.owner_window)
        owner_report = render_owner_report(owner_snapshot)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        owner_output = f"modules/decision/outputs/owner_report_{stamp}.md"
        out = write_output(root, owner_output, owner_report)
        out_rel = _root_relative(out, root)

        owner_record = {
            "id": next_id_for_rel_path(root, "or", "orchestrator/logs/owner_reports.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "window_days": args.owner_window,
            "summary": {k: v["status"] for k, v in owner_snapshot["metrics"]["metrics"].items()},
            "report_path": out_rel,
            "source_artifacts": owner_snapshot["source_artifacts"],
        }
        log_owner_report(root, owner_record)

        schedule_record = {
            "id": next_id_for_rel_path(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "cycle": args.cycle,
            "routine_id": "rt_weekly_owner_report_auto",
            "module": "decision",
            "skill": "owner_report",
            "provider": provider,
            "result_path": out_rel,
        }
        log_schedule_run(root, schedule_record)
        print(f"- rt_weekly_owner_report_auto -> {out_rel}")

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    root = repo_root()
    result = validate_repo(root)

    checked = result["checked"]
    print("Validation summary")
    print(f"- modules_checked: {checked['modules']}")
    print(f"- skills_checked: {checked['skills']}")
    print(f"- jsonl_checked: {checked['jsonl']}")
    print(f"- records_checked: {checked['records']}")
    print(f"- routines_checked: {checked['routines']}")
    print(f"- warnings: {len(result['warnings'])}")
    print(f"- errors: {len(result['errors'])}")

    if result["warnings"]:
        print("Warnings:")
        for w in result["warnings"]:
            print(f"- [{w['code']}] {w['path']}: {w['message']}")

    if result["errors"]:
        print("Errors:")
        for e in result["errors"]:
            print(f"- [{e['code']}] {e['path']}: {e['message']}")

    if result["errors"]:
        print("Validation status: FAIL")
        return 1
    if args.strict and result["warnings"]:
        print("Validation status: FAIL (strict mode)")
        return 1

    print("Validation status: PASS")
    return 0


def cmd_web(args: argparse.Namespace) -> int:
    from webapp import start_web_ui

    root = repo_root()
    start_web_ui(root=root, host=args.host, port=args.port, open_browser=args.open_browser)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Personal Core OS Orchestrator")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--task", required=True)
    common.add_argument("--module", default=None)
    common.add_argument("--with-retrieval", action="store_true")
    common.add_argument("--retrieval-top-k", type=int, default=6)

    sp_inspect = sub.add_parser("inspect", parents=[common])
    sp_inspect.set_defaults(func=cmd_inspect)

    sp_run = sub.add_parser("run", parents=[common])
    sp_run.add_argument("--provider", default=None, choices=["dry-run", "handoff", "openai"])
    sp_run.add_argument("--model", default=None)
    sp_run.set_defaults(func=cmd_run)

    sp_index = sub.add_parser("index")
    sp_index.add_argument("--source-glob", action="append", default=[])
    sp_index.set_defaults(func=cmd_index)

    sp_search = sub.add_parser("search")
    sp_search.add_argument("--query", required=True)
    sp_search.add_argument("--module", default=None)
    sp_search.add_argument("--top-k", type=int, default=8)
    sp_search.set_defaults(func=cmd_search)

    sp_ingest_chat = sub.add_parser("ingest-chat")
    sp_ingest_chat.add_argument("--input", required=True)
    sp_ingest_chat.add_argument("--max-events", type=int, default=50)
    sp_ingest_chat.add_argument("--tag", action="append", default=[])
    sp_ingest_chat.add_argument("--dry-run", action="store_true")
    sp_ingest_chat.set_defaults(func=cmd_ingest_chat)

    sp_ingest_learning = sub.add_parser("ingest-learning")
    sp_ingest_learning.add_argument("--input", required=True)
    sp_ingest_learning.add_argument("--title", default=None)
    sp_ingest_learning.add_argument("--source-type", default="video")
    sp_ingest_learning.add_argument("--max-points", type=int, default=6)
    sp_ingest_learning.add_argument("--confidence", type=int, default=7)
    sp_ingest_learning.add_argument("--tag", action="append", default=[])
    sp_ingest_learning.add_argument("--dry-run", action="store_true")
    sp_ingest_learning.set_defaults(func=cmd_ingest_learning)

    sp_log_schema = sub.add_parser("log-schema")
    sp_log_schema.add_argument("--topic", required=True)
    sp_log_schema.add_argument("--schema-name", required=True)
    sp_log_schema.add_argument("--summary", required=True)
    sp_log_schema.add_argument("--assumption", action="append", default=[])
    sp_log_schema.add_argument("--prediction", action="append", default=[])
    sp_log_schema.add_argument("--boundary", action="append", default=[])
    sp_log_schema.add_argument("--schema-id", default=None)
    sp_log_schema.add_argument("--parent-schema-version-id", default=None)
    sp_log_schema.add_argument("--source-ref", action="append", default=[])
    sp_log_schema.add_argument("--tag", action="append", default=[])
    sp_log_schema.set_defaults(func=cmd_log_schema)

    sp_log_assimilation = sub.add_parser("log-assimilation")
    sp_log_assimilation.add_argument("--topic", required=True)
    sp_log_assimilation.add_argument("--schema-version-id", required=True)
    sp_log_assimilation.add_argument("--input-summary", required=True)
    sp_log_assimilation.add_argument("--interpreted-as", required=True)
    sp_log_assimilation.add_argument("--fit-score", type=int, default=7)
    sp_log_assimilation.add_argument("--stretch-point", action="append", default=[])
    sp_log_assimilation.add_argument("--source-ref", action="append", default=[])
    sp_log_assimilation.add_argument("--tag", action="append", default=[])
    sp_log_assimilation.set_defaults(func=cmd_log_assimilation)

    sp_detect_diseq = sub.add_parser("detect-disequilibrium")
    sp_detect_diseq.add_argument("--topic", required=True)
    sp_detect_diseq.add_argument("--window", type=int, default=30)
    sp_detect_diseq.add_argument("--schema-version-id", default=None)
    sp_detect_diseq.add_argument("--source-ref", action="append", default=[])
    sp_detect_diseq.add_argument("--tag", action="append", default=[])
    sp_detect_diseq.add_argument("--output", default=None)
    sp_detect_diseq.set_defaults(func=cmd_detect_disequilibrium)

    sp_log_accommodation = sub.add_parser("log-accommodation")
    sp_log_accommodation.add_argument("--topic", required=True)
    sp_log_accommodation.add_argument("--previous-schema-version-id", required=True)
    sp_log_accommodation.add_argument("--revision-type", required=True)
    sp_log_accommodation.add_argument("--failed-assumption", action="append", default=[])
    sp_log_accommodation.add_argument("--revision-summary", required=True)
    sp_log_accommodation.add_argument("--new-schema-hypothesis", required=True)
    sp_log_accommodation.add_argument("--no-schema-version", action="store_true")
    sp_log_accommodation.add_argument("--schema-id", default=None)
    sp_log_accommodation.add_argument("--schema-name", default=None)
    sp_log_accommodation.add_argument("--schema-summary", default=None)
    sp_log_accommodation.add_argument("--assumption", action="append", default=[])
    sp_log_accommodation.add_argument("--prediction", action="append", default=[])
    sp_log_accommodation.add_argument("--boundary", action="append", default=[])
    sp_log_accommodation.add_argument("--source-ref", action="append", default=[])
    sp_log_accommodation.add_argument("--tag", action="append", default=[])
    sp_log_accommodation.set_defaults(func=cmd_log_accommodation)

    sp_log_equilibration = sub.add_parser("log-equilibration")
    sp_log_equilibration.add_argument("--topic", required=True)
    sp_log_equilibration.add_argument("--from-schema-version-id", required=True)
    sp_log_equilibration.add_argument("--to-schema-version-id", required=True)
    sp_log_equilibration.add_argument("--stabilizing-test", action="append", default=[])
    sp_log_equilibration.add_argument("--residual-tension", action="append", default=[])
    sp_log_equilibration.add_argument("--coherence-score", type=int, default=7)
    sp_log_equilibration.add_argument("--source-ref", action="append", default=[])
    sp_log_equilibration.add_argument("--tag", action="append", default=[])
    sp_log_equilibration.set_defaults(func=cmd_log_equilibration)

    sp_guardrail = sub.add_parser("guardrail-check")
    sp_guardrail.add_argument("--domain", required=True, choices=["invest", "project", "content"])
    sp_guardrail.add_argument("--decision-ref", default=None)
    sp_guardrail.add_argument("--guardrail-check-id", default=None)
    sp_guardrail.add_argument("--downside", default=None)
    sp_guardrail.add_argument("--invalidation-condition", default=None)
    sp_guardrail.add_argument("--max-loss", default=None)
    sp_guardrail.add_argument("--disconfirming-signal", default=None)
    sp_guardrail.add_argument("--emotional-weight", type=int, default=0)
    sp_guardrail.add_argument("--cooldown-applied", action="store_true")
    sp_guardrail.add_argument("--cooldown-hours", type=int, default=0)
    sp_guardrail.add_argument("--override-requested", action="store_true")
    sp_guardrail.add_argument("--override-reason", default=None)
    sp_guardrail.add_argument("--owner-confirmation", default=None)
    sp_guardrail.add_argument("--provider", default="dry-run")
    sp_guardrail.add_argument("--notes", default=None)
    sp_guardrail.set_defaults(func=cmd_guardrail_check)

    sp_log_decision = sub.add_parser("log-decision")
    sp_log_decision.add_argument("--domain", required=True)
    sp_log_decision.add_argument("--decision", required=True)
    sp_log_decision.add_argument("--option", action="append", default=[])
    sp_log_decision.add_argument("--confidence", required=True, type=int)
    sp_log_decision.add_argument("--reasoning", default=None)
    sp_log_decision.add_argument("--risk", action="append", default=[])
    sp_log_decision.add_argument("--expected-outcome", default=None)
    sp_log_decision.add_argument("--time-horizon", default=None)
    sp_log_decision.add_argument("--guardrail-check-id", default=None)
    sp_log_decision.add_argument("--downside", default=None)
    sp_log_decision.add_argument("--invalidation-condition", default=None)
    sp_log_decision.add_argument("--max-loss", default=None)
    sp_log_decision.add_argument("--disconfirming-signal", default=None)
    sp_log_decision.add_argument("--emotional-weight", type=int, default=0)
    sp_log_decision.add_argument("--cooldown-applied", action="store_true")
    sp_log_decision.add_argument("--cooldown-hours", type=int, default=0)
    sp_log_decision.add_argument("--override-requested", action="store_true")
    sp_log_decision.add_argument("--override-reason", default=None)
    sp_log_decision.add_argument("--owner-confirmation", default=None)
    sp_log_decision.add_argument("--follow-up-date", default=None)
    sp_log_decision.add_argument("--outcome", default=None)
    sp_log_decision.add_argument("--provider", default="dry-run")
    sp_log_decision.add_argument("--notes", default=None)
    sp_log_decision.set_defaults(func=cmd_log_decision)

    sp_metrics = sub.add_parser("metrics")
    sp_metrics.add_argument("--window", type=int, default=7)
    sp_metrics.add_argument("--output", default=None)
    sp_metrics.set_defaults(func=cmd_metrics)

    sp_owner = sub.add_parser("owner-report")
    sp_owner.add_argument("--window", type=int, default=7)
    sp_owner.add_argument("--output", default=None)
    sp_owner.set_defaults(func=cmd_owner_report)

    sp_schedule = sub.add_parser("schedule-run")
    sp_schedule.add_argument("--cycle", required=True, choices=["daily", "weekly", "monthly"])
    sp_schedule.add_argument("--scheduler", default="manual", choices=["manual", "cron"])
    sp_schedule.add_argument("--provider", default=None, choices=["dry-run", "handoff", "openai"])
    sp_schedule.add_argument("--model", default=None)
    sp_schedule.add_argument("--with-retrieval", action="store_true")
    sp_schedule.add_argument("--retrieval-top-k", type=int, default=6)
    sp_schedule.add_argument("--limit", type=int, default=None)
    sp_schedule.add_argument("--owner-window", type=int, default=7)
    sp_schedule.add_argument("--no-owner-report", action="store_true")
    sp_schedule.set_defaults(func=cmd_schedule_run)

    sp_validate = sub.add_parser("validate")
    sp_validate.add_argument("--strict", action="store_true")
    sp_validate.set_defaults(func=cmd_validate)

    sp_web = sub.add_parser("web")
    sp_web.add_argument("--host", default="127.0.0.1")
    sp_web.add_argument("--port", type=int, default=8765)
    sp_web.add_argument("--open-browser", action="store_true")
    sp_web.set_defaults(func=cmd_web)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
