# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`; load the whole file only when an entry is load-bearing.
Scope tokens: plugin/agents, plugin/architecture, plugin/commands, plugin/commit, plugin/discovery, plugin/naming, plugin/skills

## Entries

- 2026-10-09 | [decision] | plugin/agents | Approved the QualityGates spec: a per-task quality gate (green proof, red proof, CRAP check) makes tests constrain the change; pilot deferred | docs/specs/2026-10-09_QualityGates.md
- 2026-10-08 | [decision] | plugin/architecture | ds+glm retuned: verifier/visual-critic/phraser -> glm-5.3-flash, product-critic -> deepseek-flash; GLM diversity kept where volume or vision rules out the flagship | models.yaml:76
- 2026-10-08 | [find] | plugin/architecture | glm-5.3-flash: native multimodal, 1M ctx, 3x plan quota, 4.4x smaller KV, ~9x cheaper pay-go than glm-5.3; glm-5.3 is text-only | https://docs.z.ai/guides/vlm/glm-5.3-flash
- 2026-10-08 | [find] | plugin/architecture | deepseek-flash (V4.1-Flash) cache-hit input $0.003/1M off-peak, $0.006 peak - ~10x cheaper cached reads than glm-5.3-flash | https://api-docs.deepseek.com/quick_start/pricing
- 2026-10-05 | [decision] | plugin/agents | Hardened photo-generator: consent/refusal/provenance/retention gates, identity done-check, hosted cost gate, node/model pinning | agents/roles/photo-generator.md:25
- 2026-10-05 | [decision] | plugin/architecture | photo-generator re-pointed to a tool-capable text brain (deepseek-flash ds/ds+glm, glm-5.3 glm); seedream moves to a scripted API lane in the role body | models.yaml:53
- 2026-10-05 | [decision] | plugin/architecture | Reverted seedream pin: image-output-only and absent from the chat catalog, so it cannot drive a tool-using agent | openrouter.ai/api/v1/images/models
- 2026-10-05 | [outcome] | plugin/architecture | seedream-5-0-pro smoke test green: OpenRouter returned a 1024x1024 image at exactly $0.045, matching the pin's listed price | openrouter.ai/api/v1/images
- 2026-10-05 | [find] | plugin/architecture | DeepSeek API cannot generate images (text-output only); Janus-Pro is DeepSeek's 384px open-weights model, self-host or Replicate only | https://huggingface.co/deepseek-ai/Janus-Pro-7B
- 2026-10-05 | [decision] | plugin/architecture | User raised visual-critic low->max; the visual critique gate now matches the other critique seats | agents/roles/visual-critic.md:5
- 2026-10-05 | [decision] | plugin/architecture | User set builder and visual-builder to high: builder max->high, visual-builder low->high; high is the DeepSeek default | agents/roles/visual-builder.md:5
- 2026-10-05 | [decision] | plugin/architecture | Critique gate set to max: compliance-officer and product-critic raised high->max at ~$0; chief/builder/language seats held | agents/roles/compliance-officer.md:5
- 2026-10-05 | [trap] | plugin/architecture | high->max reasoning-effort is high-variance on deepseek-flash (max/high 1.35x/0.41x/1.74x); treat max raises as cheap bets | `opencode run --variant max`
- 2026-10-05 | [outcome] | plugin/architecture | effort is live: identical prompt on opencode->deepseek-flash gave reasoning low 73/229 vs max 332/323 at equal input+cache; direct API low 128 vs max 182 | opencode run --variant max
- 2026-10-05 | [decision] | plugin/architecture | Effort map final: max for the four critic/gate seats; low for code-locator, context-curator, external-researcher; the rest high (DeepSeek default) | agents/roles/claim-critic.md:5
- 2026-10-05 | [decision] | plugin/architecture | Retired deepseek-v4-pro: `ds` profile's four gate seats now all-flash; v4-pro is phasing out, 3.3x-7.3x costlier, V4.1-Flash leads on performance | models.yaml:38
- 2026-10-05 | [decision] | plugin/architecture | Dropped model-tier language from live docs; one hop role->model id; 2026-10-01 spec keeps history under a superseded banner | docs/rulebook/model-profiles.md:5
- 2026-10-05 | [decision] | plugin/architecture | Markdown style now covers posted PR/issue bodies and makes the blank line after every heading unconditional; ship-changes lints a drafted PR body first | docs/rulebook/markdown-style.md:14
- 2026-10-05 | [decision] | plugin/skills | create-spec always copies a ready-to-paste implement-spec handoff prompt to the clipboard on completion, printing it instead if the clipboard command fails | skills/create-spec/SKILL.md:68
- 2026-10-05 | [decision] | plugin/skills | create-spec always opens question rounds in the `question` tool (free-text kept, no fallback); sign-off adds `Add details` so typed additions fold in | skills/create-spec/SKILL.md:23
- 2026-10-05 | [find] | plugin/skills | OpenCode delete unshares via the ShareNext Deleted-event subscriber, so a burn revokes the public link | https://github.com/anomalyco/opencode/blob/dev/packages/opencode/src/share/share-next.ts
- 2026-10-05 | [decision] | plugin/skills | `implement-spec` cuts a kebab-case feature branch before any code (spec branch context else title); dirty tree stops rather than stashes | skills/implement-spec/SKILL.md:32
- 2026-10-05 | [decision] | plugin/skills | `ship-changes` adds `autoship`: auto commit and push plus the ask-gated PR create, trunk merge, and merged-branch cleanup chain, fail-closed, no protection bypass | skills/ship-changes/SKILL.md:22
- 2026-10-04 | [decision] | plugin/commands | `engineer-prompt` opens its question round and smoke-test confirmation via the `question` tool, no fallback | commands/engineer-prompt.md:33,46
- 2026-10-04 | [decision] | plugin/agents | Added the loop-readiness triage (repeat-worthy, auto done-check, cheap discard) to `chief.md` for deciding when to wire a loop | agents/roles/chief.md
- 2026-10-04 | [decision] | plugin/commands | Shipped `fix-bug` as an explicit-only command encoding the red-green loop (reproduce, fix via `builder`, prove via `verifier`) | commands/fix-bug.md
- 2026-10-04 | [assumption] | plugin/discovery | Specs stay historical; the spec's "never rewrite history" now conflicts with the skill's delete-superseded rule | docs/specs/2026-10-03-progressive-discovery.md
- 2026-10-04 | [decision] | plugin/discovery | Index token-capped (entry<=240, file<=8KB), evidence-liveness checked; full-read hatch dropped; superseded deleted at reconcile | skills/log-discoveries/SKILL.md scripts/check_discovery.py
- 2026-10-04 | [decision] | plugin/skills | Renamed `commit-unstaged` to `ship-changes` and moved it from stage-only to chunk, commit, then push; it never runs unprompted | skills/ship-changes/SKILL.md:2
- 2026-10-04 | [decision] | plugin/agents | Standardized recon/critique roles to full-word nouns: `investigator`->`code-locator`, `scout`->`external-researcher`, `critic`->`claim-critic` | agents/roles/code-locator.md
- 2026-10-04 | [decision] | plugin/skills | Standardized skill names to verb-object forms (`progressive-discovery`->`log-discoveries`, `specify`->`create-spec`); removed `ship-check` | docs/rulebook/roster.md:3
- 2026-10-04 | [outcome] | plugin/agents | `wordsmith`/`phraser` pairing critic pass: 7 findings all fixed (language routing, phraser redirect, list handling, tone/register, GLM seat comment); check green | agents/roles/phraser.md
- 2026-10-04 | [decision] | plugin/architecture | Deferred reduce rule: no live trigger, and an always-loaded paragraph taxes every session for a rare case; apply once wide fan-out is live or a bad-merge blowup | agents/roles/chief.md:54
- 2026-10-04 | [decision] | plugin/architecture | Swarms/fleets need no new concept: fleet is the profile crew, swarm is operator fan-out; only a general reduce step and `worktree` isolation remain unwired | agents/roles/chief.md:54

Older settled entries: see [ARCHIVE.md](ARCHIVE.md).
