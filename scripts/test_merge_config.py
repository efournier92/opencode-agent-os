#!/usr/bin/env python3
"""Tests for scripts/merge-config.py. Run with:

    python3 -m unittest scripts/test_merge_config.py -v
"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve().parent / "merge-config.py"
SAMPLE = REPO / "opencode.json.sample"

_spec = importlib.util.spec_from_file_location("merge_config", SCRIPT)
merge_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge_config)


def run_merge(existing_text, sample_path=SAMPLE):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "opencode.json"
        path.write_text(existing_text)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = merge_config.main(
                ["merge-config.py", str(path), str(sample_path)]
            )
        return code, path.read_text(), out.getvalue(), err.getvalue()


class TestMergeConfig(unittest.TestCase):
    def test_overrides_managed_preserves_rest(self):
        existing = {
            "provider": {"foo": {"models": {"bar": {}}}},
            "permission": {"edit": "deny"},
            "agent": {"custom": {"disable": True}},
            "default_agent": "stale",
        }
        code, text, out, _ = run_merge(json.dumps(existing))
        self.assertEqual(code, 0)
        cfg = json.loads(text)
        sample = json.loads(SAMPLE.read_text())

        self.assertEqual(cfg["provider"], existing["provider"])
        self.assertEqual(cfg["permission"]["edit"], "deny")
        self.assertEqual(
            cfg["permission"]["external_directory"], {"/tmp/*": "allow"}
        )
        self.assertEqual(cfg["agent"]["custom"], {"disable": True})
        self.assertEqual(cfg["default_agent"], sample["default_agent"])
        self.assertEqual(cfg["subagent_depth"], sample["subagent_depth"])
        self.assertEqual(cfg["compaction"]["prune"], sample["compaction"]["prune"])
        self.assertEqual(cfg["agent"]["build"], sample["agent"]["build"])
        self.assertEqual(cfg["agent"]["scout"], sample["agent"]["scout"])
        self.assertIn("set default_agent:", out)
        self.assertIn("wrote ", out)

    def test_nested_sibling_preserved(self):
        existing = {"compaction": {"reserved": 20000}}
        code, text, _, _ = run_merge(json.dumps(existing))
        self.assertEqual(code, 0)
        cfg = json.loads(text)
        self.assertEqual(cfg["compaction"]["reserved"], 20000)
        self.assertTrue(cfg["compaction"]["prune"])

    def test_noop_leaves_bytes_identical(self):
        sample = json.loads(SAMPLE.read_text())
        existing = {
            "provider": {"keep": 1},
            "default_agent": sample["default_agent"],
            "subagent_depth": sample["subagent_depth"],
            "compaction": {"prune": sample["compaction"]["prune"]},
            "agent": {
                "build": {"disable": sample["agent"]["build"]["disable"]},
                "scout": {"disable": sample["agent"]["scout"]["disable"]},
            },
            "permission": {
                "external_directory": sample["permission"]["external_directory"]
            },
        }
        original = json.dumps(existing, indent=4)
        code, text, out, _ = run_merge(original)
        self.assertEqual(code, 0)
        self.assertEqual(text, original)
        self.assertIn("no changes", out)

    def test_unparseable_existing_exits_3_no_write(self):
        original = "// jsonc comment\n{}\n"
        code, text, _, err = run_merge(original)
        self.assertEqual(code, 3)
        self.assertEqual(text, original)
        self.assertIn("warning:", err)

    def test_sample_guard(self):
        config = json.loads(SAMPLE.read_text())
        self.assertTrue(config["compaction"]["prune"])
        self.assertEqual(config["subagent_depth"], 2)


if __name__ == "__main__":
    unittest.main()
