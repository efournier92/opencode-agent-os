---
name: ship-changes
description: Chunk unstaged work into logical commits and push it. Defaults to per-commit review (stage, show the diff, let the user edit the message, then commit); an explicit autonomy cue such as "ship autonomously" runs unattended, and "autoship" additionally asks through PR creation, trunk merge, and merged-branch cleanup. Fires on "commit", "commit unstaged", "commit and push", "ship", "ship changes", or "autoship".
license: MIT
compatibility: opencode
---

# Ship Changes

User-invocable, low effort.

## Role

Turns a repo's unstaged work into logical, reviewable commits and pushes them.
Runs in one of three modes: `review` (default) pauses at each chunk for the user to approve or edit the message, `auto` shows one pre-flight plan for veto then commits and pushes without further stops, and `autoship` does all of `auto` plus the ask-gated PR chain after the push (create, merge into the trunk, clean up the merged branches).
Runs only when the user asks; never unprompted.

## Modes

- `review` (default): per-chunk gate; the user approves or edits each message before it commits, and the push is confirmed once at the end.
- `auto`: one pre-flight gate; show the full plan (repos, branch, remote, chunks, messages, push target) and wait for a go-ahead or veto; then commit each and push without further stops, except that a default or protected branch must be named explicitly in the approval.
- `autoship`: all of `auto`, plus the PR follow-through in Phase 5; after the push, three `question` rounds, one per step (create the PR, merge it into the detected trunk, clean up the merged branches), each its own explicit approval.
- Select `auto` only on an explicit autonomy cue in the invoking message ("ship autonomously", "just ship", "no review"), and `autoship` only on the literal cue "autoship"; anything else, including a bare "commit" and any ambiguous cue, is `review`.
- Never infer the mode from the repo, the diff, or a project file.
- The cue and the instruction to run must both arrive with the invocation; a standing instruction ("ship when green") never authorizes a later run.
- Announce the mode at the start of the run so a wrong default is visible before anything commits; for `autoship`, also name the three upcoming asks and the trunk once it is detected in Phase 4.

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
In `auto` and `autoship`, wait at this pre-flight for a go-ahead or veto; in `review`, this report is a heads-up and the per-chunk gate is the approval point.

**Phase 3: Commit loop** (per chunk, in order): stage the chunk by exact path, including its discovery files (untracked files must be added explicitly); show the staged diff; in `review`, display the draft message in a column-1 fenced block and wait, treating `ok` as accept, a fenced replacement as the new message, and `regroup: <instruction>` as unstaging and re-running Phase 2 for that chunk; in `auto`, commit it directly; verify the chunk committed and nothing remains staged; report the short SHA and subject.

**Phase 4: Push**: for each repo that received commits, resolve the branch and remote from the existing upstream, or the sole configured remote when no upstream exists; stop and report on a detached HEAD, multiple remotes with no upstream, or no remote.
Detect the default branch from the resolved remote's `HEAD` (`git symbolic-ref refs/remotes/<remote>/HEAD`), falling back to the names `main`, `master`, `develop`, and `trunk`, and treat an undetermined branch as default in `auto` and `autoship`.
In `review`, show every repo, branch, and remote and wait for one confirmation before pushing; in `auto` and `autoship`, the pre-flight approval covers the push; in any mode, pushing a default or protected branch requires the approval to name that branch; then push and stop on divergence or rejection; never force-push; report each pushed branch and commit range.

**Phase 5: PR Follow-Through** (`autoship` only): run after Phase 4, per repo that received a push, in order. Check preconditions before the first ask and report rather than guess: the pushed branch differs from the trunk; `gh` is installed and authenticated; the remote is GitHub. If a precondition fails, report it with the exact next command (`gh pr create --base <trunk> --head <branch>`) and skip the chain for that repo; the push itself stands. Stop the chain on any decline, blocked state, or failed command; never run a later step past an earlier failure.

