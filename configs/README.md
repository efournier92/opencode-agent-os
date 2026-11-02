# Configs

The vendor-specific `opencode.jsonc.<vendor>` swap files were retired on 2026-10-01.
Provider and model selection now lives in `models.yaml` profiles; no swap step remains.

## What Replaced The Swap Files

- `models.yaml` holds `profiles:` (per-profile role-to-model maps) and `default_profile:`.
- `scripts/apply-models.py` renders those profiles into `agents/generated/*.md` and `opencode.json.sample`.
- The active primaries are `chief-go` (the default), `chief-ds`, `chief-glm`, and `chief-local` (offline Qwen3); switch between them with Shift+Tab in the TUI.

## Choosing A Profile

1. Edit `models.yaml`; set `default_profile:` to the profile you want as the default chief.
2. Run `python3 scripts/apply-models.py`.
3. Reinstall the generated agents per `../INSTALL.md`, then merge `opencode.json.sample` into your `~/.config/opencode/opencode.json` or `opencode.jsonc`.

To change a model ID for a lane, edit that profile's `roles:` entry for the role, not any config file.

## Archiving A Profile

`scripts/archive-profile.py` retires a profile without losing its settings:

```bash
python3 scripts/archive-profile.py --stamp 2026-10 glm
```

It writes `configs/archive/<stamp>_<profile>.yaml` as a standalone YAML document, removes the profile from `models.yaml`, and regenerates the agents so the retired profile is no longer generated or installed.
Archived files preserve the profile's role mappings and comments for reference.
To restore one, re-indent the block under `profiles:` in `models.yaml` and run `python3 scripts/apply-models.py`.
Use `--dry-run` to preview the change without writing anything.
Archived profiles are `2026-10_glm.yaml`, `2026-10_local.yaml`, and `2026-11_ds+glm.yaml`.

## Snapshotting An Active Profile

`scripts/archive-profile.py --copy` keeps a reference copy of a profile that stays active:

```bash
python3 scripts/archive-profile.py --copy --stamp 2026-10 go
```

It writes `configs/snapshots/<stamp>_<profile>.yaml` as a standalone YAML document.
Unlike archiving, a snapshot leaves `models.yaml` unchanged and does not affect what is generated or installed; the profile stays active.
Use `--dry-run` to print the target path without writing anything.

## Install The Plugin

Install the plugin itself first. From the repo root:

```bash
mkdir -p ~/.config/opencode/agents ~/.config/opencode/skills
cp -n agents/generated/*.md ~/.config/opencode/agents/
cp -Rn skills/* ~/.config/opencode/skills/
cp -n AGENTS.md ~/.config/opencode/AGENTS.md
```

Then merge `opencode.json.sample` into `~/.config/opencode/opencode.json` or `opencode.jsonc`:

```bash
cp -n opencode.json.sample ~/.config/opencode/opencode.jsonc
```

Full instructions: `../INSTALL.md`.
