# Handoff: Agent-OS Hardening And Redteam Pickup

- Date: 2026-10-11.
- Repo: /Users/e/mnt/bnk/cs/opencode-agent-os (branch `grill-skill`).
- Companion: /Users/e/mnt/bnk/cs/Log_Builder (branch `main`).

## Start Here (Resume Prompt)

Paste into a fresh OpenCode session (restart first so the newly installed config loads). Read this file, run the verify commands, then run the `redteam` skill (or `/redteam`) with this goal:

> Analyze the opencode-agent-os plugin for runtime cost and behavior across the whole plugin surface (agents, skills, commands, config, `scripts/install`, docs, and the installed global layout). Converge on evidence and put only human-only decisions to the user.

Scope chosen by the user: "Runtime cost and behavior" plus "Whole plugin surface". The operator owns the ledger; write it to `docs/critique/2026-10-11_PluginRuntimeCost.md`.

## Current State

Done this session:

- Retired the discovery orphan-archive warning; the validator now keeps only the filename-vs-heading check. Re-vendored to Log_Builder. See `D-20261010-07`.
- Renamed the critique feature: `grill` to `redteam`, `adversary` to `redteamer`, `adjudicator` to `referee`; dropped `product-critic` and `compliance-officer`. See `D-20261010-08`.
- Redteam audit of the roster: only `photo-generator` was droppable. See `D-20261011-01`.
- Demoted `photo-generator` to an explicit-only command plus a rulebook reference. See `D-20261011-02`.
- Trimmed `chief.md` from 97 to 85 lines and offloaded two sections. See `D-20261011-03`.
- Added `apply-models.py --check` and wired it into `check.sh`. See `D-20261011-04`.
- Patched `install.sh` to drop renamed or removed plugin commands. See `D-20261011-05`.
- Installed to `~/.config/opencode`: 42 agents, 13 skills, 4 commands; backup at `~/.config/opencode/backup-2026-10-11_124015`.

In progress / not started:

- The redteam run itself; this handoff sets it up.
- Nothing is committed. The whole change set is uncommitted in the working tree.

Per-repo branch state:

- `opencode-agent-os`: branch `grill-skill`, `HEAD` `da8adb6`, large uncommitted change set.
- `Log_Builder`: branch `main`, uncommitted `scripts/check_discovery.py` plus `scripts/check_discovery.sha256` (re-vendored).

## Key Decisions

Recorded as IDs in `docs/discovery/DISCOVERY.md`; link them, do not restate: `D-20261010-07`, `D-20261010-08`, `D-20261011-01`, `D-20261011-02`, `D-20261011-03`, `D-20261011-04`, `D-20261011-05`.

Do not re-litigate the audit outcomes (`D-20261011-01`): the `context-curator`/`system-fixer` merge, the `phraser`/`wordsmith` fold, the visual-pair drop, the `tighten-prose` and `simplify-code` drops, the three-record-skill collapse, profile trimming, and `subagent_depth` removal were all refuted by deliberate contracts.

## Next Actions

1. Restart OpenCode so the installed config loads, then start a fresh session.
2. In that session, read this file and run the verify commands below.
3. Run `redteam` with the stated goal and scope; build the ledger at `docs/critique/2026-10-11_PluginRuntimeCost.md`; converge and put only human-only decisions to the user.
4. Record the run's outcomes as `[decision]`/`[outcome]` entries in `docs/discovery/DISCOVERY.md` (Phase 8).

## Verify Commands

```bash
cd /Users/e/mnt/bnk/cs/opencode-agent-os
scripts/check.sh                                  # expect: all checks passed
python3 scripts/apply-models.py --check            # expect: generated agents fresh
ls -1 ~/.config/opencode/agents | wc -l            # expect: 42
ls -1 ~/.config/opencode/commands                  # expect: engineer-prompt, fix-bug, photo-generator, redteam
git -C /Users/e/mnt/bnk/cs/opencode-agent-os status --short
```

If any command diverges from the expected output, note it before proceeding.

## Open Risks

- Config is installed but this session is pinned to the pre-install config: its crew is still `adversary`/`adjudicator` and its skill list is `grill`. Only a restarted session exposes `redteamer`/`referee`, the `/redteam` command, and the `redteam` skill.
- The working tree is large and uncommitted; do not assume `HEAD` reflects the described state. Committing is the user's call via `ship-changes`.
- `install.sh` preserves user command files and only drops an explicit stale list (currently `grill.md`); a future command rename must be added there.
- `apply-models.py` reads the repo `models.yaml`, not the installed copy; the installed `models.yaml` is preserved across reinstalls and may be an older schema.
