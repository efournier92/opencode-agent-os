#!/usr/bin/env python3
"""Tests for plugins/stale-session-guard.js. Run with:

    python3 -m unittest scripts/test_stale_guard.py
"""

import shutil
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "plugins" / "stale-session-guard.js"
THROW = 'throw new Error("STALE_SESSION_GUARD")'


def matching_brace(source, start):
    depth = 0
    for index in range(start, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return -1


class TestStaleGuard(unittest.TestCase):
    def test_node_syntax(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node not installed")
        result = subprocess.run(
            [node, "--check", str(SRC)], capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_contract(self):
        source = SRC.read_text()
        self.assertIn("STALE_SESSION_GUARD", source)
        self.assertIn('OPENCODE_STALE_GUARD === "0"', source)
        self.assertIn("OPENCODE_STALE_GUARD_IDLE_MS", source)
        self.assertIn("60 * 60 * 1000", source)
        self.assertIn("50000", source)
        throw = source.index(THROW)
        catch = source.rfind("catch", 0, throw)
        self.assertGreater(catch, -1)
        self.assertLess(matching_brace(source, source.index("{", catch)), throw)


if __name__ == "__main__":
    unittest.main()
