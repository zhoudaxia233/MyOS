from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from config import load_runtime_config
from guardrails import evaluate_guardrail, load_domain_guardrails
from loader import load_context_bundle
from metrics import compute_drift_metrics, render_metrics_report
from owner_report import build_owner_snapshot, render_owner_report
from planner import plan_task
from plugin_contract import validate_repo
from retrieval import build_index, format_hits, load_retrieval_config, search_index
from router import route_trace
from runner import run_with_provider
from scheduling import task_from_routine
from schedulers.cron import cron_hint
from schedulers.manual import get_cycle
from writer import (
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


def _next_id(root: Path, prefix: str, log_rel_path: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = root / log_rel_path
    max_seq = 0

    if path.exists() and path.is_file():
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

    return f"{prefix}_{date}_{max_seq + 1:03d}"


def _root_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        try:
            return str(path.resolve().relative_to(root.resolve()))
        except ValueError:
            return str(path)


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
        "id": _next_id(root, "rq", cfg["query_log_path"]),
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
    route = route_trace(task, forced_module=forced_module, repo_root=root)
    module = route["module"]
    plan = plan_task(task, module, skill_hint=skill_hint, routine_id=routine_id, repo_root=root)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"], skill_path=plan["skill"])

    hits: list[dict] = []
    if with_retrieval:
        hits = _retrieval_hits(root, task, module, retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    content = run_with_provider(provider, task, module, plan, bundle, model)
    out = write_output(root, plan["output_path"], content)
    output_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    run_record = {
        "id": _next_id(root, "run", "orchestrator/logs/runs.jsonl"),
        "created_at": _utc_now(),
        "status": "active",
        "task": task,
        "module": module,
        "provider": provider,
        "skill": plan["skill"],
        "route_reason": route["reason"],
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
    route = route_trace(args.task, forced_module=args.module, repo_root=root)
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
    print(f"Skill: {plan['skill']}")
    print(f"Output path: {plan['output_path']}")
    print("Files:")
    for f in bundle["files"]:
        print(f"- {f['path']}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    root = repo_root()
    cfg = load_runtime_config(root)
    provider = args.provider or cfg["default_provider"]
    model = args.model or cfg["default_openai_model"]

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
            "id": _next_id(root, "go", "modules/decision/logs/guardrail_overrides.jsonl"),
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
        "id": _next_id(root, "mt", "orchestrator/logs/metrics_snapshots.jsonl"),
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
        "id": _next_id(root, "or", "orchestrator/logs/owner_reports.jsonl"),
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
    provider = args.provider or cfg["default_provider"]
    model = args.model or cfg["default_openai_model"]

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
            "id": _next_id(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
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
            "id": _next_id(root, "or", "orchestrator/logs/owner_reports.jsonl"),
            "created_at": _utc_now(),
            "status": "active",
            "window_days": args.owner_window,
            "summary": {k: v["status"] for k, v in owner_snapshot["metrics"]["metrics"].items()},
            "report_path": out_rel,
            "source_artifacts": owner_snapshot["source_artifacts"],
        }
        log_owner_report(root, owner_record)

        schedule_record = {
            "id": _next_id(root, "sr", "orchestrator/logs/schedule_runs.jsonl"),
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
    sp_run.add_argument("--provider", default=None, choices=["manual", "openai"])
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
    sp_guardrail.add_argument("--provider", default="manual")
    sp_guardrail.add_argument("--notes", default=None)
    sp_guardrail.set_defaults(func=cmd_guardrail_check)

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
    sp_schedule.add_argument("--provider", default=None, choices=["manual", "openai"])
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

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
