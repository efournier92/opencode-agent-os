#!/usr/bin/env python3
"""Tests for scripts/cost-report.py. Run with:

    python3 -m unittest scripts/test_cost_report.py -v
"""

import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent / "cost-report.py"

_spec = importlib.util.spec_from_file_location("cost_report", SCRIPT)
cost_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cost_report)

SCHEMA = """
CREATE TABLE session (
    id TEXT,
    agent TEXT,
    cost REAL,
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_cache_read INTEGER,
    time_created INTEGER,
    parent_id TEXT,
    time_compacting INTEGER
)
"""


class TestCostReport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "test.db"
        conn = sqlite3.connect(self.db)
        conn.execute(SCHEMA)
        conn.executemany(
            "INSERT INTO session VALUES (?,?,?,?,?,?,?,?,?)",
            [
                ("a", "builder", 1.00, 100, 10, 5, 1000, None, None),
                ("b", "builder", 2.00, 200, 20, 7, 2000, None, None),
                ("c", "verifier", 0.50, 30, 3, 1, 3000, "a", None),
            ],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_per_agent_aggregation(self):
        conn = cost_report.connect(self.db)
        rows = cost_report.aggregate(conn)
        conn.close()
        by_agent = {r[0]: r for r in rows}
        self.assertEqual(len(rows), 2)
        self.assertEqual(by_agent["builder"][1], 2)
        self.assertAlmostEqual(by_agent["builder"][2], 3.00)
        self.assertEqual(by_agent["builder"][3], 300)
        self.assertEqual(by_agent["builder"][4], 30)
        self.assertEqual(by_agent["builder"][5], 12)
        self.assertEqual(rows[0][0], "builder")

    def test_since_filtering(self):
        conn = cost_report.connect(self.db)
        rows = cost_report.aggregate(conn, since_ms=2500)
        conn.close()
        by_agent = {r[0]: r for r in rows}
        self.assertEqual(set(by_agent), {"verifier"})
        self.assertEqual(by_agent["verifier"][1], 1)

    def test_totals(self):
        conn = cost_report.connect(self.db)
        n, cost, subagents, compacted = cost_report.totals(conn)
        conn.close()
        self.assertEqual(n, 3)
        self.assertAlmostEqual(cost, 3.50)
        self.assertEqual(subagents, 1)
        self.assertEqual(compacted, 0)

    def test_sliding_max_drops_points_outside_window(self):
        day = cost_report.WINDOW_MS["5h"]
        points = [(0, 1.0), (1000, 2.0), (day + 5000, 4.0)]
        self.assertAlmostEqual(cost_report.sliding_max(points, day), 4.0)

    def test_window_spend_trailing_sum_for_30d(self):
        points = [(0, 1.0), (1000, 2.0), (10_000_000, 4.0)]
        self.assertAlmostEqual(
            cost_report.window_spend(points, cost_report.WINDOW_MS["30d"]), 7.0
        )

    def test_window_spend_is_sliding_for_5h(self):
        day = cost_report.WINDOW_MS["5h"]
        points = [(0, 1.0), (1000, 2.0), (day + 5000, 4.0)]
        self.assertAlmostEqual(cost_report.window_spend(points, day), 4.0)

    def test_archive_rows_fold_into_windows(self):
        conn = mock.MagicMock()
        conn.execute.return_value = []
        now = 1_700_000_000_000
        archive = [
            {
                "time_created": now,
                "model": "glm-5.3",
                "tokens_input": 10_000_000,
                "tokens_output": 0,
                "tokens_cache_read": 0,
            }
        ]
        spend = cost_report.model_spend(
            conn, now - 1, cost_report.WINDOW_MS["30d"], archive
        )
        self.assertAlmostEqual(spend["glm-5.3"], 14.0)

    def test_archive_rows_older_than_since_ignored(self):
        conn = mock.MagicMock()
        conn.execute.return_value = []
        now = 1_700_000_000_000
        archive = [
            {
                "time_created": now - 1000,
                "model": "glm-5.3",
                "tokens_input": 10_000_000,
            }
        ]
        spend = cost_report.model_spend(
            conn, now, cost_report.WINDOW_MS["30d"], archive
        )
        self.assertAlmostEqual(spend["glm-5.3"], 0.0)


if __name__ == "__main__":
    unittest.main()
