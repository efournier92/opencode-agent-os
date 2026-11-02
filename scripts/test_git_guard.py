#!/usr/bin/env python3
"""Tests for plugins/git-guard.js. Run with:

    python3 -m unittest scripts/test_git_guard.py
"""

import json
import shutil
import subprocess
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "plugins" / "git-guard.js"
NODE = shutil.which("node")

BLOCKED = [
    "git reset --hard",
    "git clean -fd",
    "git checkout -- file",
    "git restore file",
    "git stash clear",
    "git stash drop",
    "git stash pop",
    "git commit --amend",
    "git commit -a -m x",
    "git add -A",
    "git push --force origin main",
    "git push --force-with-lease origin main",
    "git push origin +main",
    "git push --mirror origin",
    "git push -f origin main",
    "git checkout .",
    "gh pr merge 1 --admin",
    "git commit -m x --no-verify",
    "cd x && git reset --hard",
    "git add -A; git commit -m x",
    "bash -c 'git reset --hard'",
    "git -C . reset --hard",
    "/usr/bin/git reset --hard",
    'git reset "--hard"',
]
ALLOWED = [
    "git status --short",
    "git checkout -b feat",
    "git checkout main",
    "git restore --staged file",
    "git reset --soft HEAD~1",
    "git push origin main",
    "OPENCODE_GIT_GUARD=0 git reset --hard",
    "git reset --hard # git-guard: allow",
]


def run_node(commands):
    script = (
        "import { classify } from %r;\n"
        "const cmds = JSON.parse(process.argv[1]);\n"
        "console.log(JSON.stringify(cmds.map((c) => classify(c))));"
    ) % SRC.as_uri()
    out = subprocess.run(
        [NODE, "--input-type=module", "-e", script, json.dumps(commands)],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(out.stdout)


@unittest.skipUnless(NODE, "node not installed")
class TestGitGuard(unittest.TestCase):
    def test_verdicts(self):
        verdicts = run_node(BLOCKED + ALLOWED)
        for command, verdict in zip(BLOCKED, verdicts):
            self.assertIsNotNone(verdict, command)
            self.assertTrue(verdict["message"].startswith(verdict["rule"]), command)
        for command, verdict in zip(ALLOWED, verdicts[len(BLOCKED):]):
            self.assertIsNone(verdict, command)


if __name__ == "__main__":
    unittest.main()
