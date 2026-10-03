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

It backs up what it replaces, installs the generated agents, skills, and rulebook, seeds `models.yaml` and the config on a fresh machine, and sets the TUI keybinds so agent switching is on `shift+tab` (only when those keys are unset).
See [`INSTALL.md`](INSTALL.md) for the manual steps and the per-project install.

### Verify

1. **Run `/agents` in the OpenCode TUI**
    - Expect all primaries and their crews: `chief-ds`, `chief-glm`, `chief-ds+glm`, and each `<role>-<profile>` subagent *(`builder-ds`, `qa-ds+glm`, etc).*
2. The `skill` tool description should list all 13 skills *(`specify`, `implement`, etc).*

## Contents

### `AGENTS.md`

- Shared rulebook *(operating loop, delegation contract, shell discipline, roster)*.
- Install to either:
  - `~/.config/opencode/AGENTS.md` *(global)*.
  - `<project-root>/AGENTS.md` *(per-project)*.

### `INSTALL.md`

- Agent-oriented install guide for global and per-project setups.

### `docs/discovery/`

- Opt-in per repository: a repo enables discovery by containing this directory, and only inside a git working tree.
- The index `docs/discovery/DISCOVERY.md` holds one line per finding, decision, assumption, trap, question, or outcome, each with evidence.
- Grep it by scope token or `[type]` when scoping a task; open a linked detail file only when an entry is load-bearing.
- The operator appends at checkpoints; the commit skill reconciles and stages it. Without the directory, the practice is skipped and nothing is created or read. See Progressive Discovery in `AGENTS.md`.

### `models.yaml`

- Single source of truth for profiles and the concrete model each one pins per role.
  - *One `roles:` map per profile; no tier indirection.*

### `scripts/apply-models.py`

- Resolves `models.yaml` into one generated agent per profile under `agents/generated/`, named `<role>-<prefix>` (for example `builder-ds`).
- Renders `opencode.json.sample` and strips any stray `model:` line from role frontmatter; fails loud if a skill file ever grows one.

### `scripts/install.sh`

- Installs generated agents, skills, the rulebook, and the TUI keybinds into the OpenCode config dir, with a timestamped backup.
- Overwrites plugin-owned agents, skills, and rulebook; keeps an existing `models.yaml`.
- Merges only the plugin-managed config keys into an existing `opencode.json`/`opencode.jsonc`, overriding those and preserving every other key; seeds the sample on a fresh install; sets keybinds only when unset.

### `scripts/release.sh`

- Tags a release with today's date (`YYYY-MM-DD`) and pushes the branch and tag.
- Re-running the same day moves that day's tag to the new `HEAD`; other dates are never touched.

### `opencode.json.sample`

- Sample global config: `chief-ds+glm` as default agent, the default model, the built-in `build` and `scout` agents disabled, `subagent_depth: 2`, and `compaction.prune: true`.
- The installer merges the plugin-managed keys from this sample into an existing config; see Managed Config Keys in `INSTALL.md`.

### `agents/`

- Role sources live in `agents/roles/` *(markdown + YAML frontmatter)*.
- `scripts/apply-models.py` renders each role into one generated agent per profile under `agents/generated/`, named `<role>-<prefix>` (for example `builder-ds`).

