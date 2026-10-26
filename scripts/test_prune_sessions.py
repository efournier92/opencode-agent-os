#!/usr/bin/env python3
"""Tests for skills/prune-sessions/scripts/prune_sessions.py. Run with:

    python3 -m unittest scripts/test_prune_sessions.py -v

Every test builds a throwaway SQLite DB with the same tables and cascades
as the live OpenCode store, then drives the script against it.
"""

import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "skills" / "prune-sessions" / "scripts" / "prune_sessions.py"

SCHEMA = """
CREATE TABLE session (
    id TEXT PRIMARY KEY,
    parent_id TEXT,
    slug TEXT,
    directory TEXT,
    title TEXT,
    share_url TEXT,
    time_created INTEGER NOT NULL,
    time_updated INTEGER NOT NULL
);
CREATE TABLE message (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    time_created INTEGER,
    time_updated INTEGER,
    data TEXT
);
CREATE TABLE part (
    id TEXT PRIMARY KEY,
    message_id TEXT NOT NULL REFERENCES message(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    data TEXT
);
CREATE TABLE todo (
    session_id TEXT NOT NULL REFERENCES session(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    status TEXT NOT NULL,
    priority TEXT NOT NULL,
    position INTEGER NOT NULL,
    time_created INTEGER,
    time_updated INTEGER
);
CREATE TABLE session_share (
    session_id TEXT PRIMARY KEY REFERENCES session(id) ON DELETE CASCADE,
    id TEXT,
    url TEXT NOT NULL,
    secret TEXT
);
CREATE TABLE event (
    id TEXT PRIMARY KEY,
    aggregate_id TEXT NOT NULL,
    seq INTEGER,
    data TEXT
);
CREATE TABLE event_sequence (
    aggregate_id TEXT NOT NULL,
    seq INTEGER NOT NULL,
    owner_id TEXT,
    PRIMARY KEY (aggregate_id, seq)
);
"""


def ago(days):
    return int(time.time() * 1000) - days * 86400 * 1000


class PruneTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "opencode.db"
        self.calls = self.root / "calls.log"
        bindir = self.root / "bin"
        bindir.mkdir()
        fake = bindir / "opencode"
        fake.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sqlite3, sys\n"
            "with open(os.environ['FAKE_LOG'], 'a') as log:\n"
            "    log.write(' '.join(sys.argv[1:]) + '\\n')\n"
            "if os.environ.get('FAKE_FAIL') == '1':\n"
            "    sys.exit(1)\n"
            "if sys.argv[1:3] == ['session', 'delete']:\n"
            "    import time\n"
            "    conn = sqlite3.connect(os.environ['FAKE_DB'])\n"
            "    conn.execute('PRAGMA foreign_keys=ON')\n"
            "    conn.execute('DELETE FROM session WHERE id = ?', (sys.argv[3],))\n"
            "    if os.environ.get('FAKE_BUMP'):\n"
            "        conn.execute('UPDATE session SET time_updated = ? WHERE id = ?',\n"
            "                     (int(time.time() * 1000), os.environ['FAKE_BUMP']))\n"
            "    conn.commit()\n"
            "    conn.close()\n"
        )
        fake.chmod(0o755)
        self.env = dict(os.environ)
        self.env.pop("OPENCODE_DISABLE_SHARE", None)
        self.env["PATH"] = str(bindir) + os.pathsep + os.environ["PATH"]
        self.env["FAKE_LOG"] = str(self.calls)
        self.env["FAKE_DB"] = str(self.db)
        conn = sqlite3.connect(self.db)
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    def add_session(
        self, sid, age_days, parent=None, share_url=None, share_row=False
    ):
        ts = ago(age_days)
        conn = sqlite3.connect(self.db)
        conn.execute(
            "INSERT INTO session"
            "(id, parent_id, slug, directory, title, share_url,"
            " time_created, time_updated) VALUES (?,?,?,?,?,?,?,?)",
            (sid, parent, sid, "/tmp", sid, share_url, ts - 1000, ts),
        )
        conn.execute(
            "INSERT INTO message(id, session_id, time_created, time_updated, data)"
            " VALUES (?,?,?,?,?)",
            ("msg_" + sid, sid, ts, ts, "{}"),
        )
        conn.execute(
            "INSERT INTO part(id, message_id, session_id, data) VALUES (?,?,?,?)",
            ("prt_" + sid, "msg_" + sid, sid, "{}"),
        )
        conn.execute(
            "INSERT INTO todo"
            "(session_id, content, status, priority, position, time_created,"
            " time_updated) VALUES (?,?,?,?,?,?,?)",
            (sid, "task", "pending", "high", 1, ts, ts),
        )
        conn.execute(
            "INSERT INTO event(id, aggregate_id, seq, data) VALUES (?,?,?,?)",
            ("evt_" + sid, sid, 1, "{}"),
        )
        conn.execute(
            "INSERT INTO event_sequence(aggregate_id, seq, owner_id) VALUES (?,?,?)",
            (sid, 1, "owner"),
        )
        if share_url or share_row:
            conn.execute(
                "INSERT INTO session_share(session_id, id, url, secret)"
                " VALUES (?,?,?,?)",
                (sid, "shr_" + sid, share_url or "https://example.test/s", "secret"),
            )
        conn.commit()
        conn.close()

    def run_script(self, *args, env=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--db", str(self.db), *args],
            capture_output=True,
            text=True,
            env=env or self.env,
        )

    def count(self, table, column, sid):
        conn = sqlite3.connect(self.db)
        try:
            return conn.execute(
                f"SELECT COUNT(*) FROM {table} WHERE {column} = ?", (sid,)
            ).fetchone()[0]
        finally:
            conn.close()

    def test_old_family_deleted(self):
        self.add_session("ses_old", 10)
        self.add_session("ses_child", 9, parent="ses_old", share_row=True)
        self.add_session("ses_recent", 0)

        result = self.run_script("--apply", "--no-vacuum")

        self.assertEqual(result.returncode, 0, result.stderr)
        for sid in ("ses_old", "ses_child"):
            for table, column in (
                ("session", "id"),
                ("message", "session_id"),
                ("part", "session_id"),
                ("todo", "session_id"),
                ("session_share", "session_id"),
                ("event", "aggregate_id"),
                ("event_sequence", "aggregate_id"),
            ):
                self.assertEqual(self.count(table, column, sid), 0, (table, sid))
        self.assertEqual(self.count("session", "id", "ses_recent"), 1)
        self.assertEqual(self.count("message", "session_id", "ses_recent"), 1)
        self.assertIn("deleted: 2 sessions", result.stdout)

    def test_recent_child_protects_family(self):
        self.add_session("ses_old", 10)
        self.add_session("ses_child", 0, parent="ses_old")

        result = self.run_script("--apply", "--no-vacuum")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.count("session", "id", "ses_old"), 1)
        self.assertEqual(self.count("session", "id", "ses_child"), 1)

    def test_dry_run_deletes_nothing(self):
        self.add_session("ses_old", 10)
        self.add_session("ses_recent", 0)

        result = self.run_script("--no-vacuum")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("dry run", result.stdout)
        self.assertEqual(self.count("session", "id", "ses_old"), 1)
        self.assertEqual(self.count("message", "session_id", "ses_old"), 1)

    def test_nothing_to_delete_skips_vacuum(self):
        self.add_session("ses_recent", 0)

        result = self.run_script("--apply")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("nothing to delete", result.stdout)
        self.assertNotIn("vacuum:", result.stdout)

    def test_days_override_keeps_ten_day_session(self):
        self.add_session("ses_ten", 10)
        self.add_session("ses_forty", 40)
        self.add_session("ses_recent", 0)

        result = self.run_script("--days", "30", "--apply", "--no-vacuum")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.count("session", "id", "ses_ten"), 1)
        self.assertEqual(self.count("session", "id", "ses_forty"), 0)

    def test_days_zero_rejected_without_write(self):
        self.add_session("ses_old", 10)
        self.add_session("ses_recent", 0)

        result = self.run_script("--days", "0", "--apply")

        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("--days", result.stderr)
        self.assertEqual(self.count("session", "id", "ses_old"), 1)

    def test_newest_session_survives_clock_skew(self):
        self.add_session("ses_old", 10)
        self.add_session("ses_newest", 9, parent="ses_old")

        result = self.run_script("--apply", "--no-vacuum")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.count("session", "id", "ses_newest"), 1)
        self.assertEqual(self.count("session", "id", "ses_old"), 0)

    def test_shared_expired_session_revokes_then_deletes(self):
        self.add_session("ses_shared", 10, share_row=True)
        self.add_session("ses_recent", 0)

        result = self.run_script("--apply", "--no-vacuum")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("session delete ses_shared", self.calls.read_text())
        self.assertEqual(self.count("session", "id", "ses_shared"), 0)
        self.assertEqual(self.count("session_share", "session_id", "ses_shared"), 0)

    def test_resume_during_share_phase_survives(self):
        self.add_session("ses_shared", 10, share_row=True)
        self.add_session("ses_resumed", 10)
        self.add_session("ses_recent", 0)
        env = dict(self.env, FAKE_BUMP="ses_resumed")

        result = self.run_script("--apply", "--no-vacuum", env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.count("session", "id", "ses_shared"), 0)
        self.assertEqual(self.count("session", "id", "ses_resumed"), 1)
        self.assertIn("deleted: 1 sessions", result.stdout)

    def test_disable_share_skips_shared_session(self):
        self.add_session("ses_shared", 10, share_row=True)
        self.add_session("ses_recent", 0)
        env = dict(self.env, OPENCODE_DISABLE_SHARE="1")

        result = self.run_script("--apply", "--no-vacuum", env=env)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.count("session", "id", "ses_shared"), 1)
        self.assertIn("OPENCODE_DISABLE_SHARE", result.stderr)
        self.assertFalse(self.calls.exists())

    def test_share_revoke_failure_aborts(self):
        self.add_session("ses_shared", 10, share_row=True)
        self.add_session("ses_old", 10)
        self.add_session("ses_recent", 0)
        env = dict(self.env, FAKE_FAIL="1")

        result = self.run_script("--apply", "--no-vacuum", env=env)

        self.assertEqual(result.returncode, 1)
        self.assertIn("aborted before local deletion", result.stderr)
        self.assertEqual(self.count("session", "id", "ses_shared"), 1)
        self.assertEqual(self.count("session", "id", "ses_old"), 1)

    def test_second_apply_is_idempotent(self):
        self.add_session("ses_old", 10)
        self.add_session("ses_child", 9, parent="ses_old")
        self.add_session("ses_recent", 0)

        first = self.run_script("--apply", "--no-vacuum")
        second = self.run_script("--apply", "--no-vacuum")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("nothing to delete", second.stdout)


if __name__ == "__main__":
    unittest.main()
