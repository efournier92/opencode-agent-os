# Discovery Archive

Settled entries moved out of the index to hold its size cap. Same line format and evidence rules; newest first. The index links here when an entry is load-bearing.

## Entries

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
