# Critique Ledger: Ship To Remote And Install

- Goal: Commit and push everything uncommitted on `main`, then run install so the live `~/.config/opencode` matches the repo.
- Started: 2026-10-26
- Branch: main (HEAD d321139, tracking origin/main, 0 ahead 0 behind at intake)
- Lens set: correctness, security, data-integrity, reliability

## Findings

- C-20261026-10 | 2026-10-26 | correctness | high | high | addressed | Install copies the working tree; push ships the index, so untracked files install but never reach origin | scripts/test_install.py:41
  - rebuttal | addressed | scripts/install.sh:58 | Staging everything with add -A collapses the gap.
- C-20261026-11 | 2026-10-26 | correctness | medium | high | rejected | IF_ABSENT never retracts a seed, so a deleted tmp allow is re-added; a limitation, not a defect | scripts/merge-config.py:67
  - rebuttal | rejected | scripts/test_merge_config.py:78 | Present-value-wins is intended; key removal stays re-seeded, so D-20261026-04 holds.
- C-20261026-12 | 2026-10-26 | correctness | medium | high | addressed | A live config that fails strict JSON makes the merge a no-op while install still exits 0 | scripts/install.sh:101
  - rebuttal | addressed | scripts/install.sh:106 | The live file parses today; residual risk is stderr-visible and confined to merged keys.
- C-20261026-13 | 2026-10-26 | correctness | low | medium | rejected | Install never runs the generated-agent drift check | .githooks/pre-commit:10
  - rebuttal | rejected | scripts/check.sh:19 | The pre-commit hook runs the drift check before install or push.
- C-20261026-14 | 2026-10-26 | security | high | high | addressed | Unattended prune --apply on every curator sweep contradicts the skill confirm gate | agents/roles/context-curator.md:32
  - rebuttal | addressed | agents/roles/context-curator.md:32 | User ruled standing auto-prune allowed; skill step 2 now states the sweep applies without prompting while a manual run waits.
- C-20261026-15 | 2026-10-26 | security | medium | high | addressed | --days accepts 0 or negative, so --apply deletes every family but the newest | skills/prune-sessions/scripts/prune_sessions.py:341
  - rebuttal | addressed | skills/prune-sessions/scripts/prune_sessions.py:103 | Guarded with exit 2 plus a test.
- C-20261026-16 | 2026-10-26 | security | medium | medium | rejected | Config backups can hold provider keys if opencode.jsonc ever gains one | scripts/install.sh:48
  - rebuttal | rejected | scripts/install.sh:141 | No key names in the live config; auth lives outside the config dir.
- C-20261026-17 | 2026-10-26 | security | low | high | rejected | Backup pruner deletes any backup-* directory, not only its own | scripts/install.sh:149
  - rebuttal | rejected | scripts/install.sh:143 | Unchanged by this diff; pre-existing install behavior, out of scope here.
- C-20261026-18 | 2026-10-26 | security | low | medium | rejected | --db accepts any existing file, so a typo can target an unrelated SQLite DB | skills/prune-sessions/scripts/prune_sessions.py:69
  - rebuttal | rejected | skills/prune-sessions/scripts/prune_sessions.py:198 | Resolution order is documented and missing-table errors abort.
- C-20261026-19 | 2026-10-26 | data-integrity | high | high | rejected | D-20261026-04 ships a trap the same diff is said to fix | scripts/test_merge_config.py:78
  - rebuttal | rejected | scripts/merge-config.py:66 | Verified false: an absent key is re-seeded, so the trap stands and the entry is accurate.
- C-20261026-20 | 2026-10-26 | data-integrity | high | high | addressed | D-20261026-05 says the CONVERGED wording fix is pending; this diff lands it | docs/discovery/DISCOVERY.md:12
  - rebuttal | addressed | docs/discovery/DISCOVERY.md:12 | Rewritten as an outcome in this ship.
- C-20261026-21 | 2026-10-26 | data-integrity | low | high | addressed | Evidence pack misstated the roster delta and omitted this ledger | docs/rulebook/roster.md:42
  - rebuttal | addressed | docs/rulebook/roster.md:42 | Actual delta is one row; lenses found the real surface regardless.
- C-20261026-22 | 2026-10-26 | reliability | medium | high | addressed | A failure after rm -rf leaves a partial live config, restorable only from a backup dir | scripts/install.sh:55
  - rebuttal | addressed | scripts/install.sh:45 | User approved install; the live config tree is copied to tmp first, so rollback is a copy back.
- C-20261026-23 | 2026-10-26 | reliability | low | high | rejected | A preserved live models.yaml could disagree with shipped generated agents | scripts/install.sh:85
  - rebuttal | rejected | models.yaml:1 | Verified byte-identical to the live copy, so regeneration stays consistent.
- C-20261026-24 | 2026-10-26 | maintainability | medium | high | addressed | The prune-sessions vertical is a new feature riding a retune push | skills/prune-sessions/SKILL.md:1
  - rebuttal | addressed | skills/prune-sessions/SKILL.md:1 | One commit follows the push directive; a file-level split would put the Downloads doc change in the prune commit.
- C-20261026-25 | 2026-10-26 | correctness | high | high | addressed | Docstring claims a removed key stays removed; the file's own test proves re-seeding | scripts/merge-config.py:28
  - rebuttal | addressed | scripts/merge-config.py:28 | Wording corrected to present-value-wins; behavior unchanged.
- C-20261026-26 | 2026-10-26 | correctness | medium | high | addressed | Test named survives_removal asserts present-value-wins, not removal | scripts/test_merge_config.py:63
  - rebuttal | addressed | scripts/test_merge_config.py:63 | Renamed to state what it asserts.