- **Create.** Use the trunk detected in Phase 4 (fall back to `gh repo view --json defaultBranchRef`). Draft the PR title and body from the pushed commits, write the body to a temp file, and run `scripts/lint-markdown.py` on it before posting, fixing any violation first. If the branch already has an open PR (`gh pr list --head <branch>`), `question` options are `Reuse existing PR #<n> (Recommended)` and skip, and on yes report that existing URL and never run `gh pr create`; otherwise `question` options are the drafted PR (Recommended) and skip, and on yes run `gh pr create --base <trunk> --head <branch>` and report the URL.
- **Merge.** Requires a confirmed open PR. Read `gh pr view <n> --json state,mergeable,mergeStateStatus` and `gh repo view --json squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`; stop and report when the PR is not open, not mergeable, or blocked (conflicts, draft, behind, required checks pending or failed). `question` options: only the methods the repo allows, the likely default first and marked `(Recommended)` (squash when allowed, else merge commit), plus a "Do not merge" choice. On a merge choice, merge through the platform (`gh pr merge <n> --squash|--merge|--rebase`), never `--admin`, never bypass branch protection, never a local push to the trunk; confirm the PR state is `MERGED` before continuing.
- **Cleanup.** Only after a confirmed merge. `question` options: "Delete local and remote branch (Recommended)", "Keep both". On yes: switch to the trunk (only from a clean working tree; otherwise report and leave it), `git pull --ff-only`, `git branch -d <branch>`, `git push <remote> --delete <branch>` (a no-op when the platform already removed it), `git fetch --prune`. If `-d` refuses and the PR is confirmed `MERGED` (squash or rebase leaves the original commits unreachable), `git branch -D` is allowed with that confirmation. If the branch is checked out in a linked worktree, skip the local delete and say so (the `manage-worktrees` skill owns worktree removal) while still offering the remote delete. Never delete the trunk, an unmerged branch, or any branch other than the one just merged.

**Phase 6: Handoff**: show the new commit log; confirm every repo committed in is committed and pushed; after `autoship`, also report the PR URL, merge result, deleted branches, and whether the trunk was updated; name the next step.

## Hard Rules

1. **User-invoked only.** Never runs unprompted; the shared rulebook's no-unprompted-commit rule stands.
2. **Review is the default.** A bare "commit" and any ambiguous cue pause at each chunk; only an explicit autonomy cue selects `auto`, and only the literal `autoship` cue adds the PR chain; `auto` still shows one pre-flight plan and waits for a go-ahead or veto before any commit; never infer the mode from the repo or the diff, and a standing instruction never carries.
3. **No local history rewriting.** No amend, rebase, or force-push of local history; mistakes get a new commit. The platform's `--rebase` merge option in Phase 5 merges the PR, not the local branch.
4. **Push safety.** Resolve the remote before pushing; stop and report on a detached HEAD, an ambiguous or missing remote, divergence, a rejected push, or a default/protected branch without approval; never push a repo the work didn't reach.
5. **Tight logical grouping.** No mixing unrelated concerns; a schema change includes the model/logic setup that immediately uses it.
6. **Messages follow the contract.** The skill drafts each message; in `review` the user's final wording is committed as given, in `auto` the skill's draft is final.
7. **Discovery carries evidence.** Evidence is a `path:line`, a URL, or an exact command; an entry without any is an `[assumption]`, not a `[find]`, and is never staged as fact.
8. **PR follow-through is ask-gated and fail-closed.** Each of create, merge, and cleanup needs its own explicit answer naming its target; a standing approval never carries; any decline, unmet precondition, or failed command stops the chain in place, never a partial merge or an unspecified cleanup.
9. **No protection bypass.** Merge only through a PR GitHub reports mergeable, with no `--admin` and no local push to the trunk; clean up only after a confirmed `MERGED` state, using `-d` first and `-D` only with that confirmation, never on the trunk or an unmerged branch.
