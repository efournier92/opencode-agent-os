#!/usr/bin/env python3
"""Validator for the Progressive Discovery store. Run with:

    python3 scripts/check_discovery.py [path]

Validates the index (six-field ID format, entry and file caps, external
evidence, scope header) and its sibling `archive/` directory (filename-to-heading
match) in one run. Exit 0 = clean, 1 = violation; orphan archive files warn on
stdout without changing the exit code. Evidence paths resolve against the target
repo root.
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT = "docs/discovery/DISCOVERY.md"
MAX_LINE = 240
MAX_BYTES = 8192
TYPES = ("find", "decision", "assumption", "trap", "question", "outcome")
EXTERNAL_TYPES = ("find", "decision", "trap", "outcome")
EXTS = (".md", ".py", ".sh", ".yaml", ".yml", ".json", ".txt")
ENTRY_RE = re.compile(
    r"^- (D-\d{8}-\d{2,}) \| (\d{4}-\d{2}-\d{2}) \| \[("
    + "|".join(TYPES)
    + r")\] \| ([^|]+?) \| ([^|]+?) \| (.+)$"
)
COMMAND_RE = re.compile(r"`([^`]+)`")


def find_base(target):
    for parent in target.resolve().parents:
        if (parent / ".git").exists():
            return parent
    return target.resolve().parent


def is_self_citation(base, candidate):
    discovery = (base / "docs" / "discovery").resolve()
    try:
        (base / candidate).resolve().relative_to(discovery)
        return True
    except ValueError:
        return False


def evidence_errors(lineno, evidence, base, entry_type):
    errors = []
    external = bool(COMMAND_RE.search(evidence))
    for raw in evidence.split():
        token = raw.strip("`").rstrip(".,;)")
        if not token:
            continue
        if "://" in token:
            external = True
            continue
        if "*" in token or "?" in token:
            continue
        head, sep, tail = token.rpartition(":")
        if sep and tail.isdigit():
            candidate, line_no = head, int(tail)
        else:
            candidate, line_no = token, None
        self_cite = is_self_citation(base, candidate)
        if not candidate.endswith(EXTS):
            if line_no is not None and not self_cite:
                external = True
            continue
        target = base / candidate
        if not target.exists():
            errors.append((lineno, f"dead evidence: {candidate}"))
        elif line_no is not None and line_no > len(target.read_text(errors="replace").splitlines()):
            errors.append((lineno, f"evidence line out of range: {candidate}:{line_no}"))
        if not self_cite:
            external = True
    if entry_type in EXTERNAL_TYPES and not external:
        errors.append((lineno, "insufficient evidence: self-citation only"))
    return errors


def entry_errors(lines, base):
    errors = []
    seen = set()
    for i, line in enumerate(lines, 1):
        if not line.startswith("- "):
            continue
        if len(line) > MAX_LINE:
            errors.append((i, f"entry line exceeds {MAX_LINE} characters"))
        match = ENTRY_RE.match(line)
        if not match:
            errors.append((i, "malformed entry: want `- D-YYYYMMDD-NN | YYYY-MM-DD | [type] | scope | finding | evidence`"))
            continue
        entry_id, date, entry_type, _, _, evidence = match.groups()
        if entry_id[2:10] != date.replace("-", ""):
            errors.append((i, f"id date mismatch: {entry_id}"))
        if entry_id in seen:
            errors.append((i, f"duplicate id: {entry_id}"))
        else:
            seen.add(entry_id)
        errors.extend(evidence_errors(i, evidence, base, entry_type))
    return errors


def scope_errors(lines):
    header = None
    header_line = 1
    used = {}
    for i, line in enumerate(lines, 1):
        if line.startswith("Scope tokens:"):
            header = {t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()}
            header_line = i
        elif line.startswith("- "):
            match = ENTRY_RE.match(line)
            if match:
                used.setdefault(match.group(4).strip(), i)
    header = header or set()
    errors = []
    for scope, lineno in used.items():
        if scope not in header:
            errors.append((lineno, f"undeclared scope: {scope}"))
    for scope in header:
        if scope not in used:
            errors.append((header_line, f"unused scope token: {scope}"))
    return errors


def archive_errors(archive_dir, live_ids):
    errors = []
    warnings = []
    if not archive_dir.is_dir():
        return errors, warnings
    for path in sorted(archive_dir.glob("*.md")):
        heading = ""
        for line in path.read_text(errors="replace").splitlines():
            if line.strip():
                heading = line.strip()
                break
        if heading != f"# {path.stem}":
            errors.append((path, f"archive header mismatch: {path}"))
        if path.stem not in live_ids:
            warnings.append(f"orphan archive: {path}")
    return errors, warnings


def main(argv):
    target = Path(argv[0]) if argv else Path(DEFAULT)
    if not target.is_absolute():
        target = REPO / target
    if not target.exists():
        print(f"{target}:1: file not found")
        return 1
    data = target.read_bytes()
    base = find_base(target)
    lines = data.decode("utf-8", "replace").splitlines()
    errors = entry_errors(lines, base) + scope_errors(lines)
    if len(data) > MAX_BYTES:
        errors.append((1, f"file exceeds {MAX_BYTES} bytes"))
    live_ids = {m.group(1) for m in (ENTRY_RE.match(line) for line in lines) if m}
    archive_errs, warnings = archive_errors(target.parent / "archive", live_ids)
    for lineno, message in sorted(errors):
        print(f"{target}:{lineno}: {message}")
    for path, message in archive_errs:
        print(f"{path}:1: {message}")
    for warning in warnings:
        print(warning)
    return 1 if errors or archive_errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
