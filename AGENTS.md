# Multi-Agent System: Shared Rulebook

Domain-agnostic rules for the agent/skill system shipped as an OpenCode plugin; role behavior lives in `agents/roles/`, workflow detail in `skills/`, reference material in `docs/rulebook/`.
Read a referenced `docs/rulebook/` file with the Read tool when its rule applies; in a global install that directory is `~/.config/opencode/docs/rulebook/`, beside the installed `AGENTS.md`. Never preload them all.

## Shape

One **operator** role runs a session: it decomposes work, routes to specialist subagents, verifies output, and writes handoffs, and never re-does their work.
The operator resolves per profile as `chief-ds`, `chief-glm`, or `chief-ds+glm` (the default); its loop, dispatch tactics, and voice live in `agents/roles/chief.md`.

## Delegation Contract (Every Dispatch)

Every subagent prompt states: scope/location, goal, exact paths if known, output shape ("fact + location, no prose"), and what NOT to re-report.
Include shell discipline (below).
Subagents enforce their own contracts and return `NEED-INPUT: <gap>` when underspecified; fill the gap, do not force it.
Prefer a specific pinned agent over a generic catch-all whenever one fits the lane.

## Decisions

Decide and log; do not ask when the action is reversible and in scope.
Ask the user only for destructive or irreversible operations, scope changes, deploy-affecting choices, and any change touching a cross-system contract such as a shared schema.
Never invoke `ship-changes` unprompted.
When implementation is verified, report done and stop; committing and pushing are the user's call via `ship-changes` (never unprompted).

## Verify Before "Done"

Never claim green without having run the project's check command this session; verification evidence is executed commands, not intent.
Long convergence loops (a suite to green, a gate to clean) go to the user as a settable goal: proving command plus turn cap, and a cheap automatic evaluator keeps the loop honest without the operator polling its own context.

## Memory And Handoffs

Durable decisions and preferences go to the auto-memory index; session handoffs use the `write-handoff` skill.
The operator format for both lives in `agents/roles/chief.md`.

## Progressive Discovery

Opt-in per repository: active only where a git working tree contains `docs/discovery/`; otherwise create nothing and read nothing.
In an opted-in repo, load the `log-discoveries` skill and grep `docs/discovery/DISCOVERY.md` by scope token when scoping; the operator appends at checkpoints and subagents return candidates, never write.

## Markdown Style (Every Agent, Every File)

Applies to every Markdown file an agent writes or edits; full rules and examples live in `docs/rulebook/markdown-style.md`.
`scripts/lint-markdown.py` enforces rules 1 to 4 (no banned glyphs or smart quotes, no LLM-artifact phrases, a blank line after every heading, no sentence split across lines); run it on any Markdown deliverable before PASS.
Rule 5 is review-enforced: Capitalize Every Word In Titles And Headings.

## Patch The System

Fix friction hit in-session as its own small diff and tell the user; never work around it silently.
When the same friction appears twice, dispatch `system-fixer` in improvement mode: root cause, fix, and an executable check.

## Shell Discipline (Every Agent, Every Dispatch)

- Use absolute paths instead of `cd`.
- Scope git commands explicitly to a path, not cwd.
- Never combine `cd` with `&&`-chains or output redirection.
- One simple command per shell call where practical.
- Keep read-only work to side-effect-free commands (status/log/diff/show, grep, ls, find, head, tail).
- Use `/tmp` for scratch files; it is allowed by default and does not prompt.

## Stash Discipline (Destructive Git Operations)

Destructive working-tree or index operations (`git checkout --`, `git reset --hard`, `git restore`, `git clean -fd`, broad `rm -rf`) require the procedure in `docs/rulebook/stash-discipline.md`.
Never drop or pop a stash you did not create this invocation, never `git stash clear`, and when in doubt copy the affected paths to `/tmp` instead of stashing.

## Reference

The full agent and skill catalog and the model-profile contract live in `docs/rulebook/`; the `task` and `skill` tools list the live crew.

## Context Size Budget

Context-loaded files (`agents/roles/*.md`, `agents/generated/*.md`, `skills/*/SKILL.md`) stay at 200 lines; the always-loaded pair (`AGENTS.md`, `agents/roles/chief.md`) is held to 120.
A cap means split into an on-demand reference (`docs/rulebook/` or a skill sibling), never shrink the process it describes.
`scripts/test_doc_budget.py` enforces the caps; `scripts/check.sh` runs it with the unit suite and markdown linter.
