"""MyOS MCP Server — thin tool layer for Claude Code integration.

Exposes 6 focused tools. Routing, context loading, and governance protocol
are internalized by the LLM through CLAUDE.md + core/ROUTER.md + skill files.
This server only handles operations that require schema validation, ID
generation, or aggregation that cannot be done safely by raw file writes.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure orchestrator/src is in sys.path when run directly
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from mcp.server.fastmcp import FastMCP

from guardrails import evaluate_guardrail, load_domain_guardrails
from idgen import next_id_for_rel_path
from main import log_decision_core
from metrics import compute_cognition_trend, compute_drift_metrics, render_metrics_report
from plugin_contract import validate_repo
from retrieval import build_index, format_hits, load_retrieval_config, search_index
from validators import append_jsonl, ensure_parent


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


mcp = FastMCP("myos")


@mcp.tool()
def myos_append_log(log_rel_path: str, id_prefix: str, record: dict) -> str:
    """Append a validated record to a MyOS JSONL log file.

    Automatically generates a unique ID and UTC timestamp. The log file must
    already exist with a valid _schema header on line 1.

    Args:
        log_rel_path: Path relative to repo root (e.g. 'modules/decision/logs/decisions.jsonl')
        id_prefix: Short prefix for the auto-generated ID (e.g. 'dc' for decisions, 'me' for memory events)
        record: The record fields to append. Do NOT include 'id' or 'created_at' — those are auto-set.

    Returns:
        The generated record ID (e.g. 'dc_20260315_001')
    """
    root = _repo_root()
    record_id = next_id_for_rel_path(root, id_prefix, log_rel_path)
    full_record = {
        "id": record_id,
        "created_at": _utc_now(),
        **{k: v for k, v in record.items() if k not in ("id", "created_at")},
    }
    if "status" not in full_record:
        full_record["status"] = "active"
    log_path = root / log_rel_path
    append_jsonl(log_path, full_record)
    return record_id


@mcp.tool()
def myos_search(query: str, top_k: int = 8, module: str | None = None) -> str:
    """Search the MyOS retrieval index across all log history.

    Args:
        query: Search query string (natural language or keywords)
        top_k: Number of results to return (default 8)
        module: Optional module filter ('decision', 'memory', 'content', 'profile', 'cognition', 'principles')

    Returns:
        Formatted search results with score, module, and matched text
    """
    root = _repo_root()
    hits = search_index(root, query, top_k=top_k, module=module)
    if not hits:
        return "No results found."
    return format_hits(hits)


@mcp.tool()
def myos_validate(strict: bool = True) -> str:
    """Run plugin contract validation on the full MyOS repository.

    Checks module structure, skill references, JSONL schema headers,
    record-level integrity (id / timestamp / status / source_refs),
    routes config, and cadence references.

    Args:
        strict: If True, treat warnings as errors (default True)

    Returns:
        Validation report with PASS/FAIL status, error count, and error details
    """
    root = _repo_root()
    result = validate_repo(root)
    errors = result.get("errors", [])
    warnings = result.get("warnings", [])

    passed = not errors and (not strict or not warnings)
    lines = [
        f"Status: {'PASS' if passed else 'FAIL'}",
        f"Errors: {len(errors)}",
        f"Warnings: {len(warnings)}",
    ]
    if errors:
        lines.append("\nErrors:")
        for e in errors:
            lines.append(f"  - {e.get('message', str(e))}")
    if warnings and strict:
        lines.append("\nWarnings (strict mode — treated as errors):")
        for w in warnings:
            lines.append(f"  - {w.get('message', str(w))}")
    return "\n".join(lines)


@mcp.tool()
def myos_metrics(window_days: int = 7) -> str:
    """Compute and return the MyOS drift metrics report.

    Aggregates decision, memory, and profile drift indicators over the
    specified window. Includes cognitive schema evolution trend.

    Args:
        window_days: Time window in days. Use 7 for weekly, 30 for monthly.

    Returns:
        Formatted metrics report in markdown with status indicators
    """
    root = _repo_root()
    snapshot = compute_drift_metrics(root, window_days)
    snapshot["cognitive_trend"] = compute_cognition_trend(root)
    return render_metrics_report(snapshot)


@mcp.tool()
def myos_guardrail_check(
    domain: str,
    guardrail_check_id: str,
    downside: str | None = None,
    invalidation_condition: str | None = None,
    max_loss: str | None = None,
    disconfirming_signal: str | None = None,
    emotional_weight: int = 0,
    cooldown_applied: bool = False,
    cooldown_hours: int = 0,
    override_requested: bool = False,
    override_reason: str | None = None,
    owner_confirmation: str | None = None,
) -> str:
    """Evaluate domain guardrail policy for a decision payload.

    Checks the decision against domain-specific risk rules (blocking conditions,
    emotion thresholds, cooldown requirements, principle constraints).

    Args:
        domain: Decision domain ('invest', 'project', 'content')
        guardrail_check_id: Reference ID for this check (use next available pc_YYYYMMDD_NNN)
        downside: Downside risk description
        invalidation_condition: Condition that invalidates the thesis
        max_loss: Maximum acceptable loss (e.g. '0.5R')
        disconfirming_signal: Signal that would disconfirm the decision
        emotional_weight: Emotional pressure level 0-10 (0=none, 10=maximum)
        cooldown_applied: Whether a cooldown period was observed before this decision
        cooldown_hours: Duration of cooldown applied in hours
        override_requested: Whether owner is requesting to override a guardrail violation
        override_reason: Rationale for the override
        owner_confirmation: Owner confirmation text for the override

    Returns:
        Guardrail evaluation result: status, violations, cooldown requirements
    """
    root = _repo_root()
    policy = load_domain_guardrails(root)
    payload = {
        "guardrail_check_id": guardrail_check_id,
        "downside": downside,
        "invalidation_condition": invalidation_condition,
        "max_loss": max_loss,
        "disconfirming_signal": disconfirming_signal,
        "emotional_weight": emotional_weight,
        "cooldown_applied": cooldown_applied,
        "cooldown_hours": cooldown_hours,
        "override_requested": override_requested,
        "override_reason": override_reason,
        "owner_confirmation": owner_confirmation,
    }
    result = evaluate_guardrail(policy, domain, payload)

    lines = [
        f"Status: {result['status']}",
        f"Violations: {result['violations']}",
        f"Cooldown required: {result['cooldown_required']}",
    ]
    if result["cooldown_required"]:
        lines.append(f"Required cooldown hours: {result['required_cooldown_hours']}")
    if result.get("missing_override_fields"):
        lines.append(f"Missing override fields: {result['missing_override_fields']}")
    return "\n".join(lines)


@mcp.tool()
def myos_build_index() -> str:
    """Rebuild the MyOS retrieval index over all JSONL log history.

    Indexes records from decision, memory, profile, content, and cognition logs
    using TF-IDF scoring for semantic search.

    Returns:
        Summary: number of documents indexed and index path
    """
    root = _repo_root()
    cfg = load_retrieval_config(root)
    index = build_index(root, cfg.get("source_globs"))
    doc_count = len(index.get("docs", []))
    index_path = cfg.get("index_path", "orchestrator/retrieval/index.json")
    return f"Index built: {doc_count} documents indexed at {index_path}"


if __name__ == "__main__":
    mcp.run()
