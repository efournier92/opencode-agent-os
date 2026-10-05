# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`; load the whole file only when an entry is load-bearing.
Scope tokens: plugin/agents, plugin/architecture, plugin/commands, plugin/commit, plugin/discovery, plugin/naming, plugin/skills

## Entries

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
- 2026-10-04 | [decision] | plugin/agents | Added the `phraser` subagent for ranked wording riffs and made it sole owner of the options lane; pinned GLM 5.3 under `glm`/`ds+glm`, DeepSeek under `ds` | agents/roles/phraser.md
- 2026-10-04 | [decision] | plugin/architecture | Deferred reduce rule: no live trigger, and an always-loaded paragraph taxes every session for a rare case; apply once wide fan-out is live or a bad-merge blowup | agents/roles/chief.md:54
- 2026-10-04 | [decision] | plugin/architecture | Swarms/fleets need no new concept: fleet is the profile crew, swarm is operator fan-out; only a general reduce step and `worktree` isolation remain unwired | agents/roles/chief.md:54
- 2026-10-04 | [decision] | plugin/agents | Renamed the `qa` role to `verifier` (full-word role noun); generated agents go `qa-<profile>` -> `verifier-<profile>` on the next `apply-models.py` run | agents/roles/verifier.md
- 2026-10-04 | [decision] | plugin/skills | Renamed the `ui-craft` skill to `frontend-design`, a full-word topic noun; `ui-craft` kept as a legacy trigger alias | skills/polish-ui/SKILL.md:2
- 2026-10-03 | [outcome] | plugin/commands | `critic` pass on `engineer-prompt`: 10 findings all addressed (undefined "cheapest tier" dropped, smoke-test consent, empty-arg fix, install test, uninstall parity); green | scripts/check.sh
- 2026-10-03 | [decision] | plugin/commands | Shipped `engineer-prompt` as a command, not a skill: skills advertise their description every turn, commands cost nothing until invoked | commands/engineer-prompt.md
- 2026-10-03 | [decision] | plugin/naming | Renamed the repo `opencode-agent-team` to `opencode-agent-os`, scoped to agents; rejected `opencode-operating-system` as overclaiming | https://github.com/efournier92/opencode-agent-os
- 2026-10-03 | [decision] | plugin/skills | `specify` names its spec `docs/specs/YYYY-MM-DD_TopicName.md` (date, underscore, PascalCase topic); existing kebab-case specs are not renamed | skills/create-spec/SKILL.md:56
- 2026-10-03 | [decision] | plugin/skills | Glossary writes are gated on presence of a `docs/` directory (single gate, no extra confirmation); the earlier `docs/discovery/` tightening is reverted | skills/create-spec/SKILL.md:71
- 2026-10-03 | [decision] | plugin/skills | `specify` adopts dependency-ordered frontier rounds (whole frontier per round, materiality filter), user stories, a test-seam round, and a prototype exception | skills/create-spec/SKILL.md:37
- 2026-10-03 | [decision] | plugin/skills | `specify` writes one `docs/`-gated artifact, `docs/GLOSSARY.md`; durable decisions fold into the committed spec, so ADRs are not adopted | skills/create-spec/SKILL.md:71
- 2026-10-03 | [outcome] | plugin/skills | `specify` rewrite verified green: markdown lint clean, doc budget clean, 29 tests pass | `bash scripts/check.sh`
- 2026-10-03 | [decision] | plugin/discovery | Moved the full convention into the on-demand log-discoveries skill; AGENTS keeps a short opt-in gate, lowering the always-loaded rulebook tax | skills/log-discoveries/SKILL.md
- 2026-10-03 | [decision] | plugin/discovery | Renamed the practice from continuous discovery to Progressive Discovery; the external Teresa Torres framework name is unchanged | AGENTS.md:35
- 2026-10-03 | [decision] | plugin/discovery | Opt-in gate: discovery runs only where a repo has `docs/discovery/`; index moves under it; never auto-create | docs/specs/2026-10-03-progressive-discovery.md
- 2026-10-03 | [outcome] | plugin/discovery | Practice implemented and committed; markdown lint clean; 26 plugin tests pass | scripts/lint-markdown.py
- 2026-10-03 | [decision] | plugin/discovery | Adopted a committed per-repo discovery index, one line per entry, operator-written, commit-reconciled | docs/specs/2026-10-03-progressive-discovery.md
- 2026-10-03 | [trap] | plugin/commit | The ship-changes skill never runs unless the user invokes it, so findings must be appended at checkpoints, not deferred to commit | skills/ship-changes/SKILL.md:16
