#!/usr/bin/env python3
"""Tests for scripts/install.sh. Run with:

    python3 -m unittest scripts/test_install.py
"""

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "scripts" / "install.sh"


def expected_agent_count():
    data = yaml.safe_load((REPO / "models.yaml").read_text())
    return sum(len(profile["roles"]) for profile in data["profiles"].values())


def run_install(cfg):
    env = dict(os.environ, OPENCODE_CONFIG_DIR=str(cfg))
    return subprocess.run(
        ["bash", str(INSTALL)], env=env, capture_output=True, text=True
    )


class TestInstall(unittest.TestCase):
    def test_fresh_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_install(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                len(list((root / "agents").glob("*.md"))), expected_agent_count()
            )
            self.assertEqual(len(list((root / "skills").glob("*/SKILL.md"))), 12)
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertTrue((root / "opencode.jsonc").is_file())
            self.assertIn("default_profile", (root / "models.yaml").read_text())
            keybinds = json.loads((root / "tui.json").read_text())["keybinds"]
            self.assertEqual(keybinds["agent_cycle"], "shift+tab")
            self.assertEqual(keybinds["agent_cycle_reverse"], "none")

    def test_reinstall_preserves(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tui.json").write_text(
                json.dumps(
                    {"keybinds": {"app_exit": "ctrl+q", "agent_cycle": "ctrl+g"}}
                )
            )
            (root / "opencode.jsonc").write_text('{"model": "custom/x"}')
            (root / "models.yaml").write_text("# custom\n")

            result = run_install(root)
            self.assertEqual(result.returncode, 0, result.stderr)

            keybinds = json.loads((root / "tui.json").read_text())["keybinds"]
            self.assertEqual(keybinds["app_exit"], "ctrl+q")
            self.assertEqual(keybinds["agent_cycle"], "ctrl+g")
            self.assertEqual(keybinds["agent_cycle_reverse"], "none")
            self.assertIn("custom/x", (root / "opencode.jsonc").read_text())
            self.assertIn("# custom", (root / "models.yaml").read_text())
            self.assertTrue(list(root.glob("backup-*")), "no backup dir written")

    def test_refuses_root(self):
        env = dict(os.environ, OPENCODE_CONFIG_DIR="/")
        result = subprocess.run(
            ["bash", str(INSTALL)], env=env, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
