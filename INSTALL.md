# Installation Guide

Install this plugin into OpenCode so the multi-agent system is available in every session.

## What Gets Installed

- Generated per-profile agents in `agents/generated/` to `<config-dir>/agents/`
- **12 skills** in `skills/` to `<config-dir>/skills/`
- **Shared rulebook** `AGENTS.md` to `~/.config/opencode/AGENTS.md` (global) or `<project-root>/AGENTS.md` (per-project)
- **OpenCode config** `opencode.json.sample` merged into `~/.config/opencode/opencode.json` or `opencode.jsonc`
- **Model pins** `models.yaml` to `<config-dir>/models.yaml` (copied only if not already present; never overwrites a customized copy on reinstall)
- **TUI keybinds** `tui.json`: sets `agent_cycle: shift+tab` and `agent_cycle_reverse: none` only when those keys are unset. A keybind you chose is never overridden and no other keybind is touched.

Each generated agent carries a concrete `model:` line injected from its profile.
Role sources under `agents/roles/` and skill `.md` files declare mode and permissions but never a `model:` line; the generator strips and reports any stray one.

## Scripted Install (Recommended)

Run the installer from the plugin checkout:

```bash
scripts/install.sh
```

- Writes to `~/.config/opencode` by default; override with `--config-dir DIR` or `OPENCODE_CONFIG_DIR`.
- Backs up whatever it replaces into `backup-<timestamp>` before touching it, so it is safe to re-run.
- Overwrites `agents/`, `skills/`, and `AGENTS.md`; these are plugin-owned. Local additions in `agents/` and `skills/` are removed, so keep machine-specific agents and skills outside `~/.config/opencode/agents` and `~/.config/opencode/skills`.
- Keeps an existing `models.yaml` and `opencode.json`/`opencode.jsonc`; merge `opencode.json.sample` by hand when a config already exists.
- In `tui.json`, sets the agent-switch keybinds only when unset, leaving your keybinds alone.

The manual steps below are what the installer performs, for running by hand or for a per-project install.

## Prerequisites

- OpenCode installed and able to locate `~/.config/opencode/`.
- Know the install type: **global install** (personal, applies to every workspace) or **per-project install** (team-shared, applies to one repo).

## Global Install (Recommended)

Makes agents and skills available everywhere OpenCode runs.

1. Open a terminal in this plugin directory.

2. Copy agents and skills:

```bash
mkdir -p ~/.config/opencode/agents
cp -n agents/generated/*.md ~/.config/opencode/agents/

mkdir -p ~/.config/opencode/skills
cp -Rn skills/* ~/.config/opencode/skills/
```

3. Copy the shared rulebook:

```bash
cp -n AGENTS.md ~/.config/opencode/AGENTS.md
```

4. Copy the model-pin mapping (preserved on reinstall), then merge the sample config into your global OpenCode config.

OpenCode reads both `~/.config/opencode/opencode.json` and `~/.config/opencode/opencode.jsonc`. The model-pin mapping is copied only if you don't already have one; reinstalling never overwrites a customized `models.yaml`:

```bash
if [ -f ~/.config/opencode/models.yaml ]; then
  echo "Keeping existing ~/.config/opencode/models.yaml (edit it to change model pins)."
else
  cp models.yaml ~/.config/opencode/models.yaml
fi
```

If you already have an OpenCode config, add the keys from `opencode.json.sample` into it. If neither config exists, copy the sample directly:

```bash
if [ -f ~/.config/opencode/opencode.jsonc ]; then
  # Manually merge: add model, default_agent, permission, and agent keys
  # from opencode.json.sample into the existing JSONC object.
  echo "Merge opencode.json.sample into ~/.config/opencode/opencode.jsonc"
elif [ -f ~/.config/opencode/opencode.json ]; then
  echo "Merge opencode.json.sample into ~/.config/opencode/opencode.json"
else
  cp opencode.json.sample ~/.config/opencode/opencode.jsonc
fi
```

The sample sets:
- `default_agent`: `chief-ds+glm`: every new session starts as the hybrid operator agent (DeepSeek operator model, GLM on the verification gates). `chief-ds` and `chief-glm` are the other primaries; press Tab to switch between them.
- `model`: the fallback for any agent without an explicit override; every generated agent carries its own `model` line, so this rarely applies.
- `agent.build.disable` and `agent.scout.disable`: hide the built-in `build` primary and the built-in `scout` subagent.
- `permission`: `edit`/`bash` ask, `skill` allow.

To change model IDs later, edit the repo's `models.yaml`, run `python3 scripts/apply-models.py` (prerequisite: Python 3 with PyYAML installed; `pip install pyyaml`), then reinstall the regenerated `agents/generated/*.md` and merge the regenerated `opencode.json.sample` back into your `opencode.json` or `opencode.jsonc`. Note: `apply-models.py` reads the **repo** copy, not the installed `<config-dir>/models.yaml`; the installed copy is preserved across reinstalls and documents your chosen model pins.

