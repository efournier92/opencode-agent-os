#!/usr/bin/env python3
"""Prune OpenCode session families idle for N days, then reclaim space.

A family is a root session plus every subagent session below it. It is
expired when its newest `time_updated` is older than the cutoff. The single
newest session in the whole DB is always protected.

Dry run by default. `--apply` deletes, then vacuums immediately or defers
the vacuum until OpenCode exits, because a running client holds the DB open.
"""

import argparse
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DAYS = 7
DAY_MS = 86400 * 1000
TRUTHY = {"1", "true", "yes", "on"}

FAMILY_SQL = """
WITH RECURSIVE roots(id) AS (
    SELECT id FROM session
    WHERE parent_id IS NULL OR parent_id NOT IN (SELECT id FROM session)
),
family(root, id) AS (
    SELECT id, id FROM roots
    UNION
    SELECT family.root, s.id FROM session s JOIN family ON s.parent_id = family.id
)
SELECT family.id FROM family
JOIN (
    SELECT family.root AS root, MAX(s.time_updated) AS newest
    FROM family JOIN session s ON s.id = family.id
    GROUP BY family.root
) fam ON fam.root = family.root
WHERE fam.newest < ?
"""

SHARED_SQL = """
SELECT id FROM session
WHERE share_url IS NOT NULL AND share_url <> ''
  AND id IN (SELECT id FROM candidate_ids)
UNION
SELECT session_id FROM session_share
WHERE session_id IN (SELECT id FROM candidate_ids)
"""


def human_size(n):
    return f"{n / 1048576:.1f} MB" if n >= 1048576 else f"{n} bytes"


def db_size(db):
    total = 0
    for suffix in ("", "-wal", "-shm"):
        path = Path(str(db) + suffix)
        if path.is_file():
            total += path.stat().st_size
    return total


