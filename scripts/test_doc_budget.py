#!/usr/bin/env python3
"""Context size budget and layout checks. Run with:

    python3 -m unittest scripts/test_doc_budget.py -v
    python3 scripts/test_doc_budget.py

Enforces the "Context Size Budget" section of AGENTS.md:

  1. Every context-loaded instruction file stays at 200 lines or fewer:
     agents/roles/*.md, agents/generated/*.md, skills/*/SKILL.md. The
     always-loaded pair (AGENTS.md, agents/roles/chief.md) is capped at 120.
  2. A 16 KB byte cap backstops line count (10 KB for the always-loaded pair).
  3. Every relative markdown link in a SKILL.md resolves to a file that exists.
  4. Every sibling file in a skill directory is referenced from its SKILL.md.
  5. Every `docs/rulebook/<name>.md` reference in an always-loaded or agent file
     resolves to a file that exists.

The 160-line warning band prints a note without failing. Exit code 0 =
clean, 1 = violation. Human docs (README.md, INSTALL.md) and historical or
append-only docs (docs/specs/, docs/discovery/) are out of scope.
"""

import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
CAP = 200
WARN = 160
MAX_BYTES = 16 * 1024
ALWAYS_ON = {"AGENTS.md", "agents/roles/chief.md"}
ALWAYS_ON_CAP = 120
ALWAYS_ON_BYTES = 10 * 1024
SKIP_PARTS = {"__pycache__", ".git"}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(\s*<?([^)>\s]+)")
RULEBOOK_RE = re.compile(r"`docs/rulebook/([A-Za-z0-9._-]+\.md)`")


def skill_files():
    return sorted(SKILLS.glob("*/SKILL.md"))


def budget_files():
    return (
        [REPO / "AGENTS.md"]
        + sorted((REPO / "agents" / "roles").glob("*.md"))
        + sorted((REPO / "agents" / "generated").glob("*.md"))
        + skill_files()
    )


def size_issues(paths):
    warnings, failures = [], []
    for path in paths:
        text = path.read_text()
        rel = path.relative_to(REPO).as_posix()
        lines = len(text.splitlines())
        nbytes = len(text.encode())
        cap = ALWAYS_ON_CAP if rel in ALWAYS_ON else CAP
        max_bytes = ALWAYS_ON_BYTES if rel in ALWAYS_ON else MAX_BYTES
        if lines > cap:
            failures.append((path, f"{lines} lines exceeds the {cap}-line cap"))
        elif lines > WARN:
            warnings.append((path, f"{lines} lines is over the {WARN}-line warn band"))
        if nbytes > max_bytes:
            failures.append((path, f"{nbytes} bytes exceeds the {max_bytes}-byte cap"))
    return warnings, failures


def layout_issues(paths):
    failures = []
    for path in paths:
        text = path.read_text()
        for target in MARKDOWN_LINK_RE.findall(text):
            if "://" in target or target.startswith(("mailto:", "#", "/")):
                continue
            if not (path.parent / target).exists():
                failures.append((path, f"link target not found: {target}"))
        for sibling in sorted(path.parent.rglob("*")):
            if not sibling.is_file() or sibling == path:
                continue
            if SKIP_PARTS.intersection(sibling.parts):
                continue
            rel = sibling.relative_to(path.parent).as_posix()
            if rel not in text:
                failures.append((path, f"sibling not referenced: {rel}"))
    return failures


def rulebook_issues(paths):
    failures = []
    for path in paths:
        for name in RULEBOOK_RE.findall(path.read_text()):
            if not (REPO / "docs" / "rulebook" / name).exists():
                failures.append((path, f"rulebook reference not found: docs/rulebook/{name}"))
    return failures


def main():
    paths = budget_files()
    missing = [p for p in paths if not p.exists()]
    if missing or not paths:
        print("missing budget file(s): " + ", ".join(str(p) for p in missing))
        return 1
    warnings, failures = size_issues(paths)
    failures += layout_issues(skill_files())
    failures += rulebook_issues(paths)
    for path, message in warnings:
        print(f"warning: {path.relative_to(REPO)}: {message}")
    for path, message in failures:
        print(f"error: {path.relative_to(REPO)}: {message}")
    if failures:
        print(f"\n{len(failures)} doc budget violation(s)")
        return 1
    print(f"doc budget clean ({len(paths)} files, cap {CAP} lines / {MAX_BYTES} bytes)")
    return 0


class TestDocBudget(unittest.TestCase):
    def test_within_size_budget(self):
        _, failures = size_issues(budget_files())
        self.assertEqual(failures, [], f"file(s) over budget: {failures}")

    def test_skill_layout_references_resolve(self):
        failures = layout_issues(skill_files())
        self.assertEqual(failures, [], f"skill layout problem(s): {failures}")

    def test_rulebook_references_resolve(self):
        failures = rulebook_issues(budget_files())
        self.assertEqual(failures, [], f"rulebook reference(s) dangling: {failures}")


if __name__ == "__main__":
    sys.exit(main())
