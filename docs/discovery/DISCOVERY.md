# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`. Load the whole file only when an entry is load-bearing.
Scope tokens: docs/notes, plugin/agents, plugin/architecture, plugin/skills

## Entries

- D-20261101-15 | 2026-11-01 | [trap] | plugin/architecture | OpenCode invokes every plugin export as a plugin, so helper exports must accept context and return empty hooks | plugins/git-guard.js:68
- D-20261101-14 | 2026-11-01 | [decision] | plugin/architecture | Stale-session guard: 2h idle and 150k context aborts once at zero cost, writes a noReply note, resend overrides | plugins/stale-session-guard.js
- D-20261101-13 | 2026-11-01 | [decision] | plugin/architecture | Added a plugins/ dir, copied by install.sh, with git-guard (blocks destructive git verbs, OPENCODE_GIT_GUARD=0 override) | plugins/git-guard.js
- D-20261101-12 | 2026-11-01 | [find] | docs/notes | Cheap tiers trade data, allowance, or jurisdiction. DeepSeek trains by default, stores in PRC | https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html
- D-20261101-11 | 2026-11-01 | [decision] | plugin/architecture | Retired ds+glm to configs/archive/2026-11_ds+glm.yaml; active profiles are ds, glm, go (default), local | configs/archive/2026-11_ds+glm.yaml
- D-20261101-10 | 2026-11-01 | [decision] | plugin/architecture | Made chief-go the default profile: Go allowance headroom measured at 46% of $100 at 1x, and the flat $10 plan carries the daily driver | models.yaml:43
- D-20261101-09 | 2026-11-01 | [decision] | plugin/architecture | Removed opencode-go/glm-5.3 from the go profile, referee to glm-5.3-flash: $6.95/mo (46.3% of $15) to $0.78/mo (1.3% of $60), flash pool $4.29/mo | models.yaml:114
- D-20261101-08 | 2026-11-01 | [decision] | plugin/agents | Intake gate: requests need goal, effort, verify or the operator asks once with defaults, and labels assumptions when unattended | docs/rulebook/operator-detail.md:15
- D-20261101-07 | 2026-11-01 | [decision] | plugin/architecture | Semicolons banned in prose (rule 5), enforced by lint with old hits grandfathered in a baseline | scripts/markdown-semicolon-baseline.txt
- D-20261101-06 | 2026-11-01 | [decision] | plugin/architecture | Added --copy snapshots to configs/snapshots. The active profile is copied, not retired. ds+glm snapshotted 2026-10 | configs/snapshots/2026-10_ds+glm.yaml
- D-20261101-05 | 2026-11-01 | [decision] | plugin/architecture | Made go the default, archived local, and set active primaries chief-go, chief-ds, chief-ds+glm | configs/archive/2026-10_local.yaml
- D-20261101-04 | 2026-11-01 | [decision] | plugin/architecture | Archived the glm profile to configs/archive/2026-10_glm.yaml, and archive-profile.py retires a profile without generating or installing it | configs/archive/2026-10_glm.yaml
- D-20261101-03 | 2026-11-01 | [decision] | plugin/architecture | Option C: claim-critic to glm-5.3-flash, glm-5.3 referee-only. 46% of the $15 pool last month, 92.8% at 2x, and check_usage.py blocks at 90% | scripts/check_usage.py:1
- D-20261101-02 | 2026-11-01 | [decision] | plugin/architecture | Reverted code-locator and context-curator to deepseek-v4.1-flash: highest injection/persistence risk, $2-3/mo saving not worth it. Supersedes D-20261101-01 | models.yaml:135
- D-20261101-01 | 2026-11-01 | [decision] | plugin/architecture | Added go profile on OpenCode Go: deepseek-v4.1-flash volume seats, glm-5.3 review, mimo locators, and $35/mo projected against the $100 allowance | models.yaml:115
- D-20261026-01 | 2026-10-26 | [outcome] | plugin/skills | Redteam loop redesigned for tokens: shared pack, 4-lens cap, consolidated rebuttal, 6-dispatch budget. Replay hit the bar at 694k | docs/critique/2026-10-26_RedteamTokenCost.md
- D-20261026-02 | 2026-10-26 | [decision] | plugin/skills | Evidence pack is built by one code-locator dispatch, 1.2-1.5k tokens, HEAD-guarded. Lenses read it first and source reads stay unrestricted | skills/redteam/SKILL.md:79
- D-20261026-03 | 2026-10-26 | [trap] | plugin/agents | Agent rules concat after global and last match wins, so role bash allow beats the global ask, and bash and grep skip read denies | docs/critique/2026-10-26_PermissionsReplay.md:11
- D-20261026-04 | 2026-10-26 | [trap] | plugin/architecture | merge-config force-merges permission.external_directory./tmp/* every install, silently reverting a user who removed it | scripts/merge-config.py:24
- D-20261026-05 | 2026-10-26 | [outcome] | plugin/skills | CONVERGED clause now keys on "still open", so a high finding rejected inside the round no longer blocks | skills/redteam/SKILL.md:55
- D-20261025-01 | 2026-10-25 | [decision] | plugin/skills | Session retention: 7 days. `prune-sessions` wipes expired families, spares the newest, revokes shares, defers vacuum to exit. Curator applies it | skills/prune-sessions/SKILL.md
- D-20261025-02 | 2026-10-25 | [trap] | plugin/architecture | Session delete leaves event rows (no session FK). Old events held 16 GB of an 18.9 GB DB, so prune events by aggregate_id first | skills/prune-sessions/scripts/prune_sessions.py
- D-20261019-01 | 2026-10-19 | [decision] | plugin/architecture | Kept chief-local core, and removed capability gating, standalone lane, archive retrofit | models.yaml
- D-20261019-02 | 2026-10-19 | [question] | plugin/architecture | Title egress accepted, and num_ctx dropped from profile options as advisory | INSTALL.md
- D-20261019-03 | 2026-10-19 | [outcome] | plugin/architecture | Minimality redteam converged: 18 findings, 14 settled, 4 human decisions | docs/critique/2026-10-19_ChiefLocalMinimality.md
- D-20261017-04 | 2026-10-17 | [outcome] | plugin/agents | Permission redteam converged: 17 findings, 4 rejected on evidence, residual bash/grep/symlink risk accepted | docs/critique/2026-10-17_Permission-Loosening.md
- D-20261017-03 | 2026-10-17 | [trap] | plugin/agents | Read denies gate only the read tool, and bash and grep skip them, so treat the list as accident protection | INSTALL.md:118
- D-20261017-02 | 2026-10-17 | [decision] | plugin/agents | Roles no longer set read. Agent rules append after global and last-match wins, so role read allow would nullify global denies | agents/roles/chief.md:6
- D-20261017-01 | 2026-10-17 | [decision] | plugin/architecture | Hold OpenCode 1.19.3: V1 patches ship same-day. V2 ignores subagent_depth and compaction.prune, and the DB migration blocks downgrade | https://opencode.ai/v2/docs/migrate-v1
- D-20261011-01 | 2026-10-11 | [decision] | plugin/architecture | Redteam audit found only photo-generator droppable. All other merge/drop proposals refuted by deliberate contracts | docs/rulebook/roster.md
- D-20261011-02 | 2026-10-11 | [decision] | plugin/agents | Demoted photo-generator to a /photo-generator command plus docs/rulebook/photo-generator.md. Dropped from crew and models.yaml | commands/photo-generator.md
- D-20261011-03 | 2026-10-11 | [decision] | plugin/architecture | chief.md trimmed 92->85: dropped AGENTS.md-duplicate lines. Offloaded loop triage and memory format to operator-detail.md | docs/rulebook/operator-detail.md
- D-20261011-04 | 2026-10-11 | [decision] | plugin/architecture | Added apply-models.py --check for generated-agent drift and wired it into check.sh | scripts/apply-models.py
- D-20261011-05 | 2026-10-11 | [decision] | plugin/architecture | install.sh drops an explicit list of plugin commands renamed or removed across versions, and grill.md removed after the redteam rename | scripts/install.sh
- D-20261011-06 | 2026-10-11 | [outcome] | plugin/architecture | Runtime-cost redteam converged: 33 findings, no live spend leak. Always-loaded duplication cut | docs/critique/2026-10-11_PluginRuntimeCost.md
- D-20261011-07 | 2026-10-11 | [decision] | plugin/architecture | Hardened model config: model-id allowlist plus sample gate. Repo models.yaml is the single source, and install backup retention keeps the newest 3 | scripts/apply-models.py

