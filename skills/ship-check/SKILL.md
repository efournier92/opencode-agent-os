---
name: ship-check
description: Run a parallel pre-ship quality gate on a feature branch. Scope the diff once, then fan out read-only reviewer agents in parallel.
license: MIT
compatibility: opencode
---

# ship-check

Runs entirely in the current agent for scoping, then fans out read-only reviewer agents in parallel.

## Role

Proves a feature branch is ship-ready by fanning out multiple review-style agents in a single parallel dispatch. The main thread scopes the diff exactly once; agents never re-derive it themselves; this keeps the fan-out cheap.

## Steps

1. Resolve inputs: which repo/service, which branch (default: current), and an optional one-line statement of intent.
2. Scope the diff once in the main thread: find the merge-base against the trunk branch, then get the file-level diff stat. Do **not** read the actual hunks in the main thread; that's each reviewer's job on its own slice.
3. Pick the reviewer roster from the file list:
   - **Always**: the active profile's `qa` (targeted checks on touched code) and the active profile's `critic` (diff vs. claimed scope/intent).
   - **Conditionally**: the compliance pre-filter (`@compliance-officer`) if any path touches migrations or other compliance-sensitive surfaces (project-specific list); the product critique agent (`@product-manager`) if a genuinely user-facing surface changed (UI code, API schema/mutations, user-visible copy/errors); the browser-QA agent via the `browser-verify` skill if the frontend changed and the local dev stack is actually reachable; one feature per dispatch.
4. Use the `task` tool to spawn every selected agent in a single message (parallel). Each prompt includes: repo, branch, base commit, file list, intent line, and an explicit "scope is pre-computed; don't re-derive it, only read the hunks/files you actually need." Agents that inherit the operator's model by design get no model override. The verification agent's prompt names the exact checks to run.
5. Aggregate one summary table: `agent | verdict | findings`. Then print findings verbatim (each reviewer already caps/terse-formats its own output). Close with exactly one line: `SHIP` (everything clean/PASS) or `HOLD: <blocking items>`.

## Constraints

- All reviewers are read-only on the branch; nothing mutates during this gate.
- Skipped agents are named explicitly with a one-phrase reason (e.g. "compliance-officer skipped: no sensitive surface touched").
- Findings are reported, never auto-fixed; fixing is always a separate, later dispatch.
- If the user wants the gate iterated until clean, suggest they set an automatic goal condition (proving command: this skill returns `SHIP`; plus a turn cap) so a cheap evaluator can keep the loop honest without burning the operator's own context.
