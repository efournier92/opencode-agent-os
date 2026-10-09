# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`; load the whole file only when an entry is load-bearing.
Scope tokens: plugin/agents, plugin/architecture, plugin/commands, plugin/discovery, plugin/skills

## Entries

- D-20261009-01 | 2026-10-09 | [decision] | plugin/architecture | QualityGates hardened after red-team: green needs executed assertions, new-file red ties to green, CRAP drops uncovered functions | docs/rulebook/quality-gates.md
- D-20261009-02 | 2026-10-09 | [decision] | plugin/agents | Approved QualityGates spec: a per-task quality gate (green proof, red proof, CRAP check) makes tests constrain the change; pilot deferred | docs/specs/2026-10-09_QualityGates.md
- D-20261009-03 | 2026-10-09 | [decision] | plugin/discovery | Adopted entry IDs D-YYYYMMDD-NN and per-ID archive files under docs/discovery/archive/; validator checks IDs and headings | docs/specs/2026-10-09_DiscoveryHardening.md
- D-20261009-04 | 2026-10-09 | [decision] | plugin/discovery | Discovery evidence must name an artifact outside docs/discovery/; self-citation is supplementary only, enforced by the vendored validator | scripts/check_discovery.py
- D-20261009-05 | 2026-10-09 | [trap] | plugin/discovery | Self-vendoring the plugin aborts: cp of source equal to dest fails under set -e; guard with a same-file test before copying | scripts/vendor-discovery-check.sh
- D-20261008-01 | 2026-10-08 | [decision] | plugin/architecture | ds+glm retuned: verifier/visual-critic/phraser -> glm-5.3-flash, product-critic -> deepseek-flash; GLM kept where volume or vision rules out the flagship | models.yaml:76
- D-20261008-02 | 2026-10-08 | [find] | plugin/architecture | glm-5.3-flash: native multimodal, 1M ctx, 3x plan quota, 4.4x smaller KV, ~9x cheaper pay-go than glm-5.3; glm-5.3 is text-only | https://docs.z.ai/guides/vlm/glm-5.3-flash
- D-20261008-03 | 2026-10-08 | [find] | plugin/architecture | deepseek-flash (V4.1-Flash) cache-hit input $0.003/1M off-peak, $0.006 peak - ~10x cheaper cached reads than glm-5.3-flash | https://api-docs.deepseek.com/quick_start/pricing
- D-20261005-01 | 2026-10-05 | [decision] | plugin/agents | Hardened photo-generator: consent/refusal/provenance/retention gates, identity done-check, hosted cost gate, node/model pinning | agents/roles/photo-generator.md:25
- D-20261005-02 | 2026-10-05 | [decision] | plugin/architecture | photo-generator re-pointed to a tool-capable text brain (deepseek-flash ds/ds+glm, glm-5.3 glm); seedream moves to a scripted API lane in the role body | models.yaml:53
- D-20261005-03 | 2026-10-05 | [decision] | plugin/architecture | Reverted seedream pin: image-output-only and absent from the chat catalog, so it cannot drive a tool-using agent | https://openrouter.ai/api/v1/images/models
- D-20261005-04 | 2026-10-05 | [outcome] | plugin/architecture | seedream-5-0-pro smoke test green: OpenRouter returned a 1024x1024 image at exactly $0.045, matching the pin's listed price | https://openrouter.ai/api/v1/images
- D-20261005-05 | 2026-10-05 | [find] | plugin/architecture | DeepSeek API cannot generate images (text-only); Janus-Pro is DeepSeek's 384px open-weights model, self-host or Replicate only | https://huggingface.co/deepseek-ai/Janus-Pro-7B
- D-20261005-06 | 2026-10-05 | [decision] | plugin/architecture | User raised visual-critic low->max; the visual critique gate now matches the other critique seats | agents/roles/visual-critic.md:5
- D-20261005-07 | 2026-10-05 | [decision] | plugin/architecture | User set builder and visual-builder to high: builder max->high, visual-builder low->high; high is the DeepSeek default | agents/roles/visual-builder.md:5
- D-20261005-08 | 2026-10-05 | [decision] | plugin/architecture | Critique gate set to max: compliance-officer and product-critic raised high->max at ~$0; chief/builder/language seats held | agents/roles/compliance-officer.md:5
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
- D-20261004-01 | 2026-10-04 | [decision] | plugin/commands | `engineer-prompt` opens its question round and smoke-test confirmation via the `question` tool, no fallback | commands/engineer-prompt.md:33
- D-20261004-02 | 2026-10-04 | [decision] | plugin/agents | Added the loop-readiness triage (repeat-worthy, auto done-check, cheap discard) to `chief.md` for deciding when to wire a loop | agents/roles/chief.md
- D-20261004-03 | 2026-10-04 | [decision] | plugin/commands | Shipped `fix-bug` as an explicit-only command encoding the red-green loop (reproduce, fix via `builder`, prove via `verifier`) | commands/fix-bug.md
- D-20261004-04 | 2026-10-04 | [assumption] | plugin/discovery | Specs stay historical; the spec's "never rewrite history" now conflicts with the skill's delete-superseded rule | docs/specs/2026-10-03-progressive-discovery.md
- D-20261004-05 | 2026-10-04 | [decision] | plugin/discovery | Index capped (entry<=240, file<=8KB), evidence checked; full-read hatch dropped; superseded deleted at reconcile | skills/log-discoveries/SKILL.md scripts/check_discovery.py
- D-20261004-09 | 2026-10-04 | [outcome] | plugin/agents | `wordsmith`/`phraser` pairing critic pass: 7 findings all fixed (language routing, phraser redirect, list handling, tone, GLM seat); check green | agents/roles/phraser.md
- D-20261004-10 | 2026-10-04 | [decision] | plugin/architecture | Deferred reduce rule: no live trigger, and an always-loaded paragraph taxes every session; apply once wide fan-out is live or a bad-merge blowup | agents/roles/chief.md:54
