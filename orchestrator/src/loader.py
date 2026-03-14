from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from runtime_eligibility import RUNTIME_MATURITY_HOURS, list_runtime_influence_candidates

PATH_RE = re.compile(r"(?:core|modules|routines|orchestrator)/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|jsonl|json)")
TOKEN_RE = re.compile(r"[a-z0-9_]+")
RUNTIME_CONTEXT_LIMIT = 12
RUNTIME_CONTEXT_PATH = "orchestrator://runtime_eligible_artifacts"
INTENT_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
    "your",
    "about",
    "task",
    "tasks",
    "work",
    "need",
    "want",
    "should",
    "would",
    "could",
    "maybe",
    "then",
    "than",
    "when",
    "where",
    "what",
    "which",
    "while",
    "just",
    "also",
    "only",
    "very",
    "more",
    "less",
    "make",
    "done",
}


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


def _parse_iso8601(ts: str) -> datetime | None:
    text = str(ts or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _clip(text: str, limit: int) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 3)] + "..."


def _intent_terms(text: str | None, *, limit: int = 12) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for token in TOKEN_RE.findall(str(text or "").lower()):
        if len(token) < 3:
            continue
        if token in INTENT_STOPWORDS:
            continue
        if token in seen:
            continue
        seen.add(token)
        terms.append(token)
        if len(terms) >= max(1, int(limit)):
            break
    return terms


def _candidate_terms(row: dict) -> set[str]:
    text = " ".join(
        [
            str(row.get("artifact_type", "")).strip(),
            str(row.get("candidate_type", "")).strip(),
            str(row.get("title", "")).strip(),
            str(row.get("statement", "")).strip(),
            str(row.get("source_material_ref", "")).strip(),
        ]
    )
    out: set[str] = set()
    for token in TOKEN_RE.findall(text.lower()):
        if len(token) < 3:
            continue
        if token in INTENT_STOPWORDS:
            continue
        out.add(token)
    return out


def _rank_runtime_rows(rows: list[dict], intent_terms: list[str]) -> tuple[list[tuple[dict, int]], bool]:
    terms = set(intent_terms)
    scored: list[tuple[int, datetime, dict]] = []
    for row in rows:
        overlap = 0
        if terms:
            overlap = len(terms.intersection(_candidate_terms(row)))
        created = _parse_iso8601(str(row.get("promoted_at", "")).strip()) or _parse_iso8601(str(row.get("created_at", "")).strip())
        if created is None:
            created = datetime(1970, 1, 1, tzinfo=timezone.utc)
        scored.append((overlap, created, row))

    has_matches = any(item[0] > 0 for item in scored)
    if terms and has_matches:
        scored = [item for item in scored if item[0] > 0]

    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    ranked = [(row, overlap) for overlap, _, row in scored]
    return ranked, has_matches


def _build_runtime_context(
    repo_root: Path,
    module: str,
    now: datetime,
    intent_text: str | None = None,
) -> tuple[str, list[dict]]:
    rows = list_runtime_influence_candidates(repo_root, module, now=now)
    if not rows:
        return "", []

    intent_terms = _intent_terms(intent_text)
    ranked_rows, has_intent_matches = _rank_runtime_rows(rows, intent_terms)

    lines = [
        "# Runtime Eligible Artifacts (Injected)",
        "",
        f"- module: {module}",
        f"- maturity_hours: {RUNTIME_MATURITY_HOURS}",
        f"- source_count: {len(rows)}",
        f"- selected_count: {len(ranked_rows)}",
    ]
    if intent_terms:
        lines.append(f"- intent_terms: {', '.join(intent_terms)}")
        lines.append(f"- intent_filter: {'matched_only' if has_intent_matches else 'recent_fallback'}")
    lines.extend(
        [
            "",
        ]
    )
    influences: list[dict] = []
    for row, overlap in ranked_rows[:RUNTIME_CONTEXT_LIMIT]:
        candidate_type = str(row.get("artifact_type", "")).strip() or "unknown"
        title = _clip(str(row.get("title", "")).strip() or "candidate", 96)
        statement = _clip(str(row.get("statement", "")).strip(), 240)
        match_tag = f" [match={overlap}]" if intent_terms else ""
        selection_reason = "intent_match" if intent_terms and overlap > 0 else "recent_fallback"
        scope_modules = [str(item).strip() for item in row.get("scope_modules", []) if str(item).strip()]
        scope_summary = ",".join(scope_modules) if scope_modules else "-"
        autonomy_ceiling = str(row.get("autonomy_ceiling", "")).strip() or "suggest_only"
        artifact_ref = str(row.get("artifact_ref", "")).strip()
        promotion_ref = str(row.get("promotion_ref", "")).strip()
        approval_ref = str(row.get("approval_ref", "")).strip()
        source_summary = statement or title
        influences.append(
            {
                "artifact_ref": artifact_ref,
                "artifact_type": candidate_type,
                "title": title or None,
                "promotion_ref": promotion_ref or None,
                "approval_ref": approval_ref or None,
                "eligibility_ref": str(row.get("eligibility_ref", "")).strip() or None,
                "eligibility_status": str(row.get("eligibility_status", "")).strip() or None,
                "scope_modules": scope_modules,
                "autonomy_ceiling": autonomy_ceiling,
                "selection_reason": selection_reason,
                "match_score": overlap,
                "source_summary": source_summary or None,
            }
        )
        if statement:
            lines.append(
                f"- [{candidate_type}] {title}{match_tag} "
                f"(artifact={artifact_ref or '-'}, scope={scope_summary}, autonomy={autonomy_ceiling}): {statement}"
            )
        else:
            lines.append(
                f"- [{candidate_type}] {title}{match_tag} "
                f"(artifact={artifact_ref or '-'}, scope={scope_summary}, autonomy={autonomy_ceiling})"
            )
    return "\n".join(lines), influences


def load_context_bundle(
    repo_root: Path,
    module: str,
    max_chars: int,
    skill_path: str | None = None,
    intent_text: str | None = None,
) -> dict:
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
    runtime_influences: list[dict] = []

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

    if budget > 0:
        runtime_text, runtime_influences = _build_runtime_context(
            repo_root,
            module,
            now=datetime.now(timezone.utc),
            intent_text=intent_text,
        )
        if runtime_text:
            if len(runtime_text) > budget:
                runtime_text = runtime_text[: max(0, budget)]
            if runtime_text:
                bundle.append({"path": RUNTIME_CONTEXT_PATH, "content": runtime_text})

    return {"module": module, "files": bundle, "runtime_influences": runtime_influences}
