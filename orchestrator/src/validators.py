from __future__ import annotations

import json
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, obj: dict, schema_header: dict | None = None) -> None:
    ensure_parent(path)
    if not path.exists():
        if schema_header is None:
            raise ValueError(f"Missing schema_header for new JSONL file: {path}")
        path.write_text(json.dumps(schema_header, ensure_ascii=True) + "\n", encoding="utf-8")
    first = path.read_text(encoding="utf-8").splitlines()[0]
    if '"_schema"' not in first:
        raise ValueError(f"Missing _schema header in {path}")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=True) + "\n")
