from __future__ import annotations

import json
import re
from pathlib import Path

from manifests import discover_module_manifests

TOKEN_RE = re.compile(r"[a-z0-9]+")

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
        {
            "module": "cognition",
            "keywords": [
                "schema",
                "mental model",
                "cognition",
                "assimilation",
                "accommodation",
                "disequilibrium",
                "equilibration",
                "contradiction",
                "model mismatch",
            ],
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


def _normalized_tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(str(text).lower())


def _normalized_keyword(text: str) -> str:
    return " ".join(_normalized_tokens(text))


def _match_keywords(task_tokens: list[str], keywords: list[str]) -> list[str]:
    task_token_set = set(task_tokens)
    task_norm = " ".join(task_tokens)

    matched: list[str] = []
    for raw in keywords:
        keyword = _normalized_keyword(raw)
        if not keyword:
            continue
        kw_tokens = keyword.split()
        if not kw_tokens:
            continue
        if len(kw_tokens) == 1:
            if kw_tokens[0] in task_token_set:
                matched.append(keyword)
            continue
        if " ".join(kw_tokens) in task_norm:
            matched.append(keyword)
    return matched


def _normalized_weights(raw: dict | None) -> dict[str, int]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, int] = {}
    for key, value in raw.items():
        kw = _normalized_keyword(str(key))
        if not kw:
            continue
        try:
            weight = int(value)
        except (TypeError, ValueError):
            continue
        out[kw] = max(1, min(weight, 100))
    return out


def _weight_for_keyword(keyword: str, weights: dict[str, int]) -> int:
    configured = weights.get(keyword)
    if configured is not None:
        return configured
    return 2 if " " in keyword else 1


def _score_matches(matched: list[str], weights: dict[str, int]) -> int:
    return sum(_weight_for_keyword(kw, weights) for kw in matched)


def _rank_manifest_candidates(task_tokens: list[str], manifests: dict[str, dict]) -> list[dict]:
    ranked: list[dict] = []
    for idx, (module_name, manifest) in enumerate(manifests.items()):
        routing = manifest.get("routing", {})
        positives = routing.get("keywords", [])
        negatives = routing.get("negative_keywords", [])
        weights = _normalized_weights(routing.get("keyword_weights"))

        matched_pos = _match_keywords(task_tokens, positives)
        if not matched_pos:
            continue
        matched_neg = _match_keywords(task_tokens, negatives)

        score = _score_matches(matched_pos, weights) - _score_matches(matched_neg, weights)
        if score <= 0:
            continue
        ranked.append(
            {
                "module": module_name,
                "score": score,
                "positive_hits": len(matched_pos),
                "negative_hits": len(matched_neg),
                "matched_keywords": matched_pos[:5],
                "negative_matches": matched_neg[:5],
                "_order": idx,
            }
        )

    ranked.sort(
        key=lambda c: (c["score"], c["positive_hits"], -c["negative_hits"], -c["_order"]),
        reverse=True,
    )
    return ranked


def _rank_routes_candidates(task_tokens: list[str], rules: dict) -> list[dict]:
    ranked: list[dict] = []

    for idx, rule in enumerate(rules["routes"]):
        module = str(rule.get("module", "")).strip()
        positives = [str(k).lower().strip() for k in rule.get("keywords", []) if str(k).strip()]
        negatives = [str(k).lower().strip() for k in rule.get("negative_keywords", []) if str(k).strip()]
        weights = _normalized_weights(rule.get("keyword_weights"))

        matched_pos = _match_keywords(task_tokens, positives)
        if not matched_pos:
            continue
        matched_neg = _match_keywords(task_tokens, negatives)

        score = _score_matches(matched_pos, weights) - _score_matches(matched_neg, weights)
        if score <= 0:
            continue
        ranked.append(
            {
                "module": module,
                "score": score,
                "positive_hits": len(matched_pos),
                "negative_hits": len(matched_neg),
                "matched_keywords": matched_pos[:5],
                "negative_matches": matched_neg[:5],
                "_order": idx,
            }
        )

    ranked.sort(
        key=lambda c: (c["score"], c["positive_hits"], -c["negative_hits"], -c["_order"]),
        reverse=True,
    )
    return ranked


def route_trace(task: str, forced_module: str | None = None, repo_root: Path | None = None) -> dict:
    if forced_module:
        return {
            "module": forced_module,
            "reason": "forced_module",
            "matched_keywords": [],
            "scoring": {
                "strategy": "forced_module",
                "manifest_candidates": [],
                "routes_candidates": [],
            },
        }

    task_tokens = _normalized_tokens(task)
    scoring: dict = {
        "strategy": "weighted_keyword",
        "manifest_candidates": [],
        "routes_candidates": [],
    }

    manifests = discover_module_manifests(repo_root) if repo_root else {}
    if manifests:
        manifest_ranked = _rank_manifest_candidates(task_tokens, manifests)
        scoring["manifest_candidates"] = [
            {k: v for k, v in candidate.items() if k != "_order"} for candidate in manifest_ranked[:5]
        ]
        if manifest_ranked:
            best = manifest_ranked[0]
            return {
                "module": best["module"],
                "reason": "manifest_keyword_match",
                "matched_keywords": best["matched_keywords"][:5],
                "scoring": scoring,
            }

    rules = load_route_rules(repo_root)
    route_ranked = _rank_routes_candidates(task_tokens, rules)
    scoring["routes_candidates"] = [{k: v for k, v in candidate.items() if k != "_order"} for candidate in route_ranked[:5]]
    if route_ranked:
        best = route_ranked[0]
        return {
            "module": best["module"],
            "reason": "routes_keyword_match",
            "matched_keywords": best["matched_keywords"][:5],
            "scoring": scoring,
        }

    return {
        "module": str(rules.get("default_module", "decision")),
        "reason": "fallback_default",
        "matched_keywords": [],
        "scoring": scoring,
    }


def route_task(task: str, forced_module: str | None = None, repo_root: Path | None = None) -> str:
    return route_trace(task, forced_module=forced_module, repo_root=repo_root)["module"]
