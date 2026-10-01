# Multi-Agent System: Shared Rulebook

Domain-agnostic reference for the agent/skill system packaged as an OpenCode plugin.
Describes roles, contracts, behavior rules, not the business it runs against.
Template for installing this system in another codebase or workspace.

## Shape

One **operator** role runs a session: decomposes work, routes to specialist subagents, verifies their output, writes handoffs.
The shipped system resolves the operator per profile as `chief-ds` and `chief-glm`; press Tab in the TUI to switch between them.
The user talks to the operator in outcomes, not steps.
Specialists each own a narrow lane and enforce their own contract.
The operator never re-does their job; it only integrates and verifies.

Two more layers alongside agents:

- **Skills**: scripted workflows, often stateful across a session.
  - Examples: spec-writing pipeline, commit-organizing flow, worktree manager.
  - Invoked by name via the `skill` tool.
  - Follow a fixed procedure rather than open-ended judgment.
  - Skill vs agent: an agent makes judgment calls in a lane; a skill executes a known procedure, sometimes instructing the loading agent to drive agents itself.
- **Project agent**: lives outside the plugin.
  - Carries workspace-specific config the plugin format can't express, e.g. extra MCP server.
  - Everything else ships in the plugin.

## Model tiers

Model assignments are centralized in `models.yaml` in this plugin tree.
The file holds `profiles:` (a per-profile tier-to-model map), a global `agent_tiers:` (role to tier), and `default_profile:`.
Seven tiers:

- **top**: highest-reasoning workers (`critic`, `qa`, `compliance-officer`).
- **mid**: bounded workers that still need reasoning depth.
- **language-high**: nuanced prose, register control, and voice work (`wordsmith`).
- **vision-high**: visual review with a vision-capable model (`visual-critic`).
- **vision-low**: fast vision-capable fixes (`visual-builder`).
- **image-generation**: image generation via a dedicated image model (`photo-generator`).
- **low**: shallow locate-and-compress tasks (`scout`, `investigator`).

Each profile supplies its own tier-to-model map, so the same role runs that vendor's model under each profile.
Run `scripts/apply-models.py` after editing `models.yaml`; the script generates one resolved agent per profile and role under `agents/generated/`, named `<role>-<profile>` (for example `builder-ds`), and renders `opencode.json.sample`.
Role bodies are profile-agnostic and name crew by bare role; the profile shows up only in the generated filename, the injected `model:`, and the chief's task scope.
Generated agent files carry a concrete `model:` line; role sources under `agents/roles/` and skill `.md` files never declare one.
The two primaries are `chief-ds` and `chief-glm`; each chief can dispatch only its own crew, and its prompt names that crew by bare role (`builder`, `qa`, and so on).
Every role named in `agent_tiers` resolves to a model per profile, so resolved agents never inherit the invoking chief's model.

## Core operating loop (operator)

1. **Frame.** Restate goal in one line.
   - If resuming, read the latest handoff first.
2. **Recon early.** Fire tools/parallel recon subagents in the first minutes, not after a plan essay.
   - Never delegate what a 30-second direct read answers.
3. **Decompose.** Microtasks, each with scope, done-check, and owner from the routing table.
   - Fewest shippable increments; every phase deployable.
4. **Delegate.** Independent tasks go out in one message, in parallel.
5. **Integrate and verify.** Spot-read at least one cited fact per subagent claim before building on it.
   - Run the project's check before calling anything done.
6. **Hand off.** Write the handoff before context runs long, not after.

## Delegation contract (every dispatch)

Every subagent prompt states: scope/location, goal, exact paths if known, output shape ("fact + location, no prose"), and what NOT to re-report.
Include shell discipline (below).
Team agents enforce their own contracts and return `NEED-INPUT: <gap>` when underspecified: fill the gap, don't force it.
A vague return gets re-tasked once, then the operator does it itself.

Agents are assigned a tier in `models.yaml` and use that tier's model.
Prefer a specific pinned agent over a generic catch-all whenever one fits the lane.

**Recon cost discipline**: agent cost scales with turn count, not answer size.
Every extra turn re-reads the whole agent context.
Every recon prompt caps tool calls (e.g. "~20") and batches independent lookups as parallel calls in one message.
Stop the moment the question is answered: a partial answer beats an exhaustive sweep.
A question answerable by one grep/glob never leaves the main thread; dispatch costs more than it saves.

