---
name: prune-sessions
description: Deletes OpenCode session families with no activity for 7 days and reclaims the database space. Use when the user says "prune sessions", "clean up old sessions", "wipe old sessions", or "reclaim session db space". Dry-run first; deletion is irreversible.
license: MIT
compatibility: opencode
---

# Prune Sessions

User-invocable. Deletes every session family whose newest activity is older than 7 days, then reclaims the space in `opencode.db`.

## Retention Policy

A family is one root session plus every subagent session below it. A family is expired when its newest `session.time_updated` is older than the cutoff, so recent subagent work protects the whole family.

Expired families are deleted completely: session rows, messages, parts, todos, share rows, and event and event_sequence rows. Deletion is irreversible.

Two protections always apply:

- The single newest session by `time_updated` is never deleted.
- A shared expired session has its public link revoked with `opencode session delete <id>` before local deletion.

The policy is 7 days by default; `--days N` changes the cutoff.

## Procedure

1. Run the dry run first. It changes nothing:

   ```
   python3 ~/.config/opencode/skills/prune-sessions/scripts/prune_sessions.py
   ```

   A per-project install uses `.opencode/skills/prune-sessions/scripts/prune_sessions.py` instead. The script resolves the DB from `--db`, then `$OPENCODE_DB`, then `opencode db path`, then `~/.local/share/opencode/opencode.db`.

2. Show the total session count, the expired count, the cutoff date, and the DB size. A person running this by hand waits for explicit confirmation before applying; a `context-curator` sweep applies the recorded 7-day policy without prompting and reports the deleted count and reclaimed space.

3. Apply:

   ```
   python3 ~/.config/opencode/skills/prune-sessions/scripts/prune_sessions.py --apply
   ```

4. Report the deleted session count, the events deleted, and whether the vacuum ran or was deferred.

Other options: `--no-vacuum` skips the vacuum, `--vacuum-only` runs only the vacuum, and `--db PATH` targets another database.

## Shared Links

An expired session with a `share_url` or a `session_share` row is removed through `opencode session delete` first, which revokes the public link. If that command fails, the run aborts before any local deletion.

When `OPENCODE_DISABLE_SHARE` is truthy the share service is inert, so the script skips those sessions and warns instead of leaving a live public link behind. Run `/unshare` and prune again to clear them.

## Deferred Vacuum

`VACUUM` needs exclusive access, so `--apply` behaves differently by process state:

- OpenCode running: a detached watcher waits for `pgrep -x opencode` to go empty, then runs the vacuum. Its `vacuum.pid` and `vacuum.log` live under `~/.local/share/opencode/prune/`.
- OpenCode not running: the vacuum runs immediately after deletion.

`--vacuum-only` refuses to start while OpenCode is running and needs free space of at least 1.2 times the DB size. A vacuum that is armed but not yet fired can be stopped by killing the watcher pid named in the output.

## Caveats

- The deletion commits immediately, even when the vacuum is deferred. Sessions that an open TUI still holds may error on their next write until OpenCode restarts.
- The script never touches `auth.json`, logs, `tool-output/`, snapshots, or the DB file path itself.
- A second run finds nothing to delete; the prune is idempotent.
