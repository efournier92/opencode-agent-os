# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`; load the whole file only when an entry is load-bearing.
Scope tokens: plugin/agents, plugin/architecture, plugin/discovery, plugin/skills

## Entries

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
- D-20261010-05 | 2026-10-10 | [decision] | plugin/skills | Grill walkthrough caps 7 batched human-only decisions and 3 rounds with evidence-gated convergence; shipping stays confirm-gated | docs/specs/2026-10-10_Grill.md
- D-20261009-01 | 2026-10-09 | [decision] | plugin/architecture | QualityGates hardened after red-team: green needs executed assertions, new-file red ties to green, CRAP drops uncovered functions | docs/rulebook/quality-gates.md
- D-20261009-02 | 2026-10-09 | [decision] | plugin/agents | Approved QualityGates spec: a per-task quality gate (green proof, red proof, CRAP check) makes tests constrain the change; pilot deferred | docs/specs/2026-10-09_QualityGates.md
- D-20261009-03 | 2026-10-09 | [decision] | plugin/discovery | Adopted entry IDs D-YYYYMMDD-NN and per-ID archive files under docs/discovery/archive/; validator checks IDs and headings | docs/specs/2026-10-09_DiscoveryHardening.md
- D-20261009-04 | 2026-10-09 | [decision] | plugin/discovery | Discovery evidence must name an artifact outside docs/discovery/; self-citation is supplementary only, enforced by the vendored validator | scripts/check_discovery.py
- D-20261009-05 | 2026-10-09 | [trap] | plugin/discovery | Self-vendoring the plugin aborts: cp of source equal to dest fails under set -e; guard with a same-file test before copying | scripts/vendor-discovery-check.sh
- D-20261008-01 | 2026-10-08 | [decision] | plugin/architecture | ds+glm retuned: verifier/visual-critic/phraser -> glm-5.3-flash, product-critic -> deepseek-flash; GLM kept where volume or vision rules out the flagship | models.yaml:76
- D-20261008-02 | 2026-10-08 | [find] | plugin/architecture | glm-5.3-flash: native multimodal, 1M ctx, 3x plan quota, 4.4x smaller KV, ~9x cheaper pay-go than glm-5.3; glm-5.3 is text-only | https://docs.z.ai/guides/vlm/glm-5.3-flash
- D-20261008-03 | 2026-10-08 | [find] | plugin/architecture | deepseek-flash (V4.1-Flash) cache-hit input $0.003/1M off-peak, $0.006 peak - ~10x cheaper cached reads than glm-5.3-flash | https://api-docs.deepseek.com/quick_start/pricing
- D-20261005-09 | 2026-10-05 | [trap] | plugin/architecture | high->max reasoning-effort is high-variance on deepseek-flash (max/high 1.35x/0.41x/1.74x); treat max raises as cheap bets | `opencode run --variant max`
- D-20261005-10 | 2026-10-05 | [outcome] | plugin/architecture | effort is live: same prompt on opencode->deepseek-flash gave reasoning low 73/229 vs max 332/323 at equal input; direct API low 128 vs max 182 | `opencode run --variant max`
- D-20261005-11 | 2026-10-05 | [decision] | plugin/architecture | Effort map: max for the four critic/gate seats; low for code-locator, context-curator, external-researcher; rest high (DeepSeek default) | agents/roles/claim-critic.md:5
- D-20261005-12 | 2026-10-05 | [decision] | plugin/architecture | Retired deepseek-v4-pro: `ds` profile's four gate seats now all-flash; v4-pro is phasing out, 3.3x-7.3x costlier, V4.1-Flash leads on performance | models.yaml:38
- D-20261005-13 | 2026-10-05 | [decision] | plugin/architecture | Dropped model-tier language from live docs; one hop role->model id; 2026-10-01 spec keeps history under a superseded banner | docs/rulebook/model-profiles.md:5
- D-20261005-14 | 2026-10-05 | [decision] | plugin/architecture | Markdown style covers posted PR/issue bodies and requires a blank line after each heading; ship-changes lints a drafted PR body first | docs/rulebook/markdown-style.md:14
- D-20261005-15 | 2026-10-05 | [decision] | plugin/skills | create-spec always copies the implement-spec handoff prompt to the clipboard on completion, printing it if the clipboard command fails | skills/create-spec/SKILL.md:68
- D-20261005-16 | 2026-10-05 | [decision] | plugin/skills | create-spec always opens question rounds in the `question` tool (free-text kept); sign-off adds `Add details` so typed additions fold in | skills/create-spec/SKILL.md:23
- D-20261005-17 | 2026-10-05 | [find] | plugin/skills | OpenCode delete unshares via the ShareNext Deleted-event subscriber; a burn revokes the link | https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/share/share-next.ts
- D-20261005-18 | 2026-10-05 | [decision] | plugin/skills | `implement-spec` cuts a kebab-case feature branch before any code (spec branch context else title); dirty tree stops rather than stashes | skills/implement-spec/SKILL.md:32
- D-20261005-19 | 2026-10-05 | [decision] | plugin/skills | `ship-changes` adds `autoship`: auto commit and push plus ask-gated PR create, trunk merge, and merged-branch cleanup chain, fail-closed | skills/ship-changes/SKILL.md:22
