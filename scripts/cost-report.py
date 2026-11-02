#!/usr/bin/env python3
"""Per-agent cost report from the OpenCode SQLite DB. Read-only."""

import argparse
import os
import sqlite3
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pricing import GO_PRICES  # noqa: E402
import usage_archive  # noqa: E402

DEFAULT_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

# Sliding windows for 5h and 7d; 30d is a plain trailing sum.
WINDOW_MS = {"5h": 5 * 60 * 60 * 1000, "7d": 7 * 86400 * 1000, "30d": 30 * 86400 * 1000}

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

AGENT_MODEL_SQL = """
SELECT COALESCE(agent, '(unknown)') AS agent,
       COALESCE(json_extract(model, '$.id'), '(unknown)') AS model,
       COUNT(*) AS sessions,
       COALESCE(SUM(cost), 0) AS cost,
       COALESCE(SUM(tokens_input), 0) AS tokens_input,
       COALESCE(SUM(tokens_output), 0) AS tokens_output,
       COALESCE(SUM(tokens_cache_read), 0) AS tokens_cache_read
FROM session
{where}
GROUP BY agent, model
ORDER BY cost DESC
LIMIT ?
"""

MODEL_SESSIONS_SQL = """
SELECT time_created, tokens_input, tokens_cache_read,
       tokens_output, tokens_reasoning,
       json_extract(model, '$.id') AS mid
FROM session
WHERE time_created >= ?
ORDER BY time_created
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


def aggregate_agent_model(conn, since_ms=None, limit=30):
    where = "WHERE time_created >= ?" if since_ms is not None else ""
    params = (since_ms, limit) if since_ms is not None else (limit,)
    return conn.execute(AGENT_MODEL_SQL.format(where=where), params).fetchall()


def sliding_max(points, window_ms):
    """Largest cost sum over any trailing window. points: (ts_ms, cost)."""
    best = cur = 0.0
    start = 0
    for i, (ts, cost) in enumerate(points):
        cur += cost
        while ts - points[start][0] > window_ms:
            cur -= points[start][1]
            start += 1
        best = max(best, cur)
    return best


def window_spend(points, window_ms):
    if window_ms >= WINDOW_MS["30d"]:
        return sum(cost for _, cost in points)
    return sliding_max(points, window_ms)


def model_spend(conn, since_ms, window_ms, archive_rows=()):
    per_model = {mid: [] for mid in GO_PRICES}
    for row in conn.execute(MODEL_SESSIONS_SQL, (since_ms,)):
        mid = row[5]
        if mid not in GO_PRICES:
            continue
        pin, pout, pcached, _ = GO_PRICES[mid]
        cost = (
            (row[1] or 0) / 1e6 * pin
            + (row[2] or 0) / 1e6 * pcached
            + ((row[3] or 0) + (row[4] or 0)) / 1e6 * pout
        )
        per_model[mid].append((row[0], cost))
    for row in archive_rows:
        ts, mid = row.get("time_created"), row.get("model")
        if ts is None or ts < since_ms or mid not in GO_PRICES:
            continue
        pin, pout, pcached, _ = GO_PRICES[mid]
        cost = (
            (row.get("tokens_input") or 0) / 1e6 * pin
            + (row.get("tokens_cache_read") or 0) / 1e6 * pcached
            + (row.get("tokens_output") or 0) / 1e6 * pout
        )
        per_model[mid].append((ts, cost))
    for points in per_model.values():
        points.sort()
    return {mid: window_spend(points, window_ms) for mid, points in per_model.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--since", type=parse_since, metavar="YYYY-MM-DD")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--window", choices=tuple(WINDOW_MS), default="30d")
    args = parser.parse_args(argv)

    if not args.db.exists():
        print(f"cost-report: database not found: {args.db}", file=sys.stderr)
        return 1

    window_ms = WINDOW_MS[args.window]
    since_ms = args.since
    if since_ms is None:
        since_ms = int(time.time() * 1000) - WINDOW_MS["30d"]

    archive_path = os.environ.get("OPENCODE_USAGE_ARCHIVE") or usage_archive.DEFAULT_PATH
    archive_rows = usage_archive.load_rows(archive_path)

    conn = connect(args.db)
    try:
        try:
            rows = aggregate_agent_model(conn, since_ms, args.limit)
            grand = totals(conn, since_ms)
            spend = model_spend(conn, since_ms, window_ms, archive_rows)
        except sqlite3.OperationalError as exc:
            print(f"cost-report: cannot read session table: {exc}", file=sys.stderr)
            return 1
    finally:
        conn.close()

    print(f"{'AGENT':<24}{'MODEL':<24}{'SESSIONS':>9}{'COST':>10}{'INPUT':>14}{'OUTPUT':>14}{'CACHE-READ':>14}")
    for agent, model, sessions, cost, tin, tout, tcache in rows:
        print(f"{agent:<24}{model:<24}{sessions:>9}{cost:>10.2f}{tin:>14}{tout:>14}{tcache:>14}")

    n, cost, subagents, compacted = grand
    print(f"total sessions: {n}")
    print(f"total cost: {cost:.2f}")
    print(f"subagent sessions: {subagents}")
    print(f"compacted sessions: {compacted}")

    print(f"\nmodel spend ({args.window} window):")
    for mid, (_, _, _, limit) in GO_PRICES.items():
        spent = spend[mid]
        print(f"{mid}: ${spent:.2f} of ${limit} monthly ({spent / limit * 100:.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
