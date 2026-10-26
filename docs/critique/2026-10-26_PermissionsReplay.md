# Critique Ledger: Permissions Replay

- Goal: Prove the permission changes in commit d3fc49d are safe to ship, weighting prompt-injection (secret exfiltration, harness self-rewrite) and accidental destructive edits equally.
- Started: 2026-10-26
- Branch: bench replay at f7ca2ac
- Lens set: correctness, abuse, security, cost

## Findings

- C-20261026-01 | 2026-10-26 | correctness | high | high | addressed | Artifact was not applied at dispatch, so three lenses attacked the pre-change tree until the operator applied it | `git -C /tmp/rta-bench diff f7ca2ac d3fc49d`
  - rebuttal | addressed | `git -C /tmp/rta-bench status --short` | Diff applied; 0 of 14 role files still carry read allow (verifier V9)
- C-20261026-02 | 2026-10-26 | abuse | high | high | open | 12 of 14 roles keep bash allow, which overrides the global bash ask, so an injected agent reads secrets with cat bypassing every read deny | agents/roles/builder.md:10
  - rebuttal | open | https://raw.githubusercontent.com/anomalyco/opencode/v1.19.3/packages/opencode/src/tool/shell.ts | Verifier V5: bash never consults read rules; V4: last match wins, so role bash allow beats global ask
- C-20261026-03 | 2026-10-26 | abuse | high | high | open | bash allow with no path gate rewrites the harness without a prompt, contradicting the shipped claim that harness edits keep prompting | INSTALL.md:117
- C-20261026-04 | 2026-10-26 | abuse | high | high | open | Recommending **/mnt/** allow makes a whole repos tree silent read and write for edit-allowed roles, so the bound is per name not per root | INSTALL.md:111
  - rebuttal | open | https://raw.githubusercontent.com/anomalyco/opencode/v1.19.3/packages/opencode/src/tool/external-directory.ts | Verifier V7: raw string match, no realpath; with wildcard crossing slashes a planted mnt symlink reaches home
- C-20261026-05 | 2026-10-26 | security | medium | high | open | The sample ships no read denies, so the secret denylist the change depends on is delegated to the user and protects nothing out of the box | opencode.json.sample:12
- C-20261026-06 | 2026-10-26 | security | medium | high | addressed | merge-config force-merges the /tmp allow on every install, silently reverting a user who hardened it | scripts/merge-config.py:24
  - rebuttal | addressed | `scripts/merge-config.py:31` | IF_ABSENT seeds the /tmp allow once; a user who removed it keeps it removed (tests at scripts/test_merge_config.py)
- C-20261026-07 | 2026-10-26 | correctness | medium | medium | open | The load-bearing claim that agent rules are appended last and win is untested anywhere in the repo | INSTALL.md:106
- C-20261026-08 | 2026-10-26 | correctness | medium | medium | rejected | Removing the read grants leaves read governed by the built-in default with no migration note for users who set read ask or deny | INSTALL.md:119
  - rebuttal | rejected | `INSTALL.md:120` | The added paragraph is the migration note; removing role read grants can only make a user read ask or deny more effective
- C-20261026-09 | 2026-10-26 | correctness | medium | medium | rejected | The paragraph says a wildcard matches slashes, which contradicts its own ~/mnt/** versus **/mnt/** distinction | INSTALL.md:112
  - rebuttal | rejected | `INSTALL.md:116` | Slash-crossing (trailing) and anchor position (leading) are orthogonal; verifier V8 confirms star crosses slashes, so the text is consistent
- C-20261026-10 | 2026-10-26 | abuse | medium | high | rejected | The documented symlink pivot from an allowlisted writable root into the config dir stays open and is shipping as known | INSTALL.md:116
  - rebuttal | rejected | `INSTALL.md:116` | Duplicate of C-03: direct bash writes already reach the config dir with no symlink, so the doc variant adds no mechanism
- C-20261026-11 | 2026-10-26 | abuse | medium | medium | open | Slash matching grants silent writes across the whole temp tree, allowing payload staging and volume exhaustion | INSTALL.md:113
  - rebuttal | open | https://raw.githubusercontent.com/anomalyco/opencode/v1.19.3/packages/core/src/util/wildcard.ts | Verifier V8 confirms star crosses slashes, so the temp-tree staging surface is real; severity drops to low
- C-20261026-12 | 2026-10-26 | abuse | low | medium | addressed | Allowlisting the browser Downloads directory gives injected agents a silent installer swap route | INSTALL.md:114
  - rebuttal | addressed | `INSTALL.md:111` | User decision: the Downloads entry and its prose are removed; nothing in the repo consumes that directory
- C-20261026-13 | 2026-10-26 | abuse | low | low | rejected | The recommended *.env deny plausibly never matches the canonical .env dotfile under common glob semantics | INSTALL.md:118
  - rebuttal | rejected | https://raw.githubusercontent.com/anomalyco/opencode/v1.19.3/packages/core/src/util/wildcard.ts | Verifier V8: pattern compiles to ^.*\.env$ and matches bare .env, so the deny recipe works
- C-20261026-14 | 2026-10-26 | correctness | low | high | open | No gate prevents a future role edit from re-adding read allow, which is the exact state this commit exists to remove | scripts/test_apply_models.py:94
- C-20261026-15 | 2026-10-26 | correctness | medium | high | open | INSTALL ships four more unverified upstream assertions: slash-crossing, tilde expansion, inherited read defaults, edit/bash split | `INSTALL.md:116`
  - rebuttal | open | `rg -n external_directory /tmp/rta-bench` | Verifier V3 and V7: no ordering test and no matcher in-repo; all glob-dependent findings inherit that dependence
- C-20261026-16 | 2026-10-26 | maintainability | medium | high | addressed | Delete the Downloads allowlist entry: nothing in the repo stages or consumes it, so it only widens silent-write surface | `INSTALL.md:114`
  - rebuttal | addressed | `INSTALL.md:111` | Downloads entry deleted; the ledger's own replay found no shipped consumer
- C-20261026-17 | 2026-10-26 | maintainability | medium | high | rejected | Delete the blanket **/mnt/** sample entry and its hedge: the text already tells users to add their own roots | `INSTALL.md:111`
  - rebuttal | rejected | `INSTALL.md:111` | User decision: keep **/mnt/** as the workspace-root example and retain the any-depth warning
- C-20261026-18 | 2026-10-26 | maintainability | low | high | open | Delete the symlink mechanism clause: it adds no mechanism beyond the bash channel already filed as C-03 | `INSTALL.md:116`
- C-20261026-19 | 2026-10-26 | maintainability | low | high | open | Delete the always-session sentence: no shipped sample or advice uses that option | `INSTALL.md:116`
