# Dual-Chief Architecture: Chief-DS And Chief-GLM With Per-Profile Rosters

Branch context: `main`. Working tree already carries uncommitted GLM work (`configs/opencode.jsonc.glm` untracked; `models.yaml`, `opencode.json.sample`, `README.md`, `AGENTS.md`, `configs/*`, `agents/photo-generator.md` modified). This spec builds on that state, not on `HEAD`.

## Context And Motivation

- The user now has a GLM Coding Plan (provider `zai-coding-plan`) in addition to the direct DeepSeek API.
- Goal: two operator identities, Chief-DS and Chief-GLM, both usable in one OpenCode TUI session and switchable with Tab.
- Each chief must be isolated at the config level: its crew runs that vendor's models, not a shared pool.
- The design must be extensible to a third chief later by editing one data file, not by hand-copying agent files.
- The built-in `build` agent must not appear as a TUI primary option.
- Today's model is one `chief`, one global tier map, and whole-roster vendor swaps via `configs/`. That cannot express two simultaneous vendors, and swapping is manual.

## Glossary

- Profile: a named provider bundle: id, display label, provider slug, and a per-tier model map.
- Role: a provider-agnostic agent definition (prompt, mode, permissions, prompt body) stored once under `agents/roles/`.
- Resolved agent: a generated per-profile agent, named `<role>-<profile>` (for example `builder-ds`), with a concrete `model` injected.
- Crew: every resolved agent belonging to one profile.
- Tier: a logical model slot, one of `top`, `mid`, `low`, `language-high`, `vision-high`, `vision-low`, `image-generation`.
- Prefix: the profile id as it appears in agent names, for example `ds` or `glm`.

## Current State

- `agents/chief.md:3` defines the single operator as `mode: primary`; its routing table at `agents/chief.md:38-56` dispatches bare names such as `@builder` and `@qa`.
- `models.yaml:18-25` holds one global `tiers:` map; `models.yaml:39-55` maps each agent to a tier via `agent_tiers`.
- `scripts/apply-models.py:129-143` renders `opencode.json.sample`, and at `:138` marks `chief` as the only primary agent (`mode = "primary" if agent_name == "chief" else "subagent"`).
- `scripts/apply-models.py:91-126` strips any `model:` line from `agents/*.md` frontmatter and fails loud if a skill pins a model. The stated invariant (`models.yaml:7-10`, `INSTALL.md:13-14`) is that model pinning lives only in the JSON config.
- `opencode.json.sample:3-4` sets a global `model` and `default_agent: chief`; `:14` pins `chief` to a model inside the JSON `agent` block.
- Vendor swapping is documented in `configs/README.md:44-99` and implemented by copying `configs/opencode.jsonc.<vendor>` over the global config.
- OpenCode behavior (docs, Agents page, Model section): a subagent with no `model` inherits the model of the primary agent that invokes it. Current subagents are pinned per tier, so they do not inherit today.
- Both providers are already authenticated in `~/.local/share/opencode/auth.json` (`deepseek`, `zai-coding-plan`, plus `opencode-go`, `google`, `openrouter`). Verified with `opencode models` that `deepseek/deepseek-flash`, `deepseek/deepseek-v4-pro`, `zai-coding-plan/glm-5.3`, and `zai-coding-plan/glm-5.3-flash` all resolve.
- `agents/scout.md` currently shadows OpenCode's built-in `scout`; once roles are namespaced, the built-in resurfaces unless disabled.
- Skills reference bare agent names in two places: `skills/implement/SKILL.md:31` (`@builder`) and `skills/ship-check/SKILL.md:21` (`@qa`, `@critic`).

## Goals

- Two primary agents in one config, `chief-ds` and `chief-glm`, selectable with Tab.
- Each chief's crew is pinned to that profile's provider and tier map, so DeepSeek lanes never call the GLM provider and GLM lanes never call `deepseek`.
- The seven-tier vocabulary stays; each profile supplies its own tier-to-model map.
- Vision lanes work on both profiles (`zai-coding-plan/glm-5.3-flash` is the GLM multimodal lane; the GLM chief text model is text-only).
- `photo-generator` is duplicated per profile, per the user's decision.
- Adding a third profile is a `models.yaml` edit plus a generator run; no hand-authored agent copies.
- The built-in `build` agent is absent from the TUI.
- Each chief can dispatch only its own crew, enforced by `permission.task`.

## Non-Goals

- No runtime OpenCode plugin; the roster is generated at build time.
- No change to skill semantics beyond making the two bare-name references prefix-aware.
- No new tiers and no collapse of the existing seven.
- No change to the terse, minimalist, or other skill behavior.
- No per-profile permission model beyond the task-scope restriction; `edit` and `bash` stay `ask` globally.

## Prerequisites

