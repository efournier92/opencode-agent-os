#!/usr/bin/env python3
"""Tests for scripts/check_discovery.py. Run with:

    python3 -m unittest scripts/test_check_discovery.py -v
"""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_discovery as cd

VALID = "- 2026-10-04 | [find] | plugin | a finding | foo.md:1\n"


def run_quiet(argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return cd.main(argv)


class TestCheckDiscovery(unittest.TestCase):
    def setUp(self):
        self._repo = cd.REPO
        self.tmp = tempfile.TemporaryDirectory()
        cd.REPO = Path(self.tmp.name)

    def tearDown(self):
        cd.REPO = self._repo
        self.tmp.cleanup()

    def write(self, name, text):
        path = cd.REPO / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self, name):
        return run_quiet([str(cd.REPO / name)])

    def test_valid_file_passes(self):
        self.write("foo.md", "line one\n")
        self.write("DISCOVERY.md", VALID)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_missing_evidence_path_flagged(self):
        self.write("DISCOVERY.md", VALID.replace("foo.md", "gone.md"))
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_line_out_of_range_flagged(self):
        self.write("foo.md", "line one\n")
        self.write("DISCOVERY.md", VALID.replace("foo.md:1", "foo.md:99"))
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_long_entry_flagged(self):
        self.write("foo.md", "line one\n")
        long_line = "- 2026-10-04 | [find] | plugin | " + "x" * 250 + " | foo.md:1\n"
        self.write("DISCOVERY.md", long_line)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_oversized_file_flagged(self):
        self.write("DISCOVERY.md", "prose\n" * 1400)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_url_and_command_tokens_ignored(self):
        self.write("foo.md", "line one\n")
        entry = "- 2026-10-04 | [find] | plugin | a finding | https://example.com bash python3 foo.md:1\n"
        self.write("DISCOVERY.md", entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_glob_token_ignored(self):
        entry = "- 2026-10-04 | [find] | plugin | a finding | scripts/test_*.py:1\n"
        self.write("DISCOVERY.md", entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_evidence_resolves_against_target_repo_root(self):
        (cd.REPO / ".git").mkdir()
        self.write("foo.md", "line one\n")
        self.write("nested/DISCOVERY.md", VALID)
        self.assertEqual(run_quiet([str(cd.REPO / "nested" / "DISCOVERY.md")]), 0)

    def test_missing_evidence_in_target_repo_flagged(self):
        (cd.REPO / ".git").mkdir()
        self.write("nested/DISCOVERY.md", VALID.replace("foo.md", "gone.md"))
        self.assertEqual(run_quiet([str(cd.REPO / "nested" / "DISCOVERY.md")]), 1)

    def test_default_target_resolved_from_repo(self):
        (cd.REPO / ".git").mkdir()
        self.write("foo.md", "line one\n")
        self.write(cd.DEFAULT, VALID)
        self.assertEqual(run_quiet([]), 0)

    def test_missing_cli_path_flagged(self):
        self.assertEqual(run_quiet([str(cd.REPO / "nope.md")]), 1)


if __name__ == "__main__":
    unittest.main()
