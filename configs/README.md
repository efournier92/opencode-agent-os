# Configs

The vendor-specific `opencode.jsonc.<vendor>` swap files were retired on 2026-10-01.
Provider and model selection now lives in `models.yaml` profiles; no swap step remains.

## What Replaced The Swap Files

- `models.yaml` holds `profiles:` (per-profile role-to-model maps) and `default_profile:`.
- `scripts/apply-models.py` renders those profiles into `agents/generated/*.md` and `opencode.json.sample`.
- The primaries are `chief-ds`, `chief-glm`, and `chief-ds+glm` (the hybrid default: DeepSeek volume seats, GLM gates); switch between them with Tab in the TUI.

## Choosing A Profile

1. Edit `models.yaml`; set `default_profile:` to the profile you want as the default chief.
2. Run `python3 scripts/apply-models.py`.
3. Reinstall the generated agents per `../INSTALL.md`, then merge `opencode.json.sample` into your `~/.config/opencode/opencode.json` or `opencode.jsonc`.

To change a model ID for a lane, edit that profile's `roles:` entry for the role, not any config file.

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