5. Restart OpenCode or reload config.

6. Verify:
   - Run `/agents` in the TUI; expect `chief-ds`, `chief-glm`, `chief-ds+glm`, plus all installed subagents.
   - Check the `skill` tool description; it should list all 12 skills.
   - Start a new session; it should begin as `chief-ds+glm`; press Tab to cycle to `chief-ds` and `chief-glm`.

## Per-Project Install

Use when the plugin should travel with a specific repo.

1. Open a terminal in the project root.

2. Copy agents and skills into `.opencode/`:

```bash
mkdir -p .opencode/agents
cp -n agents/generated/*.md .opencode/agents/

mkdir -p .opencode/skills
cp -Rn skills/* .opencode/skills/
```

3. Copy the shared rulebook to the project root (not inside `.opencode/`):

```bash
cp -n AGENTS.md ./AGENTS.md
```

If the repo already has an `AGENTS.md`, merge this plugin's `AGENTS.md` into it.

4. Optional: copy the model-pin mapping (preserved on reinstall), then copy or merge the sample config:

```bash
mkdir -p .opencode
if [ -f .opencode/models.yaml ]; then
  echo "Keeping existing .opencode/models.yaml (edit it to change model pins)."
else
  cp models.yaml .opencode/models.yaml
fi
if [ -f .opencode/opencode.jsonc ] || [ -f .opencode/opencode.json ]; then
  echo "Merge opencode.json.sample into the existing project config"
else
  cp -n opencode.json.sample .opencode/opencode.jsonc
fi
```

5. Restart OpenCode or switch into the project directory and reload config.

6. Verify the same way as the global install.

## Mixed Installs

Combine global and per-project pieces. Example:
- Keep agents/skills globally in `~/.config/opencode/`.
- Put a project-specific `AGENTS.md` at `<project-root>/AGENTS.md` for repo-specific rules.

OpenCode merges config and rules from all discovered locations; later sources override earlier ones.

## Reinstalling / Upgrading

`cp -n` and `cp -Rn` only add files; they never remove renamed or deleted ones.
Reinstalling over an older version therefore leaves stale entries behind; in particular the older bare agents (`builder`, `qa`, and the rest) coexist with the per-profile agents that replace them (`builder-ds`, `builder-glm`, and so on).
Before upgrading, clear the agent and skill dirs so no stale bare agent survives, then reinstall fresh:

```bash
# global
rm -rf ~/.config/opencode/agents ~/.config/opencode/skills
# then re-run the copy commands from the global install section

# per-project
rm -rf .opencode/agents .opencode/skills
# then re-run the copy commands from the per-project section
```

This release changes `models.yaml` from `profiles:` plus a global `agent_tiers:` tier map to per-profile `roles:` model maps.
Replace the installed copy so it matches the generator's schema, backing the old one up first.

```bash
ts=$(date +%Y-%m-%d_%H%M%S)
[ -f ~/.config/opencode/models.yaml ] && cp ~/.config/opencode/models.yaml ~/.config/opencode/models.yaml.bak-$ts
cp models.yaml ~/.config/opencode/models.yaml
```

Replace the active config rather than merging it: the old per-agent `model` pins name agents that no longer exist (`chief`, `builder`), and the sample now sets `default_agent: chief-ds+glm` and disables the built-ins.
Back up the current config, then copy the regenerated `opencode.json.sample` over it (or hand-merge only the `model`, `default_agent`, `permission`, `provider`, and `agent` keys).

## Uninstall

Remove the files you copied:

```bash
# global
rm -rf ~/.config/opencode/agents
rm -rf ~/.config/opencode/skills
rm ~/.config/opencode/AGENTS.md
# edit ~/.config/opencode/opencode.jsonc (or opencode.json) to remove the plugin keys

# per-project
rm -rf .opencode/agents
rm -rf .opencode/skills
rm AGENTS.md
# edit .opencode/opencode.jsonc (or opencode.json) to remove the plugin keys
```

## Troubleshooting

- **Agents not listed**: confirm the `.md` files are in a directory OpenCode searches (`~/.config/opencode/agents/` or `.opencode/agents/`) and that YAML frontmatter is valid.
- **Skills not listed**: confirm each skill is in its own folder with a file named exactly `SKILL.md` and that the frontmatter `name` matches the folder name.
- **Chief is not the default**: confirm `default_agent: chief-ds+glm` (or `chief-ds` / `chief-glm`) is set in the active `opencode.json` or `opencode.jsonc`.
- **Model overrides not applied**: confirm the provider prefix in `models.yaml` matches your OpenCode provider, then re-run `python3 scripts/apply-models.py` and merge the regenerated `opencode.json.sample` into your active config.
