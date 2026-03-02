from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import uuid

from config import load_runtime_config
from loader import load_context_bundle
from planner import plan_task
from router import route_task
from runner import run_with_provider
from writer import log_run, write_output


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cmd_inspect(args: argparse.Namespace) -> int:
    root = repo_root()
    cfg = load_runtime_config(root)
    module = route_task(args.task, args.module)
    bundle = load_context_bundle(root, module, cfg["max_context_chars"])
    plan = plan_task(args.task, module)

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

    print(f"Wrote: {out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Personal Core OS Orchestrator")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--task", required=True)
    common.add_argument("--module", default=None)

    sp_inspect = sub.add_parser("inspect", parents=[common])
    sp_inspect.set_defaults(func=cmd_inspect)

    sp_run = sub.add_parser("run", parents=[common])
    sp_run.add_argument("--provider", default=None, choices=["manual", "openai"])
    sp_run.add_argument("--model", default=None)
    sp_run.set_defaults(func=cmd_run)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
