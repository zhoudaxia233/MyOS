from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import uuid

from config import load_runtime_config
from loader import load_context_bundle
from planner import plan_task
from retrieval import build_index, format_hits, load_retrieval_config, search_index
from router import route_task
from runner import run_with_provider
from writer import log_retrieval_query, log_run, write_output


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


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
        "id": f"rq_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "active",
        "query": query,
        "module": module,
        "top_k": top_k,
        "result_count": result_count,
    }
    log_retrieval_query(root, rec, cfg["query_log_path"])


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

    module = route_task(args.task, args.module)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"])
    plan = plan_task(args.task, module)

    hits: list[dict] = []
    if args.with_retrieval:
        hits = _retrieval_hits(root, args.task, module, args.retrieval_top_k)
        bundle = _bundle_with_hits(bundle, hits)

    content = run_with_provider(provider, args.task, module, plan, bundle, model)
    out = write_output(root, plan["output_path"], content)

    record = {
        "id": f"run_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{str(uuid.uuid4())[:8]}",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "active",
        "task": args.task,
        "module": module,
        "provider": provider,
        "result_path": str(out.relative_to(root)),
    }
    log_run(root, record)

    if args.with_retrieval:
        _log_retrieval(root, args.task, module, args.retrieval_top_k, len(hits))

    print(f"Wrote: {out}")
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

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
