from __future__ import annotations

from pathlib import Path

MINIMAL_MAP = {
    "content": [
        "modules/content/data/voice.yaml",
        "modules/content/data/anti_patterns.md",
        "modules/content/skills/write_fahou_message.md",
    ],
    "decision": [
        "modules/decision/data/heuristics.yaml",
        "modules/decision/data/impulse_guardrails.yaml",
        "modules/decision/data/audit_rules.yaml",
        "modules/decision/skills/weekly_review.md",
    ],
    "profile": [
        "modules/profile/data/identity.yaml",
        "modules/profile/data/operating_preferences.yaml",
        "modules/profile/data/psych_profile.yaml",
        "modules/profile/skills/profile_snapshot.md",
    ],
    "memory": [
        "modules/memory/data/memory_policy.yaml",
        "modules/memory/data/pattern_taxonomy.yaml",
        "modules/memory/skills/extract_chat_patterns.md",
    ],
}


def load_context_bundle(repo_root: Path, module: str, max_chars: int) -> dict:
    files = ["core/ROUTER.md", f"modules/{module}/MODULE.md"] + MINIMAL_MAP.get(module, [])
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
