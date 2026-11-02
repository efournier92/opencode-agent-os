#!/usr/bin/env python3
"""Per-session artifact paths and best-effort cleanup helpers.

Tool-output files are per-part (referenced from part.data) and session diffs
are per-session. `snapshot/` is a shared, content-addressed git-object store
and is never touched here. The database is opened read-only.
"""

import os
import sqlite3
import sys
from pathlib import Path

OUTPUT_PATH_SQL = (
    "SELECT json_extract(data, '$.state.metadata.outputPath') FROM part "
    "WHERE session_id = ?"
)
DB_SUFFIXES = ("", "-wal", "-shm")


def _inside(path, root):
    try:
        Path(path).resolve().relative_to(root)
        return True
    except (OSError, ValueError):
        return False


def paths_for_session(db_path, session_id, root):
    """Return artifacts owned by session_id, all confined to root."""
    root = Path(root).resolve()
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        found = [row[0] for row in conn.execute(OUTPUT_PATH_SQL, (session_id,))]
    finally:
        conn.close()
    paths = []
    for raw in found:
        if not raw or not _inside(raw, root):
            continue
        candidate = Path(raw).resolve()
        if candidate not in paths:
            paths.append(candidate)
    diff = root / "storage" / "session_diff" / f"{session_id}.json"
    if diff.is_file() and diff not in paths:
        paths.append(diff)
    return [str(path) for path in paths]


def delete_paths(paths):
    """Unlink every path, returning (deleted, failed) string lists."""
    deleted, failed = [], []
    for path in paths:
        try:
            os.unlink(str(path))
            deleted.append(str(path))
        except OSError:
            failed.append(str(path))
    return deleted, failed


def harden_db(db_path):
    """Make the session DB and its sidecars owner-only. Returns changed paths."""
    changed = []
    for suffix in DB_SUFFIXES:
        path = Path(str(db_path) + suffix)
        if not path.is_file():
            continue
        try:
            os.chmod(path, 0o600)
        except OSError:
            continue
        changed.append(str(path))
    return changed


def _main(argv):
    if len(argv) < 5 or argv[1] not in ("paths", "delete"):
        print("usage: session_artifacts.py paths|delete DB SESSION_ID ROOT", file=sys.stderr)
        return 2
    command, db, sid, root = argv[1:5]
    paths = paths_for_session(db, sid, root)
    if command == "paths":
        for path in paths:
            print(path)
        return 0
    deleted, failed = delete_paths(paths)
    for path in deleted:
        print(f"deleted: {path}")
    for path in failed:
        print(f"skipped: {path}")
    for path in harden_db(db):
        print(f"hardened: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
