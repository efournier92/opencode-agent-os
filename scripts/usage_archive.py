#!/usr/bin/env python3
"""Append-only archive of pruned session usage, so pruning cannot blind the gate."""

import json
import os
from pathlib import Path

DEFAULT_PATH = Path(
    os.environ.get("OPENCODE_USAGE_ARCHIVE")
    or Path.home() / ".local" / "share" / "opencode" / "usage-archive.jsonl"
)

KEYS = (
    "time_created",
    "time_updated",
    "model",
    "tokens_input",
    "tokens_output",
    "tokens_cache_read",
)


def append_rows(rows, path=DEFAULT_PATH):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(path.parent, 0o700)
    with open(path, "a", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps({key: row.get(key) for key in KEYS}) + "\n")
    os.chmod(path, 0o600)


def load_rows(path=DEFAULT_PATH):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows
