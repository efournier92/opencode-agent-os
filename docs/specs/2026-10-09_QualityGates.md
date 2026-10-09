# Quality Gates: Proof-Enforced Test-First Discipline For Builder Agents

Branch context: `quality-gates` (cut from `main`). This spec is system-only: role docs, skill docs, one command doc, one rulebook file, and a glossary. The lecoursville pilot is a separate follow-up spec.

## Context And Motivation

- Builder agents today verify via a done-check command only (`agents/roles/builder.md:29`); nothing obliges a change to arrive with tests that constrain it, and `implement-spec` writes tests after implementation (`skills/implement-spec/SKILL.md:48-49`).
- The failure mode this fixes: a test written after the implementation asserts current behavior instead of intended behavior, and passes trivially; coverage alone cannot distinguish the two.
- Robert C. Martin's 2026 guidance rejects imposing human rituals (write-order TDD) on agents, because agents drift back to function-then-test, while endorsing deterministic tools as the enforcement layer. Sources: https://victorinollc.com/thinking/impose-values-not-disciplines-on-agents (2026-09-11, analysis of the August 2026 Matt Pocock interview) and https://blog.alexrusin.com/uncle-bob-ai-coding-agents/ (2026-08-20). His worker-calibrated CRAP numbers: below 4 for humans, 6 for agents, possibly 8. This spec adopts order-independent proof enforcement and starts at threshold 8, tightening to 6 later.
- The enforcement unit is one command per implementation task, the quality gate, with three components: green proof, red proof, CRAP check. The term quality gate avoids collision with the Ruby framework and with the existing `npm run e2e:gate` in other repos.
- Cost constraint: the gate is exit codes and one shell call, not conversation; no new agent dispatches and no per-step policing. The plugin is domain-agnostic, so detailed mechanics live in one on-demand rulebook file while role docs carry obligations and pointers.
- The design survived five critic passes during this session (plan red-team, tooling feasibility, no-spec policy, full-design consistency, fix-bug contradiction). Their findings are folded in: /tmp-based revert instead of stash, no bare source paths fed to the test runner, assertion-failure parsing, hunk-scoped CRAP, explicit exemption statuses, and verifier routing that never re-runs the destructive proof.

## Glossary

- Quality gate: the single per-task command that runs the green proof, the red proof, and the CRAP check.
- Green proof: targeted tests pass on the final tree.
- Red proof: the same targeted tests fail when the change is absent; the order-independent form of "prove it fails first".
- CRAP check: per-function Change Risk Anti-Patterns score from cyclomatic complexity and coverage, `comp^2 * (1 - cov)^3 + comp`, threshold 8.
- Gate artifact: the timestamped log file the gate writes; its path is quoted in builder output and audited by the verifier.
- Gate command: the repo-provided executable entry point (a `quality-gate` script) or the rulebook's fallback manual procedure.
- Status vocabulary: `GATE-EXEMPT`, `NO-SPEC`, `RED-EXEMPT`, `RED-UNPROVABLE`, `CRAP-FAIL`, `CRAP-UNAVAILABLE`.

The four core terms are also written to `docs/GLOSSARY.md` by this spec (requirement R7).

## Current State

- `agents/roles/builder.md:26-33` Contract: input required, scope discipline, code minimalism, verify before returning, comment discipline, never commit, discovery candidates, stuck rule. No test or quality obligation exists.
- `agents/roles/builder.md:37` Output: files changed, done-check result, assumptions, undone work.
- `skills/implement-spec/SKILL.md:48-51` Workflow: implement in dependency order (step 5), then write tests (step 6), fix one failing test at a time (step 7), final verification runs tests (step 8).
- `skills/implement-spec/SKILL.md:30` Hard rule 9: no tests for pure wiring. `skills/implement-spec/SKILL.md:32` Hard rule 11: dirty tree stops the run instead of stashing.
- `commands/fix-bug.md:26` two independent red runs with a frozen check; `:30` and `:34` revert via `git stash` per `docs/rulebook/stash-discipline.md`; `:38` independent verifier dispatch.
- `agents/roles/verifier.md:16` read-only on code; `:27` never edits files; `:28-29` command-backed behavioral evidence; `:34` tabular output.
- `agents/roles/chief.md:42` decompose assigns scope, done-check, and owner; `:66` nontrivial done claims route to verifier.
- `AGENTS.md:11-16` delegation contract; `AGENTS.md:25-26` verify-before-done. This spec does not change either.
- `docs/rulebook/` holds roster, model-profiles, markdown-style, and stash-discipline; no quality-gate contract exists.
- `scripts/check.sh:16-25` runs doc budget, unit tests, markdown lint, and discovery check; `.githooks/pre-commit:10` invokes it; CI runs it as well.
- `scripts/test_doc_budget.py:30-35` caps context files at 200 lines and the always-loaded pair at 120; `:45-51` governs `agents/roles/*.md`, `agents/generated/*.md`, and `skills/*/SKILL.md`; `:72-98` verifies referenced rulebook files resolve.
- `scripts/apply-models.py` regenerates `agents/generated/<role>-<profile>.md` from `agents/roles/*.md` and `models.yaml` for every profile.
- Spec naming convention is `docs/specs/YYYY-MM-DD_TopicName.md`; older files use kebab case.
- No `docs/GLOSSARY.md` exists.
- Grounded discovery entries: fix-bug shipped (`docs/discovery/DISCOVERY.md:32`), implement-spec branch and dirty-tree rule (`docs/discovery/DISCOVERY.md:28`), create-spec question-tool convention (`docs/discovery/DISCOVERY.md:25-26`).

