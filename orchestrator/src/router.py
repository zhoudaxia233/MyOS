from __future__ import annotations

import json
from pathlib import Path

from manifests import discover_module_manifests

DEFAULT_RULES = {
    "default_module": "decision",
    "routes": [
        {
            "module": "content",
            "keywords": ["write", "publish", "thread", "tone", "edit", "post", "draft", "message"],
        },
        {
            "module": "decision",
            "keywords": ["decision", "priority", "review", "failure", "risk", "audit", "tradeoff", "plan"],
        },
        {
            "module": "profile",
            "keywords": ["profile", "goal", "value", "alignment", "psych", "drift", "trigger", "identity"],
        },
        {
            "module": "memory",
            "keywords": ["memory", "reflect", "insight", "distill", "paradigm", "pattern", "chat", "journal"],
        },
    ],
}


def load_route_rules(repo_root: Path | None = None) -> dict:
    if repo_root is None:
        return DEFAULT_RULES
    path = repo_root / "orchestrator" / "config" / "routes.json"
    if not path.exists():
        return DEFAULT_RULES
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return DEFAULT_RULES
    routes = data.get("routes", [])
    if not isinstance(routes, list):
        routes = []
    return {
        "default_module": str(data.get("default_module", DEFAULT_RULES["default_module"])),
        "routes": [r for r in routes if isinstance(r, dict) and "module" in r],
    }


def route_trace(task: str, forced_module: str | None = None, repo_root: Path | None = None) -> dict:
    if forced_module:
        return {
            "module": forced_module,
            "reason": "forced_module",
            "matched_keywords": [],
        }

    t = task.lower()
    manifests = discover_module_manifests(repo_root) if repo_root else {}
    if manifests:
        for module_name, manifest in manifests.items():
            keywords = manifest.get("routing", {}).get("keywords", [])
            matched = [k for k in keywords if k in t]
            if matched:
                return {
                    "module": module_name,
                    "reason": "manifest_keyword_match",
                    "matched_keywords": matched[:5],
                }

    rules = load_route_rules(repo_root)

    for rule in rules["routes"]:
        module = str(rule.get("module", "")).strip()
        keywords = [str(k).lower().strip() for k in rule.get("keywords", []) if str(k).strip()]
        matched = [k for k in keywords if k in t]
        if matched:
            return {
                "module": module,
                "reason": "routes_keyword_match",
                "matched_keywords": matched[:5],
            }

    return {
        "module": str(rules.get("default_module", "decision")),
        "reason": "fallback_default",
        "matched_keywords": [],
    }


def route_task(task: str, forced_module: str | None = None, repo_root: Path | None = None) -> str:
    return route_trace(task, forced_module=forced_module, repo_root=repo_root)["module"]
