#!/usr/bin/env python3
"""Warn when a global AGENTS.md is a byte-identical copy of the repo rulebook.

A global install plus a byte-identical project-root copy makes OpenCode load
the rulebook twice. Compares the repo AGENTS.md with
$OPENCODE_CONFIG_DIR/AGENTS.md (default ~/.config/opencode/AGENTS.md) and
prints a WARN when both exist and match. Always exits 0 so CI on a machine
without a global config is unaffected.
"""

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "AGENTS.md"
CFG = Path(os.environ.get("OPENCODE_CONFIG_DIR", str(Path.home() / ".config" / "opencode")))
DEST = CFG / "AGENTS.md"


def main():
    if SRC.is_file() and DEST.is_file() and SRC.read_bytes() == DEST.read_bytes():
        print(
            f"WARN: {DEST} is byte-identical to {SRC}; "
            "OpenCode loads the rulebook twice"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
