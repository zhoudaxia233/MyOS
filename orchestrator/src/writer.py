from __future__ import annotations

from pathlib import Path

from validators import append_jsonl, ensure_parent


def write_output(repo_root: Path, output_rel: str, content: str) -> Path:
    p = repo_root / output_rel
    ensure_parent(p)
    p.write_text(content, encoding="utf-8")
    return p


def log_run(repo_root: Path, record: dict) -> None:
    runs = repo_root / "orchestrator" / "logs" / "runs.jsonl"
    append_jsonl(runs, record)
