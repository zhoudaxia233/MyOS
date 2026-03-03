from __future__ import annotations

import json
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory

import main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_jsonl(path: Path, schema_name: str, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema = {"_schema": {"name": schema_name, "version": "1.0", "fields": fields, "notes": "append-only"}}
    with path.open("w", encoding="utf-8") as f:
        f.write(json.dumps(schema) + "\n")
        for row in rows:
            f.write(json.dumps(row) + "\n")


def _manifest(module: str, keywords: list[str], rules: list[dict]) -> str:
    return json.dumps(
        {
            "module": module,
            "routing": {"keywords": keywords},
            "planning": {
                "default_skill": "MODULE",
                "default_output_prefix": "task",
                "rules": rules,
            },
        }
    )


def _build_repo(root: Path) -> None:
    _write(root / "core/ROUTER.md", "# Router\n")
    _write(root / "orchestrator/config/runtime.yaml", 'default_provider: "manual"\ndefault_openai_model: "gpt-4.1-mini"\nmax_context_chars: 24000\n')
    _write(
        root / "orchestrator/config/routes.json",
        json.dumps(
            {
                "default_module": "decision",
                "routes": [{"module": "decision", "keywords": ["decision", "review"]}],
            }
        ),
    )

    _write(
        root / "routines/cadence.yaml",
        "\n".join(
            [
                "routines:",
                "  daily:",
                "  weekly:",
                "    - id: \"rt_weekly_decision_review\"",
                "      module: \"decision\"",
                "      skill: \"weekly_review\"",
                "      objective: \"Run weekly decision review\"",
                "  monthly:",
            ]
        )
        + "\n",
    )

    # Template module
    _write(root / "modules/_template/MODULE.md", "# Template\n")
    _write(root / "modules/_template/module.manifest.yaml", _manifest("_template", [], []))
    for d in ["data", "logs", "skills", "outputs"]:
        (root / f"modules/_template/{d}").mkdir(parents=True, exist_ok=True)

    # Content module
    _write(root / "modules/content/MODULE.md", "# Content\n")
    _write(
        root / "modules/content/module.manifest.yaml",
        _manifest(
            "content",
            ["write", "post"],
            [{"id": "fahou", "match_any": ["fahou"], "skill": "write_fahou_message", "output_prefix": "fahou"}],
        ),
    )
    _write(root / "modules/content/skills/write_fahou_message.md", "# Skill\n1. `modules/content/data/voice.yaml`\n")
    _write(root / "modules/content/data/voice.yaml", "tone: clear\n")
    _write_jsonl(
        root / "modules/content/logs/posts.jsonl",
        "posts",
        ["id", "created_at", "status", "platform", "title", "url", "idea_id", "metrics"],
        [],
    )
    (root / "modules/content/outputs").mkdir(parents=True, exist_ok=True)

    # Decision module
    _write(root / "modules/decision/MODULE.md", "# Decision\n")
    _write(
        root / "modules/decision/module.manifest.yaml",
        _manifest(
            "decision",
            ["decision", "review", "audit"],
            [
                {
                    "id": "weekly_review",
                    "match_any": ["weekly", "review"],
                    "skill": "weekly_review",
                    "output_prefix": "weekly_review",
                },
                {
                    "id": "decision_audit",
                    "match_any": ["audit"],
                    "skill": "audit_decision_system",
                    "output_prefix": "decision_audit",
                },
            ],
        ),
    )
    _write(
        root / "modules/decision/skills/weekly_review.md",
        "\n".join(
            [
                "# Skill",
                "1. `modules/decision/data/heuristics.yaml`",
                "2. `modules/decision/logs/decisions.jsonl`",
                "3. `modules/decision/logs/failures.jsonl`",
                "4. `modules/decision/logs/experiences.jsonl`",
                "5. `modules/decision/logs/precommit_checks.jsonl`",
                "6. `modules/decision/logs/guardrail_overrides.jsonl`",
            ]
        )
        + "\n",
    )
    _write(root / "modules/decision/skills/audit_decision_system.md", "# Skill\n")
    _write(root / "modules/decision/skills/owner_report.md", "# Skill\n")
    _write(root / "modules/decision/data/heuristics.yaml", "priorities:\n  - focus\n")
    _write(root / "modules/decision/data/impulse_guardrails.yaml", "high_risk_domains:\n  - \"invest\"\n  - \"project\"\n")
    _write(root / "modules/decision/data/audit_rules.yaml", "rules: []\n")
    _write(root / "modules/decision/data/domain_guardrails.yaml", "domains:\n  content:\n    require_precommit: false\n")
    _write_jsonl(
        root / "modules/decision/logs/decisions.jsonl",
        "decisions",
        ["id", "created_at", "status", "domain", "decision", "options", "reasoning", "risks", "expected_outcome", "time_horizon", "confidence", "guardrail_check_id", "follow_up_date", "outcome"],
        [
            {
                "id": "dc_20260304_001",
                "created_at": "2026-03-04T10:00:00Z",
                "status": "active",
                "domain": "project",
                "decision": "Ship weekly review",
                "options": ["ship", "delay"],
                "reasoning": "Need cadence stability",
                "risks": ["minor bug"],
                "expected_outcome": "faster loop",
                "time_horizon": "1 week",
                "confidence": 8,
                "guardrail_check_id": None,
                "follow_up_date": None,
                "outcome": None,
            }
        ],
    )
    _write_jsonl(
        root / "modules/decision/logs/failures.jsonl",
        "failures",
        ["id", "created_at", "status", "domain", "what_happened", "root_cause", "prevention", "lesson", "emotional_weight"],
        [],
    )
    _write_jsonl(
        root / "modules/decision/logs/experiences.jsonl",
        "experiences",
        ["id", "created_at", "status", "event", "why_it_mattered", "signals", "emotional_weight", "tags"],
        [],
    )
    _write_jsonl(
        root / "modules/decision/logs/precommit_checks.jsonl",
        "precommit_checks",
        ["id", "created_at", "status", "domain", "proposed_decision", "emotional_weight", "downside", "invalidation_condition", "max_loss", "disconfirming_signal", "cooldown_required", "override_reason", "owner_confirmation", "result"],
        [],
    )
    _write_jsonl(
        root / "modules/decision/logs/guardrail_overrides.jsonl",
        "guardrail_overrides",
        ["id", "created_at", "status", "domain", "decision_ref", "violations", "override_reason", "owner_confirmation", "provider", "notes"],
        [],
    )
    (root / "modules/decision/outputs").mkdir(parents=True, exist_ok=True)

    # Memory module
    _write(root / "modules/memory/MODULE.md", "# Memory\n")
    _write(
        root / "modules/memory/module.manifest.yaml",
        _manifest(
            "memory",
            ["memory", "distill", "pattern"],
            [{"id": "distill", "match_any": ["weekly", "distill"], "skill": "distill_weekly", "output_prefix": "weekly_memory"}],
        ),
    )
    _write(root / "modules/memory/skills/distill_weekly.md", "# Skill\n")
    _write(root / "modules/memory/data/memory_policy.yaml", "policy: simple\n")
    _write_jsonl(
        root / "modules/memory/logs/memory_events.jsonl",
        "memory_events",
        ["id", "created_at", "status", "source_type", "event", "why_it_matters", "tags", "source_refs"],
        [],
    )
    (root / "modules/memory/outputs").mkdir(parents=True, exist_ok=True)

    # Profile module
    _write(root / "modules/profile/MODULE.md", "# Profile\n")
    _write(
        root / "modules/profile/module.manifest.yaml",
        _manifest(
            "profile",
            ["profile", "alignment", "trigger"],
            [{"id": "snapshot", "match_any": ["snapshot"], "skill": "profile_snapshot", "output_prefix": "profile_snapshot"}],
        ),
    )
    _write(root / "modules/profile/skills/profile_snapshot.md", "# Skill\n")
    _write(root / "modules/profile/data/identity.yaml", "north_star: stable\n")
    _write_jsonl(
        root / "modules/profile/logs/trigger_events.jsonl",
        "trigger_events",
        ["id", "created_at", "status", "context", "trigger_signal", "response", "mitigation", "emotional_weight", "tags"],
        [],
    )
    _write_jsonl(
        root / "modules/profile/logs/psych_observations.jsonl",
        "psych_observations",
        ["id", "created_at", "status", "observation", "evidence", "source_refs", "confidence", "suggested_stabilizer", "tags"],
        [],
    )
    _write_jsonl(
        root / "modules/profile/logs/profile_changes.jsonl",
        "profile_changes",
        ["id", "created_at", "status", "change_type", "change_summary", "reason", "expected_effect", "source_refs"],
        [],
    )
    (root / "modules/profile/outputs").mkdir(parents=True, exist_ok=True)


def test_e2e_cli_command_chain(monkeypatch, capsys) -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        _build_repo(root)
        monkeypatch.setattr(main, "repo_root", lambda: root)

        rc = main.cmd_validate(Namespace(strict=True))
        assert rc == 0
        out = capsys.readouterr().out
        assert "Validation status: PASS" in out

        rc = main.cmd_inspect(
            Namespace(task="run weekly decision review", module=None, with_retrieval=False, retrieval_top_k=6)
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "Route: modules/decision" in out
        assert "Route reason: manifest_keyword_match" in out
        assert "modules/decision/skills/weekly_review.md" in out

        rc = main.cmd_run(
            Namespace(
                task="run weekly decision review",
                module=None,
                with_retrieval=False,
                retrieval_top_k=6,
                provider="manual",
                model=None,
            )
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "Wrote:" in out
        assert len(list((root / "modules/decision/outputs").glob("weekly_review_*.md"))) >= 1
        runs_path = root / "orchestrator/logs/runs.jsonl"
        lines = runs_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) >= 2
        record = json.loads(lines[-1])
        assert record["route_reason"] in {"manifest_keyword_match", "routes_keyword_match", "forced_module", "fallback_default"}
        assert record["skill"] == "modules/decision/skills/weekly_review.md"
        assert isinstance(record["matched_keywords"], list)
        assert isinstance(record["loaded_files"], list)
        assert len(record["output_hash"]) == 64

        rc = main.cmd_metrics(Namespace(window=7, output=None))
        assert rc == 0
        capsys.readouterr()
        assert len(list((root / "modules/decision/outputs").glob("metrics_*.md"))) == 1

        rc = main.cmd_owner_report(Namespace(window=7, output=None))
        assert rc == 0
        capsys.readouterr()
        assert len(list((root / "modules/decision/outputs").glob("owner_report_*.md"))) == 1

        rc = main.cmd_schedule_run(
            Namespace(
                cycle="weekly",
                scheduler="manual",
                provider="manual",
                model=None,
                with_retrieval=False,
                retrieval_top_k=6,
                limit=1,
                owner_window=7,
                no_owner_report=True,
            )
        )
        assert rc == 0
        out = capsys.readouterr().out
        assert "Running cycle: weekly" in out
        assert "rt_weekly_decision_review" in out

        rc = main.cmd_validate(Namespace(strict=True))
        assert rc == 0
        out = capsys.readouterr().out
        assert "Validation status: PASS" in out
