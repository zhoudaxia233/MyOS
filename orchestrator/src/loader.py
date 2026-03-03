from __future__ import annotations

from pathlib import Path
import re

PATH_RE = re.compile(r"(?:core|modules|routines|orchestrator)/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|jsonl|json)")


def _ordered_unique(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def _extract_paths_from_skill(text: str, module: str) -> list[str]:
    out: list[str] = []
    module_prefix = f"modules/{module}/"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Optional references are skipped by default for tighter progressive loading.
        if "only if" in line.lower() or "unless" in line.lower():
            continue
        for match in PATH_RE.findall(line):
            rel = match.strip()
            if "<" in rel or ">" in rel or "*" in rel:
                continue
            if "/outputs/" in rel:
                continue
            if rel.startswith("modules/") and not rel.startswith(module_prefix):
                continue
            out.append(rel)
    return _ordered_unique(out)


def load_context_bundle(repo_root: Path, module: str, max_chars: int, skill_path: str | None = None) -> dict:
    module_file = f"modules/{module}/MODULE.md"
    files = ["core/ROUTER.md", module_file]
    dynamic_refs: list[str] = []

    if skill_path and skill_path != module_file:
        files.append(skill_path)
        skill_abs = repo_root / skill_path
        if skill_abs.exists() and skill_abs.is_file():
            skill_text = skill_abs.read_text(encoding="utf-8")
            dynamic_refs.extend(_extract_paths_from_skill(skill_text, module))

    files = _ordered_unique(files + dynamic_refs)
    bundle: list[dict] = []
    budget = max_chars

    for rel in files:
        path = repo_root / rel
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if len(text) > budget:
            text = text[: max(0, budget)]
        budget -= len(text)
        bundle.append({"path": rel, "content": text})
        if budget <= 0:
            break

    return {"module": module, "files": bundle}