## Goals

- Every behavior-changing builder task emits machine-checkable evidence: green proof, red proof, and a CRAP result or an explicit `CRAP-UNAVAILABLE`.
- The contract is defined once in `docs/rulebook/quality-gates.md` and referenced by every role or skill doc that must honor it.
- Enforcement is proof-based; write order is not policed. Tests-first remains the preferred recipe inside `implement-spec`, where sequencing costs nothing.
- The gate costs one shell call and adds no agent dispatches; verifier routing changes only where it must: audit the artifact for small diffs, re-run green and CRAP on nontrivial diffs, never the red proof.
- Exempt classes (`GATE-EXEMPT`, `RED-EXEMPT`, `NO-SPEC`) are explicit, visible, and auditable; silent skipping never happens.
- `fix-bug` uses the same /tmp-backed revert procedure as the gate, removing its stash dependency.
- All additions stay inside doc budgets and pass `scripts/check.sh`.

## User Stories

1. As the operator, I want builder done-claims for behavior changes backed by red and green evidence, so that "tests pass" cannot mean "tests were written to match the implementation".
2. As the operator, I want the gate to run as one command, so discipline costs one shell call instead of coordination turns.
3. As the operator, I want CRAP pressure scoped to changed functions only, so legacy complexity does not block ordinary edits while new complexity stays bounded.
4. As the operator, I want CRAP reporting simple and honest (8 now, 6 later), so simpler code is chosen incrementally without refactor waves.
5. As a builder, I want the full contract in one referenced file (components, statuses, fallback), so I can comply without guessing.
6. As a builder, I want explicit exemption statuses, so docs, config, test-only, and declared-refactor tasks are not blocked but remain visible in the evidence.
7. As a builder, I want a defined fallback when a repo has no gate command, so I am never stuck and never skip silently.
8. As a verifier, I want a non-destructive re-run mode (green and CRAP only) and an audit path for small diffs, so I can certify gate claims while staying read-only on code.
9. As a future adopter repository, I want the contract precise enough to implement a conforming gate command without re-deriving decisions.
10. As the user, I want the term quality gate used consistently, never bare "the gate", so naming does not collide with the Ruby framework or with the existing e2e gate in other repos.
11. As the user, I want fix-bug's revert mechanism aligned to the /tmp procedure, so one revert mechanism serves the whole system.
12. As the maintainer, I want the additions budgeted and linted, so always-loaded context stays cheap.

## Non-Goals

- No application-repo changes; the lecoursville pilot is a separate follow-up spec.
- No CI wiring and no new workflows.
- No mutation testing.
- No CRAP ratchet or no-spec ratchet baseline yet; tightening shares one deferred trigger defined in the rulebook.
- No runtime plugin or hooks; enforcement stays prompt contracts plus command exit codes.
- No new agent roles, skills, or commands.
- No `AGENTS.md` changes.
- No stack-specific executable code in this repo; the rulebook is normative text plus reference notes.

## Prerequisites

- `docs/rulebook/` is the established home for on-demand reference material.
- `scripts/apply-models.py` and `scripts/check.sh` work on `main` today (branch `main`, clean tree).
- The follow-up pilot spec implements the first conforming gate command in `lecoursville`; it is explicitly out of scope here.

## Design Principles

