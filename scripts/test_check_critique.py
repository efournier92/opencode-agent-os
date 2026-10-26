#!/usr/bin/env python3
"""Tests for scripts/check_critique.py. Run with:

    python3 -m unittest scripts/test_check_critique.py -v
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_critique as cc

HEADER = (
    "# Critique Ledger: Toy\n\n"
    "- Goal: toy goal\n"
    "- Started: 2026-10-10\n"
    "- Branch: none\n\n"
    "## Findings\n\n"
)


def finding(cid, date, lens, sev, conf, status, text, ev="foo.md:1"):
    return f"- {cid} | {date} | {lens} | {sev} | {conf} | {status} | {text} | {ev}\n"


VALID = HEADER + (
    finding("C-20261010-01", "2026-10-10", "security", "high", "high", "open", "a finding")
    + finding("C-20261010-02", "2026-10-10", "scale", "medium", "low", "addressed", "another")
    + finding("C-20261010-03", "2026-10-10", "cost", "low", "medium", "rejected", "third")
    + finding("C-20261010-04", "2026-10-10", "reliability", "high", "low", "escalated", "fourth")
    + finding("C-20261010-05", "2026-10-10", "testing", "medium", "high", "open", "fifth")
    + "  - rebuttal | addressed | foo.md:1 | fixed\n"
)


def run_quiet(argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return cc.main(argv)


class TestCheckCritique(unittest.TestCase):
    def setUp(self):
        self._repo = cc.REPO
        self.tmp = tempfile.TemporaryDirectory()
        cc.REPO = Path(self.tmp.name)
        (cc.REPO / ".git").mkdir()

    def tearDown(self):
        cc.REPO = self._repo
        self.tmp.cleanup()

    def write(self, name, text):
        path = cc.REPO / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_happy_path_passes(self):
        self.write("foo.md", "line one\n")
        self.write("critique/LEDGER.md", VALID)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 0)

    def test_malformed_id_flagged(self):
        self.write("foo.md", "line one\n")
        text = HEADER + finding("C-2026-1", "2026-10-10", "security", "high", "high", "open", "x")
        self.write("critique/LEDGER.md", text)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_id_date_mismatch_flagged(self):
        self.write("foo.md", "line one\n")
        text = HEADER + finding("C-20261010-01", "2026-10-11", "security", "high", "high", "open", "x")
        self.write("critique/LEDGER.md", text)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_unknown_enum_values_flagged(self):
        self.write("foo.md", "line one\n")
        cases = [
            finding("C-20261010-01", "2026-10-10", "security", "critical", "high", "open", "x"),
            finding("C-20261010-02", "2026-10-10", "security", "high", "certain", "open", "x"),
            finding("C-20261010-03", "2026-10-10", "security", "high", "high", "fixed", "x"),
            finding("C-20261010-04", "2026-10-10", "vibes", "high", "high", "open", "x"),
        ]
        for i, line in enumerate(cases):
            self.write(f"critique/LEDGER{i}.md", HEADER + line)
            self.assertEqual(run_quiet([str(cc.REPO / "critique" / f"LEDGER{i}.md")]), 1)

    def test_dead_evidence_path_flagged(self):
        self.write("foo.md", "line one\n")
        text = HEADER + finding("C-20261010-01", "2026-10-10", "security", "high", "high", "open", "x", "gone.md:1")
        self.write("critique/LEDGER.md", text)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_evidence_line_out_of_range_flagged(self):
        self.write("foo.md", "line one\n")
        text = HEADER + finding("C-20261010-01", "2026-10-10", "security", "high", "high", "open", "x", "foo.md:99")
        self.write("critique/LEDGER.md", text)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_command_and_url_evidence_pass(self):
        text = HEADER + (
            finding("C-20261010-01", "2026-10-10", "security", "high", "high", "open", "x", "`pytest -q`")
            + finding("C-20261010-02", "2026-10-10", "scale", "low", "low", "open", "y", "https://example.com")
        )
        self.write("critique/LEDGER.md", text)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 0)

    def test_long_line_flagged(self):
        self.write("foo.md", "line one\n")
        text = HEADER + finding("C-20261010-01", "2026-10-10", "security", "high", "high", "open", "x" * 250)
        self.write("critique/LEDGER.md", text)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_oversized_file_flagged(self):
        self.write("critique/LEDGER.md", "prose\n" * 3000)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_duplicate_ids_flagged(self):
        self.write("foo.md", "line one\n")
        line = finding("C-20261010-01", "2026-10-10", "security", "high", "high", "open", "x")
        self.write("critique/LEDGER.md", HEADER + line + line)
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 1)

    def test_no_findings_file_passes(self):
        self.write("critique/LEDGER.md", "# Critique Ledger: Empty\n\nSome prose with no findings.\n")
        self.assertEqual(run_quiet([str(cc.REPO / "critique")]), 0)

    def test_missing_cli_path_flagged(self):
        self.assertEqual(run_quiet([str(cc.REPO / "nope")]), 1)

    def test_missing_default_dir_passes(self):
        self.assertEqual(run_quiet([]), 0)


if __name__ == "__main__":
    unittest.main()
