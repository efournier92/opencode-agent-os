# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`; load the whole file only when an entry is load-bearing.
Scope tokens: plugin/agents, plugin/architecture, plugin/discovery, plugin/skills

## Entries

- D-20261026-01 | 2026-10-26 | [outcome] | plugin/skills | Redteam loop redesigned for tokens: shared pack, 4-lens cap, consolidated rebuttal, 6-dispatch budget; replay hit the bar at 694k | docs/critique/2026-10-26_RedteamTokenCost.md
- D-20261026-02 | 2026-10-26 | [decision] | plugin/skills | Evidence pack is built by one code-locator dispatch, 1.2-1.5k tokens, HEAD-guarded; lenses read it first and source reads stay unrestricted | skills/redteam/SKILL.md:79
- D-20261026-03 | 2026-10-26 | [trap] | plugin/agents | Agent rules concat after global and last match wins, so role bash allow beats the global ask; bash and grep skip read denies | docs/critique/2026-10-26_PermissionsReplay.md:11
- D-20261026-04 | 2026-10-26 | [trap] | plugin/architecture | merge-config force-merges permission.external_directory./tmp/* every install, silently reverting a user who removed it | scripts/merge-config.py:24
- D-20261026-05 | 2026-10-26 | [outcome] | plugin/skills | CONVERGED clause now keys on "still open", so a high finding rejected inside the round no longer blocks | skills/redteam/SKILL.md:55
- D-20261025-01 | 2026-10-25 | [decision] | plugin/skills | Session retention: 7 days; `prune-sessions` wipes expired families, spares the newest, revokes shares, defers vacuum to exit; curator applies it | skills/prune-sessions/SKILL.md
- D-20261025-02 | 2026-10-25 | [trap] | plugin/architecture | Session delete leaves event rows (no session FK); old events held 16 GB of an 18.9 GB DB, so prune events by aggregate_id first | skills/prune-sessions/scripts/prune_sessions.py
- D-20261019-01 | 2026-10-19 | [decision] | plugin/architecture | Kept chief-local core; removed capability gating, standalone lane, archive retrofit | models.yaml
- D-20261019-02 | 2026-10-19 | [question] | plugin/architecture | Title egress accepted; num_ctx dropped from profile options as advisory | INSTALL.md
- D-20261019-03 | 2026-10-19 | [outcome] | plugin/architecture | Minimality redteam converged: 18 findings, 14 settled, 4 human decisions | docs/critique/2026-10-19_ChiefLocalMinimality.md
- D-20261017-04 | 2026-10-17 | [outcome] | plugin/agents | Permission redteam converged: 17 findings, 4 rejected on evidence, residual bash/grep/symlink risk accepted | docs/critique/2026-10-17_Permission-Loosening.md
- D-20261017-03 | 2026-10-17 | [trap] | plugin/agents | Read denies gate only the read tool; bash and grep skip them, so treat the list as accident protection | INSTALL.md:118
- D-20261017-02 | 2026-10-17 | [decision] | plugin/agents | Roles no longer set read; agent rules append after global and last-match wins, so role read allow would nullify global denies | agents/roles/chief.md:6
- D-20261017-01 | 2026-10-17 | [decision] | plugin/architecture | Hold OpenCode 1.19.3: V1 patches ship same-day; V2 ignores subagent_depth and compaction.prune; DB migration blocks downgrade | https://opencode.ai/v2/docs/migrate-v1
- D-20261011-01 | 2026-10-11 | [decision] | plugin/architecture | Redteam audit found only photo-generator droppable; all other merge/drop proposals refuted by deliberate contracts | docs/rulebook/roster.md
- D-20261011-02 | 2026-10-11 | [decision] | plugin/agents | Demoted photo-generator to a /photo-generator command plus docs/rulebook/photo-generator.md; dropped from crew and models.yaml | commands/photo-generator.md
- D-20261011-03 | 2026-10-11 | [decision] | plugin/architecture | chief.md trimmed 92->85: dropped AGENTS.md-duplicate lines; offloaded loop triage and memory format to operator-detail.md | docs/rulebook/operator-detail.md
- D-20261011-04 | 2026-10-11 | [decision] | plugin/architecture | Added apply-models.py --check for generated-agent drift and wired it into check.sh | scripts/apply-models.py
- D-20261011-05 | 2026-10-11 | [decision] | plugin/architecture | install.sh drops an explicit list of plugin commands renamed or removed across versions; grill.md removed after the redteam rename | scripts/install.sh
- D-20261011-06 | 2026-10-11 | [outcome] | plugin/architecture | Runtime-cost redteam converged: 33 findings, no live spend leak; always-loaded duplication cut | docs/critique/2026-10-11_PluginRuntimeCost.md
- D-20261011-07 | 2026-10-11 | [decision] | plugin/architecture | Hardened model config: model-id allowlist plus sample gate; repo models.yaml single source; install backup retention keeps newest 3 | scripts/apply-models.py
- D-20261010-08 | 2026-10-10 | [decision] | plugin/architecture | Renamed grill->redteam, adversary->redteamer, adjudicator->referee; dropped product-critic and compliance-officer | docs/specs/2026-10-10_Grill.md
- D-20261010-07 | 2026-10-10 | [decision] | plugin/discovery | Retired the orphan-archive warning; archive is authoritative, an index line is optional; only the heading check stays | docs/specs/2026-10-09_DiscoveryHardening.md
- D-20261010-01 | 2026-10-10 | [decision] | plugin/architecture | Adopted grill: operator-run adversarial convergence with a shared ledger, rebuttals, un-ship pass, minimal walkthrough | docs/specs/2026-10-10_Grill.md
- D-20261010-02 | 2026-10-10 | [decision] | plugin/architecture | Nesting stays flat (depth 2) after external plus adversarial review; operator routes critic findings to builders | docs/specs/2026-10-10_Grill.md
- D-20261010-03 | 2026-10-10 | [decision] | plugin/agents | Added adversary (lens red-team) and adjudicator (convergence gate, minimal agenda); ds+glm pins both on GLM flash and flagship | docs/specs/2026-10-10_Grill.md
- D-20261010-04 | 2026-10-10 | [decision] | plugin/architecture | Critique ledger Markdown-first at docs/critique/, operator-only writes; SQLite graduation on concurrency, size, or query triggers | docs/specs/2026-10-10_Grill.md
- D-20261010-06 | 2026-10-10 | [trap] | plugin/architecture | Bare `scripts/lint-markdown.py` in AGENTS.md reads project-local, so a chief in a non-plugin repo reports a missing path; only capture-session qualifies it | AGENTS.md:43
- D-20261009-01 | 2026-10-09 | [decision] | plugin/architecture | QualityGates hardened after red-team: green needs executed assertions, new-file red ties to green, CRAP drops uncovered functions | docs/rulebook/quality-gates.md
- D-20261009-02 | 2026-10-09 | [decision] | plugin/agents | Approved QualityGates spec: a per-task quality gate (green proof, red proof, CRAP check) makes tests constrain the change; pilot deferred | docs/specs/2026-10-09_QualityGates.md
- D-20261009-03 | 2026-10-09 | [decision] | plugin/discovery | Adopted entry IDs D-YYYYMMDD-NN and per-ID archive files under docs/discovery/archive/; validator checks IDs and headings | docs/specs/2026-10-09_DiscoveryHardening.md
- D-20261009-04 | 2026-10-09 | [decision] | plugin/discovery | Discovery evidence must name an artifact outside docs/discovery/; self-citation is supplementary only, enforced by the vendored validator | scripts/check_discovery.py
- D-20261009-05 | 2026-10-09 | [trap] | plugin/discovery | Self-vendoring the plugin aborts: cp of source equal to dest fails under set -e; guard with a same-file test before copying | scripts/vendor-discovery-check.sh
- D-20261008-01 | 2026-10-08 | [decision] | plugin/architecture | ds+glm retuned: verifier/visual-critic/phraser -> glm-5.3-flash, product-critic -> deepseek-flash; GLM kept where volume or vision rules out the flagship | models.yaml:76
- D-20261008-02 | 2026-10-08 | [find] | plugin/architecture | glm-5.3-flash: native multimodal, 1M ctx, 3x plan quota, 4.4x smaller KV, ~9x cheaper pay-go than glm-5.3; glm-5.3 is text-only | https://docs.z.ai/guides/vlm/glm-5.3-flash
- D-20261008-03 | 2026-10-08 | [find] | plugin/architecture | deepseek-flash (V4.1-Flash) cache-hit input $0.003/1M off-peak, $0.006 peak - ~10x cheaper cached reads than glm-5.3-flash | https://api-docs.deepseek.com/quick_start/pricing