- OpenCode 1.18.33 or later, with `deepseek` and `zai-coding-plan` authenticated.
- Python 3 with PyYAML, already required by `scripts/apply-models.py:28`.
- No live sessions running against the config while it is regenerated.

## Design Principles

- `models.yaml` stays the single source of truth; every other artifact is generated.
- Role prompts are authored once and shared by every profile; only `model` and the profile prefix vary.
- Generated files are committed, matching the existing precedent of the committed `opencode.json.sample`.
- Provider isolation is enforced mechanically (`permission.task` globs), not by convention.
- The generator is idempotent: a second run with no input change writes nothing.

## Backend Requirements

This project has no database or service API. "Backend" here is the generator, the config, and the file layout.

### 1. `models.yaml` Schema

Replace the top-level `tiers:` block with `profiles:`, keep `agent_tiers`, and add `default_profile`.

```yaml
default_profile: ds

agent_tiers:
  chief: mid
  builder: mid
  qa: top
  critic: top
  system-fixer: mid
  product-manager: mid
  compliance-officer: top
  context-curator: mid
  photo-generator: image-generation
  wordsmith: language-high
  visual-critic: vision-high
  visual-builder: vision-low
  scout: low
  investigator: low

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

Validation rules, all failing loud with a named error:

- `default_profile` must be a key in `profiles`.
- Each profile id matches `^[a-z][a-z0-9]*$`.
- Each profile's `tiers` must define every tier referenced by `agent_tiers`.
- Every key in `agent_tiers` must have an `agents/roles/<key>.md` file.
- Profile ids must be unique (a YAML map enforces this; a duplicate key is a parse error).

### 2. Role File Layout

- Move the current hand-authored files from `agents/<role>.md` to `agents/roles/<role>.md`.
- Role files keep description, mode, and permission frontmatter, and keep the body.
- Role files must never declare `model:`; the existing strip-and-fail behavior moves to the roles directory.
- Role bodies are profile-agnostic and carry no profile token; they name crew by bare role. The chief's `permission.task` scopes its task tool to its own crew, so a bare role name resolves unambiguously and the chief never needs the profile suffix.
- Optional per-role reasoning effort lives in role frontmatter as `options: {reasoningEffort: <value>}` and is copied verbatim. Effort table, carried from the current DeepSeek config:

| Role | reasoningEffort |
|---|---|
| `chief`, `critic`, `system-fixer`, `product-manager`, `builder`, `qa`, `compliance-officer`, `wordsmith` | `high` |
| `context-curator`, `visual-critic`, `visual-builder`, `scout`, `investigator` | `low` |
| `photo-generator` | (unset) |

### 3. Generated Agent Files

- Generator output path: `agents/generated/<role>-<prefix>.md`.
- The generated file is the role file with these changes:
  - `model:` injected from `profiles[<prefix>].tiers[agent_tiers[<role>]]`.
  - `options:` copied from the role frontmatter when present.
  - `description`, `mode`, and `permission` copied from the role frontmatter.
  - For the `chief` role only, `permission.task` is replaced with `{"*": "deny", "*-<prefix>": "allow"}` so a chief can dispatch only its own crew and the other crew is removed from its Task tool description.
  - Role bodies are copied unchanged: they refer to crew by bare role name and carry no profile token.
- The generator asserts no `{{` remains in any generated file and raises if one does.
- Mode is taken from the role file, so `chief` stays `mode: primary` and every other role stays `mode: subagent`.

### 4. `opencode.json.sample` Contents

The JSON no longer carries per-agent model pins; those live in the generated agent files. The sample contains:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "deepseek/deepseek-flash",
  "default_agent": "chief-ds",
  "permission": {
    "edit": "ask",
    "bash": "ask",
    "skill": { "*": "allow" }
  },
  "agent": {
    "build": { "disable": true },
    "scout": { "disable": true }
  }
}
```

- `model` is `profiles[default_profile].tiers[agent_tiers["chief"]]`.
- `default_agent` is `chief-<default_profile>`.
- `agent.build.disable` removes the built-in primary from the TUI.
- `agent.scout.disable` prevents OpenCode's built-in `scout` from reappearing once our role is namespaced.
- No `provider` block is emitted: the GLM profile uses the dedicated `zai-coding-plan` provider, whose endpoint is the coding plan by definition. This replaces the earlier `provider.zai.options.baseURL` workaround.

### 5. `scripts/apply-models.py` Changes

- Constants (`:30-34`): add `ROLES_DIR = ROOT / "agents" / "roles"` and `GENERATED_DIR = ROOT / "agents" / "generated"`; stop treating `ROOT / "agents"` as the agent source.
- `load_models` (`:42-49`): load `profiles`, `agent_tiers`, `default_profile`; drop the top-level `tiers` key.
- `validate_models` (`:52-63`): apply the validation rules in section 1.
- `strip_agent_model_lines` (`:91-108`): scan `ROLES_DIR`; a stray `model:` in a role source is stripped and reported; a `model:` in a generated file is expected and untouched.
- `assert_no_skill_model_lines` (`:111-126`): unchanged.
- `render_sample_config` (`:129-143`): emit the JSON in section 4 instead of the per-agent model block.
- New `generate_agents(profiles, agent_tiers)`: write section 3 output; skip writes whose content is byte-identical; return the count of changed files.
- `main` (`:165-189`): run validation, strip roles, generate agents, render and verify the sample, print counts, and re-verify on-disk sample equality as it does today.

### 6. Install And Upgrade Changes

- Global install copies generated agents, not role sources: `cp -n agents/generated/*.md ~/.config/opencode/agents/` (replaces `INSTALL.md:30-31` and `README.md:24-29`).
- Upgrade must clear stale bare agents first, extending the existing warning at `INSTALL.md:136-150`: `rm -rf ~/.config/opencode/agents` then re-copy.
- `models.yaml` copy behavior (preserve-if-present) is unchanged.

### 7. Retire The Vendor-Swap Configs

- Delete `configs/opencode.jsonc.deepseek`, `configs/opencode.jsonc.minimax`, `configs/opencode.jsonc.glm`, and `configs/opencode.jsonc.2026-09-mixed`, and rewrite `configs/README.md` to point at the unified config and `models.yaml` profiles.
- Rationale: the swap workflow and the profile system are two competing mechanisms for the same job; keeping both invites drift.

### 8. Documentation And Skill Ripple

- `AGENTS.md:25-41` (model tiers) and `AGENTS.md:171-` (roster): describe profiles, the `<role>-<prefix>` naming, and that each profile supplies its own tier map; state that the two primaries are `chief-ds` and `chief-glm`.
- `agents/roles/chief.md`: keep the H1 and routing table on bare role names; add one line stating the task tool lists only the chief's own crew.
- `skills/implement/SKILL.md:31`: replace `@builder` with the active profile's builder (`<prefix>-builder`).
- `skills/ship-check/SKILL.md:21`: replace `@qa` and `@critic` with the active profile's `qa` and `critic`.
- `README.md:106-156`: rewrite the Model Tiers section for `profiles:` and generated agents.
- `INSTALL.md`: update copy paths, the sample-config description (`:69-75`), and the reinstall section (`:136-150`).

## UI Requirements

- `/agents` lists two primaries (`chief-ds`, `chief-glm`) plus every `<role>-<prefix>` subagent, and does not list `build`.
- Tab cycles between the two chiefs.
- The Task tool offered to `chief-ds` lists only `*-ds` subagents; likewise for `chief-glm`.
- No web UI is touched by this change.

## Production Risks And Mitigations

- GLM coding plan: the profile targets the dedicated `zai-coding-plan` provider, whose endpoint is the coding plan, so no `baseURL` override is needed. If a lane still returns `1113 insufficient balance`, that key is not on the coding plan.
- GLM effort parameter: OpenCode ignores `reasoningEffort` on `glm-*` (open issues `sst/opencode` #46295 and #49551), so GLM lanes run at the model default `max`. Mitigation: accepted for now; the generated `options` take effect if upstream fixes it.
- Model IDs: the tier map uses the plain IDs the `zai-coding-plan` provider exposes (`glm-5.3`, `glm-5.3-flash`); any context-window variant is out of scope until the provider lists one.
- Generated-file drift: a hand edit to a generated file is lost on the next run. Mitigation: the generators overwrite deterministically and the test suite asserts regeneration.
- Stale bare agents after upgrade: old `builder.md` and similar in the install dir would coexist with `builder-ds` and `builder-glm`. Mitigation: the upgrade step clears the agents directory (`INSTALL.md:136-150`).
- Built-in disable support: if `agent.<name>.disable` is not honored by the installed OpenCode, `build` remains. Mitigation: verify via `/agents` after restart; fall back to overriding `build` with `permission: {edit: deny, bash: deny}` and reporting the gap.
- Cost asymmetry: the DeepSeek crew's `top` tier is `deepseek-v4-pro` while GLM's is `glm-5.3`; behavior across profiles will differ in depth. Mitigation: documented per profile, tunable in `models.yaml`.

## Rollout Plan

1. Create `agents/roles/` and move the 14 role files; add the crew-scope line to `chief.md`.
2. Rewrite `models.yaml` to the profiles schema.
3. Update `scripts/apply-models.py` per section 5.
4. Run the generator; review the 28 generated files and the new `opencode.json.sample`.
5. Update skills, `AGENTS.md`, `README.md`, `INSTALL.md`; delete `configs/*.jsonc` and rewrite `configs/README.md`.
6. Run the test suite and the markdown linter.
7. Install: clear `~/.config/opencode/agents`, copy `agents/generated/*.md`, merge the sample config.
8. Restart OpenCode and verify.

## Test Plan

Add `scripts/test_apply_models.py` (stdlib `unittest`, run with `python3 -m unittest`). Cases:

- `test_generates_all_resolved_agents`: for every profile and every role, `agents/generated/<role>-<prefix>.md` exists.
- `test_model_resolution`: generated frontmatter `model` equals `profiles[p].tiers[agent_tiers[role]]` for each pair.
- `test_profile_models_match_provider`: every non-image tier model starts with the profile's `provider` prefix.
- `test_role_sources_have_no_model`: no `model:` line in `agents/roles/*.md`.
- `test_no_unresolved_tokens`: no `{{` remains in any generated file.
- `test_chief_task_scope`: each `chief-<prefix>.md` has `permission.task == {"*": "deny", "*-<prefix>": "allow"}`.
- `test_chief_is_primary`: each `chief-<prefix>.md` has `mode: primary`; every other generated file has `mode: subagent`.
- `test_sample_config_shape`: `opencode.json.sample` parses; `default_agent == "chief-<default_profile>"`; `agent.build.disable` and `agent.scout.disable` are `true`; no `provider` block is emitted.
- `test_idempotent`: a second generator run reports zero changed files.
- `test_third_profile`: with a temporary third profile added to a copied `models.yaml`, the generator emits that profile's full crew (run against a temp root).
- `test_validation_errors`: unknown tier in `agent_tiers` raises; a missing role file raises; an unknown `default_profile` raises; an invalid profile id raises.
- `test_no_skill_model_lines`: `assert_no_skill_model_lines` passes.

Markdown deliverables, including the generated agent files, pass `scripts/lint-markdown.py`.

## Summary Of Changes

Confirm this checklist captures everything needed for the feature to be functionally complete:

- [ ] `agents/roles/` holds the 14 hand-authored role files with no `model:`.
- [ ] `agents/roles/chief.md` uses bare role names and a crew-scope line.
- [ ] `models.yaml` uses `profiles:`, `agent_tiers:`, `default_profile:`.
- [ ] `scripts/apply-models.py` validates, strips roles, generates agents, and renders the sample.
- [ ] `agents/generated/` holds `ds-*` and `glm-*` agents with injected models.
- [ ] `opencode.json.sample` disables `build` and `scout` and sets `default_agent: chief-ds`.
- [ ] `permission.task` locks each chief to its own crew.
- [ ] `skills/implement` and `skills/ship-check` are prefix-aware.
- [ ] `AGENTS.md`, `README.md`, `INSTALL.md`, `configs/README.md` updated.
- [ ] `configs/*.jsonc` deleted.
- [ ] `scripts/test_apply_models.py` passes.
- [ ] `scripts/lint-markdown.py` clean on all changed markdown.

## Verification Steps

Run from the repo root, in order:

```bash
python3 scripts/apply-models.py
python3 -m unittest scripts/test_apply_models.py
python3 scripts/lint-markdown.py .
```

Then install and check the TUI:

```bash
rm -rf ~/.config/opencode/agents
mkdir -p ~/.config/opencode/agents
cp -n agents/generated/*.md ~/.config/opencode/agents/
# merge the regenerated opencode.json.sample into ~/.config/opencode/opencode.jsonc
```

- Restart OpenCode, run `/agents`: expect `chief-ds`, `chief-glm`, and both crews; no `build`.
- Press Tab: cycles `chief-ds` and `chief-glm`.
- Under `chief-ds`, dispatch a trivial task; confirm the child session reports a `deepseek/*` model.
- Under `chief-glm`, repeat; confirm a `zai-coding-plan/*` model and that the `visual-critic-glm` lane resolves to `zai-coding-plan/glm-5.3-flash`.

## Open Questions

- Resolved: the profile uses the dedicated `zai-coding-plan` provider, so no `baseURL` override is needed. Confirm with one live GLM call that plan quota applies.
- Resolved for now: the tier map uses the plain `zai-coding-plan/glm-5.3` and `zai-coding-plan/glm-5.3-flash` ids. Revisit if the provider exposes a long-context variant.
- Should the built-in `plan`, `general`, and `explore` agents also be disabled for a cleaner TUI? The spec disables only `build` and `scout` as agreed.
- Committing the 28 generated agent files is chosen for reviewability, matching `opencode.json.sample`. An alternative is to gitignore `agents/generated/` and generate during install; not chosen here.
- Is `google/gemini-3-pro-image` still the preferred DeepSeek-profile image lane, or should both profiles share `openrouter/google/gemini-2.5-flash-image`? The spec keeps the per-vendor choices from the current configs.
