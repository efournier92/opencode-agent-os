# Critique Ledger: ChiefLocalMinimality

- Goal: Ship only the chief-local addition with a minimal diff and no behavior change for the existing ds, glm, or ds+glm profiles.
- Started: 2026-10-19
- Branch: main

## Findings

- C-20261019-01 | 2026-10-19 | maintainability | high | high | addressed | Capability gating system (CAPABILITY_MAP, denies, Profile Limits, related tests) is out of scope for adding chief-local | `scripts/apply-models.py:49`
  - rebuttal | addressed | `grep -RIn incapable scripts models.yaml` | Removed the map, validation, deny helpers, Profile Limits splicer, and five tests; regeneration is clean.
- C-20261019-02 | 2026-10-19 | maintainability | high | high | addressed | Standalone-agent lane added for a directory that does not exist; installer, test, and doc churn are out of scope | `scripts/install.sh:58`
  - rebuttal | addressed | `grep -RIn agents/standalone scripts INSTALL.md README.md` | Removed the install branch, count helper, and doc passages; the directory never existed.
- C-20261019-03 | 2026-10-19 | maintainability | high | high | addressed | Discovery archive retrofit is unrelated: 8 index lines removed, 10 added, 6 untracked archive files, 5 blank lines left | `docs/discovery/DISCOVERY.md:42`
  - rebuttal | addressed | `git -C /mnt/bnk/cs/opencode-agent-os diff --stat HEAD -- docs/discovery` | Rebuilt from HEAD plus three 2026-10-19 entries; archive files deleted and blank lines gone.
- C-20261019-04 | 2026-10-19 | maintainability | high | high | addressed | Stale 2026-10-12 spec, handoff, and critique contradict the shipped pin and should be deleted, not committed | `docs/specs/2026-10-12_LocalChiefProfile.md:18`
  - rebuttal | addressed | `test ! -e docs/specs/2026-10-12_LocalChiefProfile.md` | All three untracked artifacts deleted; no committed history was lost.
- C-20261019-05 | 2026-10-19 | maintainability | medium | high | addressed | Advisory num_ctx and serialization prose is repeated in models.yaml twice, INSTALL, and the rulebook; keep one source | `models.yaml:35`
  - rebuttal | addressed | `models.yaml:114` | Header and profile comments trimmed to local facts plus one INSTALL pointer; INSTALL owns the context and systemd prose.
- C-20261019-06 | 2026-10-19 | correctness | medium | high | addressed | apply_denies adds skill `*: allow` to 13 local roles that lack a skill key, which can nullify user-global skill denies | `scripts/apply-models.py:290`
  - rebuttal | addressed | `agents/generated/builder-local.md:6` | Gating removal deletes the injection; local subagents now inherit role-source permissions only.
- C-20261019-07 | 2026-10-19 | correctness | medium | high | rejected | No test pins the 42 non-local generated agents to HEAD bytes; test_nonlocal checks selected keys only | `scripts/test_apply_models.py:345`
  - rebuttal | rejected | `scripts/test_apply_models.py:285` | Over-severe; the test pins task shape, skill and bash passthrough, web allows; byte-pinning is brittleness.
- C-20261019-08 | 2026-10-19 | correctness | low | high | rejected | Options and local tests assert generated output against the same generator, and task-scope expectation derives from CAPABILITY_MAP | `scripts/test_apply_models.py:141`
  - rebuttal | rejected | `scripts/test_apply_models.py:141` | Not tautological; options test asserts hardcoded reasoningEffort low. The CAPABILITY_MAP-derived expectation was removed with C-01.
- C-20261019-09 | 2026-10-19 | correctness | low | high | addressed | Widened regex admits malformed ids with empty segments or multiple colons; allowlist still gates but validation is weaker | `scripts/apply-models.py:43`
  - rebuttal | addressed | `scripts/apply-models.py:43` | Regex narrowed to one optional non-empty colon tag; malformed ids fail at the shape check.
- C-20261019-10 | 2026-10-19 | correctness | low | medium | addressed | Profile Limits insertion assumes a blank line after the chief title; a different body shape splices mid-paragraph | `scripts/apply-models.py:354`
  - rebuttal | addressed | `grep -RIn "Profile Limits" scripts agents` | Splicer removed with the gating bundle; generated chiefs carry only their role body.
- C-20261019-11 | 2026-10-19 | product | high | high | addressed | INSTALL bullet says OLLAMA_MAX_LOADED_MODELS=1 is set but the systemd snippet omits it; default 3 can load a second model | `INSTALL.md:101`
  - rebuttal | addressed | `INSTALL.md:94` | Env line added to the snippet beside the other three.
- C-20261019-12 | 2026-10-19 | product | high | high | addressed | INSTALL requires small_model in prose but the jsonc snippet omits it; a verbatim follower keeps title egress | `INSTALL.md:53`
  - rebuttal | addressed | `INSTALL.md:52` | User accepted title egress; the small_model bullet was removed and INSTALL now states titles may use the cloud default.
- C-20261019-13 | 2026-10-19 | security | medium | high | addressed | Stripping gating removes the only webfetch, websearch, and git commit/push denies while model-profiles still claims coverage | `docs/rulebook/model-profiles.md:13`
  - rebuttal | addressed | `docs/rulebook/model-profiles.md:9` | Gating prose removed; local agents keep role-source allows and no doc claims tool, skill, or task denies.
- C-20261019-14 | 2026-10-19 | security | low | high | rejected | GLOSSARY says no agent can reach a remote provider, but local agents keep bash allow-all and title closure depends on hand-merged keys | `docs/GLOSSARY.md:49`
  - rebuttal | rejected | `docs/GLOSSARY.md:49` | Claim is provider-scoped and stays true under pin-only enforcement; bash allow-all is pre-existing accepted risk.
- C-20261019-15 | 2026-10-19 | product | low | medium | addressed | INSTALL's 93/7 CPU/GPU figure is not corroborated by the 10-18 ledger or the 10-17 stack note | `INSTALL.md:83`
  - rebuttal | addressed | `grep -n "93/7" INSTALL.md` | Uncorroborated figure removed; ledgered decode and prefill numbers remain.
- C-20261019-16 | 2026-10-19 | correctness | low | medium | rejected | Permission upgrade fires for every profile because resolve_capability_denies always returns a truthy dict | `scripts/apply-models.py:341`
  - rebuttal | rejected | `agents/roles/builder.md:6` | Dead code; all 14 role sources declare permission, and the helper was removed with C-01.
- C-20261019-17 | 2026-10-19 | maintainability | medium | high | rejected | 2026-10-18 and 2026-10-19 critique ledgers are untracked process artifacts not required by the minimal diff | `docs/critique/2026-10-18_LocalChiefPremise.md:1`
  - rebuttal | rejected | `docs/discovery/DISCOVERY.md:6` | Prior ledgers are committed and the redteam process mandates a committed ledger; commit rather than drop.
- C-20261019-18 | 2026-10-19 | maintainability | medium | high | addressed | Profile `num_ctx: 8192` is a no-op by the repo's own docs yet lands in all 14 generated agents; keep only reasoningEffort | `models.yaml:130`
  - rebuttal | addressed | `models.yaml:119` | num_ctx removed from the profile options; all 14 local agents now carry only reasoningEffort low.
