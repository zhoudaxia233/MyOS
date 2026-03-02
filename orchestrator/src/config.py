from __future__ import annotations

from pathlib import Path


def parse_simple_yaml(path: Path) -> dict:
    data: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip().strip('"')
    return data


def load_runtime_config(repo_root: Path) -> dict:
    cfg = parse_simple_yaml(repo_root / "orchestrator" / "config" / "runtime.yaml")
    return {
        "default_provider": cfg.get("default_provider", "manual"),
        "default_openai_model": cfg.get("default_openai_model", "gpt-4.1-mini"),
        "max_context_chars": int(cfg.get("max_context_chars", "24000")),
        "output_dir": cfg.get("output_dir", "orchestrator/logs"),
    }
