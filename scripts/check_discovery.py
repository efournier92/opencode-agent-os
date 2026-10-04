#!/usr/bin/env python3
"""Validator for the Progressive Discovery index. Run with:

    python3 scripts/check_discovery.py [path]

Checks entry size, line format, and evidence liveness. Exit 0 = clean,
1 = violation. Evidence paths resolve against the target repo root.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT = "docs/discovery/DISCOVERY.md"
MAX_LINE = 240
MAX_BYTES = 8192
TYPES = ("find", "decision", "assumption", "trap", "question", "outcome")
EXTS = (".md", ".py", ".sh", ".yaml", ".yml", ".json", ".txt")
ENTRY_RE = re.compile(
    r"^- \d{4}-\d{2}-\d{2} \| \[(?:" + "|".join(TYPES) + r")\] \| .+ \| .+ \| .+$"
)


def find_base(target):
    for parent in target.resolve().parents:
        if (parent / ".git").exists():
            return parent
    return target.resolve().parent


def evidence_errors(lineno, evidence, base):
    errors = []
    for raw in evidence.split():
        token = raw.strip("`").rstrip(".,;)")
        if "://" in token or "*" in token or "?" in token:
            continue
        head, sep, tail = token.rpartition(":")
        if sep and tail.isdigit():
            candidate, line_no = head, int(tail)
        else:
            candidate, line_no = token, None
        if not candidate.endswith(EXTS):
            continue
        target = base / candidate
        if not target.exists():
            errors.append((lineno, f"dead evidence: {candidate}"))
        elif line_no is not None:
            lines = len(target.read_text(errors="replace").splitlines())
            if line_no > lines:
                errors.append((lineno, f"evidence line out of range: {candidate}:{line_no}"))
    return errors


def entry_errors(lines, base):
    errors = []
    for i, line in enumerate(lines, 1):
        if not line.startswith("- "):
            continue
        if len(line) > MAX_LINE:
            errors.append((i, f"entry line exceeds {MAX_LINE} characters"))
        if not ENTRY_RE.match(line):
            errors.append((i, "malformed entry: want `- YYYY-MM-DD | [type] | scope | finding | evidence`"))
            continue
        errors.extend(evidence_errors(i, line.split(" | ", 4)[4], base))
    return errors


def main(argv):
    target = Path(argv[0]) if argv else Path(DEFAULT)
    if not target.is_absolute():
        target = REPO / target
    if not target.exists():
        print(f"{target}:1: file not found")
        return 1
    data = target.read_bytes()
    base = find_base(target)
    errors = []
    if len(data) > MAX_BYTES:
        errors.append((1, f"file exceeds {MAX_BYTES} bytes"))
    errors.extend(entry_errors(data.decode("utf-8", "replace").splitlines(), base))
    for lineno, message in sorted(errors):
        print(f"{target}:{lineno}: {message}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
