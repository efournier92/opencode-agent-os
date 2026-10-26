#!/usr/bin/env python3
"""Validator for the critique ledger store. Run with:

    python3 scripts/check_critique.py [path]

Validates every `*.md` ledger under the target (default `docs/critique`): the
eight-field finding format, ID/date agreement, lens/severity/confidence/status
enums, resolving evidence (a `path:line`, a backticked command, or a URL), the
per-line and per-file caps, and ID uniqueness. Exit 0 = clean, 1 = violation.
Evidence paths resolve against the target repo root.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT = "docs/critique"
MAX_LINE = 240
MAX_BYTES = 16 * 1024
LENSES = (
    "security", "scale", "reliability", "cost", "abuse", "data-integrity",
    "maintainability", "correctness", "testing", "product", "compliance",
    "visual", "research",
)
LEVELS = ("high", "medium", "low")
STATUSES = ("open", "addressed", "rejected", "escalated")
FINDING_RE = re.compile(
    r"^- (C-\S+) \| (\d{4}-\d{2}-\d{2}) \| ([^|]+?) \| ([^|]+?) \| "
    r"([^|]+?) \| ([^|]+?) \| ([^|]+?) \| (.+)$"
)
ID_RE = re.compile(r"^C-(\d{8})-(\d{2,})$")
COMMAND_RE = re.compile(r"`([^`]+)`")


def find_base(target):
    start = (target if target.is_dir() else target.parent).resolve()
    for parent in [start, *start.parents]:
        if (parent / ".git").exists():
            return parent
    return start


def evidence_errors(lineno, evidence, base):
    errors = []
    evidence = evidence.strip()
    if not evidence:
        return [(lineno, "missing evidence")]
    if COMMAND_RE.search(evidence):
        return errors
    ok = False
    for raw in evidence.split():
        token = raw.strip("`").rstrip(".,;)")
        if not token:
            continue
        if "://" in token:
            ok = True
            continue
        if "*" in token or "?" in token:
            continue
        head, sep, tail = token.rpartition(":")
        if sep and tail.isdigit():
            candidate, line_no = head, int(tail)
        else:
            candidate, line_no = token, None
        target = base / candidate
        if not target.exists():
            errors.append((lineno, f"dead evidence: {candidate}"))
        elif line_no is not None and line_no > len(
            target.read_text(errors="replace").splitlines()
        ):
            errors.append((lineno, f"evidence line out of range: {candidate}:{line_no}"))
        else:
            ok = True
    if not ok and not errors:
        errors.append((lineno, "insufficient evidence: want a path, a command, or a URL"))
    return errors


def finding_errors(lineno, line, base):
    errors = []
    if len(line) > MAX_LINE:
        errors.append((lineno, f"finding line exceeds {MAX_LINE} characters"))
    match = FINDING_RE.match(line)
    if not match:
        errors.append((
            lineno,
            "malformed finding: want `- C-YYYYMMDD-NN | YYYY-MM-DD | lens | "
            "severity | confidence | status | finding | evidence`",
        ))
        return errors, None
    cid, date, lens, severity, confidence, status, _, evidence = match.groups()
    if "|" in evidence:
        errors.append((lineno, "pipe inside a field"))
    idm = ID_RE.match(cid)
    if not idm:
        errors.append((lineno, f"malformed id: {cid}"))
    elif idm.group(1) != date.replace("-", ""):
        errors.append((lineno, f"id date mismatch: {cid}"))
    if lens not in LENSES:
        errors.append((lineno, f"unknown lens: {lens}"))
    if severity not in LEVELS:
        errors.append((lineno, f"unknown severity: {severity}"))
    if confidence not in LEVELS:
        errors.append((lineno, f"unknown confidence: {confidence}"))
    if status not in STATUSES:
        errors.append((lineno, f"unknown status: {status}"))
    errors.extend(evidence_errors(lineno, evidence, base))
    return errors, cid


def file_errors(path):
    errors = []
    data = path.read_bytes()
    if len(data) > MAX_BYTES:
        errors.append((1, f"file exceeds {MAX_BYTES} bytes"))
    base = find_base(path)
    lines = data.decode("utf-8", "replace").splitlines()
    seen = set()
    in_findings = False
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "## Findings":
            in_findings = True
            continue
        if not in_findings or not line.startswith("- "):
            continue
        line_errors, cid = finding_errors(i, line, base)
        if cid is not None:
            if cid in seen:
                line_errors.append((i, f"duplicate id: {cid}"))
            else:
                seen.add(cid)
        errors.extend(line_errors)
    return errors


def main(argv):
    target = Path(argv[0]) if argv else Path(DEFAULT)
    if not target.is_absolute():
        target = REPO / target
    if not target.exists():
        if not argv:
            print(f"critique ledger clean (no {DEFAULT} directory)")
            return 0
        print(f"{target}:1: file not found")
        return 1
    files = sorted(target.glob("*.md")) if target.is_dir() else [target]
    errors = []
    for path in files:
        errors.extend((path, lineno, message) for lineno, message in file_errors(path))
    for path, lineno, message in errors:
        print(f"{path}:{lineno}: {message}")
    if errors:
        return 1
    print(f"critique ledger clean ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
