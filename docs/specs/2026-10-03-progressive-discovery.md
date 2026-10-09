# Progressive Discovery: A Committed, Indexed Discovery Record For Every Workspace

> Note: this spec's lifecycle, evidence, archive, and read-contract rules are superseded by `docs/specs/2026-10-09_DiscoveryHardening.md`; the rest is historical.

Branch context: `main`. Builds on the current plugin state (dual-chief architecture, 14 roles, 12 skills before this work). This spec adds one opt-in, per-repo artifact, one on-demand skill, and one gate rule. It adds no agent.

## Context And Motivation

- Product management's "continuous discovery" premise (Teresa Torres): teams that continuously make build decisions must stay continuously connected to current reality, capturing opportunities and assumptions at a regular cadence instead of trusting stale memory.
  - Source: https://www.producttalk.org/continuous-discovery/ (practitioner framework; the keystone-habit causal claim is self-labeled unproven at https://www.producttalk.org/keystone-habit/).
- An LLM agent's context is finite and costly, and retrieval accuracy falls as input grows even when the needed fact is present.
  - Sources: Anthropic context engineering, just-in-time retrieval (https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); Chroma context rot (https://research.trychroma.com/context-rot); Lost in the Middle (https://arxiv.org/abs/2307.03172).
- The proven patterns this borrows: architecture decision records (atomic, in-repo, superseded not edited, https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions), docs-as-code (https://www.writethedocs.org/guide/docs-as-code/), and index-versus-content agent memory (https://docs.anthropic.com/en/docs/claude-code/memory).
- The plugin today captures knowledge only on demand (`capture`) and resume state per thread (`handoff`). Nothing accumulates atomic findings across sessions in one cheap-to-scan place.
- Result of the gap: a fresh agent re-explores known facts, repeats known traps, and acts on stale assumptions.

## Glossary

- Discovery entry: one grep-friendly line recording a fact, decision, assumption, trap, question, or outcome, with evidence.
- Discovery index: the committed file `docs/discovery/DISCOVERY.md` in an opted-in repository, holding every entry.
- Detail file: an optional `capture` knowledge file linked from an entry when one line is not enough.
- Checkpoint: a moment the operator appends an entry (recon done, decision locked, incident fixed, assumption validated, verify run, open question left).
- Reconcile: the commit skill's sweep that verifies, dedupes, supersedes, syncs, and stages discovery.
- Supersede: mark an existing entry outdated and append a replacement, rather than editing history.

## Current State

- `AGENTS.md` (Core Operating Loop, Memory And Handoffs) defines handoffs and an auto-memory index, but no workspace-level discovery record.
- `skills/capture/SKILL.md:14` defines capture as topic-oriented and user-invoked; its files accumulate.
- `skills/handoff/SKILL.md:21` defines handoff as resume-oriented, one file per thread, overwritten in place.
- `agents/roles/context-curator.md:27` and `:30` patrol the memory directory and handoffs, with no discovery index in its beat.
- `agents/roles/scout.md:35` and `agents/roles/investigator.md:27` return deterministic, evidenced findings but have no standard promotion path into durable memory.
- No discovery index or findings directory existed in the workspace before this work (verified: repository tree).

## Goals

- One committed discovery index per opted-in repository that survives handoffs and is cheap to scan.
- Entries are one line, tagged, evidenced, and selectable by scope and type.
- The operator appends at checkpoints; the commit skill reconciles and stages discovery with the relevant commit.
- A future agent reads the index when scoping a task, filters, and opens a detail file only when an entry is load-bearing.
- Subagents surface discovery candidates without editing the index; the operator owns appends, and only the context-curator may otherwise prune or archive.
- The context-curator keeps the index lean and true.

## Non-Goals

- No new agent role.
- No per-entry machine format, database, or runtime plugin.
- No replacement for `handoff` or `capture`; discovery links to them.
- No cross-project or global index; v1 is one per opted-in repository.
- No auto-create: a repository opts in by containing `docs/discovery/`; without it the practice is skipped entirely.
- No discovery outside a git working tree; the practice bypasses non-git trees.
- No background writes; entries are agent actions, never a daemon.

## Prerequisites

- None. Pure Markdown and rulebook changes; works with any profile.

## Design Principles

- Index, not content: the index line must be enough to decide whether to read more.
- Evidence or it does not happen: every fact carries a location; unproven belief is an assumption, not a finding.
- Append and supersede: history is never rewritten; reality changes are new lines.
- Progressive disclosure: one file always read, detail read on demand.
- Single writer: the operator owns the index; subagents propose.
- Opt-in and rulebook economy: discovery costs nothing in a repo without `docs/discovery/`, and the always-loaded rule in `AGENTS.md` is the self-sufficient minimum; rationale and examples stay out of the always-loaded file.
- Commit is the lock-in: settled, verified, reviewable, committed with the work.

## Required Changes

### 1. The Discovery Index

- Opt-in marker: a repository opts in by containing a `docs/discovery/` directory. No directory means discovery is skipped entirely: read nothing, create nothing, write nothing.
- Path: `docs/discovery/DISCOVERY.md` inside the opted-in repository, committed there. Setup is deliberate and never automatic.
- Git only: the durable record is committed, so the practice applies solely inside a git working tree. Outside one, in a bare repo, or on a tree with no commits, bypass it and fall back to `capture` only if a standalone note is genuinely needed.
- Reading rule: within an opted-in repository, use its `docs/discovery/DISCOVERY.md`. A linked worktree and a submodule each use their own toplevel and their own marker.
- Structure, newest first by date (within a day, order is not significant):

```markdown
# Discovery

Findings, decisions, assumptions, traps, questions, and outcomes for this repository. One line per entry. Detail files are linked, not inlined. Newest first. Evidence required.

## Entries

- 2026-10-03 | [decision] | plugin/discovery | Index is one line per entry; detail loads on demand | docs/specs/2026-10-03-progressive-discovery.md
- 2026-10-03 | [find] | api/auth | Token refresh drops scopes on retry | src/auth/refresh.py:88
- 2026-10-03 | [trap] | plugin/commit | Commit skill never runs unless the user invokes it | skills/commit/SKILL.md:10
```

- Line format: `- YYYY-MM-DD | [<type>] | <scope> | <one-line finding> | <evidence>`.
- `<type>` is one of `find`, `decision`, `assumption`, `trap`, `question`, `outcome`.
- `<scope>` is a lowercase slash token naming the subsystem, with no spaces (for example `api/auth`, `plugin/skills`).
- `<evidence>` is a `path:line`, a URL, or the exact command and its result; `[question]` and `[assumption]` may instead name what would settle them.
- Fields contain no `|`; if a command needs one, link a detail file instead.
- A short entry is self-contained. When one line cannot carry it, write a `capture` file and append a link to it on the entry.

### 2. Entry Lifecycle

- Append only; never edit an entry's meaning.
- Supersede: append a replacement and mark the old line ` | superseded YYYY-MM-DD`. Never delete a superseded line until the curator prunes it.
- Evidence required: `[find]`, `[decision]`, `[trap]`, and `[outcome]` carry a location or command; otherwise downgrade to `[assumption]`.
- Prune: the context-curator removes or archives entries whose subject has shipped and which are re-derivable, and compresses settled history.
- Size cap: the index stays under roughly 100 lines; crossing it triggers a curator sweep that archives settled entries into a linked detail file or drops re-derivable ones.

### 3. Write Contract (Operator And Subagents)

- The operator owns appends to `docs/discovery/DISCOVERY.md`; it writes at checkpoints and during the commit reconcile. The context-curator is the only other agent permitted to touch the file, and only to prune, archive, or annotate `superseded`.
- Checkpoints: recon concludes with a non-obvious fact; a durable decision is locked; an assumption is validated or invalidated; an incident is fixed; a trap is found; a build, test, or benchmark yields a noteworthy outcome; an open question is left for a future agent.
- Skip when the finding is re-derivable by one grep or read, already recorded in project docs or version control, or trivial.
- Subagents (`scout`, `investigator`, `qa`, `critic`, `builder`) return findings in their existing evidence shape; the operator promotes relevant ones. Subagents never edit the index.
- The delegation contract in `AGENTS.md` gains one line: a recon or verification return may name a discovery candidate, and the operator decides what is promoted.

### 4. Read Contract (Every Agent)

- In an opted-in repo, when scoping a task, grep `docs/discovery/DISCOVERY.md` for the scope token or `[type]` before dispatching recon; load the full file only when it is small (under roughly 60 lines) or an entry is load-bearing.
- Filter by the same grep; open a linked detail file or `capture` file only when an entry is load-bearing.
- Ignore entries outside the task's scope by design; the one-line-per-entry index exists so this filter is cheap.

### 5. Skill And Role Hooks

- `skills/progressive-discovery`: the on-demand home of the full convention (index format, checkpoints, read/write contract, lifecycle). `AGENTS.md` keeps only a short opt-in gate pointing to it, so the always-loaded rule shrinks and the detail loads only when discovery is used.
- `skills/capture`: after writing a knowledge file, append a discovery entry linking it.
- `skills/handoff`: run a discovery reconcile-ready pass; the handoff links relevant entries rather than restating them.
- `skills/specify`: read the discovery index during Phase 1 explore; cite relevant entries as grounded facts.
- `skills/implement`: read relevant entries before building; surface outcomes and traps as candidates for the operator to promote.
- `skills/commit`: run the reconcile sweep (section 6) before staging.
- `agents/roles/chief.md`: add the append and read behavior plus a routing-table row for the index.
- `agents/roles/context-curator.md`: add the index to its beat; patrol rot, duplicates, growth, and unsuperseded staleness.
- `agents/roles/scout.md` and `agents/roles/investigator.md`: state that a caller may promote their findings to discovery entries.
- `agents/roles/system-fixer.md`: a recurring failure chosen for improvement mode gets a discovery entry recording the pattern and its detector.

### 6. Commit Reconcile Sweep

Before staging any chunk, the commit skill:

1. Flushes session findings not yet in the index.
2. Verifies each new entry has evidence; downgrades unproven to `[assumption]` or drops it.
3. Dedupes against existing entries and supersedes rather than duplicates.
4. Syncs order and the header; keeps newest first.
5. Stages that repository's `docs/discovery/DISCOVERY.md` and any linked detail files with the logically related chunk, or as a final docs chunk when discovery spans the work.
6. Reports entries added or superseded. Makes no change when nothing non-rederivable was learned.

The sweep never commits; like the rest of the commit skill, it stages and waits.

## UI Requirements

- None. No TUI, web, or rendered surface changes. The artifact is plain committed Markdown.

## Production Risks And Mitigations

- Index read cost: a mature index is large, and the operator re-reads its context every turn. Mitigation: grep by scope token by default and load the full file only when it is small or an entry is load-bearing.
- Index bloat: entries accrete. Mitigation: the size cap plus the curator sweep; settled entries archive or drop.
- Low-signal noise: checkpoint discipline may over-capture. Mitigation: the skip rule and the evidence bar; the commit sweep downgrades or drops.
- Concurrent writes: parallel sessions or worktrees editing one file conflict. Mitigation: append-only lines and newest-first insertion reduce conflict; the curator resolves. This stays an open risk (see Open Questions).
- Uncommitted loss: findings in a session that never commits can be lost. Mitigation: append during work, not only at commit; handoff links entries.
- Rediscovery cost: a future agent may ignore the index. Mitigation: the read contract puts it in the scoping step.
- Divergence from `capture`: two knowledge mechanisms could drift. Mitigation: discovery links to capture, and capture appends the index entry.

## Rollout Plan

1. Add the Progressive Discovery section to `AGENTS.md` (loop, delegation contract, memory and handoffs).
2. Add the discovery behavior and routing row to `agents/roles/chief.md`.
3. Extend the five skills and five roles named in section 5.
4. Document the opt-in `docs/discovery/` directory in `README.md`.
5. Run the Markdown linter on every changed file.
6. Add `docs/discovery/` to this plugin repo as the worked example (the repo opts in).

## Test Plan

This is documentation, so verification is lint-based and manual, not a unit suite.

- `python3 scripts/lint-markdown.py` passes on every changed Markdown file.
- Grep assertions, run manually: each of the five skills and five roles names discovery where section 5 requires it; `AGENTS.md` gains the opt-in gate and read/write contract; `README.md` names `docs/discovery/`.
- A worked-example `docs/discovery/DISCOVERY.md` exists, passes the linter, and contains only entries that survive the skip bar.
- A critic pass checks the rules for contradiction, bloat, and a failure to be actionable.

## Summary Of Changes

- [x] `AGENTS.md` gains a short opt-in gate pointing at the `progressive-discovery` skill; the full convention lives in that on-demand skill.
- [x] `skills/progressive-discovery/SKILL.md` holds the index format, checkpoints, and read/write contract.
- [x] `agents/roles/chief.md` gains discovery behavior and a routing row.
- [x] `capture`, `handoff`, `specify`, `implement`, and `commit` skills reference discovery.
- [x] `context-curator`, `scout`, `investigator`, and `system-fixer` roles reference discovery.
- [x] `README.md` documents the opt-in `docs/discovery/`.
- [x] A worked-example `docs/discovery/DISCOVERY.md` exists for this repo.
- [x] `scripts/lint-markdown.py` clean on all changed Markdown.

## Verification Steps

Run from the repo root:

```bash
python3 scripts/lint-markdown.py AGENTS.md README.md docs/discovery/DISCOVERY.md docs/specs/2026-10-03-progressive-discovery.md agents/roles/chief.md agents/roles/context-curator.md agents/roles/scout.md agents/roles/investigator.md agents/roles/system-fixer.md skills/capture/SKILL.md skills/handoff/SKILL.md skills/specify/SKILL.md skills/implement/SKILL.md skills/commit/SKILL.md skills/progressive-discovery/SKILL.md
```

- Confirm each changed file names discovery in the required place.
- Confirm `docs/discovery/DISCOVERY.md` demonstrates the entry format with entries that survive the skip bar.

## Open Questions

- Resolved: a multi-repo workspace keeps one index per opted-in repository, and the commit skill stages the index of the repository it commits. A cross-repo finding may be recorded in each affected repository.
- Resolved: within an opted-in repository, the index is `docs/discovery/DISCOVERY.md`; a linked worktree and a submodule each opt in separately.
- Open: parallel worktrees each carry a diverging `docs/discovery/DISCOVERY.md`; top-insertion writes can conflict on merge. v1 accepts the risk and relies on the context-curator.
- Should a repo with a nested `AGENTS.md` also get a nested `docs/discovery/`, or is one per repository sufficient? v1 uses one per repository.
- Should the index rotate settled entries into an archive file automatically at the cap, or leave archiving to the curator's judgment? v1 leaves it to the curator.
