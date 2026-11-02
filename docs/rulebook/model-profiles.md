# Model Profiles

Model assignments are centralized in `models.yaml` in this plugin tree.
The file holds `profiles:` (each with a `roles:` map naming the concrete model for every role) and `default_profile:`.
Each role maps directly to one concrete model id: a single hop from role to model.
Single-vendor profiles pin one vendor; `ds+glm` was retired on 2026-11-01 and is archived at `configs/archive/2026-11_ds+glm.yaml`.
The `go` profile (OpenCode Go) pins every seat to `opencode-go/*` across two models: `deepseek-v4.1-flash` on the many-turn and high-stakes seats (`chief`, `verifier`, `builder`, `system-fixer`, `external-researcher`, `redteamer`, `visual-builder`, `code-locator`, `context-curator`), and `glm-5.3-flash` on the review layer and the prose/vision seats (`claim-critic`, `referee`, `wordsmith`, `phraser`, `visual-critic`).
The retired `ds+glm` profile mixed vendors per seat; its role map and rationale are preserved in `configs/archive/2026-11_ds+glm.yaml`.
The `local` profile pins every seat to `ollama/qwen3.6:35b-a3b`, the clean Qwen3.6-35B-A3B MoE, running the whole crew on-device so no local-profile agent can reach a remote model provider, and carries a profile-level `options:` map (`reasoningEffort: low`) that the generator merges into each of its agents. Only one copy of the model fits in RAM, so parallel subagent work serializes; host measurements, the served-context cap, and the protective systemd settings remain in `INSTALL.md` (Local Profile Prerequisites).
Run `scripts/apply-models.py` after editing `models.yaml`; the script generates one resolved agent per profile and role under `agents/generated/`, named `<role>-<profile>` (for example `builder-ds`), and renders `opencode.json.sample`.
Role bodies are profile-agnostic and name crew by bare role; the profile shows up only in the generated filename, the injected `model:`, and the chief's task scope.
Generated agent files carry a concrete `model:` line; role sources under `agents/roles/` and skill `.md` files never declare one.
The primaries are `chief-go` (the default), `chief-ds`, `chief-glm`, and `chief-local`; each chief can dispatch only its own crew, and its prompt names that crew by bare role (`builder`, `verifier`, and so on).
Retired profiles are moved to `configs/archive/<YYYY-MM>_<profile>.yaml` by `scripts/archive-profile.py` and are not generated or installed.
Every role carries its own pinned model, so resolved agents never inherit the invoking chief's model.
