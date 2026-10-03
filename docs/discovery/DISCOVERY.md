# Discovery

One line per finding, decision, assumption, trap, question, or outcome. Newest first. Evidence required. Grep by scope token or `[type]`; load the whole file only when it is small or an entry is load-bearing.

## Entries

- 2026-10-03 | [decision] | plugin/discovery | Moved the full convention into the on-demand progressive-discovery skill; AGENTS keeps a short opt-in gate, lowering the always-loaded rulebook tax | skills/progressive-discovery/SKILL.md
- 2026-10-03 | [decision] | plugin/discovery | Renamed the practice from continuous discovery to Progressive Discovery; the external Teresa Torres framework name is unchanged | AGENTS.md:105
- 2026-10-03 | [decision] | plugin/discovery | Opt-in gate: discovery runs only where a repo has `docs/discovery/`; index moves under it; never auto-create | docs/specs/2026-10-03-progressive-discovery.md
- 2026-10-03 | [outcome] | plugin/discovery | Practice implemented and committed; markdown lint clean; 26 plugin tests pass | `python3 scripts/lint-markdown.py .` and `python3 -m unittest scripts/test_*.py`
- 2026-10-03 | [decision] | plugin/discovery | Adopted a committed per-repo discovery index, one line per entry, operator-written, commit-reconciled | docs/specs/2026-10-03-progressive-discovery.md
- 2026-10-03 | [trap] | plugin/commit | The commit skill never runs unless the user invokes it, so findings must be appended at checkpoints, not deferred to commit | skills/commit/SKILL.md:10
