#!/usr/bin/env python3
"""Tests for scripts/check_usage.py. Run with:

    python3 -m unittest scripts/test_check_usage.py -v
"""

import contextlib
import importlib.util
import io
import os
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import usage_archive  # noqa: E402

SCRIPT = SCRIPTS / "check_usage.py"

_spec = importlib.util.spec_from_file_location("check_usage", SCRIPT)
check_usage = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_usage)

SCHEMA = """
CREATE TABLE session (
    id TEXT,
    agent TEXT,
    model TEXT,
    cost REAL,
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_reasoning INTEGER,
    tokens_cache_read INTEGER,
    time_created INTEGER
)
"""


def model_json(mid):
    return '{"id":"%s","providerID":"opencode-go"}' % mid


class TestCheckUsage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.db"
        self.archive = Path(self.tmp.name) / "archive.jsonl"
        conn = sqlite3.connect(self.db)
        conn.execute(SCHEMA)
        conn.commit()
        conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def add(self, sessions):
        conn = sqlite3.connect(self.db)
        conn.executemany(
            "INSERT INTO session VALUES (?,?,?,?,?,?,?,?,?)",
            [
                (str(i), "referee", model_json(mid), 0, tin, 0, 0, 0, ts)
                for i, (mid, tin, ts) in enumerate(sessions)
            ],
        )
        conn.commit()
        conn.close()

    def run_check(self):
        out = io.StringIO()
        env = {"OPENCODE_DB": str(self.db), "OPENCODE_USAGE_ARCHIVE": str(self.archive)}
        with mock.patch.dict(os.environ, env):
            with contextlib.redirect_stdout(out):
                code = check_usage.main()
        return code, out.getvalue()

    def test_missing_database_skips(self):
        env = {
            "OPENCODE_DB": str(self.db) + ".missing",
            "OPENCODE_USAGE_ARCHIVE": str(self.archive),
        }
        with mock.patch.dict(os.environ, env):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = check_usage.main()
        self.assertEqual(code, 0)
        self.assertIn("usage check skipped", out.getvalue())

    def test_clean(self):
        self.add([("glm-5.3", 1000, int(time.time() * 1000))])
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("usage check clean", out)

    def test_warn_at_75_pct(self):
        now = int(time.time() * 1000)
        # Each session is $1.20; ten spread over 27 days total 80% of $15.
        self.add([("glm-5.3", 857142, now - i * 3 * 86400 * 1000) for i in range(10)])
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("usage check warning", out)
        self.assertIn("usage check clean", out)

    def test_fail_at_90_pct(self):
        self.add([("glm-5.3", 10_000_000, int(time.time() * 1000))])
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("usage check FAILED", out)

    def test_warn_at_weekly_75_pct(self):
        now = int(time.time() * 1000)
        # Three $2 sessions one day apart: $6 is 80% of the $7.50 weekly cap.
        self.add([("glm-5.3", 1_428_571, now - i * 86400 * 1000) for i in range(3)])
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("usage check warning", out)
        self.assertIn("worst 7d", out)

    def test_fail_at_weekly_90_pct(self):
        now = int(time.time() * 1000)
        self.add([("glm-5.3", 1_428_571, now - i * 86400 * 1000) for i in range(4)])
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("usage check FAILED", out)

    def test_archive_rows_merged(self):
        now = int(time.time() * 1000)
        usage_archive.append_rows(
            [
                {
                    "time_created": now,
                    "time_updated": now,
                    "model": "glm-5.3",
                    "tokens_input": 10_000_000,
                    "tokens_output": 0,
                    "tokens_cache_read": 0,
                }
            ],
            path=self.archive,
        )
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("usage check FAILED", out)

    def test_archive_rows_older_than_cutoff_ignored(self):
        old = int(time.time() * 1000) - 40 * 86400 * 1000
        usage_archive.append_rows(
            [
                {
                    "time_created": old,
                    "time_updated": old,
                    "model": "glm-5.3",
                    "tokens_input": 10_000_000,
                }
            ],
            path=self.archive,
        )
        code, out = self.run_check()
        self.assertEqual(code, 0)
        self.assertIn("usage check clean", out)


if __name__ == "__main__":
    unittest.main()
