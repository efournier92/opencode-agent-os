#!/usr/bin/env python3
"""Detect drift between this repo and an installed config tree.

install.sh is manual-only, so an installed copy silently keeps serving stale
agents, skills, plugins, or rulebook after the repo changes. This compares only
the files install.sh fully owns (agents/generated, skills, plugins, docs/rulebook)
plus the plugin command files and AGENTS.md. It never flags commands/, models.yaml,
opencode.jsonc, or tui.json extras because those hold user edits.

Exit 0 when in sync or when OPENCODE_CONFIG_DIR does not exist (CI stays green).
Exit 1 and print MISSING/DIFFERS/STALE lines on any drift.
"""

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CFG = Path(os.environ.get("OPENCODE_CONFIG_DIR", str(Path.home() / ".config" / "opencode")))
SKIP = {"__pycache__", ".DS_Store"}

# (source, dest relative to CFG, full_replace). full_replace flags extras in dest.
PAIRS = (
    ("agents/generated", "agents", True),
    ("skills", "skills", True),
    ("plugins", "plugins", True),
    ("docs/rulebook", "docs/rulebook", True),
    ("commands", "commands", False),
)


def files(root):
    found = set()
    for path in root.rglob("*"):
        if path.is_file() and not SKIP.intersection(path.parts):
            found.add(path.relative_to(root).as_posix())
    return found


def compare(src, dest, full_replace):
    problems = []
    src_files = files(src)
    dest_files = files(dest) if dest.is_dir() else set()
    for rel in sorted(src_files):
        target = dest / rel
        if not target.is_file():
            problems.append(f"MISSING {target} (repo {src / rel})")
        elif (src / rel).read_bytes() != target.read_bytes():
            problems.append(f"DIFFERS {target}")
    if full_replace:
        for rel in sorted(dest_files - src_files):
            problems.append(f"STALE   {dest / rel} (not in {src})")
    return problems


def main():
    if not CFG.is_dir():
        return 0
    problems = []
    for src_rel, dest_rel, full in PAIRS:
        src = REPO / src_rel
        if src.exists():
            problems += compare(src, CFG / dest_rel, full)
    repo_agents = REPO / "AGENTS.md"
    installed = CFG / "AGENTS.md"
    if repo_agents.is_file() and installed.is_file():
        if repo_agents.read_bytes() != installed.read_bytes():
            problems.append(f"DIFFERS {installed}")
    for line in problems:
        print(line)
    if problems:
        print(f"\n{len(problems)} drifted file(s); run scripts/install.sh to sync")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
