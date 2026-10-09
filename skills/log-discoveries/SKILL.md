---
name: log-discoveries
description: Progressive Discovery for opted-in repos, the on-demand home of the docs/discovery/DISCOVERY.md index conventions. Load when scoping work in a repo that has docs/discovery/, or when appending durable findings, decisions, traps, and outcomes.
license: MIT
compatibility: opencode
---

# Log Discoveries

On demand. Not part of the always-loaded rulebook; load it only in an opted-in repo.

## Role

Maintains a committed, per-repo discovery index so a future agent can find the relevant slice of what the workspace learned and ignore the rest, at the cost of one grep instead of a full read. It borrows the cadence premise of continuous discovery (capture continuously, not only at session end) and the index-versus-content pattern from agent memory.
A repo with `docs/specs/`, `docs/handoffs/`, or `capture-session` files but no `docs/discovery/` gets one opt-in proposal (one line plus a yes/no); never create the directory unprompted.

## Opt-In

- A repository opts in by containing a `docs/discovery/` directory. No directory means skip entirely: read nothing, create nothing, write nothing. Never auto-create.
- Git working trees only. Outside one, in a bare repo, or on a tree with no commits, bypass and fall back to `capture-session` for a standalone note.
- In an opted-in repo the index is `docs/discovery/DISCOVERY.md`, committed there. A linked worktree and a submodule each opt in separately.

## Index Format

One line per entry, newest first by date (within a day, order is not significant), each entry <= 240 characters and the whole file <= 8 KB (roughly 2K tokens). Overflow goes to `docs/discovery/archive/<id>.md`, which is exempt from both caps:

```markdown
# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required.
Scope tokens: <comma-separated, sorted, lowercase list>

## Entries

- D-YYYYMMDD-NN | YYYY-MM-DD | [type] | scope | finding | evidence
```

- `D-YYYYMMDD-NN` is permanent, unique within the repo, and never reused; `NN` is the per-day sequence starting at `01`; the date in the ID matches the entry's date.
- `type` is one of `find`, `decision`, `assumption`, `trap`, `question`, `outcome`.
- `scope` is a lowercase slash token naming the subsystem; reuse an existing token when one matches, otherwise prefer the top-level directory name (for example `plugin/skills`, `api/auth`).
- `evidence` is a URL, an exact command in backticks, or a `path:line`. For `find`, `decision`, `trap`, and `outcome` at least one token must resolve outside `docs/discovery/`; name the artifact that backs the claim. A `docs/discovery/` path is a self-citation: allowed as extra detail, never the only evidence. `assumption` and `question` may instead name what would settle them.
- No `|` inside a field; if a command needs one, put it in an archive detail file.
- When one line cannot carry the content within 240 characters, write `docs/discovery/archive/<id>.md`: first line `# <id>`, then the original full entry line verbatim, then prose detail. The index line keeps the load-bearing fact and one external evidence token.
- The header lists exactly the scopes in the live index; reconcile regenerates it.

## Checkpoints (When To Append)

Append when a finding passes the decision test: would this change what a future agent does or believes? Skip it when it would not, and when `git log`, the README, a spec, or a rulebook already carries it; a `[decision]` names the rationale the committed diff does not, not a restatement of the diff.

- Recon concludes with a non-obvious fact.
- A durable decision locks.
- An assumption is validated or invalidated.
- An incident is fixed.
- A trap is found.
- A build, test, or benchmark yields a noteworthy outcome.
- An open question is left for a future agent.

## Read Contract

- Grep the `docs/discovery/` directory by scope token or `[type]` when scoping a task; do not load a match unless an entry is load-bearing. Grep is the default at any size and still reaches archived entries.
- Open `docs/discovery/archive/<id>.md` by deterministic path, or a linked `capture-session` file, only when an entry is load-bearing. Ignoring irrelevant entries is the point.
- Cite an entry by its ID, not a line number, so the reference survives insertion.

## Write Contract

- The operator owns appends; subagents return candidates (finding + evidence) and never write. The context-curator is the only other agent allowed to touch the store, and only to prune, archive, or delete superseded lines.
- Assign the ID at append: `D-YYYYMMDD-NN` from today's date, the next free per-day sequence.
- Never rewrite an entry's meaning. Supersede by appending a replacement with a new ID; at reconcile, delete the superseded line; `git log -p -- docs/discovery/DISCOVERY.md` is the history.
- Evidence is required for `find`, `decision`, `trap`, and `outcome`; otherwise the entry is an `assumption` or `question`.
- Past the 8 KB cap or the 240-character line cap, move overflow to `docs/discovery/archive/<id>.md`; drop entries `git log` or the project docs already carry.

## Commit Reconcile

In an opted-in repo, before staging, the ship-changes skill reconciles the store of the repository it commits and pushes: flush unsaved findings, assign IDs, verify each evidence path resolves outside `docs/discovery/` and downgrade self-cited or unproven entries to `assumption`, dedupe and delete superseded lines rather than duplicate, regenerate the `Scope tokens:` header, move overflow into `docs/discovery/archive/<id>.md`, enforce the 240-character and 8 KB caps, keep newest first, and stage the index and any archive files with the related chunk.

## Relationship To Other Records

- `write-handoff` resumes one work thread and is overwritten; link relevant entries by ID instead of restating them.
- `capture-session` holds long topic detail and appends an index entry linking it.
- The index outlives both and links to them.

## Verify

- Any change under `docs/discovery/` passes `scripts/lint-markdown.py` from the plugin checkout.
- `scripts/check_discovery.py` passes: IDs are well-formed, unique, and date-matched; entries stay <= 240 characters; the file stays <= 8 KB; every `find`, `decision`, `trap`, and `outcome` carries external evidence outside `docs/discovery/`; the scope header matches the live scopes; and each `archive/<id>.md` heading matches its filename.
- Every self-citation and evidence path resolves with any `:line` in range.

Rationale, threats, and worked examples live in `docs/specs/2026-10-09_DiscoveryHardening.md`.
