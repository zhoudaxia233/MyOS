from __future__ import annotations

import re
from typing import Final

SUPPORTED_MODES: Final[tuple[str, ...]] = (
    "explore",
    "learn",
    "create",
    "decide",
    "review",
    "plan",
    "capture",
)

_URL_RE = re.compile(r"https?://\S+")
_DECIDE_PHRASES = (
    "should i",
    "what should i do",
    "need to decide",
    "whether to",
    "tradeoff",
    "trade-off",
    "conflicted",
    "which option",
    "pros and cons",
    "what do i do",
)
_CREATE_PHRASES = (
    "i want to write",
    "help me write",
    "turn this into",
    "shape this idea",
    "publish",
    "outline",
    "draft",
    "script",
    "essay",
    "episode",
    "thesis",
)
_LEARN_PHRASES = (
    "i read",
    "i watched",
    "i learned",
    "article",
    "transcript",
    "video",
    "book",
    "here is the link",
    "this struck me",
    "notes from",
)
_REVIEW_PHRASES = (
    "review",
    "git diff",
    "diff",
    "critique",
    "inspect",
    "pull request",
    "architecture review",
)
_PLAN_PHRASES = (
    "plan",
    "roadmap",
    "break this down",
    "steps",
    "sequence",
    "milestone",
)
_CAPTURE_PHRASES = (
    "capture this",
    "save this",
    "remember this",
    "log this",
    "note this",
)


def normalize_mode(raw_mode: str) -> str:
    mode = raw_mode.strip().lower()
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {raw_mode}")
    return mode


def detect_mode(text: str, explicit_mode: str | None = None) -> tuple[str, str]:
    if explicit_mode is not None:
        return normalize_mode(explicit_mode), "explicit"

    lowered = text.lower()
    if _matches_any(lowered, _DECIDE_PHRASES):
        return "decide", "heuristic"
    if _matches_any(lowered, _CREATE_PHRASES):
        return "create", "heuristic"
    if _matches_any(lowered, _LEARN_PHRASES) or _URL_RE.search(text):
        return "learn", "heuristic"
    if _matches_any(lowered, _REVIEW_PHRASES):
        return "review", "heuristic"
    if _matches_any(lowered, _PLAN_PHRASES):
        return "plan", "heuristic"
    if _matches_any(lowered, _CAPTURE_PHRASES):
        return "capture", "heuristic"
    return "explore", "heuristic"


def _matches_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)
