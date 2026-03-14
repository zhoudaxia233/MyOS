from __future__ import annotations

import re
from typing import Any

REVIEW_OBJECT_TYPE_TRACE = "execution_trace"
REVIEW_OBJECT_TYPE_JUDGMENT_PROPOSAL = "judgment_proposal"

_TRACE_PREFIXES = (
    "# execution packet",
    "[begin personal core os handoff]",
)

_EXPLICIT_PROPOSAL_HEADINGS = (
    "judgment proposal",
    "owner proposal",
    "suggested judgment",
    "retained judgment",
    "content direction proposal",
    "owner action proposal",
)

_ACTION_SECTION_HEADINGS = (
    "owner actions",
    "recommended actions",
    "recommendations",
    "next actions",
    "next steps",
    "action proposals",
    "priority actions",
    "top owner actions",
    "top 3 owner actions",
    "experiments next week",
    "3 experiments next week",
    "3 owner actions",
)


def _clip(text: str, limit: int) -> str:
    raw = str(text or "").strip()
    if not raw:
        return ""
    if len(raw) <= limit:
        return raw
    return f"{raw[: max(0, limit - 3)].rstrip()}..."


def _normalize_heading(text: str) -> str:
    lowered = str(text or "").strip().lower()
    lowered = re.sub(r"[*_`>#:\-\[\]\(\)]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def _is_execution_trace_content(content: str) -> bool:
    lowered = str(content or "").strip().lower()
    if not lowered:
        return True
    return any(lowered.startswith(prefix) for prefix in _TRACE_PREFIXES)


def _extract_markdown_section(text: str, heading_aliases: tuple[str, ...]) -> tuple[str, list[str]] | None:
    lines = str(text or "").splitlines()
    active_heading = ""
    capture = False
    collected: list[str] = []

    for raw in lines:
        heading_match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", raw)
        if heading_match:
            normalized = _normalize_heading(heading_match.group(1))
            if capture:
                break
            if normalized in heading_aliases:
                capture = True
                active_heading = heading_match.group(1).strip()
                continue
        if capture:
            collected.append(raw.rstrip())

    if not active_heading:
        return None
    return active_heading, collected


def _extract_list_items(lines: list[str]) -> list[str]:
    items: list[str] = []
    for raw in lines:
        match = re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)(.+?)\s*$", raw)
        if match:
            item = _clip(match.group(1), 220)
            if item:
                items.append(item)
    return items


def _extract_paragraph_text(lines: list[str]) -> str:
    parts: list[str] = []
    for raw in lines:
        line = str(raw or "").strip()
        if not line:
            if parts:
                break
            continue
        if line.startswith("```"):
            break
        if re.match(r"^\s*(?:[-*+]\s+|\d+\.\s+)", line):
            continue
        parts.append(line)
    return _clip(" ".join(parts), 320)


def _proposal_from_section(
    *,
    heading: str,
    body_lines: list[str],
    kind: str,
    default_title: str,
    review_reason: str,
) -> dict[str, Any] | None:
    bullets = _extract_list_items(body_lines)
    paragraph = _extract_paragraph_text(body_lines)
    if not bullets and not paragraph:
        return None

    if bullets:
        first = bullets[0]
        title = _clip(f"{default_title}: {first}", 120)
        summary = _clip(" / ".join(bullets[:3]), 220)
        statement = "\n".join(f"- {item}" for item in bullets[:3])
    else:
        title = _clip(f"{default_title}: {paragraph}", 120)
        summary = _clip(paragraph, 220)
        statement = paragraph

    return {
        "review_object_type": REVIEW_OBJECT_TYPE_JUDGMENT_PROPOSAL,
        "proposal_kind": kind,
        "proposal_heading": heading,
        "proposal_title": title,
        "proposal_summary": summary,
        "proposal_statement": statement,
        "review_reason": review_reason,
    }


def extract_judgment_proposal(*, module: str, skill: str, content: str) -> dict[str, Any] | None:
    text = str(content or "").strip()
    if not text or _is_execution_trace_content(text):
        return None

    explicit = _extract_markdown_section(text, _EXPLICIT_PROPOSAL_HEADINGS)
    if explicit is not None:
        heading, body_lines = explicit
        return _proposal_from_section(
            heading=heading,
            body_lines=body_lines,
            kind="retained_judgment",
            default_title="Judgment proposal",
            review_reason="Extracted from an explicit proposal section in the run output.",
        )

    if str(module or "").strip().lower() == "decision":
        action_section = _extract_markdown_section(text, _ACTION_SECTION_HEADINGS)
        if action_section is not None:
            heading, body_lines = action_section
            return _proposal_from_section(
                heading=heading,
                body_lines=body_lines,
                kind="owner_action_proposal",
                default_title="Owner action proposal",
                review_reason="Extracted from a concrete action section in the decision output.",
            )

    if str(module or "").strip().lower() == "content":
        content_direction = _extract_markdown_section(
            text,
            ("content direction", "recommended angle", "recommended framing"),
        )
        if content_direction is not None:
            heading, body_lines = content_direction
            return _proposal_from_section(
                heading=heading,
                body_lines=body_lines,
                kind="content_direction_proposal",
                default_title="Content direction proposal",
                review_reason="Extracted from a concrete direction section in the content output.",
            )

    if str(skill or "").strip().endswith("weekly_review.md"):
        action_section = _extract_markdown_section(text, ("3 experiments next week", "experiments next week"))
        if action_section is not None:
            heading, body_lines = action_section
            return _proposal_from_section(
                heading=heading,
                body_lines=body_lines,
                kind="owner_action_proposal",
                default_title="Weekly review next-action proposal",
                review_reason="Extracted from the weekly review action section.",
            )

    return None


def build_run_review_object(*, module: str, skill: str, content: str) -> dict[str, Any]:
    proposal = extract_judgment_proposal(module=module, skill=skill, content=content)
    if proposal is not None:
        return proposal
    return {
        "review_object_type": REVIEW_OBJECT_TYPE_TRACE,
        "proposal_kind": None,
        "proposal_heading": None,
        "proposal_title": None,
        "proposal_summary": None,
        "proposal_statement": None,
        "review_reason": "Run trace only. No explicit judgment proposal was extracted from this output.",
    }


def is_reviewable_suggestion(row: dict[str, Any] | None) -> bool:
    if not isinstance(row, dict):
        return False
    if str(row.get("status", "active")).strip().lower() != "active":
        return False
    if str(row.get("review_object_type", "")).strip().lower() != REVIEW_OBJECT_TYPE_JUDGMENT_PROPOSAL:
        return False
    return any(str(row.get(key, "")).strip() for key in ("proposal_title", "proposal_summary", "proposal_statement"))
