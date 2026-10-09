# Stash Discipline (Destructive Git Operations)

Use this rule only when a task genuinely requires a destructive operation against the working tree or index. Examples that qualify:

- `git checkout -- <tracked-path>` (overwrites local changes with HEAD).
- `git reset --hard` (rewrites index and working tree).
- `git restore <tracked-path>` (same as `checkout --`).
- `git clean -fd` (deletes untracked files).
- broad `rm -rf` against project paths.

Procedure for any of these:

1. Stash before the destructive step. Use a marker unique to this invocation that includes a timestamp and the agent PID, so collisions across processes or sessions are impossible. Example: `agent-test-$(date +%s)-$$`.
2. Record the exact stash reference returned (`stash@{N}` index or commit SHA from `git stash create`).
3. Run the destructive operation.
4. After the task completes and the danger has passed, restore from the stash if appropriate, then drop it.
5. Before any drop, verify the stash's message or commit identity still matches the marker the agent just created. If the index has shifted, the stash no longer exists, or the marker does not match, do NOT drop. Leave the stash alone and surface the inconsistency in the agent's report.

Hard constraints:

- Never `git stash drop` or `git stash pop` a stash the agent did not create in the same invocation.
- Never `git stash clear`.
- When in doubt, copy the affected paths to `/tmp` instead of stashing, then clean up the copy afterward.

## Exception: The Quality Gate

The quality gate's red proof reverts changed files with `git checkout --` and an exact-path removal per `docs/rulebook/quality-gates.md`, not the stash procedure here. That procedure is self-contained: it backs up to a per-invocation `/tmp` directory first, checks the index against HEAD, and verifies the restore against a pre-proof snapshot. It never touches the stash.
