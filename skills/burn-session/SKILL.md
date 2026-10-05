---
name: burn-session
description: Deletes the current OpenCode session from local history after you quit, so it is gone from the session list. Use when the user says "burn this session", "burn it", "delete this session", "purge this session", or "forget this session". Confirms first. Never touches other sessions, logs, tool-output, or the database file.
license: MIT
compatibility: opencode
---

# Burn Session

User-invocable. Deletes the current session, but only after you quit OpenCode.

## When To Use

Trigger phrases: "burn this session", "burn it", "delete this session", "purge this session", "forget this session".

Scope is the **current session only**. Never another session, never all sessions, never the database file, never `auth.json`.

## What It Does And Does Not

- Deletes the session row from `opencode.db`; its messages and parts cascade away with it.
- Also revokes any public share link: the delete event reaches OpenCode's share service, which deletes the remote shared copy and drops the share row, so a burned session does not leave a live `opncd.ai` URL behind. Manual `/unshare` is not separately needed.
- Caveat: if `OPENCODE_DISABLE_SHARE` is truthy the share service is inert, so a previously shared session would keep its public link; run `/unshare` before burning in that case.
- Leaves `opencode.log`, `tool-output/`, shell history, and every other session untouched.

## Why Deletion Is Deferred

Deleting a live session breaks the running client: it throws `UnknownError` and a failed `insert into "part"` on its next write. So the skill never deletes in place. It arms a watcher that fires the moment the OpenCode process exits.

## Procedure

1. **Resolve and show.** Run the summary (dry run):

   ```
   sh ~/.config/opencode/skills/burn-session/scripts/burn.sh
   ```

   Use the script that sits beside this file at `scripts/burn.sh`; the global install path is shown above, a per-project install keeps it under `.opencode/skills/burn-session/scripts/burn.sh`.

   It prints the resolved session `id`, `title`, `dir`, message/part counts, and `share` (the public link, or none). The resolved session is the newest row in the DB, which is the live one.

2. **Verify it matches.** Confirm the printed `title` and `dir` describe the session you are actually in. If they do not, stop and ask. Never arm on a mismatch.

3. **Confirm every time.** Show the `id`, `title`, counts, and any share link that will be revoked, and wait for an explicit yes. This is irreversible and has no undo. Use the `question` tool; do not proceed on a soft "ok".

4. **Arm on yes.**

   ```
   sh ~/.config/opencode/skills/burn-session/scripts/burn.sh --yes
   ```

   It spawns a detached watcher keyed to the OpenCode pid and returns immediately.

5. **Tell the user to quit.** The session is purged the moment they exit OpenCode. Offer the escape hatch: `sh ~/.config/opencode/skills/burn-session/scripts/burn.sh --cancel`.

## Hard Rules

1. Current session only. No targeting other sessions, no bulk delete.
2. Never delete in place. Always defer to process exit.
3. Confirm every time, after showing the resolved id and title.
4. Stop on any title or directory mismatch.
5. Session only. Never logs, tool-output, shell history, `auth.json`, or the DB file.
6. If the user changes their mind before quitting, run `--cancel`.
