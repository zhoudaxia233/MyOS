from __future__ import annotations

import json
from pathlib import Path

DEFAULT_MANIFEST = {
    "module": "",
    "routing": {"keywords": [], "negative_keywords": [], "keyword_weights": {}},
    "planning": {
        "default_skill": "MODULE",
        "default_output_prefix": "task",
        "rules": [],
    },
}


def _normalize_manifest(raw: dict, module_name: str) -> dict:
    routing = raw.get("routing", {})
    planning = raw.get("planning", {})

    keywords = routing.get("keywords", [])
    if not isinstance(keywords, list):
        keywords = []
    keywords = [str(k).strip().lower() for k in keywords if str(k).strip()]

    negative_keywords = routing.get("negative_keywords", [])
    if isinstance(negative_keywords, str):
        negative_keywords = [negative_keywords]
    if not isinstance(negative_keywords, list):
        negative_keywords = []
    negative_keywords = [str(k).strip().lower() for k in negative_keywords if str(k).strip()]

    keyword_weights_raw = routing.get("keyword_weights", {})
    if not isinstance(keyword_weights_raw, dict):
        keyword_weights_raw = {}
    keyword_weights: dict[str, int] = {}
    for key, value in keyword_weights_raw.items():
        kw = str(key).strip().lower()
        if not kw:
            continue
        try:
            weight = int(value)
        except (TypeError, ValueError):
            continue
        keyword_weights[kw] = max(1, min(weight, 100))

    rules = planning.get("rules", [])
    if not isinstance(rules, list):
        rules = []

    normalized_rules: list[dict] = []
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            continue
        match_any = rule.get("match_any", [])
        if isinstance(match_any, str):
            match_any = [match_any]
        if not isinstance(match_any, list):
            match_any = []
        match_any = [str(v).strip().lower() for v in match_any if str(v).strip()]
        skill = str(rule.get("skill", "")).strip()
        output_prefix = str(rule.get("output_prefix", "")).strip() or "task"
        if not skill:
            continue
        normalized_rules.append(
            {
                "id": str(rule.get("id", f"rule_{i+1}")).strip() or f"rule_{i+1}",
                "match_any": match_any,
                "skill": skill,
                "output_prefix": output_prefix,
            }
        )

    manifest = {
        "module": str(raw.get("module", module_name)).strip() or module_name,
        "routing": {
            "keywords": keywords,
            "negative_keywords": negative_keywords,
            "keyword_weights": keyword_weights,
        },
        "planning": {
            "default_skill": str(planning.get("default_skill", "MODULE")).strip() or "MODULE",
            "default_output_prefix": str(planning.get("default_output_prefix", "task")).strip() or "task",
            "rules": normalized_rules,
        },
    }
    return manifest


def load_module_manifest(repo_root: Path, module_name: str) -> dict:
    path = repo_root / f"modules/{module_name}/module.manifest.yaml"
    if not path.exists() or not path.is_file():
        manifest = DEFAULT_MANIFEST.copy()
        manifest["module"] = module_name
        return manifest

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"Manifest must be an object: {path}")
    return _normalize_manifest(raw, module_name)


def discover_module_manifests(repo_root: Path) -> dict[str, dict]:
    modules_root = repo_root / "modules"
    if not modules_root.exists() or not modules_root.is_dir():
        return {}

    out: dict[str, dict] = {}
    for module_dir in sorted([d for d in modules_root.iterdir() if d.is_dir()], key=lambda p: p.name):
        if module_dir.name.startswith("."):
            continue
        name = module_dir.name
        out[name] = load_module_manifest(repo_root, name)
    return out