- Deterministic tools over prompt prose: a rule that lives only in prose is a guideline; a rule that runs as a command is a rail.
- Evidence over intent: proofs and artifacts, not self-reports.
- Order-independent proofs: enforce that tests constrain the change, not when the test was typed.
- One command, one artifact, three evidence lines.
- Fail-visible: every exemption and unavailability prints its exact status vocabulary.
- Cheapest seam: prose changes ride the existing `check.sh`; the contract's runtime behavior is validated by the pilot spec.
- Thresholds are properties of the worker, not of the standard: 8 for agents now, 6 later.

## System Requirements

### R1. New File: `docs/rulebook/quality-gates.md`

Create the file with the normative content below, organized in eight sections. Target under 130 lines. The wording below is normative; light copy-editing for lint compliance is allowed as long as meaning does not change.

Section 1, Purpose. Two or three sentences: the quality gate is the per-task enforcement of the value "code arrives with tests that constrain it"; prompts decay, commands do not; it applies to behavior-changing code in any repo that has adopted a gate command; the fallback applies elsewhere.

Section 2, Components.

- Green proof: run the targeted tests for the changed behavior on the final tree via the repo's test runner. PASS requires zero failing tests parsed from structured output (JSON reporter), never stdout scraping.
- Red proof: back up changed non-test source files to a per-invocation `/tmp` directory named with timestamp and PID; revert tracked files with `git checkout --`; remove new untracked source files by exact path from `git status --porcelain`; rerun the same test command; classify the result:
  - Valid red: at least one `assertionResults[].status === "failed"` in the JSON reporter output.
  - Valid red for a new file: zero executed assertions and an error matching `Cannot find module`, `ERR_MODULE_NOT_FOUND`, or `TS2307` that names exactly a removed path.
  - Gate FAIL: any other compile or collection error while the reverted tree should otherwise compile.
  - `RED-UNPROVABLE: <reason>`: zero executed assertions and no recognized missing-module signature; the gate fails with this status.
  - Restore every backup and verify `git status --porcelain` equals the pre-proof snapshot; any mismatch fails the gate and names the residue. Never use `git stash` for this procedure.
- CRAP check: per-function score `comp^2 * (1 - cov)^3 + comp`; complexity from the TypeScript AST; coverage from the run's lcov output; scope is functions whose source spans intersect the changed line ranges (`git diff -U0`); a zero-coverage function scores `comp * (comp + 1)`. Threshold is 8. Failures print `CRAP-FAIL <path>:<function> <score>`.
- Evidence: append a timestamped log artifact whose filename carries the git short sha and the time; quote its path plus the three evidence lines.

Section 3, Trigger Classes (first match wins).

- Behavior change: red proof plus green proof plus CRAP check.
- Declared refactor: green proof plus CRAP check; red proof skipped; the gate audits that the exported-symbol set is unchanged via AST diff, otherwise the task reclassifies as a behavior change and red proof is required.
- Docs, config, or test-only: print `GATE-EXEMPT: <class>`; the suite may still run; no red proof and no CRAP.
- Rule-9 wiring (thin glue per `skills/implement-spec/SKILL.md:30`): `RED-EXEMPT: rule-9 wiring <paths>` is valid only when no spec files exist or changed for those paths; the CRAP check still applies (thin wiring at complexity 2 passes at zero coverage); the verifier audits the path list.

Section 4, No-Spec Policy (Refined A).

- Precedence, first match wins:
  1. Classify each changed non-spec source file as NEW (added) or MODIFIED.
  2. NEW file not matching the allowlist: fail unless a sibling spec (same basename, `.spec.ts`) is added in the same diff.
  3. MODIFIED file with a sibling spec: red-provable; its spec joins the targeted test set.
  4. MODIFIED file without a sibling spec and not allowlisted: print `NO-SPEC <path>` and include the file in the CRAP set (hunk-scoped).
- Default allowlist entries are repo-relative globs for data and infrastructure only; additions require user approval. Starting set for TypeScript repos: `src/app/models/**`, `src/app/interfaces/**`, `src/app/constants/**`, `src/environments/**`, `**/*.module.ts`, `src/app/app-routing.module.ts`, `src/test-setup.ts`, `functions/src/test-support.ts`, `functions/src/index.ts`, `functions/src/config.ts`.
- Ratchet deferred: "the count of non-allowlist files lacking specs must not grow" is a future addition, not part of this contract.

Section 5, Gate Command Discovery (precedence).

1. A command path named in the dispatch or task.
2. Repo convention: a root `package.json` `quality-gate` script, or `scripts/quality-gate.sh`.
3. Fallback: the manual procedure in this rulebook (green and red proofs by hand) plus `CRAP-UNAVAILABLE: <reason>`; never skip silently.

