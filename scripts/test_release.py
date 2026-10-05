#!/usr/bin/env python3
"""Tests for scripts/release.sh. Run with:

    python3 -m unittest scripts/test_release.py

Builds a throwaway work repo and bare remote, so nothing touches the real one.
"""

import datetime
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "release.sh"
TAG = datetime.date.today().isoformat()


GIT_ENV_KEYS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
    "GIT_PREFIX",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)


def clean_env(**extra):
    # A pre-commit hook exports these; leaking them into the throwaway repo
    # would stage test files into the real index.
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_KEYS}
    env.update(extra)
    return env


def git(args, cwd):
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        capture_output=True,
        text=True,
        check=True,
        env=clean_env(),
    ).stdout.strip()


class TestRelease(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.origin = base / "origin.git"
        self.work = base / "work"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True, env=clean_env())
        subprocess.run(["git", "init", "-q", str(self.work)], check=True, env=clean_env())
        git(["config", "user.email", "t@example.com"], self.work)
        git(["config", "user.name", "t"], self.work)
        (self.work / "f.txt").write_text("1\n")
        git(["add", "."], self.work)
        git(["commit", "-qm", "one"], self.work)
        git(["branch", "-M", "main"], self.work)
        git(["remote", "add", "origin", str(self.origin)], self.work)
        self.env = clean_env(RELEASE_REPO=str(self.work))

    def tearDown(self):
        self.tmp.cleanup()

    def release(self):
        subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=self.work,
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )

    def head(self):
        return git(["rev-parse", "HEAD"], self.work)

    def tag_target(self, cwd):
        result = subprocess.run(
            ["git", "-C", str(cwd), "rev-parse", f"refs/tags/{TAG}^{{}}"],
            capture_output=True,
            text=True,
            env=clean_env(),
        )
        return result.stdout.strip() if result.returncode == 0 else None

    def test_tags_head(self):
        self.release()
        self.assertEqual(self.tag_target(self.work), self.head())
        self.assertEqual(self.tag_target(self.origin), self.head())

    def test_same_day_moves_tag(self):
        self.release()
        first = self.head()
        (self.work / "f.txt").write_text("2\n")
        git(["commit", "-qam", "two"], self.work)
        self.release()
        self.assertNotEqual(first, self.head())
        self.assertEqual(self.tag_target(self.work), self.head())
        self.assertEqual(self.tag_target(self.origin), self.head())


if __name__ == "__main__":
    unittest.main()
