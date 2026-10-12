---
name: redteam
description: Operator-run adversarial loop that pressure-tests a goal through diverse lenses, records findings in a committed ledger, converges on evidence, and puts only human-only decisions to the user. Verb usage "redteam <goal>". Invoked by the operator.
license: MIT
compatibility: opencode
---

# Redteam

Operator-run. The operator orchestrates and is the only ledger writer; subagents return findings and candidates only.

## Role

Turns a goal into a sound, evidence-converged, safe-to-ship solution by fanning out read-only adversaries across diverse lenses, recording every finding in one committed ledger, letting agents rebut and un-ship each other, then presenting only genuinely human-only decisions. Orchestrates `create-spec`, `implement-spec`, `builder`, `verifier`, and `ship-changes`; never duplicates them.

## Caps

- Walkthrough entries: 7.
- Rounds: 3.

Past either cap, the behavior in the phases below applies; the caps are constants, not suggestions.

## Ledger Schema

Path: `docs/critique/YYYY-MM-DD_Topic.md`, one file per run, created when missing; `docs/critique/` is committed. Format, exactly:

```markdown
# Critique Ledger: <Topic>

- Goal: <one line>
- Started: YYYY-MM-DD
- Branch: <branch or none>

## Findings

- C-YYYYMMDD-NN | YYYY-MM-DD | <lens> | <severity> | <confidence> | <status> | <finding> | <evidence>
  - rebuttal | <status> | <evidence> | <text>
```

- `id` is `C-YYYYMMDD-NN`; its date part equals the `date` field.
- `lens` is one lowercase token: `security`, `scale`, `reliability`, `cost`, `abuse`, `data-integrity`, `maintainability`, `correctness`, `product`, `compliance`, `visual`, `research`.
- `severity` and `confidence` are each `high`, `medium`, or `low`.
- `status` is `open`, `addressed`, `rejected`, or `escalated`.
- `evidence` is a `path:line`, a backticked command, or a URL, and is required for every finding.
- No `|` appears inside any field. A finding line is at most 240 characters; a ledger file at most 16 KB.
- Rebuttal lines are indented two spaces, start with `rebuttal | `, and never count as findings.
- Validate with `scripts/check_critique.py`.

## Convergence Predicate

Checked by the `referee`.

- `CONVERGED` when the latest round added no new `high` severity finding, every `high` or `medium` finding is `addressed` or `rejected` with evidence, and no `research` finding is `open`.
- Otherwise `NOT-CONVERGED`, naming the blocking findings.
- The loop runs at most 3 rounds; on the cap the `referee` escalates every unresolved `high` or `medium` finding to `HUMAN` with status `escalated`.

## The Loop

Phases in order.

### Phase 0: Intake

Restate the goal in one line. Run one material question round through the `question` tool, matching `skills/create-spec/SKILL.md` Phase 2: 2-4 options per decision, recommended first, no artificial cap, free-text answer kept. Every decision the user cannot answer becomes a `research` finding with status `open` in the ledger. When the goal needs a design document, delegate design to `create-spec`.

### Phase 1: Ledger Init

Write the ledger file with the header. The operator is the only writer.

### Phase 2: Diverge

Dispatch in one parallel batch: up to 3 recon agents (`code-locator`, `external-researcher`) to kill `research` findings; N `redteamer` dispatches, each a distinct lens; the specialist critics that fit the artifact (`claim-critic`, `visual-critic`); and `builder` tasks for candidate fixes. Cap tool calls per recon dispatch (about 20). Each dispatch follows the Delegation Contract: scope, goal, exact paths, output shape, what not to re-report, shell discipline, and a `NEED-INPUT` clause. Append returned findings to the ledger with new IDs and status `open`.

### Phase 3: Rebut

Re-dispatch `redteamer`, `builder`, and `verifier` to attack the current findings and each other's findings. A contradiction between findings is settled only by a `verifier` command or a resolving evidence pointer. Record each outcome as a `rebuttal | ` line and set the parent finding's status to `addressed`, `rejected`, or `escalated`.

### Phase 4: Un-Ship

Dispatch one `redteamer` with the `maintainability` lens whose only job is deletion: name the parts of the current solution that are speculative, unearned, or removable, and record them as findings. Removable items are removed, not documented.

### Phase 5: Adjudicate

Dispatch the `referee` with the ledger path and the goal. It classifies every finding as `SETTLED` or `HUMAN`, returns a convergence verdict, and emits the walkthrough agenda.

### Phase 6: Walkthrough

Present the `referee`'s `HUMAN` agenda through the `question` tool, batched, one entry per decision, capped at 7. Each entry states the decision, the recommendation, the strongest counter-argument, and the evidence pointer, and offers `Accept recommendation` (first), `Override`, and `Dig deeper`. A `Dig deeper` answer spawns a mini round on that decision (Phases 2 to 5) before the walkthrough resumes. List `SETTLED` findings to the user in one collapsed line as "settled, veto on request"; a veto reopens the item. When the human-only set exceeds 7, fold the lowest-ranked items into trusted defaults the user can veto, and say so; never silently drop a `high` severity item.

### Phase 7: Ship Gate

Only after the user explicitly agrees with everything, offer `ship-changes` through the `question` tool. Never run it unprompted.

### Phase 8: Hand Off

Append `[decision]`, `[question]`, and `[outcome]` entries to `docs/discovery/DISCOVERY.md` by ID; link them from the handoff. Subagents only ever return candidates.

## Rules

- The operator is the only ledger writer; subagents never write it.
- Settle a contradiction by executed command or resolving pointer, never by counting opinions.
- The loop ends only when the user explicitly agrees with everything; that agreement is the only trigger for the ship gate.
