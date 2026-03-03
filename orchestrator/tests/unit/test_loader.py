from pathlib import Path
from tempfile import TemporaryDirectory

from loader import load_context_bundle


def test_load_context_bundle_from_skill_required_files() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "core").mkdir(parents=True, exist_ok=True)
        (root / "core/ROUTER.md").write_text("router", encoding="utf-8")

        (root / "modules/decision").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/MODULE.md").write_text("decision module", encoding="utf-8")
        (root / "modules/decision/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/logs").mkdir(parents=True, exist_ok=True)
        (root / "modules/decision/skills").mkdir(parents=True, exist_ok=True)

        (root / "modules/decision/data/heuristics.yaml").write_text("h: 1", encoding="utf-8")
        (root / "modules/decision/logs/decisions.jsonl").write_text(
            '{"_schema":{"name":"decisions","version":"1.0","fields":[],"notes":"append-only"}}\n',
            encoding="utf-8",
        )
        (root / "modules/content/data/voice.yaml").parent.mkdir(parents=True, exist_ok=True)
        (root / "modules/content/data/voice.yaml").write_text("should_not_load: true", encoding="utf-8")

        (root / "modules/decision/skills/weekly_review.md").write_text(
            "\n".join(
                [
                    "# Skill",
                    "1. `modules/decision/data/heuristics.yaml`",
                    "2. `modules/decision/logs/decisions.jsonl`",
                    "3. `modules/content/data/voice.yaml`",
                    "4. `modules/decision/logs/failures.jsonl` (only if needed)",
                ]
            ),
            encoding="utf-8",
        )

        bundle = load_context_bundle(
            root,
            module="decision",
            max_chars=10000,
            skill_path="modules/decision/skills/weekly_review.md",
        )
        paths = [f["path"] for f in bundle["files"]]

        assert "core/ROUTER.md" in paths
        assert "modules/decision/MODULE.md" in paths
        assert "modules/decision/skills/weekly_review.md" in paths
        assert "modules/decision/data/heuristics.yaml" in paths
        assert "modules/decision/logs/decisions.jsonl" in paths
        assert "modules/content/data/voice.yaml" not in paths
        assert "modules/decision/logs/failures.jsonl" not in paths
