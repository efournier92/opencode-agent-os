# Multi-Agent Operating System For OpenCode

## Purpose

- A suite of agents and skills built for [OpenCode](https://opencode.ai/) TUI.

## Features

- Centralized model-tier config for frequent provider swapping in ever-changing world in which we're living
  - *See `models.yaml`.*

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
    - Expect both primaries and their crews: `chief-ds`, `chief-glm`, and each `<role>-<prefix>` subagent *(`builder-ds`, `qa-glm`, etc).*
2. The `skill` tool description should list all 12 skills *(`specify`, `implement`, etc).*

## Contents

### `AGENTS.md`

- Shared rulebook *(operating loop, delegation contract, shell discipline, roster)*.
- Install to either:
  - `~/.config/opencode/AGENTS.md` *(global)*.
  - `<project-root>/AGENTS.md` *(per-project)*.

### `INSTALL.md`

- Agent-oriented install guide for global and per-project setups.

### `models.yaml`

- Single source of truth for profiles, per-profile model tiers, and role-to-tier mapping.
  - *Supports (`top`, `mid`, `low`, `language-high`, `vision-high`, `vision-low`, `image-generation`).*

### `scripts/apply-models.py`

- Resolves `models.yaml` into one generated agent per profile under `agents/generated/`, named `<role>-<prefix>` (for example `builder-ds`).
- Renders `opencode.json.sample` and strips any stray `model:` line from role frontmatter; fails loud if a skill file ever grows one.

### `scripts/install.sh`

- Installs generated agents, skills, the rulebook, and the TUI keybinds into the OpenCode config dir, with a timestamped backup.
- Overwrites plugin-owned agents, skills, and rulebook; keeps an existing `models.yaml` and config; sets keybinds only when unset.

### `scripts/release.sh`

- Tags a release with today's date (`YYYY-MM-DD`) and pushes the branch and tag.
- Re-running the same day moves that day's tag to the new `HEAD`; other dates are never touched.

### `opencode.json.sample`

- Sample global config: `chief-ds` as default agent, the default model, and the built-in `build` and `scout` agents disabled.

### `agents/`

- Role sources live in `agents/roles/` *(markdown + YAML frontmatter)*.
- `scripts/apply-models.py` renders each role into one generated agent per profile under `agents/generated/`, named `<role>-<prefix>` (for example `builder-ds`).

| Role | Mode | Tier | Description |
|---|---|---|---|
| `chief` | primary | mid | Operator agent that decides, decomposes, routes work to specialists, verifies output, and writes handoffs. |
| `builder` | subagent | mid | Bounded implementation worker for a well-specified task with a clear done-check. |
| `qa` | subagent | top | PASS/FAIL verification agent that proves claims by executing commands; read-only on code. |
| `critic` | subagent | top | Red-team reviewer that attacks handoffs, plans, diffs, and claims for fake progress before they are trusted. |
| `system-fixer` | subagent | mid | Repairs the agent system itself (configs, hooks, instruction docs) and runs improvement mode for recurring failures. |
| `context-curator` | subagent | mid | Hygiene agent for instruction docs, memory index, and handoffs; keeps context lean and claims true. |
| `scout` | subagent | low | Low-tier external-research agent for docs, versions, APIs, and changelogs outside the codebase. |
| `investigator` | subagent | low | Low-tier read-only in-repo code locator that finds where symbols are defined and what calls them, with compressed deterministic output. |
| `compliance-officer` | subagent | top | Pre-filters specs, branches, and PRs for regulatory/legal/fiduciary/privacy questions worth a human compliance officer's time. |
| `product-manager` | subagent | mid | Harsh product/UX critique of specs, branches, and PRs from the user's perspective. |
| `photo-generator` | subagent | image-generation | Local AI photo-generation specialist: sets up a ComfyUI/SDXL rig, downloads models, produces identity-consistent artistic images via scripted runners. |
| `wordsmith` | subagent | language-high | Communicative-language specialist: formal writing, messages, speeches, talking points in an American Millennial voice. |
| `visual-critic` | subagent | vision-high | Holistic visual design sweep of print, PDF, and HTML deliverables. |
| `visual-builder` | subagent | vision-low | Applies visual fixes from `visual-critic` findings. |

*Mode and tier ship with each role. Each profile injects a concrete model per tier from `models.yaml` (see Model Tiers); the two primaries are `chief-ds` and `chief-glm`.*

### `skills/` (12 skills)

- 1 directory per skill, each with with a `SKILL.md` inside.

| Skill | Description |
|---|---|
| `specify` | Turn a rough design sketch into an implementation-ready spec document. |
| `implement` | Build exactly what a finished design spec says and iterate to a green test suite. |
| `commit` | Organize already-completed work into logical commits: stages chunks and suggests messages, never commits. |
| `handoff` | Write a structured session handoff so a fresh session resumes without re-exploring. |
| `capture` | Distill session learnings into a terse, standalone knowledge file for a human or future agent. |
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

## Model Tiers

### Configure

All model assignments are driven by `models.yaml`.
The file holds `profiles:` (a per-profile tier-to-model map), a global `agent_tiers:` (role to tier), and `default_profile:`.
The generator renders that file into one agent per profile under `agents/generated/` and into `opencode.json.sample`, which is the JSON config OpenCode actually reads at runtime.
Role sources under `agents/roles/` and skill `.md` files never declare a `model:` line; doing so would shadow the generated config and break this single-source-of-truth architecture.

```yaml
default_profile: ds

agent_tiers:
  chief: mid
  builder: mid
  qa: top
  critic: top
  scout: low
  investigator: low
  ...

profiles:
  ds:
    label: DeepSeek
    provider: deepseek
    tiers:
      top: deepseek/deepseek-v4-pro
      mid: deepseek/deepseek-flash
      low: deepseek/deepseek-flash
      language-high: deepseek/deepseek-flash
      vision-high: deepseek/deepseek-flash
      vision-low: deepseek/deepseek-flash
      image-generation: google/gemini-3-pro-image
  glm:
    label: GLM
    provider: zai-coding-plan
    tiers:
      top: zai-coding-plan/glm-5.3
      mid: zai-coding-plan/glm-5.3
      low: zai-coding-plan/glm-5.3-flash
      language-high: zai-coding-plan/glm-5.3
      vision-high: zai-coding-plan/glm-5.3-flash
      vision-low: zai-coding-plan/glm-5.3-flash
      image-generation: openrouter/google/gemini-2.5-flash-image
```

*The shipped default is the DeepSeek profile; the two primaries are `chief-ds` and `chief-glm`.*

### Update

To change model IDs, add a profile, or move a role between tiers, edit `models.yaml` and run:

```bash
python3 scripts/apply-models.py
```

The script regenerates `agents/generated/*.md` and `opencode.json.sample`; reinstall the generated agents and merge the sample into your `opencode.json` or `opencode.jsonc` (or copy it on top if the file is unmodified).
Role sources are touched only to strip a stray `model:` line from frontmatter; no other modification.

