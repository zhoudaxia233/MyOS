import json
from pathlib import Path
from tempfile import TemporaryDirectory

from plugin_contract import validate_repo


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_validate_repo_passes_for_minimal_valid_plugin_contract() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)

        _write(root / "core/ROUTER.md", "# Router\n")
        _write(
            root / "orchestrator/config/routes.json",
            json.dumps(
                {
                    "default_module": "content",
                    "routes": [{"module": "content", "keywords": ["write"]}],
                }
            ),
        )
        _write(
            root / "routines/cadence.yaml",
            "\n".join(
                [
                    "routines:",
                    "  daily:",
                    "    - id: \"rt_daily_content\"",
                    "      module: \"content\"",
                    "      skill: \"write_one\"",
                    "      objective: \"Write one post\"",
                    "  weekly:",
                    "  monthly:",
                ]
            )
            + "\n",
        )

        _write(root / "modules/content/MODULE.md", "# Content\n")
        _write(
            root / "modules/content/module.manifest.yaml",
            json.dumps(
                {
                    "module": "content",
                    "routing": {"keywords": ["write"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            )
            + "\n",
        )
        (root / "modules/content/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/skills").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/logs").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/outputs").mkdir(parents=True, exist_ok=True)
        _write(root / "modules/content/data/voice.yaml", "tone: clear\n")
        _write(
            root / "modules/content/skills/write_one.md",
            "\n".join(
                [
                    "# Skill",
                    "1. `core/ROUTER.md`",
                    "2. `modules/content/data/voice.yaml`",
                ]
            )
            + "\n",
        )
        _write(
            root / "modules/content/logs/posts.jsonl",
            '{"_schema":{"name":"posts","version":"1.0","fields":["id"],"notes":"append-only"}}\n',
        )

        result = validate_repo(root)
        assert result["ok"] is True
        assert result["errors"] == []


def test_validate_repo_finds_contract_violations() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)

        _write(root / "core/ROUTER.md", "# Router\n")
        _write(
            root / "orchestrator/config/routes.json",
            json.dumps(
                {
                    "default_module": "unknown_module",
                    "routes": [
                        {"module": "content", "keywords": ["write"]},
                        {"module": "missing_module", "keywords": ["ghost"]},
                    ],
                }
            ),
        )
        _write(
            root / "routines/cadence.yaml",
            "\n".join(
                [
                    "routines:",
                    "  daily:",
                    "    - id: \"rt_daily_content\"",
                    "      module: \"content\"",
                    "      skill: \"missing_skill\"",
                    "      objective: \"Write one post\"",
                    "  weekly:",
                    "  monthly:",
                ]
            )
            + "\n",
        )

        _write(root / "modules/content/MODULE.md", "# Content\n")
        _write(
            root / "modules/content/module.manifest.yaml",
            json.dumps(
                {
                    "module": "content",
                    "routing": {"keywords": ["write"]},
                    "planning": {"default_skill": "MODULE", "default_output_prefix": "task", "rules": []},
                }
            )
            + "\n",
        )
        (root / "modules/content/data").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/skills").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/logs").mkdir(parents=True, exist_ok=True)
        (root / "modules/content/outputs").mkdir(parents=True, exist_ok=True)
        _write(root / "modules/content/data/voice.yaml", "tone: clear\n")
        _write(root / "modules/decision/data/heuristics.yaml", "x: 1\n")
        _write(
            root / "modules/content/skills/write_one.md",
            "\n".join(
                [
                    "# Skill",
                    "1. `modules/content/data/voice.yaml`",
                    "2. `modules/decision/data/heuristics.yaml`",
                    "3. `modules/content/data/missing.yaml`",
                ]
            )
            + "\n",
        )
        _write(root / "modules/content/logs/posts.jsonl", '{"bad":"header"}\n')

        result = validate_repo(root)
        assert result["ok"] is False
        codes = {e["code"] for e in result["errors"]}
        assert "skill.cross_module_ref" in codes
        assert "skill.ref_missing" in codes
        assert "jsonl.schema_missing" in codes
        assert "routes.module_not_found" in codes
        assert "cadence.skill_missing" in codes
