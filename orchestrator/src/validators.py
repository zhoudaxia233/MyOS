from __future__ import annotations

import json
from pathlib import Path


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def append_jsonl(path: Path, obj: dict) -> None:
    ensure_parent(path)
    if not path.exists():
        path.write_text('{"_schema":{"name":"runs","version":"1.0","fields":["id","created_at","status","task","module","provider","result_path"],"notes":"append-only"}}\n', encoding="utf-8")
    first = path.read_text(encoding="utf-8").splitlines()[0]
    if '"_schema"' not in first:
        raise ValueError(f"Missing _schema header in {path}")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=True) + "\n")
