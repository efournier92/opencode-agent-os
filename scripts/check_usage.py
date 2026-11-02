#!/usr/bin/env python3
"""Block the repo gate before an OpenCode Go allowance drains. Read-only."""

import os
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pricing import PLAN_SPLIT, PRICES  # noqa: E402
import usage_archive  # noqa: E402

DEFAULT_DB = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

# Fail once a model reaches 90% of the allowance; warn at 75%. The monthly
# pool, the worst 7-day window, and the worst 5-hour window share a threshold.
FAIL_PCT = 90
WARN_PCT = 75

WINDOW_DAYS = 30
WINDOW_MS = {"5h": 5 * 60 * 60 * 1000, "weekly": 7 * 86400 * 1000}

QUERY = """
SELECT time_created, tokens_input, tokens_cache_read,
       tokens_output, tokens_reasoning,
       json_extract(model, '$.id') AS mid,
       json_extract(model, '$.providerID') AS provider
FROM session
WHERE time_created >= ?
ORDER BY time_created
"""


def session_cost(row, price):
    _, tin, tcache, tout, treasoning = row[:5]
    pin, pout, pcached, _ = price
    return (
        (tin or 0) / 1e6 * pin
        + (tcache or 0) / 1e6 * pcached
        + ((tout or 0) + (treasoning or 0)) / 1e6 * pout
    )


def worst_window(points, window_ms):
    best = cur = 0.0
    start = 0
    for i, (ts, cost) in enumerate(points):
        cur += cost
        while ts - points[start][0] > window_ms:
            cur -= points[start][1]
            start += 1
        best = max(best, cur)
    return best


def archive_points(rows, since):
    points = []
    for row in rows:
        ts = row.get("time_created")
        mid = row.get("model")
        provider = row.get("provider")
        if ts is None or ts < since or mid not in PRICES:
            continue
        if provider and provider != "opencode-go":
            continue
        cost_row = (
            ts,
            row.get("tokens_input"),
            row.get("tokens_cache_read"),
            row.get("tokens_output"),
            0,
        )
        points.append((mid, (ts, session_cost(cost_row, PRICES[mid]))))
    return points


def main():
    db = Path(os.environ.get("OPENCODE_DB") or DEFAULT_DB)
    if not db.exists():
        print("usage check skipped: no local database")
        return 0

    since = int(time.time() * 1000) - WINDOW_DAYS * 86400 * 1000
    try:
        conn = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            rows = conn.execute(QUERY, (since,)).fetchall()
        finally:
            conn.close()
    except sqlite3.Error:
        print("usage check skipped: no local database")
        return 0

    per_model = {mid: [] for mid in PRICES}
    for row in rows:
        mid, provider = row[5], row[6]
        # Plan-backed zai sessions reuse the same model ids; pricing them at
        # Go rates would charge another allowance's tokens to this one.
        if mid not in PRICES or (provider and provider != "opencode-go"):
            continue
        per_model[mid].append((row[0], session_cost(row, PRICES[mid])))

    archive_path = os.environ.get("OPENCODE_USAGE_ARCHIVE") or usage_archive.DEFAULT_PATH
    for mid, point in archive_points(usage_archive.load_rows(archive_path), since):
        per_model[mid].append(point)
    for points in per_model.values():
        points.sort()

    failures = []
    warnings = []
    for mid, (_, _, _, limit) in PRICES.items():
        points = per_model[mid]
        monthly = sum(cost for _, cost in points)
        pct = monthly / limit * 100
        cap5 = limit * PLAN_SPLIT["5h"]
        cap7 = limit * PLAN_SPLIT["weekly"]
        worst5 = worst_window(points, WINDOW_MS["5h"])
        worst7 = worst_window(points, WINDOW_MS["weekly"])
        pct5 = worst5 / cap5 * 100
        pct7 = worst7 / cap7 * 100
        print(
            f"{mid}: {pct:.1f}% of ${limit} monthly, "
            f"worst 5h {pct5:.1f}% of ${cap5:g}, "
            f"worst 7d {pct7:.1f}% of ${cap7:g}"
        )
        worst = max(pct, pct5, pct7)
        if worst >= FAIL_PCT:
            failures.append(f"{mid} at {worst:.1f}%")
        elif worst >= WARN_PCT:
            warnings.append(f"{mid} at {worst:.1f}%")

    for warning in warnings:
        print(f"usage check warning: {warning}")
    if failures:
        print("usage check FAILED: " + ", ".join(failures))
        return 1
    print("usage check clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