def resolve_db(explicit):
    if explicit:
        return Path(explicit)
    if os.environ.get("OPENCODE_DB"):
        return Path(os.environ["OPENCODE_DB"])
    try:
        out = subprocess.run(
            ["opencode", "db", "path"], capture_output=True, text=True, timeout=10
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    return Path.home() / ".local" / "share" / "opencode" / "opencode.db"


def opencode_pids():
    try:
        out = subprocess.run(["pgrep", "-x", "opencode"], capture_output=True, text=True)
    except OSError:
        return []
    return [line for line in out.stdout.split() if line]


def read_expired(conn, cutoff):
    total = conn.execute("SELECT COUNT(*) FROM session").fetchone()[0]
    newest = conn.execute(
        "SELECT id FROM session ORDER BY time_updated DESC, id DESC LIMIT 1"
    ).fetchone()
    expired = {row[0] for row in conn.execute(FAMILY_SQL, (cutoff,))}
    if newest:
        expired.discard(newest[0])
    return total, expired


def cutoff_ms(days):
    return int(datetime.now(timezone.utc).timestamp() * 1000) - days * DAY_MS


def cutoff_date(cutoff):
    return datetime.fromtimestamp(cutoff / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def connect_read(db):
    uri = Path(db).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def report_header(total, expired, cutoff, days, db):
    print(f"sessions: {total} total")
    print(f"expired: {len(expired)} past {cutoff_date(cutoff)} ({days} days)")
    print(f"db: {human_size(db_size(db))}")


def dry_run(db, days):
    conn = connect_read(db)
    try:
        cutoff = cutoff_ms(days)
        total, expired = read_expired(conn, cutoff)
    finally:
        conn.close()
    report_header(total, expired, cutoff, days, db)
    print("dry run: nothing deleted, pass --apply to delete")
    print("vacuum: not run (dry run)")
    return 0


def shared_ids(conn, ids):
    """Return the subset of ids that carry a public share."""
    if not ids:
        return []
    conn.execute("CREATE TEMP TABLE IF NOT EXISTS candidate_ids(id TEXT PRIMARY KEY)")
    conn.execute("DELETE FROM candidate_ids")
    conn.executemany(
        "INSERT OR IGNORE INTO candidate_ids(id) VALUES (?)", [(i,) for i in ids]
    )
    return sorted(row[0] for row in conn.execute(SHARED_SQL))


def revoke(sid):
    try:
        res = subprocess.run(
            ["opencode", "session", "delete", sid], capture_output=True, text=True
        )
    except OSError as exc:
        print(f"cannot run opencode: {exc}", file=sys.stderr)
        return False
    if res.returncode != 0:
        print(
            f"opencode session delete {sid} failed: "
            f"{res.stderr.strip() or res.stdout.strip()}",
            file=sys.stderr,
        )
        return False
    return True


def delete_expired(db, days, no_vacuum):
    cutoff = cutoff_ms(days)
    before = db_size(db)
    probe = connect_read(db)
    try:
        total, expired = read_expired(probe, cutoff)
        shared = set(shared_ids(probe, expired))
    finally:
        probe.close()

    report_header(total, expired, cutoff, days, db)
    if not expired:
        print("nothing to delete")
        return 0

    disabled = os.environ.get("OPENCODE_DISABLE_SHARE", "").lower() in TRUTHY
    skipped = set()
    if disabled:
        for sid in sorted(shared):
            print(
                f"warning: skipped shared session {sid}: "
                "OPENCODE_DISABLE_SHARE is set, revoke its link manually",
                file=sys.stderr,
            )
            skipped.add(sid)
    else:
        # Revocation is an external call, so it cannot sit inside the write
        # transaction; a failure here stops before any local deletion.
        for sid in sorted(shared):
            if not revoke(sid):
                print("aborted before local deletion", file=sys.stderr)
                return 1

    conn = sqlite3.connect(str(db), isolation_level=None)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("BEGIN IMMEDIATE")
    try:
        # Recompute under the write lock: a session resumed after the
        # preflight read must not be deleted on stale timestamps.
        _total, expired = read_expired(conn, cutoff)
        late = set(shared_ids(conn, expired - skipped)) - shared
        for sid in sorted(late):
            print(
                f"warning: skipped newly expired shared session {sid}: "
                "revoke its link manually and re-run",
                file=sys.stderr,
            )
        skipped |= late
        expired -= skipped
        revoked = shared - skipped

        conn.execute("CREATE TEMP TABLE doomed(id TEXT PRIMARY KEY)")
        conn.executemany(
            "INSERT OR IGNORE INTO doomed(id) VALUES (?)",
            [(i,) for i in expired | revoked],
        )
        events = conn.execute(
            "SELECT COUNT(*) FROM event WHERE aggregate_id IN (SELECT id FROM doomed)"
        ).fetchone()[0]
        conn.execute("DELETE FROM event WHERE aggregate_id IN (SELECT id FROM doomed)")
        conn.execute(
            "DELETE FROM event_sequence WHERE aggregate_id IN (SELECT id FROM doomed)"
        )
        conn.execute("CREATE TEMP TABLE local_ids(id TEXT PRIMARY KEY)")
        conn.executemany(
            "INSERT OR IGNORE INTO local_ids(id) VALUES (?)", [(i,) for i in expired]
        )
        local = conn.execute(
            "DELETE FROM session WHERE id IN (SELECT id FROM local_ids)"
        ).rowcount
        conn.execute("COMMIT")
    except sqlite3.Error:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()

    conn = sqlite3.connect(str(db), isolation_level=None)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    finally:
        conn.close()
    deleted = local + len(revoked)
    print(f"deleted: {deleted} sessions, {events} events")
    print(f"db: {human_size(before)} -> {human_size(db_size(db))}")
    if deleted == 0 and events == 0:
        print("nothing to delete")
        return 0

    if no_vacuum:
        print("vacuum: skipped (--no-vacuum)")
        return 0
    return handle_vacuum(db)


def vacuum(db):
    pids = opencode_pids()
    if pids:
        print(
            f"opencode is running; quit it first (pid {' '.join(pids)})",
            file=sys.stderr,
        )
        return 1
    before = db_size(db)
    free = shutil.disk_usage(Path(db).resolve().parent).free
    needed = int(before * 1.2)
    if free < needed:
        print(
            f"need about {human_size(needed)} free for vacuum, have {human_size(free)}",
            file=sys.stderr,
        )
        return 1
    conn = sqlite3.connect(str(db), isolation_level=None)
    try:
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("VACUUM")
        check = conn.execute("PRAGMA quick_check").fetchone()[0]
    finally:
        conn.close()
    if check != "ok":
        print(f"quick_check failed: {check}", file=sys.stderr)
        return 1
    print(f"vacuum: {human_size(before)} -> {human_size(db_size(db))}")
    return 0


def armed_pid(pidfile):
    try:
        pid = int(pidfile.read_text().strip())
        os.kill(pid, 0)
        return pid
    except (OSError, ValueError):
        return None


def arm_vacuum(db):
    state = Path.home() / ".local" / "share" / "opencode" / "prune"
    state.mkdir(parents=True, exist_ok=True)
    pidfile = state / "vacuum.pid"
    log = state / "vacuum.log"
    pid = armed_pid(pidfile)
    if pid:
        print(f"vacuum: already armed (watcher {pid}, log {log}); db shrinks when it runs")
        return 0
    # minimalist: a sh wait loop avoids adding a hidden --wait flag; upgrade to a subcommand only if the watcher needs retries.
    script = Path(__file__).resolve()
    command = (
        "while pgrep -x opencode >/dev/null 2>&1; do sleep 2; done; "
        f"exec {shlex.quote(sys.executable)} {shlex.quote(str(script))} "
        f"--vacuum-only --db {shlex.quote(str(db))}"
    )
    with open(log, "ab") as handle:
        proc = subprocess.Popen(
            ["/bin/sh", "-c", command],
            stdin=subprocess.DEVNULL,
            stdout=handle,
            stderr=handle,
            start_new_session=True,
            cwd=str(state),
        )
    pidfile.write_text(str(proc.pid))
    print(
        f"vacuum: deferred until opencode exits (watcher {proc.pid}, log {log}); "
        "db shrinks when it runs"
    )
    return 0


def handle_vacuum(db):
    if opencode_pids():
        return arm_vacuum(db)
    return vacuum(db)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--vacuum-only", action="store_true")
    parser.add_argument("--no-vacuum", action="store_true")
    parser.add_argument("--db")
    args = parser.parse_args(argv)

    if args.days < 1:
        print("--days must be at least 1", file=sys.stderr)
        return 2

    db = resolve_db(args.db)
    if not Path(db).is_file():
        print(f"no database at {db}", file=sys.stderr)
        return 1
    try:
        if args.vacuum_only:
            return vacuum(db)
        if args.apply:
            return delete_expired(db, args.days, args.no_vacuum)
        return dry_run(db, args.days)
    except sqlite3.Error as exc:
        print(f"sqlite error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
