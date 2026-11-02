#!/usr/bin/env python3
"""Tests for scripts/archive-profile.py. Run with:

    python3 -m unittest scripts/test_archive_profile.py -v
"""

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


archive_profile = _load("archive_profile", HERE / "archive-profile.py")
apply_models = _load("apply_models", HERE / "apply-models.py")


class TestArchiveProfile(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "agents" / "roles").mkdir(parents=True)
        shutil.copy(REPO / "models.allowlist", self.root / "models.allowlist")
        for path in (REPO / "agents" / "roles").glob("*.md"):
            shutil.copy(path, self.root / "agents" / "roles" / path.name)
        self.original = self._seed_models()

    def tearDown(self):
        self._tmp.cleanup()

    def _seed_models(self):
        data = yaml.safe_load((REPO / "models.yaml").read_text())
        if "glm" not in data["profiles"]:
            archived = yaml.safe_load(
                (REPO / "configs" / "archive" / "2026-10_glm.yaml").read_text()
            )
            data["profiles"]["glm"] = archived["glm"]
        (self.root / "models.yaml").write_text(yaml.safe_dump(data, sort_keys=False))
        return data

    def test_archive_glm(self):
        out = archive_profile.archive(self.root, "glm", "2026-10")
        self.assertEqual(out, self.root / "configs" / "archive" / "2026-10_glm.yaml")
        self.assertTrue(out.is_file())
        parsed = yaml.safe_load(out.read_text())
        self.assertIn("roles", parsed["glm"])
        profiles, default_profile = apply_models.load_models(self.root / "models.yaml")
        self.assertNotIn("glm", profiles)
        self.assertEqual(default_profile, self.original["default_profile"])

    def test_archived_roles_match(self):
        out = archive_profile.archive(self.root, "glm", "2026-10")
        parsed = yaml.safe_load(out.read_text())
        self.assertEqual(parsed["glm"]["roles"], self.original["profiles"]["glm"]["roles"])

    def test_other_profiles_remain(self):
        archive_profile.archive(self.root, "glm", "2026-10")
        profiles, _ = apply_models.load_models(self.root / "models.yaml")
        for name in self.original["profiles"]:
            if name != "glm":
                self.assertIn(name, profiles)

    def test_refuses_default_profile(self):
        default = self.original["default_profile"]
        with self.assertRaises(SystemExit):
            archive_profile.archive(self.root, default, "2026-10")
        self.assertFalse((self.root / "configs" / "archive").exists())

    def test_refuses_unknown_profile(self):
        with self.assertRaises(SystemExit):
            archive_profile.archive(self.root, "nope", "2026-10")
        self.assertFalse((self.root / "configs" / "archive").exists())

    def test_dry_run_writes_nothing(self):
        before = (self.root / "models.yaml").read_text()
        out = archive_profile.archive(self.root, "glm", "2026-10", dry_run=True)
        self.assertFalse(out.exists())
        self.assertFalse((self.root / "configs" / "archive").exists())
        self.assertEqual((self.root / "models.yaml").read_text(), before)

    def test_snapshot_active_profile(self):
        before = (self.root / "models.yaml").read_text()
        out = archive_profile.snapshot(self.root, "ds", "2026-10")
        self.assertEqual(out, self.root / "configs" / "snapshots" / "2026-10_ds.yaml")
        self.assertTrue(out.is_file())
        parsed = yaml.safe_load(out.read_text())
        self.assertEqual(parsed["ds"]["roles"], self.original["profiles"]["ds"]["roles"])
        profiles, _ = apply_models.load_models(self.root / "models.yaml")
        self.assertIn("ds", profiles)
        self.assertEqual((self.root / "models.yaml").read_text(), before)

    def test_snapshot_dry_run_writes_nothing(self):
        before = (self.root / "models.yaml").read_text()
        out = archive_profile.snapshot(self.root, "ds", "2026-10", dry_run=True)
        self.assertFalse(out.exists())
        self.assertFalse((self.root / "configs" / "snapshots").exists())
        self.assertEqual((self.root / "models.yaml").read_text(), before)

    def test_snapshot_refuses_unknown_profile(self):
        with self.assertRaises(SystemExit):
            archive_profile.snapshot(self.root, "nope", "2026-10")
        self.assertFalse((self.root / "configs" / "snapshots").exists())


if __name__ == "__main__":
    unittest.main()
