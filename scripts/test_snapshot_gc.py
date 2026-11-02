#!/usr/bin/env python3
"""Tests for scripts/snapshot_gc.py. Run with:

    python3 -m unittest discover -s scripts -p 'test_snapshot_gc.py' -v
"""

import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "snapshot_gc.py"

REFERENCED = "a" * 40
UNREFERENCED = "b" * 40
IGNORED = "not-a-hash"

SCHEMA = """
CREATE TABLE session (id TEXT PRIMARY KEY, revert TEXT);
CREATE TABLE message (id TEXT PRIMARY KEY, data TEXT);
CREATE TABLE part (id TEXT PRIMARY KEY, data TEXT);
"""


class SnapshotGcTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "snapshot"
        self.root.mkdir()
        self.db = Path(self.tmp.name) / "opencode.db"
        (self.root / REFERENCED).mkdir()
        (self.root / UNREFERENCED).mkdir()
        (self.root / IGNORED).mkdir()
        conn = sqlite3.connect(self.db)
        conn.executescript(SCHEMA)
        conn.execute(
            "INSERT INTO session(id, revert) VALUES (?, ?)",
            ("ses_1", '{"snapshot": "%s"}' % REFERENCED),
        )
        conn.commit()
        conn.close()
        self.env = dict(os.environ)
        self.env["OPENCODE_SNAPSHOT_DIR"] = str(self.root)
        self.env["OPENCODE_DB"] = str(self.db)

    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=self.env,
        )

    def test_dry_run_lists_but_does_not_delete(self):
        result = self.run_script()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("candidates: 1", result.stdout)
        self.assertIn(UNREFERENCED, result.stdout)
        self.assertNotIn(REFERENCED, result.stdout)
        self.assertTrue((self.root / REFERENCED).exists())
        self.assertTrue((self.root / UNREFERENCED).exists())

    def test_apply_deletes_only_unreferenced(self):
        result = self.run_script("--apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("deleted: 1", result.stdout)
        self.assertTrue((self.root / REFERENCED).exists())
        self.assertFalse((self.root / UNREFERENCED).exists())
        self.assertTrue((self.root / IGNORED).exists())

    def test_missing_root_is_bad_usage(self):
        self.env["OPENCODE_SNAPSHOT_DIR"] = str(Path(self.tmp.name) / "nope")

        result = self.run_script()

        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
