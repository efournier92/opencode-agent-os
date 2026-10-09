---
name: write-handoff
description: Write a structured session handoff from the current session's context so a fresh session can resume without re-exploring, then prepare a ready-to-paste resume prompt.
license: MIT
compatibility: opencode
---

# Write Handoff

User-invocable, inline (runs in the current agent, not a subagent).

## Role

Writes a structured session handoff from the current session's context so a fresh session can resume without re-exploring, then copies a ready-to-paste resume prompt to the clipboard.

## Steps

1. **Guard**: if no edits were made, no decisions recorded, and everything is clean, tell the user there's nothing to hand off and stop. Never produce an empty template just to have output.
2. **Resolve topic**: use the given argument, or infer a slug from the primary session work (lowercase, hyphenated). Check existing handoff files dated today for a similar topic before minting a new slug; prefer updating an existing file over creating a near-duplicate.
3. **Gather state**: check working-tree status and current branch for every repo/service in the workspace, in one parallel batch of calls.
4. **Flush discovery**: in an opted-in repo (`docs/discovery/`), append any checkpoint findings not yet recorded to `docs/discovery/DISCOVERY.md`, and link relevant entries by ID from the handoff instead of restating them (see Progressive Discovery in `AGENTS.md`). When the repo has `docs/specs/` or `docs/handoffs/` but no `docs/discovery/`, state once in the handoff that the repo could opt in; never create the directory.
5. **Write the handoff**: dated, topic-named file, overwritten in place if it already exists (progressive update, not accumulation). Required sections: current state (done / in-progress / per-repo branch state); key decisions and why (only ones that affect future work); next actions (ordered, each with exact file paths and expected outcome); verify commands (what the next session runs to confirm the starting state matches); open risks/blockers (empty section if none). Quality bar: a fresh session reading *only* this file should be able to continue work without re-exploring: include file paths, line numbers, branch names; exclude anything re-derivable by exploration, anything already in the project's own docs, anything already in memory files.
6. **Clean up autosave stubs**: delete any mechanical pre-compaction snapshot files so a later session isn't pointed at a stub instead of this curated handoff.
7. **Copy a resume prompt to the clipboard**, built from the exact path just written (no placeholders), instructing the next session to run the verify commands first and note any divergence before proceeding. Only claim success if the clipboard command actually succeeded; otherwise print the prompt as plain copyable text.
8. **Report**: path written, clipboard status, and the plain instruction to clear/start fresh and paste the prompt.
