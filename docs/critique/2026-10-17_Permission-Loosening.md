# Critique Ledger: Permission Loosening

- Goal: Prove the uncommitted permission changes are safe to commit and deploy, weighting prompt-injection (secret exfiltration, harness self-rewrite) and accidental destructive edits equally.
- Started: 2026-10-17
- Branch: main

## Findings

- C-20261017-01 | 2026-10-17 | security | high | high | addressed | grep skips read denies; grep allow prints denied files in allowed roots | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/tool/grep.ts#L40
  - rebuttal | addressed | INSTALL.md:118 | user accepted residual exposure; docs say denies gate the read tool only.
- C-20261017-02 | 2026-10-17 | security | high | high | addressed | bash skips read denies; interpreter one-liners bypass its path scan | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/tool/shell.ts#L29
  - rebuttal | addressed | INSTALL.md:118 | user accepted residual exposure; docs say denies gate the read tool only.
- C-20261017-03 | 2026-10-17 | abuse | high | high | rejected | Downloads .. traversal defeats the config-dir guard | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/tool/external-directory.ts#L32
  - rebuttal | rejected | `node -e path.join('/Users/e/Downloads/../.config/x','*')` | path.join normalizes .. so the glob asks instead of matching; verifier V1 FAIL.
- C-20261017-04 | 2026-10-17 | abuse | high | medium | addressed | symlink in an allowed root reaches the config dir | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/tool/external-directory.ts#L33
  - rebuttal | addressed | INSTALL.md:116 | user accepted the speed-bump wording and kept Downloads.
- C-20261017-05 | 2026-10-17 | abuse | high | high | addressed | role bash allow overrides global bash rules under findLast | agents/roles/chief.md:10
  - rebuttal | addressed | agents/roles/chief.md:10 | user accepted unattended autonomy over a per-command checkpoint.
- C-20261017-06 | 2026-10-17 | security | medium | high | addressed | **/mnt/** allowlists any dir named mnt on any volume | `opencode debug config`
  - rebuttal | addressed | INSTALL.md:116 | user accepted the breadth in the 2026-10-17 walkthrough; docs state the match semantics.
- C-20261017-07 | 2026-10-17 | security | medium | high | addressed | deny list missed .envrc .netrc .npmrc keys tfvars kube docker vault creds | `opencode debug config`
  - rebuttal | addressed | `opencode debug config` | added bare and **/ twin denies for each class.
- C-20261017-08 | 2026-10-17 | abuse | medium | high | addressed | /var/folders/* allowed the whole DARWIN_USER tree | `opencode debug config`
  - rebuttal | addressed | v1.19.3 agent.ts:110 | removed both temp entries; defaults already whitelist Global.Path.tmp (verifier V6).
- C-20261017-09 | 2026-10-17 | correctness | medium | high | addressed | internal reads are worktree-relative; **/ denies miss root-level keys | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/tool/read.ts#L257
  - rebuttal | addressed | `opencode debug config` | added bare twin patterns for each deny class (verifier V3 PASS).
- C-20261017-10 | 2026-10-17 | correctness | low | high | open | matching is case-sensitive; a MNT dir on APFS never matches the allow | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/core/src/util/wildcard.ts#L13
- C-20261017-11 | 2026-10-17 | maintainability | high | high | rejected | INSTALL says always is session-only; v1.19.3 keeps it in memory | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/permission/index.ts#L145
  - rebuttal | rejected | verifier V5 PASS | always approvals live in InstanceState memory; nothing persists; docs agree.
- C-20261017-12 | 2026-10-17 | maintainability | high | high | addressed | INSTALL claimed agents cannot rewrite the harness unattended | INSTALL.md:116
  - rebuttal | addressed | INSTALL.md:116 | reworded to a speed bump naming the symlink and bash paths.
- C-20261017-13 | 2026-10-17 | maintainability | medium | high | addressed | INSTALL called the built-in .env rule a deny; it is ask | https://github.com/anomalyco/opencode/blob/v1.19.3/packages/opencode/src/agent/agent.ts#L132
  - rebuttal | addressed | INSTALL.md:120 | wording corrected to ask (verifier V4 PASS).
- C-20261017-14 | 2026-10-17 | maintainability | low | high | addressed | bare ~ expands to an exact path that matches no external resource | INSTALL.md:116
  - rebuttal | addressed | INSTALL.md:116 | now warns against ~/* and a top-level ** instead.
- C-20261017-15 | 2026-10-17 | security | low | medium | rejected | webfetch default allow permits exfiltration; pre-existing, not widened here | `git diff -U0`
  - rebuttal | rejected | `git diff -U0` | the diff adds no webfetch rule and does not widen egress.
- C-20261017-16 | 2026-10-17 | maintainability | high | high | addressed | read-deny paragraph sold protection a bash-capable agent bypasses | INSTALL.md:118
  - rebuttal | addressed | INSTALL.md:118 | paragraph now states the denies gate the read tool only.
- C-20261017-17 | 2026-10-17 | maintainability | low | medium | rejected | docs/discovery and memory edits are out of this changeset | `git status`
  - rebuttal | rejected | `git status` | DISCOVERY edits predate this session; the memory index is local, not in the repo.
