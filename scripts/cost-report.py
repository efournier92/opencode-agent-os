#!/usr/bin/env python3
"""Per-agent cost report from the OpenCode SQLite DB. Read-only."""

import argparse
import sqlite3
import sys
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

AGGREGATE_SQL = """
SELECT COALESCE(agent, '(unknown)') AS agent,
       COUNT(*) AS sessions,
       COALESCE(SUM(cost), 0) AS cost,
       COALESCE(SUM(tokens_input), 0) AS tokens_input,
       COALESCE(SUM(tokens_output), 0) AS tokens_output,
       COALESCE(SUM(tokens_cache_read), 0) AS tokens_cache_read
FROM session
{where}
GROUP BY agent
ORDER BY cost DESC
LIMIT ?
"""

TOTALS_SQL = """
SELECT COUNT(*),
       COALESCE(SUM(cost), 0),
       SUM(CASE WHEN parent_id IS NOT NULL THEN 1 ELSE 0 END),
       SUM(CASE WHEN time_compacting IS NOT NULL THEN 1 ELSE 0 END)
FROM session
{where}
"""


def parse_since(value):
    try:
        day = date.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid date: {value!r} (want YYYY-MM-DD)")
    return int(datetime(day.year, day.month, day.day, tzinfo=timezone.utc).timestamp() * 1000)


def connect(db_path):
    # URI mode=ro keeps the connection from ever writing the DB.
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    return sqlite3.connect(uri, uri=True)


def aggregate(conn, since_ms=None, limit=30):
    where = "WHERE time_created >= ?" if since_ms is not None else ""
    params = (since_ms, limit) if since_ms is not None else (limit,)
    return conn.execute(AGGREGATE_SQL.format(where=where), params).fetchall()


def totals(conn, since_ms=None):
    where = "WHERE time_created >= ?" if since_ms is not None else ""
    params = (since_ms,) if since_ms is not None else ()
    return conn.execute(TOTALS_SQL.format(where=where), params).fetchone()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--since", type=parse_since, metavar="YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=30)
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"cost-report: database not found: {args.db}", file=sys.stderr)
        return 1

    conn = connect(args.db)
    try:
        try:
            rows = aggregate(conn, args.since, args.limit)
            grand = totals(conn, args.since)
        except sqlite3.OperationalError as exc:
            print(f"cost-report: cannot read session table: {exc}", file=sys.stderr)
            return 1
    finally:
        conn.close()

    print(f"{'AGENT':<24}{'SESSIONS':>9}{'COST':>10}{'INPUT':>14}{'OUTPUT':>14}{'CACHE-READ':>14}")
    for agent, sessions, cost, tin, tout, tcache in rows:
        print(f"{agent:<24}{sessions:>9}{cost:>10.2f}{tin:>14}{tout:>14}{tcache:>14}")

    n, cost, subagents, compacted = grand
    print(f"total sessions: {n}")
    print(f"total cost: {cost:.2f}")
    print(f"subagent sessions: {subagents}")
    print(f"compacted sessions: {compacted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
