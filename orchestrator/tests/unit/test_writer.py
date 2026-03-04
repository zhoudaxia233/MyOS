from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from writer import write_output


def test_write_output_blocks_path_escape() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        with pytest.raises(ValueError):
            write_output(root, "../escape.md", "x")


def test_write_output_accepts_repo_relative_path() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/decision/outputs").mkdir(parents=True, exist_ok=True)
        out = write_output(root, "modules/decision/outputs/a.md", "ok")
        assert out.exists()
        assert out.read_text(encoding="utf-8") == "ok"


def test_write_output_rejects_non_outputs_path() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        (root / "modules/decision/outputs").mkdir(parents=True, exist_ok=True)
        with pytest.raises(ValueError):
            write_output(root, "core/ROUTER.md", "x")


def test_write_output_rejects_unknown_module() -> None:
    with TemporaryDirectory() as td:
        root = Path(td)
        with pytest.raises(ValueError):
            write_output(root, "modules/nonexistent/outputs/a.md", "x")