Section 6, Evidence And Verification.

- The gate writes its log artifact and exits non-zero on any failure.
- The builder quotes the three evidence lines and the artifact path in its output.
- The verifier audits the artifact for small diffs; for nontrivial diffs it re-runs the gate's green proof and CRAP check in a non-destructive verify mode. It never runs the red proof and never uses `git stash`. The verifier's re-run is authoritative.

Section 7, Threshold Tightening (deferred).

- Keep threshold 8 until 20 consecutive gate logs contain no changed function scoring in the interval (6, 8]; then tighten to 6. This single trigger also covers the deferred per-function ratchet; no separate ratchet artifact is introduced now.

Section 8, Naming.

- The canonical term is quality gate; docs never say bare "the gate"; the metric component is the CRAP check.

### R2. `agents/roles/builder.md`

Exact edits:

- Add one contract bullet after `:29` (the verify-before-returning bullet):

> - **Quality gate**: when the task changes behavior, run the repo's quality-gate command once before returning: green proof, red proof, CRAP check. Quote the three evidence lines and the artifact path. With no gate command, follow `docs/rulebook/quality-gates.md` (manual proofs plus `CRAP-UNAVAILABLE`); exemptions print their exact status line.

- Extend the Output at `:37` to include gate evidence:

> Max ~25 lines: files changed (path + one line each); done-check command + result (quote the decisive line); quality-gate evidence lines and artifact path when a gate ran; assumptions made; anything left undone. Failure -> say `FAILED` + why, plainly; never dress partial work as done.

- The file grows from 37 to about 42 lines, well inside the 200-line cap.

### R3. `skills/implement-spec/SKILL.md`

Exact edits:

- Workflow reorder: step 5 becomes "Write the spec's tests first: service, model, and logic-layer focus, one test per behavior in the spec's test plan (hard rule 9 wiring excepted)." Step 6 becomes "Implement in dependency order (schema and data model first, then logic layer, then service layer, then API surface, then backfill, then caller refactors, then UI if applicable) until the tests are green."
- Add to hard rule 9: "Wiring stays test-exempt, but the CRAP check still applies to changed wiring; thin glue at complexity 2 passes at zero coverage."
- Add to hard rule 11: "The quality gate's temporary /tmp-backed revert is internal; it is not a dirty-tree stop, and the gate restores the tree before returning."
- Done When (`:57-59`) adds: "quality-gate evidence quoted (green, red, CRAP, or `CRAP-UNAVAILABLE`)."

### R4. `agents/roles/verifier.md`

Exact edits:

- Add one contract bullet after `:29`:

> - **Quality-gate verification**: audit the gate artifact for small diffs; for nontrivial diffs re-run the gate's green proof and CRAP check in verify mode (non-destructive). Never run the red proof, never `git stash`, never edit.

- The file grows from 34 to about 37 lines, inside the 200-line cap.

### R5. `agents/roles/chief.md`

Exact edits:

- Extend the Decompose bullet at `:42` with one clause: "implementation tasks name the quality-gate command when known (fallback discovery per `docs/rulebook/quality-gates.md`)."
- No other chief changes. Verification routing at `:66` stays as written because the verifier contract carries the audit-versus-re-run split.
- The file grows from 92 to about 93 lines, inside the 120-line cap.

### R6. `commands/fix-bug.md`

Exact edits:

- Replace the stash-based revert reference at `:30` with: "on the third failure, abort: report the re-dispatch count and the last error, and revert the partial fix with the /tmp backup, restore, and status check defined in `docs/rulebook/quality-gates.md` so the tree is clean or the residue is named."
- Replace the stash-based revert at `:34` with: "Revert the source fix only (per-invocation /tmp backup, `git checkout --`, restore, and post-status check per `docs/rulebook/quality-gates.md`), rerun the frozen check, and require red; then re-apply the fix."
- No other fix-bug changes; the Step 5 verifier dispatch stays.

### R7. New File: `docs/GLOSSARY.md`

Create the file with four entries in the documented format (bold term, blank line, a definition of what the concept is, then an `_Avoid_` list):

- **Quality gate**: One command run per behavior-changing implementation task, bundling green proof, red proof, and CRAP check. _Avoid_: rail, guardrail, bare "the gate".
- **Green proof**: Targeted tests pass on the final tree. _Avoid_: test pass, green run.
- **Red proof**: The same targeted tests fail when the change is absent, proving the tests constrain the change. _Avoid_: failing test, red run.
- **CRAP check**: Per-function risk score `comp^2 * (1 - cov)^3 + comp`, gated at 8 on changed functions. _Avoid_: crap score, complexity check.

