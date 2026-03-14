import json
from datetime import datetime, timezone
from pathlib import Path

from owner_report import (
    build_owner_snapshot,
    render_owner_report,
    render_owner_todos,
    resolve_owner_todo,
    summarize_suggestion_review_trend,
    summarize_suggestion_reviews,
    sync_owner_todos,
)


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_owner_snapshot_and_render() -> None:
    from tempfile import TemporaryDirectory

    now = datetime(2026, 3, 3, 10, 0, tzinfo=timezone.utc)

    with TemporaryDirectory() as td:
        root = Path(td)

        (root / "modules/decision/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/data/impulse_guardrails.yaml").write_text(
            "high_risk_domains:\n  - \"invest\"\n  - \"project\"\n", encoding="utf-8"
        )

        _write_jsonl(
            root / "modules/decision/logs/decisions.jsonl",
            "decisions",
            ["id", "created_at", "domain", "guardrail_check_id"],
            [
                {
                    "id": "dc_1",
                    "created_at": "2026-03-02T10:00:00Z",
                    "domain": "invest",
                    "guardrail_check_id": None,
                }
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/precommit_checks.jsonl",
            "precommit_checks",
            ["id", "created_at", "cooldown_required", "result"],
            [
                {
                    "id": "pc_1",
                    "created_at": "2026-03-02T10:00:00Z",
                    "cooldown_required": True,
                    "result": "pass_with_cooldown",
                }
            ],
        )

        _write_jsonl(
            root / "modules/decision/logs/failures.jsonl",
            "failures",
            ["id", "created_at", "root_cause"],
            [{"id": "fx_1", "created_at": "2026-03-02T09:30:00Z", "root_cause": "review latency"}],
        )

        _write_jsonl(
            root / "modules/profile/logs/trigger_events.jsonl",
            "trigger_events",
            ["id", "created_at", "emotional_weight"],
            [],
        )

        _write_jsonl(
            root / "modules/profile/logs/psych_observations.jsonl",
            "psych_observations",
            ["id", "created_at", "confidence"],
            [],
        )

        _write_jsonl(
            root / "modules/decision/logs/guardrail_overrides.jsonl",
            "guardrail_overrides",
            ["id", "created_at", "domain"],
            [{"id": "go_1", "created_at": "2026-03-02T11:00:00Z", "domain": "invest"}],
        )

        (root / "modules/decision/outputs").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/outputs/decision_audit_20260302.md").write_text(
            "No major exceptions in this window.", encoding="utf-8"
        )
        (root / "modules/decision/outputs/weekly_review_20260302.md").write_text(
            "Sample-size limitation noted.", encoding="utf-8"
        )
        (root / "modules/decision/outputs/metrics_20260302.md").write_text(
            "\n".join(
                [
                    "# Drift Dashboard",
                    "",
                    "| Metric | Value | Threshold | Status | Detail |",
                    "|---|---:|---:|---|---|",
                    "| Precommit Coverage | 90.0% | 80.0% | pass | 9/10 |",
                    "| Cooldown Compliance | 100.0% | 90.0% | pass | 1/1 |",
                    "| Repeat Failure Rate | 0.0% | 30.0% | pass | 0/1 |",
                    "| Profile Drift Rate | 0.0% | 40.0% | pass | 0/0 |",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        (root / "modules/cognition/outputs").mkdir(parents=True, exist_ok=True)
        (root / "modules/cognition/outputs/cognitive_timeline_20260302.md").write_text(
            "Cognitive Evolution Timeline", encoding="utf-8"
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_reports.jsonl",
            "owner_reports",
            ["id", "created_at", "status", "window_days", "summary", "report_path", "source_artifacts"],
            [
                {
                    "id": "or_20260224_001",
                    "created_at": "2026-02-24T10:00:00Z",
                    "status": "active",
                    "window_days": 7,
                    "summary": {
                        "precommit_coverage": "fail",
                        "cooldown_compliance": "pass",
                        "repeat_failure_rate": "pass",
                        "profile_drift_rate": "pass",
                        "unresolved_disequilibrium_rate": "pass",
                        "equilibration_quality_rate": "warn",
                        "schema_explicitness_rate": "warn",
                    },
                    "report_path": "modules/decision/outputs/owner_report_20260224.md",
                    "source_artifacts": {},
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/learning_candidates.jsonl",
            "learning_candidates",
            ["id", "created_at", "status", "candidate_type", "candidate_state", "proposal_target"],
            [
                {
                    "id": "lc_1",
                    "created_at": "2026-03-02T08:00:00Z",
                    "status": "active",
                    "candidate_type": "rule",
                    "candidate_state": "pending_review",
                    "proposal_target": "decision",
                },
                {
                    "id": "lc_2",
                    "created_at": "2026-03-01T08:00:00Z",
                    "status": "active",
                    "candidate_type": "insight",
                    "candidate_state": "pending_review",
                    "proposal_target": "memory",
                },
                {
                    "id": "lc_3",
                    "created_at": "2026-02-21T08:00:00Z",
                    "status": "active",
                    "candidate_type": "insight",
                    "candidate_state": "pending_review",
                    "proposal_target": "memory",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_verdicts.jsonl",
            "learning_candidate_verdicts",
            ["id", "created_at", "status", "candidate_ref", "verdict"],
            [
                {
                    "id": "lv_1",
                    "created_at": "2026-03-02T09:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_1",
                    "verdict": "reject",
                },
                {
                    "id": "lv_2",
                    "created_at": "2026-03-01T09:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_2",
                    "verdict": "accept",
                },
                {
                    "id": "lv_3",
                    "created_at": "2026-02-21T09:00:00Z",
                    "status": "active",
                    "candidate_ref": "lc_3",
                    "verdict": "accept",
                },
            ],
        )
        _write_jsonl(
            root / "modules/decision/logs/learning_candidate_promotions.jsonl",
            "learning_candidate_promotions",
            ["id", "created_at", "status", "candidate_ref", "promotion_target"],
            [
                {
                    "id": "lp_1",
                    "created_at": "2026-02-21T09:30:00Z",
                    "status": "active",
                    "candidate_ref": "lc_3",
                    "promotion_target": "memory",
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/suggestions.jsonl",
            "suggestions",
            [
                "id",
                "created_at",
                "status",
                "module",
                "task_raw",
                "review_object_type",
                "proposal_kind",
                "proposal_title",
                "proposal_summary",
            ],
            [
                {
                    "id": "sg_1",
                    "created_at": "2026-03-02T11:15:00Z",
                    "status": "active",
                    "module": "decision",
                    "task_raw": "triage weekly decision queue",
                    "review_object_type": "judgment_proposal",
                    "proposal_kind": "owner_action_proposal",
                    "proposal_title": "Owner action proposal: tighten weekly review scope",
                    "proposal_summary": "Tighten weekly review scope and add explicit risk notes.",
                },
                {
                    "id": "sg_2",
                    "created_at": "2026-03-01T10:15:00Z",
                    "status": "active",
                    "module": "memory",
                    "task_raw": "ingest learning summary",
                    "review_object_type": "judgment_proposal",
                    "proposal_kind": "retained_judgment",
                    "proposal_title": "Judgment proposal: preserve this learning summary for later review",
                    "proposal_summary": "Keep the learning summary visible for judgment review.",
                },
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_verdicts.jsonl",
            "owner_verdicts",
            ["id", "created_at", "status", "suggestion_ref", "verdict", "owner_note", "correction_ref", "source_refs"],
            [
                {
                    "id": "ov_1",
                    "created_at": "2026-03-02T11:20:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_1",
                    "verdict": "accept",
                    "owner_note": "Aligned with current execution priority.",
                    "correction_ref": None,
                    "source_refs": ["sg_1"],
                }
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_corrections.jsonl",
            "owner_corrections",
            [
                "id",
                "created_at",
                "status",
                "suggestion_ref",
                "verdict_ref",
                "target_layer",
                "replacement_judgment",
                "unlike_me_reason",
                "source_refs",
            ],
            [],
        )

        snapshot = build_owner_snapshot(root, window_days=7, now=now)
        report = render_owner_report(snapshot)

        assert snapshot["override_count"] == 1
        assert isinstance(snapshot["candidate_pipeline_summary"], dict)
        assert isinstance(snapshot["candidate_pipeline_trend"], dict)
        assert isinstance(snapshot["suggestion_review_summary"], dict)
        assert snapshot["suggestion_review_summary"]["suggestions_total"] == 2
        assert snapshot["suggestion_review_summary"]["reviewed_total"] == 1
        assert isinstance(snapshot["suggestion_review_trend"], dict)
        assert any(a.startswith("metrics_mismatch:precommit_coverage:") for a in snapshot["consistency_alerts"])
        assert any(a.startswith("decision_audit_conflict:") for a in snapshot["consistency_alerts"])
        assert any(a.startswith("weekly_review_conflict:") for a in snapshot["consistency_alerts"])
        assert isinstance(snapshot["auto_triggers"], list)
        assert "precommit_coverage" in snapshot["consecutive_fail_metrics"]
        assert any(e["type"] == "candidate_review_drift_trend" for e in snapshot["top_exceptions"])
        assert len(snapshot["escalation_todos"]) >= 1
        assert "guardrail_overrides.invest" in report
        assert "Consistency Alerts" in report
        assert "Auto Triggers" in report
        assert "Learning Candidate Pipeline" in report
        assert "Learning Candidate Trend (7d vs 30d)" in report
        assert "Suggestion Review Loop" in report
        assert "Suggestion Review Trend (7d vs 30d)" in report
        assert "Escalation Todos (2W Fail)" in report
        assert "[RED-2W]" in report
        assert "Owner Report" in report
        assert "Executive Summary" in report
        assert "cognition_timeline" in report
        todos = render_owner_todos(snapshot)
        assert "Owner Escalation Todos" in todos
        assert "(RED) precommit_coverage" in todos


def test_suggestion_review_summary_filter_and_trend() -> None:
    from tempfile import TemporaryDirectory

    now = datetime(2026, 3, 9, 10, 0, tzinfo=timezone.utc)

    with TemporaryDirectory() as td:
        root = Path(td)

        _write_jsonl(
            root / "orchestrator/logs/suggestions.jsonl",
            "suggestions",
            [
                "id",
                "created_at",
                "status",
                "module",
                "task_raw",
                "review_object_type",
                "proposal_kind",
                "proposal_title",
                "proposal_summary",
            ],
            [
                {
                    "id": "sg_1",
                    "created_at": "2026-03-08T10:00:00Z",
                    "status": "active",
                    "module": "decision",
                    "task_raw": "task a",
                    "review_object_type": "judgment_proposal",
                    "proposal_kind": "owner_action_proposal",
                    "proposal_title": "Owner action proposal A",
                    "proposal_summary": "Action bundle A",
                },
                {
                    "id": "sg_2",
                    "created_at": "2026-03-07T10:00:00Z",
                    "status": "active",
                    "module": "decision",
                    "task_raw": "task b",
                    "review_object_type": "judgment_proposal",
                    "proposal_kind": "owner_action_proposal",
                    "proposal_title": "Owner action proposal B",
                    "proposal_summary": "Action bundle B",
                },
                {
                    "id": "sg_3",
                    "created_at": "2026-02-20T10:00:00Z",
                    "status": "active",
                    "module": "memory",
                    "task_raw": "task c",
                    "review_object_type": "judgment_proposal",
                    "proposal_kind": "retained_judgment",
                    "proposal_title": "Judgment proposal C",
                    "proposal_summary": "Action bundle C",
                },
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_verdicts.jsonl",
            "owner_verdicts",
            ["id", "created_at", "status", "suggestion_ref", "verdict", "owner_note", "correction_ref", "source_refs"],
            [
                {
                    "id": "ov_1",
                    "created_at": "2026-03-08T11:00:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_1",
                    "verdict": "modify",
                    "owner_note": "n1",
                    "correction_ref": "oc_1",
                    "source_refs": ["sg_1"],
                },
                {
                    "id": "ov_2",
                    "created_at": "2026-02-21T11:00:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_3",
                    "verdict": "accept",
                    "owner_note": "n2",
                    "correction_ref": None,
                    "source_refs": ["sg_3"],
                },
            ],
        )
        _write_jsonl(
            root / "orchestrator/logs/owner_corrections.jsonl",
            "owner_corrections",
            [
                "id",
                "created_at",
                "status",
                "suggestion_ref",
                "verdict_ref",
                "target_layer",
                "replacement_judgment",
                "unlike_me_reason",
                "source_refs",
            ],
            [
                {
                    "id": "oc_1",
                    "created_at": "2026-03-08T11:05:00Z",
                    "status": "active",
                    "suggestion_ref": "sg_1",
                    "verdict_ref": "ov_1",
                    "target_layer": "decision",
                    "replacement_judgment": "r1",
                    "unlike_me_reason": "u1",
                    "source_refs": ["sg_1", "ov_1"],
                }
            ],
        )

        summary_all = summarize_suggestion_reviews(root, window_days=30, now=now)
        assert summary_all["suggestions_total"] == 3
        assert summary_all["reviewed_total"] == 2
        assert summary_all["verdicts"]["modify"] == 1
        assert summary_all["verdicts"]["accept"] == 1
        assert summary_all["corrections_total"] == 1

        summary_modify = summarize_suggestion_reviews(root, window_days=30, now=now, verdict_filter="modify")
        assert summary_modify["verdict_filter"] == "modify"
        assert summary_modify["reviewed_total"] == 1
        assert summary_modify["verdicts"]["modify"] == 1
        assert summary_modify["verdicts"]["accept"] == 0

        trend = summarize_suggestion_review_trend(root, now=now)
        assert "windows" in trend
        assert "7d" in trend["windows"]
        assert "30d" in trend["windows"]
        assert isinstance(trend.get("comparisons"), list)


def test_owner_todo_queue_sync_and_resolve() -> None:
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/decision/logs").mkdir(parents=True, exist_ok=True)
        snapshot = {
            "escalation_todos": [
                {
                    "id": "two_week_fail_precommit_coverage",
                    "metric": "precommit_coverage",
                    "priority": "red",
                    "action": "Enforce guardrail_check_id for every high-risk decision next week.",
                }
            ]
        }

        first = sync_owner_todos(root, snapshot, owner_report_ref="or_20260307_001")
        assert len(first["appended_ids"]) == 1
        assert len(first["existing_ids"]) == 0

        second = sync_owner_todos(root, snapshot, owner_report_ref="or_20260307_002")
        assert len(second["appended_ids"]) == 0
        assert len(second["existing_ids"]) == 1

        resolved = resolve_owner_todo(
            root,
            todo_id=first["appended_ids"][0],
            note="Guardrail check coverage enforcement merged.",
            owner_report_ref="or_20260314_001",
        )
        assert resolved["status"] == "archived"
        assert resolved["resolution_of"] == first["appended_ids"][0]
