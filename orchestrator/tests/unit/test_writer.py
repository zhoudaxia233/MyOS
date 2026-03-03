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
        out = write_output(root, "modules/decision/outputs/a.md", "ok")
        assert out.exists()
        assert out.read_text(encoding="utf-8") == "ok"
