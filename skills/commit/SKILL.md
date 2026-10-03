---
name: commit
description: Organize already-completed work into logical, reviewable commits. Stages changesets one chunk at a time and suggests messages, but never commits anything itself.
license: MIT
compatibility: opencode
---

# Commit

User-invocable, low effort.

## Role

Organizes already-completed work into logical, reviewable commits. Output is staged changesets, one chunk at a time; the user reviews each in their editor, commits manually with their own message, then signals to continue. This skill never commits anything itself.

## Repo/Scope Resolution (Do First)

1. Argument given (a repo name or path) -> operate there.
2. No argument, invoked from inside a repo -> operate on that repo.
3. No argument, invoked from outside any repo -> stop and ask which repo, listing the known options. Never guess.

Only extends to a second repo when the conversation clearly shows the change spans repos (e.g. a paired backend+frontend feature); never touches a repo the work didn't actually reach.

## Output Contract: Commit Message Rules (Self-Check Before Displaying)

Every suggested message must pass all of these; if any fails, rewrite before sending rather than send-and-apologize:

1. **Subject is Title Case, imperative, action-oriented.** No conventional-commit prefixes (`fix:`, `feat:`, `chore:`, etc.); forbidden regardless of convention elsewhere. Soft cap ~50 chars, hard cap 72, no trailing punctuation.
2. First bullet immediately follows the subject line; no blank line between.
3. Every line, including bullets, stays under 72 chars.
4. A bullet that would exceed the limit gets **restructured**, never wrapped; keep the main action in the parent bullet, push detail into a nested sub-bullet. A line is never the continuation of the previous line's sentence.
5. The code fence and every line inside it start at column 1; never indented to match surrounding list depth, even mid-way through a numbered workflow step. Leading whitespace forces the user to reformat after pasting.
6. Every bullet line ends in `.` or `:` (colon only when sub-bullets/a list follow). No bare line endings (subject line excepted).
7. Backticks around every code identifier, column, component, function, filename mentioned.
8. Repetition across locations is consolidated into one parent bullet with an indented location list, not one bullet per location.
9. No special characters (em dashes, arrows); use `-`, `:`, or `->`.

## Workflow

**Phase 1: Discovery Reconcile**: if the repo has opted in with a `docs/discovery/` directory, flush this session's findings into its `DISCOVERY.md`; verify each new entry carries evidence, downgrading unproven ones to `[assumption]`; dedupe against existing entries and supersede rather than duplicate; keep newest first; stage that repo's `docs/discovery/DISCOVERY.md` and any linked detail files with the logically related chunk, or as a final docs chunk when discovery spans the work; report entries added or superseded. Skip this phase when the repo has not opted in.

**Phase 2: Assess**: check working-tree status (including untracked files) and diff stats in the resolved repo (and any other repo the change is known to touch); group changes into logical chunks by intent (e.g. schema/data-model, service/logic layer, API surface, backfill/one-off tasks, frontend, tests committed with or right after the code they cover; chunks may span repos when they genuinely belong together); report the grouping and proposed commits before touching the index.

**Phase 3: Commit loop** (per chunk, in order): stage the chunk by exact path (untracked files must be added explicitly); show the staged diff; describe what's staged and why it belongs together; display the suggested message in a column-1 fenced block, self-checked against the rules above; pause explicitly for the user to review, commit manually, and say to continue; after confirmation, verify the chunk committed and nothing remains staged.

**Phase 4: Handoff**: show the new commit log; confirm everything is committed and ready for the next step (e.g. opening a PR).

## Hard Rules

1. **Never commits.** Stages and suggests only; always waits for confirmation between chunks.
2. **No history rewriting.** No amend, rebase, or force-push; mistakes get a new commit.
3. **Tight logical grouping.** No mixing unrelated concerns; a schema change includes the model/logic setup that immediately uses it.
4. **User owns the message wording.** Suggests in their style; never critiques or overrides what they actually write.
5. **Discovery carries evidence.** An entry without a location is an `[assumption]`, not a `[find]`; never stage an unevidenced factual entry.
