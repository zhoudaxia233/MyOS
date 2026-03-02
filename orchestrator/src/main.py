from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import uuid

from config import load_runtime_config
from loader import load_context_bundle
from metrics import compute_drift_metrics, render_metrics_report
from planner import plan_task
from retrieval import build_index, format_hits, load_retrieval_config, search_index
from router import route_task
from runner import run_with_provider
from scheduling import task_from_routine
from schedulers.cron import cron_hint
from schedulers.manual import get_cycle
from writer import log_metrics_snapshot, log_retrieval_query, log_run, log_schedule_run, write_output


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _id(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}"


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
        "id": _id("rq"),
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
    module = route_task(task, forced_module)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"])
    plan = plan_task(task, module, skill_hint=skill_hint, routine_id=routine_id)

    hits: list[dict] = []
    if with_retrieval:
        hits = _retrieval_hits(root, task, module, retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    content = run_with_provider(provider, task, module, plan, bundle, model)
    out = write_output(root, plan["output_path"], content)

    run_record = {
        "id": _id("run"),
        "created_at": _utc_now(),
        "status": "active",
        "task": task,
        "module": module,
        "provider": provider,
        "result_path": str(out.relative_to(root)),
    }
    log_run(root, run_record)

    if with_retrieval:
        _log_retrieval(root, task, module, retrieval_top_k, len(hits))

    return {
        "module": module,
        "plan": plan,
        "output_path": str(out.relative_to(root)),
        "retrieval_hits": len(hits),
    }


def cmd_inspect(args: argparse.Namespace) -> int:
    root = repo_root()
    cfg = load_runtime_config(root)
    module = route_task(args.task, args.module)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"])
    plan = plan_task(args.task, module)

    if args.with_retrieval:
        hits = _retrieval_hits(root, args.task, module, args.retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    print(f"Route: modules/{module}")
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


def cmd_metrics(args: argparse.Namespace) -> int:
    root = repo_root()
    snapshot = compute_drift_metrics(root, args.window)
    report = render_metrics_report(snapshot)

    if args.output:
        output_rel = args.output
    else:
        date = datetime.now(timezone.utc).strftime("%Y%m%d")
        output_rel = f"modules/decision/outputs/metrics_{date}.md"

    out = write_output(root, output_rel, report)
    try:
        report_path = str(out.relative_to(root))
    except ValueError:
        report_path = str(out)

    summary = {k: v["status"] for k, v in snapshot["metrics"].items()}
    record = {
        "id": _id("mt"),
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
            "id": _id("sr"),
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

    sp_metrics = sub.add_parser("metrics")
    sp_metrics.add_argument("--window", type=int, default=7)
    sp_metrics.add_argument("--output", default=None)
    sp_metrics.set_defaults(func=cmd_metrics)

    sp_schedule = sub.add_parser("schedule-run")
    sp_schedule.add_argument("--cycle", required=True, choices=["daily", "weekly", "monthly"])
    sp_schedule.add_argument("--scheduler", default="manual", choices=["manual", "cron"])
    sp_schedule.add_argument("--provider", default=None, choices=["manual", "openai"])
    sp_schedule.add_argument("--model", default=None)
    sp_schedule.add_argument("--with-retrieval", action="store_true")
    sp_schedule.add_argument("--retrieval-top-k", type=int, default=6)
    sp_schedule.add_argument("--limit", type=int, default=None)
    sp_schedule.set_defaults(func=cmd_schedule_run)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
