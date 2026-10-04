# Model Profiles

Model assignments are centralized in `models.yaml` in this plugin tree.
The file holds `profiles:` (each with a `roles:` map naming the concrete model for every role) and `default_profile:`.
No tier indirection: one hop from role to model id.
Single-vendor profiles pin one vendor; `ds+glm` (chief agent `chief-ds+glm`) mixes vendors per seat, keeping GLM 5.3 on the low-turn, high-stakes gates (`claim-critic`, `verifier`, `compliance-officer`, `product-critic`) and the language-quality seats (`wordsmith`, `phraser`), with DeepSeek on every many-turn seat.
Run `scripts/apply-models.py` after editing `models.yaml`; the script generates one resolved agent per profile and role under `agents/generated/`, named `<role>-<profile>` (for example `builder-ds`), and renders `opencode.json.sample`.
Role bodies are profile-agnostic and name crew by bare role; the profile shows up only in the generated filename, the injected `model:`, and the chief's task scope.
Generated agent files carry a concrete `model:` line; role sources under `agents/roles/` and skill `.md` files never declare one.
The primaries are `chief-ds`, `chief-glm`, and `chief-ds+glm`; each chief can dispatch only its own crew, and its prompt names that crew by bare role (`builder`, `verifier`, and so on).
Every role carries its own pinned model, so resolved agents never inherit the invoking chief's model.
