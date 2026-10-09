# Multi-Agent Operating System For OpenCode

## Purpose

- A suite of agents and skills built for [OpenCode](https://opencode.ai/) TUI.

## Features

- Centralized per-role model config: each profile pins a concrete model per seat
  - *See `models.yaml`.*
- Progressive Discovery: an opt-in, per-repo `docs/discovery/` index so a future agent finds relevant findings cheaply and ignores the rest.

## Installation

### Overview

- See [`INSTALL.md`](INSTALL.md) for step-by-step instructions, meant for an agent to execute.
- For the common case, run `scripts/install.sh`.
- **Supports:**
  - Global install *(recommended for personal use)*.
  - Per-project install *(team-shared, in a repo).*

### Quick Global Install

From the plugin checkout:

```bash
scripts/install.sh
```

It backs up what it replaces, installs the generated agents, skills, commands, and rulebook, seeds `models.yaml` and the config on a fresh machine, and sets the TUI keybinds so agent switching is on `shift+tab` (only when those keys are unset).
See [`INSTALL.md`](INSTALL.md) for the manual steps and the per-project install.

### Verify

1. **Run `/agents` in the OpenCode TUI**
    - Expect all primaries and their crews: `chief-ds`, `chief-glm`, `chief-ds+glm`, and each `<role>-<profile>` subagent *(`builder-ds`, `verifier-ds+glm`, etc).*
2. The `skill` tool description should list all 12 skills *(`create-spec`, `implement-spec`, etc).*
3. Typing `/engineer-prompt` in the TUI autocompletes the command.

## Contents

### `AGENTS.md`

- Always-loaded core rulebook *(cross-cutting contracts: delegation, decisions, verify, markdown, shell)*.
- Operator-only detail lives in `agents/roles/chief.md`; phase and reference detail lives in `docs/rulebook/`, read on demand.
- Install to either:
  - `~/.config/opencode/AGENTS.md` *(global)*.
  - `<project-root>/AGENTS.md` *(per-project)*.

### `INSTALL.md`

- Agent-oriented install guide for global and per-project setups.

### `docs/discovery/`

- Opt-in per repository: a repo enables discovery by containing this directory, and only inside a git working tree.
- The index `docs/discovery/DISCOVERY.md` holds one line per finding, decision, assumption, trap, question, or outcome, each with evidence.
- Grep it by scope token or `[type]` when scoping a task; open a linked detail file only when an entry is load-bearing.
- The operator appends at checkpoints; the ship-changes skill reconciles and commits it. Without the directory, the practice is skipped and nothing is created or read. See Progressive Discovery in `AGENTS.md`.

### `docs/rulebook/`

- On-demand reference split out of `AGENTS.md` and `chief.md` to keep the always-loaded pair under the context budget.
- `roster.md` is the full agent and skill catalog; `model-profiles.md` is the profile and generator contract; `markdown-style.md` is the full Markdown style rules; `stash-discipline.md` is the procedure for destructive git operations.
- `scripts/install.sh` ships this directory beside the installed `AGENTS.md`.

### `models.yaml`

- Single source of truth for profiles and the concrete model each one pins per role.
  - *One `roles:` map per profile; each role maps directly to a concrete model id.*

### `scripts/apply-models.py`

- Resolves `models.yaml` into one generated agent per profile under `agents/generated/`, named `<role>-<prefix>` (for example `builder-ds`).
- Renders `opencode.json.sample` and strips any stray `model:` line from role frontmatter; fails loud if a skill file ever grows one.

### `scripts/install.sh`

- Installs generated agents, skills, commands, the rulebook, and the TUI keybinds into the OpenCode config dir, with a timestamped backup.
- Overwrites plugin-owned agents, skills, commands, and rulebook; keeps an existing `models.yaml` and any user command files.
- Merges only the plugin-managed config keys into an existing `opencode.json`/`opencode.jsonc`, overriding those and preserving every other key; seeds the sample on a fresh install; sets keybinds only when unset.

### `scripts/release.sh`

- Tags a release with today's date (`YYYY-MM-DD`) and pushes the branch and tag.
- Re-running the same day moves that day's tag to the new `HEAD`; other dates are never touched.

### `scripts/check.sh`

- Single plugin check: context size budget, the unit suite, and the markdown linter.
- Wired into `.githooks/pre-commit` *(enable with `git config core.hooksPath .githooks`)* and `.github/workflows/check.yml`.

### `scripts/test_doc_budget.py`

- Enforces the Context Size Budget in `AGENTS.md`: a 200-line and 16 KB cap on `agents/roles/*.md`, `agents/generated/*.md`, and `skills/*/SKILL.md`, a tighter 120-line and 10 KB cap on the always-loaded `AGENTS.md` and `agents/roles/chief.md`, plus skill sibling-reference and relative-link checks.

### `opencode.json.sample`

- Sample global config: `chief-ds+glm` as default agent, the default model, the built-in `build` and `scout` agents disabled, `subagent_depth: 2`, `compaction.prune: true`, and `/tmp/*` allowed without an approval prompt.
- The installer merges the plugin-managed keys from this sample into an existing config; see Managed Config Keys in `INSTALL.md`.

### `agents/`

- Role sources live in `agents/roles/` *(markdown + YAML frontmatter)*.
- `scripts/apply-models.py` renders each role into one generated agent per profile under `agents/generated/`, named `<role>-<prefix>` (for example `builder-ds`).

| Role | Mode | Description |
|---|---|---|
| `chief` | primary | Operator agent that decides, decomposes, routes work to specialists, verifies output, and writes handoffs. |
| `builder` | subagent | Bounded implementation worker for a well-specified task with a clear done-check. |
| `verifier` | subagent | PASS/FAIL verification agent that proves claims by executing commands; read-only on code. |
| `claim-critic` | subagent | Red-team reviewer that attacks handoffs, plans, diffs, and claims for fake progress before they are trusted. |
| `system-fixer` | subagent | Repairs the agent system itself (configs, hooks, instruction docs) and runs improvement mode for recurring failures. |
| `context-curator` | subagent | Hygiene agent for instruction docs, memory index, handoffs, and the discovery index; keeps context lean and claims true. |
| `external-researcher` | subagent | Cheap external-research agent for docs, versions, APIs, and changelogs outside the codebase. |
| `code-locator` | subagent | Cheap read-only in-repo code locator that finds where symbols are defined and what calls them, with compressed deterministic output. |
| `compliance-officer` | subagent | Pre-filters specs, branches, and PRs for regulatory/legal/fiduciary/privacy questions worth a human compliance officer's time. |
| `product-critic` | subagent | Harsh product/UX critique of specs, branches, and PRs from the user's perspective. |
| `photo-generator` | subagent | AI photo-generation specialist: sets up a ComfyUI/SDXL rig or a hosted image API, downloads models, produces identity-consistent artistic images via scripted runners. |
| `wordsmith` | subagent | Communicative-language specialist: formal writing, messages, speeches, talking points in an American Millennial voice. |
| `phraser` | subagent | Riffing partner: returns distinct, ranked ways to say a phrase, sentiment, or sentence, with the top pick flagged. |
| `visual-critic` | subagent | Holistic visual design sweep of print, PDF, and HTML deliverables. |
| `visual-builder` | subagent | Applies visual fixes from `visual-critic` findings. |

*Mode ships with each role. Each profile injects a concrete model per role from `models.yaml` (see Model Profiles); the primaries are `chief-ds`, `chief-glm`, and `chief-ds+glm`.*

### `skills/` (12 Skills)

- 1 directory per skill, each with a `SKILL.md` inside, capped at 200 lines; detail moves to sibling files.

| Skill | Description |
|---|---|
| `create-spec` | Turn a rough design sketch into an implementation-ready spec document. |
| `implement-spec` | Build exactly what a finished design spec says and iterate to a green test suite. |
| `ship-changes` | Chunk unstaged work into logical commits and push; per-commit review by default, one pre-flight approval then unattended on an explicit autonomy cue. |
| `write-handoff` | Write a structured session handoff so a fresh session resumes without re-exploring. |
| `capture-session` | Distill session learnings into a terse, standalone knowledge file for a human or future agent. |
| `log-discoveries` | Maintain the opted-in `docs/discovery/DISCOVERY.md` index of durable findings, decisions, traps, and outcomes. |
| `verify-in-browser` | Prove a feature works end-to-end in a real browser against the local dev stack only. |
| `manage-worktrees` | Create, list, or remove grouped git worktrees across repos, each with isolated ports and its own database. |
| `tighten-prose` | Toggle terse, high-signal output (loads on "terse"): cut filler while keeping technical facts exact. |
| `simplify-code` | Force the laziest, minimal solution that works: cut over-engineering, reuse existing code, ship the smallest diff. |
| `polish-ui` | Sleek, distinctive frontend design guidance: typography, palette, layout, and anti-AI-slop checks. |
| `burn-session` | Delete the current session from local history once you quit, after confirming. Session-only. |

### `commands/` (2 Commands)

- User-invoked slash commands. Unlike a skill, a command adds no model context until you type it.

| Command | Description |
|---|---|
| `/engineer-prompt` | Turn a messy idea into a destination-shaped, grounded, verifiable prompt. |
| `/fix-bug` | Reproduce a bug, fix it red-green, and prove the fix. |

## Releases

Releases are marked with a date tag, `YYYY-MM-DD` (for example `2026-10-01`).

- Cut one with `scripts/release.sh`.
- It tags the current `HEAD` and pushes the branch and the tag.
- One release per day: running it again the same day moves that day's tag to the new `HEAD`, replacing the earlier tag locally and on `origin`. Tags for other dates are never touched.

## Model Profiles

### Configure

All model assignments are driven by `models.yaml`.
The file holds `profiles:` (each with a `roles:` map of role name to concrete model id) and `default_profile:`.
The generator renders that file into one agent per profile under `agents/generated/` and into `opencode.json.sample`, which is the JSON config OpenCode actually reads at runtime.
Role sources under `agents/roles/` and skill `.md` files never declare a `model:` line; doing so would shadow the generated config and break this single-source-of-truth architecture.

```yaml
default_profile: ds+glm

profiles:
  ds:
    label: DeepSeek
    roles:
      chief: deepseek/deepseek-flash
      verifier: deepseek/deepseek-flash
      claim-critic: deepseek/deepseek-flash
      ...
  glm:
    label: GLM
    roles:
      chief: zai-coding-plan/glm-5.3
      external-researcher: zai-coding-plan/glm-5.3-flash
      ...
  ds+glm:
    label: DeepSeek + GLM hybrid
    roles:
      chief: deepseek/deepseek-flash
      claim-critic: zai-coding-plan/glm-5.3
      compliance-officer: zai-coding-plan/glm-5.3
      verifier: zai-coding-plan/glm-5.3-flash
      product-critic: deepseek/deepseek-flash
      wordsmith: zai-coding-plan/glm-5.3
      phraser: zai-coding-plan/glm-5.3-flash
      visual-critic: zai-coding-plan/glm-5.3-flash
      builder: deepseek/deepseek-flash
      ...
```

*The shipped default profile is `ds+glm` (chief agent `chief-ds+glm`, prettified to Chief-Ds+Glm in the TUI): DeepSeek carries the many-turn and coding seats on pay-as-you-go pricing, GLM 5.3 is kept for the low-volume, high-stakes text gates and long-form language, and glm-5.3-flash covers the seats where GLM's independent eyes matter but volume or vision rules out the flagship. The primaries are `chief-ds`, `chief-glm`, and `chief-ds+glm`.*

### Update

To change model IDs, add a profile, or move a role to a different model, edit `models.yaml` and run:

```bash
python3 scripts/apply-models.py
```

The script regenerates `agents/generated/*.md` and `opencode.json.sample`; reinstall the generated agents and re-run the installer, which merges the plugin-managed keys into your existing `opencode.json` or `opencode.jsonc`.
Role sources are touched only to strip a stray `model:` line from frontmatter; no other modification.

