#!/usr/bin/env python3
"""Tests for scripts/session_artifacts.py. Run with:

    python3 -m unittest discover -s scripts -p 'test_session_artifacts.py' -v
"""

import json
import os
import sqlite3
import stat
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session_artifacts  # noqa: E402


class SessionArtifactsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "opencode.db"
        self.part_seq = 0
        conn = sqlite3.connect(self.db)
        conn.execute(
            "CREATE TABLE part (id TEXT PRIMARY KEY, session_id TEXT, data TEXT)"
        )
        conn.commit()
        conn.close()

    def add_part(self, session_id, output_path):
        self.part_seq += 1
        conn = sqlite3.connect(self.db)
        conn.execute(
            "INSERT INTO part(id, session_id, data) VALUES (?,?,?)",
            (
                f"prt_{session_id}_{self.part_seq}",
                session_id,
                json.dumps({"state": {"metadata": {"outputPath": str(output_path)}}}),
            ),
        )
        conn.commit()
        conn.close()

    def touch(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("x")
        return path

    def test_paths_include_inside_output_and_session_diff(self):
        inside = self.touch(self.root / "tool-output" / "a.txt")
        diff = self.touch(self.root / "storage" / "session_diff" / "ses_1.json")
        self.add_part("ses_1", inside)
        self.add_part("ses_1", inside)

        paths = session_artifacts.paths_for_session(self.db, "ses_1", self.root)

        self.assertEqual(sorted(paths), sorted([str(inside.resolve()), str(diff.resolve())]))

    def test_paths_exclude_output_outside_root(self):
        outside = self.touch(self.root.parent / "outside-artifact.txt")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        self.add_part("ses_2", outside)

        paths = session_artifacts.paths_for_session(self.db, "ses_2", self.root)

        self.assertEqual(paths, [])

    def test_paths_ignore_missing_diff_and_null_output(self):
        conn = sqlite3.connect(self.db)
        conn.execute(
            "INSERT INTO part(id, session_id, data) VALUES (?,?,?)",
            ("prt_null", "ses_3", json.dumps({"state": {"metadata": {}}})),
        )
        conn.commit()
        conn.close()

        self.assertEqual(session_artifacts.paths_for_session(self.db, "ses_3", self.root), [])

    def test_delete_paths_reports_deleted_and_failed(self):
        present = self.touch(self.root / "a.txt")
        missing = self.root / "missing.txt"

        deleted, failed = session_artifacts.delete_paths([present, missing])

        self.assertEqual(deleted, [str(present)])
        self.assertEqual(failed, [str(missing)])
        self.assertFalse(present.exists())

    def test_harden_db_sets_0600_on_db_and_sidecars(self):
        wal = self.touch(Path(str(self.db) + "-wal"))
        shm = self.touch(Path(str(self.db) + "-shm"))
        for path in (self.db, wal, shm):
            os.chmod(path, 0o644)

        changed = session_artifacts.harden_db(self.db)

        self.assertEqual(len(changed), 3)
        for path in (self.db, wal, shm):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_harden_db_tolerates_missing_sidecars(self):
        os.chmod(self.db, 0o644)

        changed = session_artifacts.harden_db(self.db)

        self.assertEqual(changed, [str(self.db)])
        self.assertEqual(stat.S_IMODE(self.db.stat().st_mode), 0o600)


if __name__ == "__main__":
    unittest.main()