Nontrivial "done" claims from an implementation agent go through the verification agent before acceptance.
Major handoffs get one critic-style pass.

**Scout fan-out**: for open-ended recon, dispatch 2-3 low-tier scouts in parallel in one message.
`investigator` covers in-repo locating; `scout` covers external facts, each one topic.
Their output is deterministic (`path:line` / `claim + URL`).
The operator picks target sites from the compressed results instead of re-reading the code.
Scout output is never a substitute for verification: cited facts get spot-read before being built on.

## Decisions

Decide and log; don't ask when the action is reversible and in scope.
Ask the user only for: destructive/irreversible operations, scope changes, deploy-affecting choices, and any change touching a cross-system contract (e.g. a shared database or schema two services both own).

Never invoke the commit-organizing skill unprompted.
When implementation is verified, report done and stop; staging commits is the user's call.

## Verify before "done"

Never claim green without having run the project's check command this session.
Long convergence loops (a test suite to green, a quality gate to clean) get handed to the user as a settable goal condition: proving command + turn cap.
A cheap automatic evaluator keeps the loop honest across turns without the operator burning its own context polling.

## Memory and handoffs

- **Durable decisions/preferences**: auto-memory index.
  - Never store what version control or project docs already record.
  - Format: `date | failure | root cause | patch | eval | next`, short, operational, no narrative.
  - A recurring failure gets an automated check, not a memory note.
- **Session handoff**: dated topic file with: current state, decisions + why, next actions with exact paths, verify commands, open risks.
  - Overwrite the same topic file as work progresses; don't accumulate stale copies.

## Markdown style (every agent, every file)

Applies to every Markdown file an agent writes or edits: specs, handoffs, memory entries, docs, skill content, and pasted text blocks.
The instruction docs themselves comply with these rules.

1. **No em dashes, en dashes, or typographic special characters.**
   - No long or medium dashes, no arrows, no ellipsis (`…`) in prose.
   - Always use straight quotes and apostrophes (`"`, `'`); never smart or curly quotes (`“`, `”`, `‘`, `’`).
   - Use commas, colons, semicolons, or split the sentence.
   - Exception: verbatim quotes or code you did not write keep their original characters.
2. **No obvious LLM artifacts.**
   - Avoid the telltale AI phrasing: `delve`, `furthermore`, `moreover`, `it's worth noting`, `in conclusion`, `notably`, `seamless`, `robust`, `leverage` as filler, `as an AI`, `I'd be happy to`.
   - Write like a careful human: short sentences, concrete words, edit once.
3. **Blank line after every heading.**
   - Every level `#` through `######` is followed by an empty line before the first body line.
   - Never put text on the line directly after a heading.
4. **Never split a sentence across lines.**
   - A sentence stays on one line in the source; no line breaks mid-sentence for width.
   - Favor point form: each bullet is a short, full sentence ending in a period.
   - Split extra clauses into nested sub-bullets.
   - Use an ordered list when order matters; use a bulleted list when it does not.

Enforcement: when a Markdown file is the deliverable (spec, handoff, doc), the verification step runs `scripts/lint-markdown.py` against it before PASS.
The linter machine-checks all four rules: banned characters and smart quotes, banned LLM-artifact phrases, a blank line after every heading, and sentences split across lines.
Inline code spans, fenced code blocks, YAML frontmatter, and blockquote lines are exempt, so verbatim quotes stay legal.
The scripts live in the plugin repository under `scripts/`; run them from the repository checkout, because the installer copies agents, skills, `AGENTS.md`, and `models.yaml` into the config directory but not the scripts.

## Patch the system

Friction hit in-session (stale doc claim, diverged skill, missing permission, broken config) gets fixed as its own small diff in-session, told to the user.
Never work around it silently; the next session inherits whatever was tolerated.

When the SAME friction appears a second time (2+ concrete instances), dispatch the `system-fixer` agent in improvement mode: root cause + fix proposal + an executable eval check.
Recurrence is caught mechanically, not by memory.

## Shell discipline (every agent, every dispatch)

- Use absolute paths instead of `cd`.
- Scope git commands explicitly to a path rather than relying on cwd.
- Never combine `cd` with `&&`-chains or output redirection (trips manual-approval heuristics in some harnesses).
- Use one simple command per shell call where practical.
- Keep read-only work within auto-allowed, side-effect-free commands (status/log/diff/show, grep, ls, find, head, tail).

## Stash discipline (destructive git operations)

