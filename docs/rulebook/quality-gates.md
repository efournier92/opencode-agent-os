# Quality Gates

The on-demand contract for the per-task quality gate. Roles and skills point here; the detailed mechanics live in this file so always-loaded context stays cheap.

## 1. Purpose

The quality gate is the per-task enforcement of one value: code arrives with tests that constrain it. Prompts decay, commands do not. It applies to behavior-changing code in any repo that has adopted a gate command; the manual fallback below applies everywhere else. A rule that only prose carries is a guideline; the gate command is the rail.

## 2. Components

- **Green proof**: run the targeted tests for the changed behavior on the final tree via the repo's test runner. PASS requires zero failing tests parsed from structured output (JSON reporter), never stdout scraping, and at least one executed assertion for each behavior the change introduces or modifies. A green run with zero executed assertions fails the green proof: a test that only imports the code constrains nothing.
- **Red proof**: back up changed non-test source files to a per-invocation `/tmp/quality-gate-<timestamp>-<pid>/` directory with a per-file manifest; print `GATE-BACKUP <dir>` and the one-line restore command before mutating, so an interrupted gate is recoverable from the backup. Confirm the index matches HEAD for every changed path first (a staged change reverts against the wrong baseline); if it does not, fail and name the staged path. Then:
  - revert tracked modified files with `git checkout --`;
  - remove new untracked source files by exact path from `git status --porcelain --untracked-files=all`, never a whole directory;
  - handle deletions and renames explicitly: a deleted file is restored from the backup, a rename is treated as a delete plus an add;
  - rerun the same test command; classify the result:
    - Valid red: at least one `assertionResults[].status === "failed"` in the JSON reporter output.
    - Valid red for a new file: the green proof executed assertions from the sibling spec, and the reverted run reports zero executed assertions with an error matching `Cannot find module`, `ERR_MODULE_NOT_FOUND`, or `TS2307` that names exactly a removed path. A new file whose spec executed no assertion in green is `RED-UNPROVABLE`.
    - Gate FAIL: any other compile or collection error while the reverted tree should otherwise compile.
    - `RED-UNPROVABLE: <reason>`: zero executed assertions and no recognized missing-module signature; the quality gate fails with this status.
  - Restore every backup and verify `git status --porcelain` equals the pre-proof snapshot; any mismatch fails the quality gate and names the residue. Never use `git stash` for this procedure.
- **CRAP check**: per-function score `comp^2 * (1 - cov)^3 + comp`; complexity from the TypeScript AST; coverage from the lcov of the green proof's targeted run. Scope is functions whose source spans intersect the changed line ranges (`git diff -U0`) and that the targeted run exercises. A changed function the targeted run does not exercise has no coverage signal and is excluded from the CRAP set; the green proof's assertion minimum carries its behavior constraint. A zero-coverage exercised function scores `comp * (comp + 1)`. Threshold is 8. Failures print `CRAP-FAIL <path>:<function> <score>`; when no lcov is available print `CRAP-UNAVAILABLE: <reason>`.
- **Evidence**: append a timestamped log artifact. The artifact lives in the repo's gitignored `.gate-logs/` directory, named with the git short sha and the time, and is written after the restore snapshot check so it never disturbs that check. Quote its path plus the three evidence lines.

## 3. Trigger Classes (First Match Wins)

The dispatch names the trigger class when it knows it; otherwise the builder classifies and prints the chosen class. The verifier re-derives the class from the diff and may reclassify.

- Behavior change: red proof plus green proof plus CRAP check.
- Declared refactor: green proof plus CRAP check; red proof skipped. Valid only when the dispatch declares it; the quality gate audits that the exported-symbol set is unchanged via AST diff. Because a same-signature change to a function body passes that audit, a declared refactor that changes any behavior reclassifies as a behavior change and requires red proof.
- Docs, config, or test-only: print `GATE-EXEMPT: <class>`; the suite may still run; no red proof and no CRAP. The class must match the diff: a `GATE-EXEMPT: config` claim touching non-config paths is a FAIL.
- Rule-9 wiring (thin glue per `skills/implement-spec/SKILL.md:30`): `RED-EXEMPT: rule-9 wiring <paths>` is valid only when no spec files exist or change for those paths; the CRAP check still applies (thin wiring at complexity 2 passes at zero coverage); the verifier audits the path list.

## 4. No-Spec Policy (Refined A)

Applies to TypeScript gate-command repos; other stacks use the gate command's own policy or the fallback.

Precedence, first match wins:

1. Classify each changed non-spec source file as NEW (added) or MODIFIED.
2. NEW file not matching the allowlist: fail unless a sibling spec (same basename, `.spec.ts`) is added in the same diff.
3. MODIFIED file with a sibling spec: red-provable; its spec joins the targeted test set.
4. MODIFIED file without a sibling spec and not allowlisted: print `NO-SPEC <path>` and include the file in the CRAP set (hunk-scoped).

- Default allowlist entries are repo-relative globs for data and infrastructure only; additions require user approval. Starting set for TypeScript repos: `src/app/models/**`, `src/app/interfaces/**`, `src/app/constants/**`, `src/environments/**`, `**/*.module.ts`, `src/app/app-routing.module.ts`, `src/test-setup.ts`, `functions/src/test-support.ts`, `functions/src/index.ts`, `functions/src/config.ts`.
- Ratchet deferred: "the count of non-allowlist files lacking specs must not grow" is a future addition, not part of this contract.

## 5. Gate Command Discovery (Precedence)

1. A command path named in the dispatch or task.
2. Repo convention: a root `package.json` `quality-gate` script, or `scripts/quality-gate.sh`.
3. Fallback: the manual procedure below, plus `CRAP-UNAVAILABLE: <reason>`; never skip silently.

Command contract: run the three components and exit non-zero on any failure; `quality-gate --verify` runs green and CRAP only (non-destructive) for the verifier.

Manual fallback (no gate command): run the targeted tests and capture the JSON reporter output for green; for red, follow the Section 2 backup, revert, and restore steps by hand and require a recognized red signature; report `CRAP-UNAVAILABLE: <reason>` when no AST or lcov tooling is present; write the `.gate-logs/` artifact with `GREEN-PROOF`, `RED-PROOF`, and `CRAP` lines. Print every status exactly, including `CRAP-UNAVAILABLE`; never substitute silence.

## 6. Evidence And Verification

- The quality gate writes its log artifact and exits non-zero on any failure.
- The builder quotes the three evidence lines and the artifact path in its output.
- Small diff: at most 2 non-test source files and 40 changed source lines (`git diff --shortstat`); the verifier audits the artifact only.
- Nontrivial diff: anything larger; the verifier re-runs the gate's green proof and CRAP check via `quality-gate --verify` (non-destructive). It never runs the red proof and never uses `git stash`; the verifier's re-run is authoritative. As the first audit step the verifier re-derives the trigger class from the diff.

## 7. Threshold Tightening (Deferred)

- Keep threshold 8 until 20 consecutive gate logs contain no changed function scoring in the interval (6, 8]; then tighten to 6. This single trigger also covers the deferred per-function ratchet; no separate ratchet artifact is introduced now.

## 8. Naming

- The canonical term is quality gate for the per-task contract and CRAP check for the metric component; docs never say bare "the gate". The plugin's own `scripts/check.sh` is a repo check, not a quality gate.