### R8. Regeneration And Checks

- Run `python3 scripts/apply-models.py` to regenerate `agents/generated/` for the changed roles (builder, chief, verifier).
- Run `bash scripts/check.sh`; it must exit 0.

## Production Risks And Mitigations

- Prompt decay: the builder clause is prose and can be treated as a guideline. Mitigation: the verifier re-runs green and CRAP; evidence lines are mandatory in output; the rulebook carries deterministic mechanics.
- Cost creep: verifier re-runs are the main new cost. Mitigation: audit path for small diffs; no new dispatches; one shell call per task.
- Legacy friction via CRAP: mitigation is hunk-scoped function selection, threshold 8, and deferred tightening.
- False red classifications: mitigation is structured JSON reporter parsing with explicit signatures and the `RED-UNPROVABLE` status instead of a silent pass or fail.
- Dirty-tree residue from the revert: mitigation is the /tmp backup, exact-path restore, post-status snapshot check, and gate failure on residue; never stash.
- Reference drift between rulebook and future pilot: the pilot spec must implement this contract; any deviation revises the rulebook in the same change.
- Doc-budget or lint breakage: `check.sh` gates the change; headroom is verified (builder 37/200, verifier 34/200, chief 92/120, implement-spec 59/200).

## Rollout Plan

- Phase 1 (this spec): rulebook, glossary, builder, implement-spec, verifier, chief, fix-bug, regeneration, checks.
- Phase 2 (follow-up spec, separate): lecoursville pilot gate command: `package.json` `quality-gate` script, coverage providers, the Node wrapper, hunk-scoped CRAP, and bootstrap experiments (vitest lane resolution, lcov path, zero-test behavior). Not in this spec.
- Phase 3 (later): threshold 8 to 6 after 20 clean logs; per-function ratchet; other stacks; CI wiring.
- Adoption: any repo gains a gate by adding the command; until then the fallback keeps builders unblocked.

## Test Plan

Seam: `scripts/check.sh` (existing), confirmed during spec creation. No new unit tests; the contract's runtime behavior is validated by the lecoursville pilot spec.

- `bash scripts/check.sh` exits 0, which covers:
  - doc budget for edited `agents/roles/*.md` and `skills/*/SKILL.md` (200-line cap; always-loaded pair 120);
  - rulebook reference integrity: `docs/rulebook/quality-gates.md` resolves for every file referencing it (`scripts/test_doc_budget.py:72-98`);
  - markdown lint across the tree, including the new rulebook, glossary, and this spec;
  - the discovery check, unchanged.
- Manual checks during implementation:
  - `grep -n "quality-gate" agents/roles/builder.md skills/implement-spec/SKILL.md commands/fix-bug.md agents/roles/verifier.md` shows the intended references.
  - `agents/generated/builder-*.md` contains the new clause after regeneration.
  - `git status --porcelain` lists only the intended files plus `agents/generated/` updates.

## Summary Of Changes

- [ ] `docs/rulebook/quality-gates.md` created with the eight-section contract from R1.
- [ ] `agents/roles/builder.md` gains the quality-gate bullet and the output evidence line.
- [ ] `skills/implement-spec/SKILL.md` reorders tests before implementation; adds rule 9 and rule 11 notes; Done When requires gate evidence.
- [ ] `agents/roles/verifier.md` gains the quality-gate verification bullet.
- [ ] `agents/roles/chief.md` decompose clause names the gate command.
- [ ] `commands/fix-bug.md` reverts use the /tmp procedure.
- [ ] `docs/GLOSSARY.md` created with four terms.
- [ ] `agents/generated/` regenerated via `scripts/apply-models.py`.
- [ ] `bash scripts/check.sh` green.
- [ ] No `AGENTS.md` changes; no new roles, skills, or commands.

## Verification Steps

1. `python3 scripts/apply-models.py` after role edits.
2. `bash scripts/check.sh`; quote the decisive final lines.
3. `python3 scripts/lint-markdown.py docs/rulebook/quality-gates.md docs/GLOSSARY.md` for a narrower lint check (check.sh covers the whole tree).
4. Spot-read `agents/generated/builder-ds.md` for the new clause.
5. `git status --porcelain` review for unintended files.

## Open Questions

None. All decisions were resolved during spec creation; deferred items are explicit non-goals or rollout phases.
