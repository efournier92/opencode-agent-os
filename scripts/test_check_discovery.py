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

HEADER = "Scope tokens: plugin\n\n"
VALID = HEADER + "- D-20261004-01 | 2026-10-04 | [find] | plugin | a finding | foo.md:1\n"


def run_quiet(argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return cd.main(argv)


def run_output(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cd.main(argv)
    return code, out.getvalue()


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

    def run_output_check(self, name):
        return run_output([str(cd.REPO / name)])

    def test_valid_file_passes(self):
        self.write("foo.md", "line one\n")
        self.write("DISCOVERY.md", VALID)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_missing_id_flagged(self):
        self.write("DISCOVERY.md", HEADER + "- 2026-10-04 | [find] | plugin | a finding | foo.md:1\n")
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_duplicate_id_flagged(self):
        entry = "- D-20261004-01 | 2026-10-04 | [find] | plugin | a finding | foo.md:1\n"
        self.write("foo.md", "line one\n")
        self.write("DISCOVERY.md", HEADER + entry + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_id_date_mismatch_flagged(self):
        entry = "- D-20261004-01 | 2026-10-05 | [find] | plugin | a finding | foo.md:1\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_malformed_id_flagged(self):
        entry = "- D-2026-10-04-1 | 2026-10-04 | [find] | plugin | a finding | foo.md:1\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_self_citation_only_flagged(self):
        self.write("docs/discovery/ARCHIVE.md", "detail\n")
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding | docs/discovery/ARCHIVE.md\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_finding_backticks_are_not_command_evidence(self):
        self.write("docs/discovery/ARCHIVE.md", "detail\n")
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding mentioning `x` | docs/discovery/ARCHIVE.md\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_self_citation_with_external_passes(self):
        self.write("docs/discovery/archive/D-20261009-01.md", "# D-20261009-01\n\noriginal entry\n")
        entry = "- D-20261009-01 | 2026-10-09 | [trap] | plugin | a trap | docs/discovery/archive/D-20261009-01.md src/a.rb:3\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_url_is_external_evidence(self):
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding | https://example.com\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_backtick_command_is_external_evidence(self):
        entry = "- D-20261009-01 | 2026-10-09 | [decision] | plugin | a decision | `gh release list`\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_assumption_without_external_evidence_passes(self):
        entry = "- D-20261009-01 | 2026-10-09 | [assumption] | plugin | an assumption | a test would settle it\n"
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_scope_undeclared_flagged(self):
        entry = "- {id} | 2026-10-09 | [find] | {scope} | a finding | foo.md:1\n"
        self.write("foo.md", "line one\n")
        text = HEADER + entry.format(id="D-20261009-01", scope="plugin")
        text += entry.format(id="D-20261009-02", scope="plugin/new")
        self.write("DISCOVERY.md", text)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_header_extra_scope_flagged(self):
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding | foo.md:1\n"
        self.write("foo.md", "line one\n")
        self.write("DISCOVERY.md", "Scope tokens: plugin, plugin/gone\n\n" + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_archive_header_mismatch_flagged(self):
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding | foo.md:1\n"
        self.write("foo.md", "line one\n")
        self.write("archive/D-20261009-01.md", "# D-20261009-02\n\noriginal entry\n")
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_archive_oversize_allowed(self):
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding | foo.md:1\n"
        self.write("foo.md", "line one\n")
        self.write("archive/D-20261009-01.md", "# D-20261009-01\n\n" + "x" * 12000 + "\n")
        self.write("DISCOVERY.md", HEADER + entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_orphan_archive_warns(self):
        entry = "- D-20261009-01 | 2026-10-09 | [find] | plugin | a finding | foo.md:1\n"
        self.write("foo.md", "line one\n")
        self.write("archive/D-20261009-99.md", "# D-20261009-99\n\noriginal entry\n")
        self.write("DISCOVERY.md", HEADER + entry)
        code, output = self.run_output_check("DISCOVERY.md")
        self.assertEqual(code, 0)
        self.assertIn("orphan archive", output)

    def test_missing_evidence_path_flagged(self):
        self.write("DISCOVERY.md", VALID.replace("foo.md", "gone.md"))
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_line_out_of_range_flagged(self):
        self.write("foo.md", "line one\n")
        self.write("DISCOVERY.md", VALID.replace("foo.md:1", "foo.md:99"))
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_long_entry_flagged(self):
        self.write("foo.md", "line one\n")
        long_line = HEADER + "- D-20261004-01 | 2026-10-04 | [find] | plugin | " + "x" * 250 + " | foo.md:1\n"
        self.write("DISCOVERY.md", long_line)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_oversized_file_flagged(self):
        self.write("DISCOVERY.md", "prose\n" * 1400)
        self.assertEqual(self.run_check("DISCOVERY.md"), 1)

    def test_url_and_command_tokens_are_external_evidence(self):
        self.write("foo.md", "line one\n")
        entry = HEADER + "- D-20261004-01 | 2026-10-04 | [find] | plugin | a finding | https://example.com bash python3 foo.md:1\n"
        self.write("DISCOVERY.md", entry)
        self.assertEqual(self.run_check("DISCOVERY.md"), 0)

    def test_glob_token_ignored(self):
        self.write("foo.md", "line one\n")
        entry = HEADER + "- D-20261004-01 | 2026-10-04 | [find] | plugin | a finding | foo.md:1 scripts/test_*.py:1\n"
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
