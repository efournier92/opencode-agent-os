---
name: ship-changes
description: Chunk unstaged work into logical commits and push it. Defaults to per-commit review (stage, show the diff, let the user edit the message, then commit); an explicit autonomy cue such as "ship autonomously" runs unattended. Fires on "commit", "commit unstaged", "commit and push", "ship", or "ship changes".
license: MIT
compatibility: opencode
---

# Ship Changes

User-invocable, low effort.

## Role

Turns a repo's unstaged work into logical, reviewable commits and pushes them.
Runs in one of two modes: `review` (default) pauses at each chunk for the user to approve or edit the message, and `auto` shows one pre-flight plan for veto, then commits and pushes without further stops.
Runs only when the user asks; never unprompted.

## Modes

- `review` (default): per-chunk gate; the user approves or edits each message before it commits, and the push is confirmed once at the end.
- `auto`: one pre-flight gate; show the full plan (repos, branch, remote, chunks, messages, push target) and wait for a go-ahead or veto; then commit each and push without further stops, except that a default or protected branch must be named explicitly in the approval.
- Select `auto` only on an explicit autonomy cue in the invoking message ("ship autonomously", "just ship", "no review"); anything else, including a bare "commit" and any ambiguous cue, is `review`.
- Never infer the mode from the repo, the diff, or a project file.
- The cue and the instruction to run must both arrive with the invocation; a standing instruction ("ship when green") never authorizes a later run.
- Announce the mode at the start of the run so a wrong default is visible before anything commits.

## Repo/Scope Resolution (Do First)

1. Argument given (a repo name or path) -> operate there.
2. No argument, invoked from inside a repo -> operate on that repo.
3. No argument, invoked from outside any repo -> stop and ask which repo, listing the known options. Never guess.

Only extends to a second repo when the conversation clearly shows the change spans repos (e.g. a paired backend+frontend feature); never touches a repo the work didn't actually reach.

## Output Contract: Commit Message Rules (Self-Check Before The Commit)

Every message must pass all of these; if any fails, rewrite before committing rather than fix after pushing:

1. **Subject is Title Case, imperative, action-oriented.** No conventional-commit prefixes (`fix:`, `feat:`, `chore:`, etc.); forbidden regardless of convention elsewhere. Soft cap ~50 chars, hard cap 72, no trailing punctuation.
2. First bullet immediately follows the subject line; no blank line between.
3. Every line, including bullets, stays under 72 chars.
4. A bullet that would exceed the limit gets **restructured**, never wrapped; keep the main action in the parent bullet, push detail into a nested sub-bullet. A line is never the continuation of the previous line's sentence.
5. The code fence and every line inside it start at column 1; the shown message is committed verbatim, so indentation would corrupt it.
6. Every bullet line ends in `.` or `:` (colon only when sub-bullets/a list follow). No bare line endings (subject line excepted).
7. Backticks around every code identifier, column, component, function, filename mentioned.
8. Repetition across locations is consolidated into one parent bullet with an indented location list, not one bullet per location.
9. No special characters (em dashes, arrows); use `-`, `:`, or `->`.

## Workflow

**Phase 1: Discovery Reconcile**: if the repo opted in with a `docs/discovery/` directory, flush this session's findings into its `DISCOVERY.md`; verify each entry's evidence (`path:line`, URL, or exact command) resolves, dropping dead ones and downgrading unproven ones to `[assumption]`; dedupe against existing entries and delete superseded lines rather than duplicate; enforce the 240-character entry and 8 KB file caps; keep newest first; report entries added, dropped, or deleted. Staging happens in Phase 3 with each entry's related chunk. Skip this phase when the repo has not opted in.

**Phase 2: Assess**: check working-tree status (including untracked files and submodule state) and diff stats in the resolved repo and any other repo the change is known to touch; stop and report a modified submodule pointer rather than guessing; group changes into logical chunks by intent (e.g. schema/data-model, service/logic layer, API surface, backfill/one-off tasks, frontend, tests with the code they cover; chunks may span repos when they genuinely belong together); draft each message to the rules above; report the grouping, the draft messages, and the intended push targets; if the index already holds staged changes, commit that set first as its own chunk or stop and ask rather than folding it into the first chunk.
In `auto`, wait at this pre-flight for a go-ahead or veto; in `review`, this report is a heads-up and the per-chunk gate is the approval point.

**Phase 3: Commit loop** (per chunk, in order): stage the chunk by exact path, including its discovery files (untracked files must be added explicitly); show the staged diff; in `review`, display the draft message in a column-1 fenced block and wait, treating `ok` as accept, a fenced replacement as the new message, and `regroup: <instruction>` as unstaging and re-running Phase 2 for that chunk; in `auto`, commit it directly; verify the chunk committed and nothing remains staged; report the short SHA and subject.

**Phase 4: Push**: for each repo that received commits, resolve the branch and remote from the existing upstream, or the sole configured remote when no upstream exists; stop and report on a detached HEAD, multiple remotes with no upstream, or no remote.
Detect the default branch from the resolved remote's `HEAD` (`git symbolic-ref refs/remotes/<remote>/HEAD`), falling back to the names `main`, `master`, `develop`, and `trunk`, and treat an undetermined branch as default in `auto`.
In `review`, show every repo, branch, and remote and wait for one confirmation before pushing; in `auto`, the pre-flight approval covers the push; in either mode, pushing a default or protected branch requires the approval to name that branch; then push and stop on divergence or rejection; never force-push; report each pushed branch and commit range.

**Phase 5: Handoff**: show the new commit log; confirm every repo committed in is committed and pushed; name the next step (e.g. opening a PR).

## Hard Rules

1. **User-invoked only.** Never runs unprompted; the shared rulebook's no-unprompted-commit rule stands.
2. **Review is the default.** A bare "commit" and any ambiguous cue pause at each chunk; only an explicit autonomy cue in the invoking message selects `auto`, which still shows one pre-flight plan and waits for a go-ahead or veto before any commit; never infer the mode from the repo or the diff, and a standing instruction never carries.
3. **No history rewriting.** No amend, rebase, or force-push; mistakes get a new commit.
4. **Push safety.** Resolve the remote before pushing; stop and report on a detached HEAD, an ambiguous or missing remote, divergence, a rejected push, or a default/protected branch without approval; never push a repo the work didn't reach.
5. **Tight logical grouping.** No mixing unrelated concerns; a schema change includes the model/logic setup that immediately uses it.
6. **Messages follow the contract.** The skill drafts each message; in `review` the user's final wording is committed as given, in `auto` the skill's draft is final.
7. **Discovery carries evidence.** Evidence is a `path:line`, a URL, or an exact command; an entry without any is an `[assumption]`, not a `[find]`, and is never staged as fact.
