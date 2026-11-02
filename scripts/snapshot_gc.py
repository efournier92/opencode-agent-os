#!/usr/bin/env python3
"""Collect snapshot objects no longer referenced by any session.

Snapshots under the snapshot root are content-addressed directories named by
40-hex git object hashes and shared across sessions, so per-session deletion is
unsafe. A directory is a candidate only when its hash appears in no text column
of `session`, `message`, or `part`.

Dry run by default. `--apply` deletes candidate directories confined to the
snapshot root. The database is opened read-only.
"""

import argparse
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

HEX40 = re.compile(r"[0-9a-f]{40}")
TABLES = ("session", "message", "part")


def resolve_root(explicit):
    if explicit:
        return Path(explicit)
    return Path(
        os.environ.get("OPENCODE_SNAPSHOT_DIR")
        or Path.home() / ".local" / "share" / "opencode" / "snapshot"
    )


def resolve_db(explicit):
    if explicit:
        return Path(explicit)
    return Path(
        os.environ.get("OPENCODE_DB")
        or Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    )


def connect_read(db):
    uri = Path(db).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def text_columns(conn, table):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows if (row[2] or "").upper() == "TEXT"]


def scan_referenced(db):
    """Return every 40-hex token found in the text columns, plus cells read."""
    conn = connect_read(db)
    try:
        referenced = set()
        scanned = 0
        for table in TABLES:
            for column in text_columns(conn, table):
                for (value,) in conn.execute(f"SELECT {column} FROM {table}"):
                    scanned += 1
                    if value:
                        referenced.update(HEX40.findall(value))
    finally:
        conn.close()
    return scanned, referenced


def list_candidates(root, referenced):
    candidates = []
    for entry in root.iterdir():
        if entry.is_dir() and HEX40.fullmatch(entry.name) and entry.name not in referenced:
            candidates.append(entry)
    return sorted(candidates)


def inside(path, root):
    try:
        Path(path).resolve().relative_to(root)
        return True
    except (OSError, ValueError):
        return False


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root")
    parser.add_argument("--db")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    root = resolve_root(args.root).resolve()
    db = resolve_db(args.db)
    if not root.is_dir():
        print(f"no snapshot directory at {root}", file=sys.stderr)
        return 2
    if not db.is_file():
        print(f"no database at {db}", file=sys.stderr)
        return 2

    scanned, referenced = scan_referenced(db)
    candidates = list_candidates(root, referenced)

    print(f"snapshot root: {root}")
    print(f"scanned: {scanned} text values")
    print(f"referenced: {len(referenced)} hashes")
    print(f"candidates: {len(candidates)}")
    for entry in candidates:
        print(f"candidate: {entry.name}")

    deleted = 0
    if args.apply:
        for entry in candidates:
            if not inside(entry, root):
                print(f"warning: skipping {entry} outside root", file=sys.stderr)
                continue
            try:
                shutil.rmtree(entry)
                deleted += 1
            except OSError as exc:
                print(f"warning: cannot delete {entry}: {exc}", file=sys.stderr)
    else:
        print("dry run: nothing deleted, pass --apply to delete")
    print(f"deleted: {deleted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
