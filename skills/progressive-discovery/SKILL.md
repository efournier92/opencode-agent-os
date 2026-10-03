---
name: progressive-discovery
description: Progressive Discovery for opted-in repos, the on-demand home of the docs/discovery/DISCOVERY.md index conventions. Load when scoping work in a repo that has docs/discovery/, or when appending durable findings, decisions, traps, and outcomes.
license: MIT
compatibility: opencode
---

# Progressive Discovery

On demand. Not part of the always-loaded rulebook; load it only in an opted-in repo.

## Role

Maintains a committed, per-repo discovery index so a future agent can find the relevant slice of what the workspace learned and ignore the rest, at the cost of one grep instead of a full read. It borrows the cadence premise of continuous discovery (capture continuously, not only at session end) and the index-versus-content pattern from agent memory.

## Opt-In

- A repository opts in by containing a `docs/discovery/` directory. No directory means skip entirely: read nothing, create nothing, write nothing. Never auto-create.
- Git working trees only. Outside one, in a bare repo, or on a tree with no commits, bypass and fall back to `capture` for a standalone note.
- In an opted-in repo the index is `docs/discovery/DISCOVERY.md`, committed there. A linked worktree and a submodule each opt in separately.

## Index Format

One line per entry, newest first by date (within a day, order is not significant), kept under roughly 100 lines:

```markdown
# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required.

## Entries

- YYYY-MM-DD | [type] | scope | finding | evidence
```

- `type` is one of `find`, `decision`, `assumption`, `trap`, `question`, `outcome`.
- `scope` is a lowercase slash token naming the subsystem; reuse an existing token when one matches, otherwise prefer the top-level directory name (for example `plugin/skills`, `api/auth`).
- `evidence` is a `path:line`, a URL, or the exact command. `assumption` and `question` may instead name what would settle them.
- No `|` inside a field; if a command needs one, link a detail file instead.
- When one line cannot carry it, write a `capture` file and link it from the entry.

## Checkpoints (When To Append)

Append when a finding passes the decision test: would this change what a future agent does or believes? Skip when it would not, and when one grep/read or the project docs already carry it.

- Recon concludes with a non-obvious fact.
- A durable decision locks.
- An assumption is validated or invalidated.
- An incident is fixed.
- A trap is found.
- A build, test, or benchmark yields a noteworthy outcome.
- An open question is left for a future agent.

## Read Contract

- Grep the index by scope token or `[type]` when scoping a task; do not load the whole file unless it is small (under roughly 60 lines) or an entry is load-bearing.
- Open a linked detail file or `capture` file only when an entry is load-bearing. Ignoring irrelevant entries is the point.

## Write Contract

- The operator owns appends; subagents return candidates (finding + evidence) and never write. The context-curator is the only other agent allowed to touch the file, and only to prune, archive, or annotate `superseded`.
- Never rewrite an entry's meaning; the only in-place change is annotating `superseded YYYY-MM-DD` alongside the replacement.
- Evidence is required for `find`, `decision`, `trap`, and `outcome`; otherwise the entry is an `assumption`.
- Past roughly 100 lines, the curator archives settled entries into a linked detail file or drops re-derivable ones.

## Commit Reconcile

In an opted-in repo, before staging, the commit skill reconciles the index of the repository it commits: flush unsaved findings, verify evidence (downgrade unproven to `assumption`), dedupe and supersede rather than duplicate, keep newest first, and stage `docs/discovery/DISCOVERY.md` with the related chunk. It never commits.

## Relationship To Other Records

- `handoff` resumes one work thread and is overwritten; link relevant entries instead of restating them.
- `capture` holds long topic detail and appends an index entry linking it.
- The index outlives both and links to them.

## Verify

- Any change to `docs/discovery/DISCOVERY.md` passes `scripts/lint-markdown.py` from the plugin checkout.
- Every `find`, `decision`, `trap`, and `outcome` entry carries evidence.

Rationale, threats, and worked examples live in `docs/specs/2026-10-03-progressive-discovery.md`.