| Role | Mode | Description |
|---|---|---|
| `chief` | primary | Operator agent that decides, decomposes, routes work to specialists, verifies output, and writes handoffs. |
| `builder` | subagent | Bounded implementation worker for a well-specified task with a clear done-check. |
| `qa` | subagent | PASS/FAIL verification agent that proves claims by executing commands; read-only on code. |
| `critic` | subagent | Red-team reviewer that attacks handoffs, plans, diffs, and claims for fake progress before they are trusted. |
| `system-fixer` | subagent | Repairs the agent system itself (configs, hooks, instruction docs) and runs improvement mode for recurring failures. |
| `context-curator` | subagent | Hygiene agent for instruction docs, memory index, handoffs, and the discovery index; keeps context lean and claims true. |
| `scout` | subagent | Cheap external-research agent for docs, versions, APIs, and changelogs outside the codebase. |
| `investigator` | subagent | Cheap read-only in-repo code locator that finds where symbols are defined and what calls them, with compressed deterministic output. |
| `compliance-officer` | subagent | Pre-filters specs, branches, and PRs for regulatory/legal/fiduciary/privacy questions worth a human compliance officer's time. |
| `product-manager` | subagent | Harsh product/UX critique of specs, branches, and PRs from the user's perspective. |
| `photo-generator` | subagent | Local AI photo-generation specialist: sets up a ComfyUI/SDXL rig, downloads models, produces identity-consistent artistic images via scripted runners. |
| `wordsmith` | subagent | Communicative-language specialist: formal writing, messages, speeches, talking points in an American Millennial voice. |
| `visual-critic` | subagent | Holistic visual design sweep of print, PDF, and HTML deliverables. |
| `visual-builder` | subagent | Applies visual fixes from `visual-critic` findings. |

*Mode ships with each role. Each profile injects a concrete model per role from `models.yaml` (see Model Profiles); the primaries are `chief-ds`, `chief-glm`, and `chief-ds+glm`.*

### `skills/` (13 Skills)

- 1 directory per skill, each with with a `SKILL.md` inside.

| Skill | Description |
|---|---|
| `specify` | Turn a rough design sketch into an implementation-ready spec document. |
| `implement` | Build exactly what a finished design spec says and iterate to a green test suite. |
| `commit` | Organize already-completed work into logical commits: stages chunks and suggests messages, never commits. |
| `handoff` | Write a structured session handoff so a fresh session resumes without re-exploring. |
| `capture` | Distill session learnings into a terse, standalone knowledge file for a human or future agent. |
| `progressive-discovery` | Maintain the opted-in `docs/discovery/DISCOVERY.md` index of durable findings, decisions, traps, and outcomes. |
| `browser-verify` | Prove a feature works end-to-end in a real browser against the local dev stack only. |
| `ship-check` | Run a parallel pre-ship quality gate on a feature branch with read-only reviewers. |
| `worktree` | Create, list, or remove grouped git worktrees across repos, each with isolated ports and its own database. |
| `terse` | Toggle terse, high-signal output: cut filler while keeping technical facts exact. |
| `minimalist` | Force the laziest, minimal solution that works: cut over-engineering, reuse existing code, ship the smallest diff. |
| `ui-craft` | Sleek, distinctive frontend design guidance: typography, palette, layout, and anti-AI-slop checks. |
| `burn` | Delete the current session from local history once you quit, after confirming. Session-only. |

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
      qa: deepseek/deepseek-v4-pro
      critic: deepseek/deepseek-v4-pro
      ...
  glm:
    label: GLM
    roles:
      chief: zai-coding-plan/glm-5.3
      scout: zai-coding-plan/glm-5.3-flash
      ...
  ds+glm:
    label: DeepSeek + GLM hybrid
    roles:
      chief: deepseek/deepseek-flash
      critic: zai-coding-plan/glm-5.3
      qa: zai-coding-plan/glm-5.3
      compliance-officer: zai-coding-plan/glm-5.3
      product-manager: zai-coding-plan/glm-5.3
      wordsmith: zai-coding-plan/glm-5.3
      builder: deepseek/deepseek-flash
      ...
```

*The shipped default profile is `ds+glm` (chief agent `chief-ds+glm`, prettified to Chief-Ds+Glm in the TUI): DeepSeek carries the many-turn seats on pay-as-you-go pricing, GLM 5.3 is kept for the low-volume, high-stakes gates. The primaries are `chief-ds`, `chief-glm`, and `chief-ds+glm`.*

### Update

To change model IDs, add a profile, or move a role to a different model, edit `models.yaml` and run:

```bash
python3 scripts/apply-models.py
```

The script regenerates `agents/generated/*.md` and `opencode.json.sample`; reinstall the generated agents and re-run the installer, which merges the plugin-managed keys into your existing `opencode.json` or `opencode.jsonc`.
Role sources are touched only to strip a stray `model:` line from frontmatter; no other modification.