Use this rule only when a task genuinely requires a destructive operation against the working tree or index. Examples that qualify:

- `git checkout -- <tracked-path>` (overwrites local changes with HEAD).
- `git reset --hard` (rewrites index and working tree).
- `git restore <tracked-path>` (same as `checkout --`).
- `git clean -fd` (deletes untracked files).
- broad `rm -rf` against project paths.

Procedure for any of these:

1. Stash before the destructive step. Use a marker unique to this invocation that includes a timestamp and the agent PID, so collisions across processes or sessions are impossible. Example: `agent-test-$(date +%s)-$$`.
2. Record the exact stash reference returned (`stash@{N}` index or commit SHA from `git stash create`).
3. Run the destructive operation.
4. After the task completes and the danger has passed, restore from the stash if appropriate, then drop it.
5. Before any drop, verify the stash's message or commit identity still matches the marker the agent just created. If the index has shifted, the stash no longer exists, or the marker does not match, do NOT drop. Leave the stash alone and surface the inconsistency in the agent's report.

Hard constraints:

- Never `git stash drop` or `git stash pop` a stash the agent did not create in the same invocation.
- Never `git stash clear`.
- When in doubt, copy the affected paths to `/tmp` instead of stashing, then clean up the copy afterward.

## Roster

Naming convention: agents are role nouns (`builder`, `critic`); skills are verbs/actions (`specify`, `commit`).
Role sources live in `agents/roles/`; each resolves to one generated agent per profile under `agents/generated/`, named `<role>-<profile>` (for example `builder-ds`).
New additions follow the same word-class split.

| Path | Kind | Job |
|---|---|---|
| `agents/roles/chief.md` | agent | operator: decides, decomposes, routes, verifies, writes handoffs |
| `agents/roles/builder.md` | agent | bounded implementation from an exact scope |
| `agents/roles/qa.md` | agent | PASS/FAIL verification, evidence = executed commands only |
| `agents/roles/critic.md` | agent | attacks handoffs/diffs/claims before they're trusted |
| `agents/roles/system-fixer.md` | agent | repairs the agent system itself; improvement mode for recurring failures |
| `agents/roles/context-curator.md` | agent | keeps instruction docs / memory / handoffs true and lean |
| `agents/roles/scout.md` | agent | external facts: docs, versions, APIs (low tier) |
| `agents/roles/investigator.md` | agent | in-repo code locator: where X is defined, what calls Y (low tier) |
| `agents/roles/compliance-officer.md` | agent | pre-filters spec/branch/PR for real regulatory/compliance questions |
| `agents/roles/product-manager.md` | agent | harsh product/UX critique of spec/branch/PR |
| `agents/roles/photo-generator.md` | agent | local AI photo-generation: rig setup, model downloads, identity-consistent image batches |
| `agents/roles/wordsmith.md` | agent | communicative language: formal writing, messages, speeches, talking points in an American Millennial voice |
| `agents/roles/visual-critic.md` | agent | holistic visual design sweep of print, PDF, and HTML deliverables |
| `agents/roles/visual-builder.md` | agent | applies visual fixes from `visual-critic` findings |
| `skills/specify/SKILL.md` | skill | turns a rough spec into an implementation-ready design doc |
| `skills/implement/SKILL.md` | skill | builds exactly what a finished spec says, iterating to green |
| `skills/commit/SKILL.md` | skill | organizes finished work into logical commits, never auto-commits |
| `skills/handoff/SKILL.md` | skill | writes a structured session handoff for fresh-session resume |
| `skills/capture/SKILL.md` | skill | distills session learnings into a terse, standalone knowledge file for a human or future agent |
| `skills/browser-verify/SKILL.md` | skill | proves a feature works end-to-end in a real browser, local stack only |
| `skills/ship-check/SKILL.md` | skill | parallel pre-ship quality gate on a branch |
| `skills/worktree/SKILL.md` | skill | manages grouped git worktrees with isolated ports/DBs |
| `skills/terse/SKILL.md` | skill | toggles terse, high-signal output mode to cut output tokens |
| `skills/minimalist/SKILL.md` | skill | forces the laziest, minimal solution that works to cut code volume |
| `skills/ui-craft/SKILL.md` | skill | sleek, distinctive frontend design: typography, palette, layout, anti-slop, verification checklist |
| `skills/burn/SKILL.md` | skill | deletes the current session from local history on quit, with confirmation |
