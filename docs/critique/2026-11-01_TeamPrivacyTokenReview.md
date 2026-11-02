# Critique Ledger: Team Privacy, Token Cost, and Harness Review

- Goal: redteam the agent team this repo ships, for privacy gaps, token waste, and 2026 harness-practice gaps
- Started: 2026-11-01
- Branch: main
- Lens set: cost, compliance, correctness, maintainability

## Findings

- C-20261101-01 | 2026-11-01 | compliance | high | high | addressed | Default go runs under a Go 0-day no-training ZDR, but unblocking DeepSeek needs Region=Global and no doc said so | README.md:41
  - rebuttal | addressed | research corrected the claim | Go is ZDR now, validity ends 2026-11-30
- C-20261101-02 | 2026-11-01 | compliance | high | high | addressed | Burn and prune deleted DB rows only, leaving tool-output and session diffs on disk, and the DB was mode 0644 | scripts/session_artifacts.py
  - rebuttal | addressed | verified by stat and grep | artifacts now unlinked, DB hardened to 0600
- C-20261101-03 | 2026-11-01 | compliance | medium | high | addressed | Sample config shipped no read denies, so auth.json and credential paths were never denied | opencode.json.sample:6
- C-20261101-04 | 2026-11-01 | compliance | medium | high | addressed | Redteam packs went world-readable to /tmp with private code and no cleanup | skills/redteam/SKILL.md:80
- C-20261101-05 | 2026-11-01 | compliance | medium | medium | addressed | Zhipu GLM terms were unassessed for 5 review seats | https://docs.z.ai/legal-agreement/privacy-policy
  - rebuttal | addressed | coding plan is no-training, data stored in Singapore | retention period still unconfirmed
- C-20261101-06 | 2026-11-01 | compliance | medium | high | rejected | The 7-day retention policy is manual and no cron or timer ships, so nothing enforces it | skills/prune-sessions/SKILL.md:10
  - rebuttal | rejected | user decision 2026-11-01 | keep manual, an auto-prune can race a live session
- C-20261101-07 | 2026-11-01 | cost | high | high | addressed | The 90 percent gate summed 30 days from the session DB while prune deletes rows past 7 days, so it forgot month-to-date spend | scripts/usage_archive.py
  - rebuttal | addressed | verified by synthetic DB run | archive now survives prune
- C-20261101-08 | 2026-11-01 | cost | medium | high | addressed | cost-report and check_usage hardcoded duplicate price tables and disagreed live | scripts/pricing.py
- C-20261101-09 | 2026-11-01 | cost | medium | high | addressed | The plan 50 percent weekly allowance cap was never checked | scripts/check_usage.py:17
- C-20261101-10 | 2026-11-01 | cost | low | high | addressed | Global and project AGENTS.md are byte-identical and both load, re-paying duplicated tokens per request | scripts/check_duplicate_agents.py
- C-20261101-11 | 2026-11-01 | cost | low | medium | addressed | Cold-cache resumes were unguarded, now the guard fires at 60 minutes idle and 50k context, both env tunable | plugins/stale-session-guard.js:5
- C-20261101-12 | 2026-11-01 | correctness | high | high | addressed | git-guard missed bash -c, git -C, /usr/bin/git, quoted --hard, +main force push, and checkout dot | plugins/git-guard.js:1
  - rebuttal | addressed | verified by node classify | six of six bypass forms now BLOCKED
- C-20261101-13 | 2026-11-01 | correctness | medium | high | addressed | ship-changes claimed the guard blocks rebase and force-push, which it did not | skills/ship-changes/SKILL.md:75
- C-20261101-14 | 2026-11-01 | maintainability | medium | high | addressed | INSTALL said 2 commands, the installer ships 4 | INSTALL.md:9
- C-20261101-15 | 2026-11-01 | maintainability | medium | high | addressed | Doctrine text contradicted the go assignment, and 56 generated agents churn on most commits | models.yaml:144
- C-20261101-16 | 2026-11-01 | maintainability | low | high | addressed | AGENTS.md assigned project edits to subagents but chief grants edit allow, so no permission enforced the split | AGENTS.md:9
- C-20261101-17 | 2026-11-01 | compliance | medium | high | addressed | Snapshot store outlived burn, opt-in gc now removes only unreferenced snapshot dirs | scripts/snapshot_gc.py
- C-20261101-18 | 2026-11-01 | compliance | low | high | addressed | README exposed subscription terms and expiry dates, now generalized to provider-level facts | README.md:43
