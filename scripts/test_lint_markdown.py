#!/usr/bin/env python3
"""Tests for scripts/lint-markdown.py semicolon rule. Run with:

    python3 -m unittest scripts.test_lint_markdown -v
"""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent / "lint-markdown.py"

_spec = importlib.util.spec_from_file_location("lint_markdown", SCRIPT)
lint_markdown = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lint_markdown)


def run(root, target):
    with mock.patch.object(lint_markdown, "REPO", root), \
            mock.patch.object(lint_markdown, "BASELINE", root / "baseline.txt"):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = lint_markdown.main([str(target)])
        return code, out.getvalue()


class SemicolonTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        path = self.root / name
        path.write_text(text)
        return path

    def test_prose_semicolon_flagged(self):
        path = self.write("a.md", "Hello; world.\n")
        code, out = run(self.root, path)
        self.assertEqual(code, 1)
        self.assertIn("semicolon in prose, use a period", out)

    def test_code_and_fence_exempt(self):
        path = self.write("a.md", "Use `a; b` here.\n\n```\nx; y\n```\n")
        code, out = run(self.root, path)
        self.assertEqual(code, 0, out)

    def test_under_allowance_passes(self):
        path = self.write("a.md", "One; two.\n")
        (self.root / "baseline.txt").write_text("2\ta.md\n")
        code, out = run(self.root, path)
        self.assertEqual(code, 0, out)

    def test_over_allowance_fails(self):
        path = self.write("a.md", "One; two; three.\n")
        (self.root / "baseline.txt").write_text("1\ta.md\n")
        code, out = run(self.root, path)
        self.assertEqual(code, 1)
        self.assertIn("semicolon in prose", out)

    def test_absent_from_baseline_fails(self):
        path = self.write("a.md", "One; two.\n")
        code, out = run(self.root, path)
        self.assertEqual(code, 1)
        self.assertIn("semicolon in prose", out)


if __name__ == "__main__":
    unittest.main()
