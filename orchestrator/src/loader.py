from __future__ import annotations

import re
import json
from datetime import datetime, timezone
from pathlib import Path

from runtime_eligibility import RUNTIME_MATURITY_HOURS, list_runtime_influence_candidates

PATH_RE = re.compile(r"(?:core|modules|routines|orchestrator)/[A-Za-z0-9_./-]+\.(?:md|yaml|yml|jsonl|json)")
TOKEN_RE = re.compile(r"[a-z0-9_]+")
RUNTIME_CONTEXT_LIMIT = 12
RUNTIME_CONTEXT_PATH = "orchestrator://runtime_eligible_artifacts"
CONTENT_DIRECTION_CONTEXT_PREFIX = "orchestrator://accepted_content_direction/"
CONTENT_DIRECTION_REF_RE = re.compile(
    r"(?:content direction proposal ref|accepted content direction ref|direction proposal ref|内容方向提案(?:\s*ref)?|已接受的内容方向提案(?:\s*ref)?)\s*[:：]\s*(sg_[A-Za-z0-9_]+)",
    re.IGNORECASE,
)
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


def _read_jsonl_records(path: Path) -> list[dict]:
    if not path.exists() or not path.is_file():
        return []
    rows: list[dict] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if i == 1 and '"_schema"' in line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def _find_jsonl_record_by_id(path: Path, record_id: str) -> dict | None:
    rid = str(record_id).strip()
    if not rid:
        return None
    for row in reversed(_read_jsonl_records(path)):
        if str(row.get("id", "")).strip() == rid:
            return row
    return None


def _find_latest_jsonl_record_by_field(path: Path, *, key: str, value: str) -> dict | None:
    match_value = str(value).strip()
    if not match_value:
        return None
    for row in reversed(_read_jsonl_records(path)):
        if str(row.get(key, "")).strip() == match_value and str(row.get("status", "active")).strip().lower() == "active":
            return row
    return None


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


def _content_direction_ref(intent_text: str | None) -> str | None:
    text = str(intent_text or "").strip()
    if not text:
        return None
    match = CONTENT_DIRECTION_REF_RE.search(text)
    if not match:
        return None
    ref = str(match.group(1) or "").strip()
    return ref or None


def _allows_content_direction_context(module: str, skill_path: str | None) -> bool:
    if str(module or "").strip().lower() != "content":
        return False
    skill_norm = str(skill_path or "").strip().replace("\\", "/").lower()
    if not skill_norm:
        return False
    return not skill_norm.endswith("propose_content_direction.md")


def _build_content_direction_context(
    repo_root: Path,
    *,
    suggestion_id: str,
) -> tuple[str, str] | None:
    suggestions_path = repo_root / "orchestrator/logs/suggestions.jsonl"
    verdicts_path = repo_root / "orchestrator/logs/owner_verdicts.jsonl"
    corrections_path = repo_root / "orchestrator/logs/owner_corrections.jsonl"

    suggestion = _find_jsonl_record_by_id(suggestions_path, suggestion_id)
    if not isinstance(suggestion, dict):
        return None
    if str(suggestion.get("status", "active")).strip().lower() != "active":
        return None
    if str(suggestion.get("proposal_kind", "")).strip().lower() != "content_direction_proposal":
        return None

    verdict = _find_latest_jsonl_record_by_field(verdicts_path, key="suggestion_ref", value=suggestion_id)
    if not isinstance(verdict, dict):
        return None
    verdict_kind = str(verdict.get("verdict", "")).strip().lower()
    if verdict_kind not in {"accept", "modify"}:
        return None

    correction: dict | None = None
    verdict_id = str(verdict.get("id", "")).strip()
    if verdict_id:
        correction = _find_latest_jsonl_record_by_field(corrections_path, key="verdict_ref", value=verdict_id)
    if correction is None:
        correction = _find_latest_jsonl_record_by_field(corrections_path, key="suggestion_ref", value=suggestion_id)

    effective_direction = ""
    if verdict_kind == "modify" and isinstance(correction, dict):
        effective_direction = str(correction.get("replacement_judgment", "")).strip()
    if not effective_direction:
        effective_direction = (
            str(suggestion.get("proposal_statement", "")).strip()
            or str(suggestion.get("proposal_summary", "")).strip()
            or str(suggestion.get("proposal_title", "")).strip()
        )
    if not effective_direction:
        return None

    source_output_path = str(suggestion.get("recommendation_path", "")).strip()
    owner_note = str(verdict.get("owner_note", "")).strip()
    proposal_title = str(suggestion.get("proposal_title", "")).strip()

    lines = [
        "# Accepted Content Direction Context",
        "",
        f"- suggestion_ref: {suggestion_id}",
        f"- verdict: {verdict_kind}",
    ]
    if source_output_path:
        lines.append(f"- source_output_path: {source_output_path}")
    if proposal_title:
        lines.append(f"- proposal_title: {proposal_title}")
    lines.extend(
        [
            "- usage: treat this as framing guidance for the draft; do not copy this heading or metadata into the final artifact.",
            "",
            "## Effective Direction",
            effective_direction,
        ]
    )
    if owner_note:
        lines.extend(["", "## Owner Note", owner_note])
    if isinstance(correction, dict):
        unlike_me_reason = str(correction.get("unlike_me_reason", "")).strip()
        if unlike_me_reason:
            lines.extend(["", "## Rewrite Rationale", unlike_me_reason])

    return f"{CONTENT_DIRECTION_CONTEXT_PREFIX}{suggestion_id}", "\n".join(lines)


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
    content_direction_ref = None
    if _allows_content_direction_context(module, skill_path):
        content_direction_ref = _content_direction_ref(intent_text)

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

    if budget > 0 and content_direction_ref:
        direction_context = _build_content_direction_context(repo_root, suggestion_id=content_direction_ref)
        if direction_context is not None:
            virtual_path, content = direction_context
            if len(content) > budget:
                content = content[: max(0, budget)]
            if content:
                budget -= len(content)
                bundle.append({"path": virtual_path, "content": content})

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
