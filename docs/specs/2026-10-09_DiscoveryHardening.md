# Discovery Hardening: Week-1 Pilot Retrofit For The Opted-In Discovery Index

Branch context: `main`. Supersedes the lifecycle, evidence, archive, and read-contract rules of `docs/specs/2026-10-03-progressive-discovery.md` after one week of pilot use in `opencode-agent-os`, `Log_Builder`, `emoji_to_text`, and `lecoursville`. Adds stable entry IDs, relevance-checked evidence, an archive directory, a vendored validator, and an opt-in proposal. No new agent role. No database.

## Context And Motivation

One week of pilot use produced the first real evidence about whether the opt-in discovery index works. The artifacts exist and are committed, so the idea is being used; the failures are governance and format failures, not disinterest.

- Volume and cadence are real: `opencode-agent-os/docs/discovery/DISCOVERY.md` is 8025 bytes with 35 entries over 4 active days; `Log_Builder/docs/discovery/DISCOVERY.md` is 6673 bytes with 39 entries over 4 active days.
- The evidence rule is gamed. `Log_Builder/docs/discovery/DISCOVERY.md:37` and roughly 24 other entries cite `docs/discovery/ARCHIVE.md` as their only evidence, which points at the archive's copy of the same entry rather than an artifact backing the claim. `scripts/check_discovery.py:32-52` only checks that a path exists and that a `:line` is in range, so self-citation passes.
- The archive is the real store and is unregulated. `Log_Builder/docs/discovery/ARCHIVE.md` is 16542 bytes, has 34 lines over the 240-character cap, and uses `[finding]`, which is not a valid type; `python3 scripts/check_discovery.py .../ARCHIVE.md` exits 1. The 8 KB and 240-character caps bind only the one file the validator is pointed at.
- Line citations rot. `docs/specs/2026-10-09_QualityGates.md:42` cites `docs/discovery/DISCOVERY.md:25-26, :28, :32`; newest-first insertion has moved those entries to `:27-28, :30, :34`, so the spec now cites the wrong entries.
- Cap pressure displaces knowledge. `opencode-agent-os` sits at 8025 of 8192 bytes after 4 active days, and the scopes `plugin/commit` and `plugin/naming` survive only in `ARCHIVE.md`, so the documented read (`grep DISCOVERY.md`, `skills/log-discoveries/SKILL.md:56`) can no longer reach them.
- Adoption stalled where history is densest. `emoji_to_text` maintained an 8-term glossary and 3 specs in the same window but has no index; `lecoursville` carries about 16 legacy `design_specs` files and no index. The opt-in rule (`skills/log-discoveries/SKILL.md:18`, "Never auto-create") has no activation path.
- Enforcement never leaves the plugin. `scripts/check.sh:25` runs the validator for the plugin only; no consumer repo runs it (`Log_Builder/.github/workflows/ci.yml:20-21` runs only rspec and rubocop), and `scripts/install.sh:52-72` ships no scripts into projects.
- The index is decision-heavy. 26 of 35 `opencode-agent-os` entries are `[decision]` whose evidence is the committed artifact itself, which is re-derivable from `git log`; the method's own skip test (`skills/log-discoveries/SKILL.md:44`) would reject most.
- Scope tokens drift. `Log_Builder` uses `services` for 20 of 39 entries and `repo` for 8, while `opencode-agent-os` hand-maintains a `Scope tokens:` header listing `plugin/commit` and `plugin/naming`, which no longer have live entries.
- The method contradicts itself. `docs/specs/2026-10-03-progressive-discovery.md:98` says mark a superseded line and never delete it; `skills/log-discoveries/SKILL.md:62` says delete it at reconcile. The conflict was logged on 2026-10-04 (`DISCOVERY.md:35`) and is unresolved after 5 days.
- The v1 spec deliberately ruled out a database (`docs/specs/2026-10-03-progressive-discovery.md:45`, "No per-entry machine format, database, or runtime plugin"). Week 1 does not overturn that: a committed SQLite store is a binary in git, is unreviewable in a diff, and would hide exactly the text-visible failures above. The scale of about 35 to 100 rows per repo does not justify it either. This spec keeps markdown canonical and treats a generated, non-committed query index or an out-of-repo usage store as future options, not deliverables.

## Glossary

Definitions the requirements depend on. Project domain terms live in `docs/GLOSSARY.md`; this spec stands alone for the implementer.

**Discovery entry**: one line in a discovery index recording a fact, decision, assumption, trap, question, or outcome, with evidence.

**Discovery index**: the committed file `docs/discovery/DISCOVERY.md` in an opted-in repository.

**Entry ID**: a permanent identifier of the form `D-YYYYMMDD-NN`, unique within a repository and never reused, assigned when an entry is first appended.

**Archive detail file**: a prose file at `docs/discovery/archive/<entry-id>.md` holding overflow or settled detail that no longer fits the index.

**External evidence**: a URL, an exact command, or a `path:line` whose path resolves outside `docs/discovery/`. The artifact that actually backs a claim.

**Self-citation**: evidence that points inside `docs/discovery/`, such as `docs/discovery/ARCHIVE.md` or an archive detail file. Permitted as supplementary detail, never as the only evidence for a typed entry.

**Scope token**: a lowercase slash token naming a subsystem, such as `plugin/skills`, used to select entries by grep.

**Reconcile**: the commit-time sweep in `ship-changes` that flushes, verifies, dedupes, supersedes, and stages discovery.

**Vendored validator**: the byte-identical copy of the plugin's `check_discovery.py` committed into an opted-in repository.

## Current State

- `docs/specs/2026-10-03-progressive-discovery.md` is the v1 design: format (`:88-93`), lifecycle (`:95-101`), read contract (`:111-115`), reconcile (`:130-141`), the database non-goal (`:45`), and the supersede contradiction (`:60`, `:98`).
- `skills/log-discoveries/SKILL.md` is the live method: opt-in (`:18`), caps (`:24`), format (`:36-40`), checkpoints (`:42-52`), read contract (`:56-57`), write contract (`:59-64`), reconcile (`:68`), verify (`:76-80`).
- `scripts/check_discovery.py` is the validator: constants (`:14-19`), entry regex (`:20-22`), existence-only evidence check (`:32-52`), entry check (`:55-66`), main (`:69-84`). It validates exactly one file and has no notion of IDs, self-citation, scope headers, or an archive.
- `scripts/test_check_discovery.py` is the unit seam: 11 tests (`:44-97`).
- `scripts/check.sh:24-25` runs the validator for the plugin only; `.githooks/pre-commit:10` execs `check.sh`; `.github/workflows/check.yml:18` runs `check.sh` on push and pull request.
- `scripts/install.sh:52-72` installs agents, skills, commands, and the rulebook into `~/.config/opencode`; it ships no scripts into any project.
- The plugin repo is public at `github.com/efournier92/opencode-agent-os`; all four repos are GitHub-hosted; no repo sets `core.hooksPath`.
- Reader and writer call sites: `agents/roles/chief.md:31,38,45`; `agents/roles/context-curator.md:31`; `AGENTS.md:37-38`; `skills/ship-changes/SKILL.md:52,79`; `skills/create-spec/SKILL.md:35,68`; `skills/write-handoff/SKILL.md:21`; `skills/capture-session/SKILL.md:14,114`; `skills/implement-spec/SKILL.md:45`; `commands/engineer-prompt.md:29,50`; `commands/fix-bug.md:26,42`; `README.md:11,55-60,139`.

## Goals

- Every entry carries a stable ID so other docs cite entries without depending on a line number.
- Evidence for `find`, `decision`, `trap`, and `outcome` names a real artifact outside `docs/discovery/`; self-citation no longer passes.
- The archive is a directory of prose detail files, exempt from caps, with link integrity checked, so the capped index and the uncapped detail store have separate, honest contracts.
- The caps bind the whole store: a validator run validates the index against its caps and the archive against its naming.
- The read contract reaches archived knowledge: grep the `docs/discovery/` directory, not one file.
- The header's scope-token list is exact and validator-enforced.
- Any opted-in repo can enforce the validator locally and in CI with a vendored, byte-identical copy and a drift check.
- A repo with durable specs or handoffs but no index gets a one-time opt-in proposal.
- The supersede rule is single-valued: reconcile deletes the superseded line and keeps the replacement; `git log` is the history.
- The checkpoint test rejects entries re-derivable from `git log` or existing project docs.

## User Stories

1. As a future agent scoping a task, I want each entry to have a stable ID, so that I can cite and re-find it after the index has grown.
2. As a spec author, I want to cite a discovery entry by ID, so that my citation does not break when a newer entry is inserted above it.
3. As an operator running reconcile, I want the validator to reject evidence that points inside `docs/discovery/`, so that a claim cannot satisfy the evidence rule by pointing at the index itself.
4. As a reader, I want evidence to name the artifact that backs a claim, so that one grep plus one open reaches ground truth.
5. As an operator, I want over-length or settled entries moved to a per-ID archive file, so that the capped index stays scannable without losing detail.
6. As a reader, I want the archive file for an entry reachable by a deterministic path, so that I can open it when an entry is load-bearing.
7. As a maintainer, I want the archive directory validated for naming and type integrity, so that it cannot silently rot the way a single unvalidated `ARCHIVE.md` did.
8. As an operator, I want the read contract to grep the whole `docs/discovery/` directory, so that an archived entry is still discoverable by scope.
9. As a maintainer, I want the header's scope-token list to match the live index exactly, so that the list never advertises a scope with no entries.
10. As a contributor to an opted-in repo, I want a vendored validator plus a pre-commit hook and a CI step, so that the caps are enforced without depending on a running agent session.
11. As the plugin maintainer, I want one command that writes the vendored copy and one that detects drift, so that the copies have a single writer and cannot silently diverge.
12. As an operator in a repo with specs but no index, I want a one-time opt-in proposal, so that adoption does not depend on someone remembering the rule.
13. As an operator, I want a single supersede rule (delete at reconcile, replacement keeps a new ID), so that the spec and the skill stop contradicting each other.
14. As a reader, I want the checkpoint test to name the `git log` and project-docs cases explicitly, so that decision-restating entries are not captured.
15. As the plugin maintainer, I want the format change covered by the existing unit seam, so that the rules are provable without a new test harness.
16. As a future agent, I want `emoji_to_text` and `lecoursville` to be offered opt-in on their next handoff, so that the repos with the most history stop re-exploring.

## Non-Goals

- No committed database, no SQLite file, no runtime query plugin. Markdown stays canonical (upholds `docs/specs/2026-10-03-progressive-discovery.md:45`).
- No generated query index or usage-telemetry store in this spec; both are deferred with named triggers in Open Questions.
- No change to `docs/GLOSSARY.md` or its format; the glossary was healthy in week 1.
- No change to `docs/handoffs/` content or `docs/specs/` naming.
- No auto-create of `docs/discovery/`; the opt-in proposal is a suggestion the user accepts or declines.
- No change to the validator's language or dependency surface (Python 3 standard library only).
- No global or cross-repo index; one index per opted-in repository.
- No migration of `lecoursville`'s or `emoji_to_text`'s docs beyond offering opt-in; they are not opted in.

## Prerequisites

- Python 3 available in each opted-in repo's CI (already true for the plugin, `Log_Builder`, and `emoji_to_text`).
- The choice to keep markdown canonical and skip a database, recorded here.
- The plugin repo stays public for the optional future reusable-workflow path; the vendored path does not depend on it.

## Design Principles

- Index, not content; detail by deterministic path, loaded only when load-bearing.
- Evidence or it does not happen; the evidence must back the claim, not restate it.
- Stable identity over positional identity; cite the ID, not the line.
- Separate contracts per store: the index is capped and typed; the archive is uncapped prose.
- Single writer: the operator owns the index; the plugin owns the canonical validator.
- Enforcement travels with the docs: a vendored, byte-identical, drift-checked copy in each opted-in repo.
- Markdown only, no binary artifact, so the failures that motivated this spec stay visible in a diff.

## Backend Requirements

This section covers the validator, the index and archive data layer, and the distribution scripts. There is no server.

### 1. Entry Format And Stable IDs

- New index line format: `- <id> | <YYYY-MM-DD> | [<type>] | <scope> | <finding> | <evidence>`.
- `<id>` grammar: `D-YYYYMMDD-NN`, where `NN` is a per-repo, per-day sequence starting at `01`, zero-padded to two digits, and may grow past two digits on a busy day. The date embedded in the ID must equal the `<YYYY-MM-DD>` field.
- IDs are permanent and unique within a repository. An entry keeps its ID when archived. A replacement entry for a superseded one gets a new ID.
- `<type>` stays one of `find`, `decision`, `assumption`, `trap`, `question`, `outcome`. `[finding]` is removed and treated as invalid; existing uses migrate to `[find]`.
- Rename the existing ENTRY_RE at `scripts/check_discovery.py:20-22` to match the six-field format and the ID grammar.
- The 240-character cap applies to the whole line, including the ID. The 8 KB cap applies to `docs/discovery/DISCOVERY.md` only. The v1 "roughly 100 lines" target at `docs/specs/2026-10-03-progressive-discovery.md:101` is dropped; the byte cap is the gate.

### 2. Evidence Validation

Replace the existence-only check at `scripts/check_discovery.py:32-52` with a class-based check.

- Parse the `<evidence>` field into tokens: URL tokens (contain `://`), command tokens (a backtick-quoted span in the raw line), and path tokens (end with `.md`, `.py`, `.sh`, `.yaml`, `.yml`, `.json`, or `.txt`).
- A path token that resolves under `docs/discovery/` is a self-citation. It is allowed to exist and resolve, but it does not count as external evidence.
- For `find`, `decision`, `trap`, and `outcome`: require at least one external evidence token (a URL, a command, or a path resolving outside `docs/discovery/`). Fail with `insufficient evidence: self-citation only` when none exists.
- For `assumption` and `question`: external evidence is not required; the field may name what would settle them.
- Keep the dead-path check (`dead evidence: <path>`) and the line-range check (`evidence line out of range: <path>:<line>`) for every path token, including self-citations.
- Commands are detected by backticks only; the validator cannot verify a command executed, and the spec accepts that (a command documents intent and is the strongest available form for external, non-file facts).

### 3. Archive Detail Files

- Location: `docs/discovery/archive/<entry-id>.md`, flat and ID-named.
- Contents: the first non-blank line is the heading `# <id>`; the next non-blank line is the original full entry line, verbatim, even past 240 characters; then prose detail. No size or line cap.
- The matching index entry keeps a short line of at most 240 characters that carries the load-bearing fact and at least one external evidence token. The archive file holds the overflow and is reached by the deterministic path; no link is required in the index line.
- When detail lives in a `capture-session` file outside `docs/discovery/`, the entry links it in `<evidence>`; that link is a normal path token and counts as external evidence, and it is the one permitted cross-record link.
- Retire the single-file archive. `Log_Builder/docs/discovery/ARCHIVE.md` and `opencode-agent-os/docs/discovery/ARCHIVE.md` are migrated (Rollout Plan step 5) and deleted.
- Validator archive checks (new): for each `docs/discovery/archive/*.md`, the filename stem must equal the `# <id>` heading, else fail `archive header mismatch: <file>`. An archive file with no live or known-deleted index entry prints `orphan archive: <file>` as a warning and does not fail the run. Index entries keep all type and cap checks; archive files are exempt from them.

### 4. Scope Tokens And The Header

- The index carries a header line `Scope tokens: <comma-separated, sorted, lowercase list>` listing exactly the scopes present in the live index.
- Validator check: every scope used by an index entry must appear in the header, and every header token must be used by at least one index entry; either mismatch fails with `undeclared scope: <token>` or `unused scope token: <token>`.
- Reconcile regenerates the header from the live entries, so the list cannot advertise a scope with no entries, the failure seen in `opencode-agent-os/docs/discovery/DISCOVERY.md:4`.

### 5. Index Lifecycle, Supersede, And Caps

- Append only. Newest first by date; within a day, order is not significant.
- Supersede: at reconcile, delete the superseded line and keep the replacement, which carries a new ID. `git log` holds the removed line. This is canonical and aligns `skills/log-discoveries/SKILL.md:62` with `docs/specs/2026-10-03-progressive-discovery.md:98`.
- Caps: entry at most 240 characters; `DISCOVERY.md` at most 8192 bytes. A line that cannot carry its content within 240 characters moves the overflow to `docs/discovery/archive/<id>.md`.
- Dedupe by ID (must be unique) and by normalized `<finding>` text at reconcile.
- Checkpoint test, strengthened and stated in the skill: do not capture an entry that `git log`, the README, a spec, or a rulebook already carries; a `[decision]` entry must name the rationale the committed diff does not, not restate the diff. This addresses the 26 `[decision]` entries at `opencode-agent-os/docs/discovery/DISCOVERY.md:8-42`.

### 6. Validator CLI And Exit Codes

- Keep `python3 scripts/check_discovery.py [path]`; the default target stays `docs/discovery/DISCOVERY.md` resolved against the repo containing the script (`scripts/check_discovery.py:14-15,69-77`), which is correct for a vendored copy at `<repo>/scripts/check_discovery.py`.
- Add a companion default for the archive directory: `docs/discovery/archive`. A single run validates the index and the archive directory together, so one command covers the whole store.
- Exit 0 when clean, 1 on any violation. Warnings (orphan archive) print to stdout and do not change the exit code.

### 7. Vendored Enforcement

- Canonical source stays `scripts/check_discovery.py` in the plugin.
- New script `scripts/vendor-discovery-check.sh <repo-path>`:
  - copies the canonical validator byte-identically to `<repo-path>/scripts/check_discovery.py`, creating `scripts/` if absent;
  - writes `<repo-path>/scripts/check_discovery.sha256` containing the canonical sha256;
  - prints the hook and CI snippet below; it does not modify `.githooks/` or CI, to avoid clobbering repo-local files.
- New mode `scripts/vendor-discovery-check.sh --check <repo-path>`: recompute the sha256 and exit 1 with a diff summary when the vendored copy is stale. Run it from the context-curator sweep (`agents/roles/context-curator.md:31`).
- Per-repo hook `.githooks/pre-commit`: `python3 scripts/check_discovery.py` (default path). The hook is active only after `git config core.hooksPath .githooks` in that clone; the spec requires the rollout to run that command and requires CI as the real gate.
- Per-repo CI step, added to the existing workflow (`Log_Builder/.github/workflows/ci.yml:16`): `python3 scripts/check_discovery.py`.
- `scripts/install.sh` explicitly does not change: it still ships only into `~/.config/opencode` (`scripts/install.sh:52-72`); vendoring is a per-repo operation.

### 8. Skill, Role, And Command Refactors

- `skills/log-discoveries/SKILL.md`: update the format block (`:36-40`) and caps (`:24`) to the six-field ID format; rewrite evidence rules (`:38`) with the self-citation ban and external-evidence classes; rewrite the read contract (`:56-57`) to grep the `docs/discovery/` directory and open `archive/<id>.md` by deterministic path; rewrite the write contract (`:61-64`) to the delete-at-reconcile rule and ID assignment; update the reconcile contract (`:68`) with ID uniqueness, header regeneration, and archive moves; update the verify list (`:76-80`) with the ID, self-citation, archive-header, and scope-header checks; add the opt-in proposal to the role section.
- `skills/ship-changes/SKILL.md:52`: add "outside `docs/discovery/`" to the evidence-resolution clause; add ID uniqueness, scope-header regeneration, and archive moves to the reconcile sweep. Keep `:79`.
- `skills/write-handoff/SKILL.md:21`: add the opt-in proposal: when the repo has `docs/specs/` or `docs/handoffs/` but no `docs/discovery/`, state once that the repo could opt in; never create the directory.
- `skills/capture-session/SKILL.md:14,114`: the entry now carries an ID, and the capture file link is a path token that counts as external evidence only when the capture is outside `docs/discovery/`; a typed entry still needs external evidence.
- `skills/implement-spec/SKILL.md:45`: read `docs/discovery/` by scope and cite entries by ID.
- `skills/create-spec/SKILL.md:35`: read `docs/discovery/` by scope; `:68` unchanged (specs are cited by path, not ID).
- `commands/engineer-prompt.md:29,50` and `commands/fix-bug.md:26,42`: grep the `docs/discovery/` directory and cite by ID.
- `agents/roles/chief.md:31,38,45`: grep the directory; reference entries by ID; keep the opt-in proposal in the handoff step.
- `agents/roles/context-curator.md:31`: run the vendored `--check`, patrol ID uniqueness, self-citations, archive orphans, header truth, and growth past the caps; move settled entries into archive detail files and delete re-derivable ones.
- `AGENTS.md:37-38`: keep the two-line opt-in gate; change the read rule from "grep DISCOVERY.md" to "grep `docs/discovery/`".
- `README.md:11,55-60,139`: document the ID format, the archive directory, the vendored check, and the opt-in proposal.
- `docs/specs/2026-10-03-progressive-discovery.md`: add a one-line note under the title that its lifecycle, evidence, archive, and read-contract rules are superseded by this spec, leaving the rest historical.
- Regenerate `agents/generated/*.md` with `python3 scripts/apply-models.py` after the role edits.

### 9. Adoption Activation

- The operator raises opt-in once, at handoff, when a repo has `docs/specs/`, `docs/handoffs/`, or `capture-session` files but no `docs/discovery/`.
- The proposal is one line in the handoff plus a yes/no question; a yes runs the rollout for that repo; a no is final until the user reopens it.
- Never auto-create. The v1 opt-in gate in `AGENTS.md:37` is unchanged.

### 10. Backfill And Migration

- Migrate the two live indexes (`opencode-agent-os`, `Log_Builder`) to the six-field ID format in the rollout, using the validator as the feedback loop; assign IDs per day in existing order.
- Migrate each existing `ARCHIVE.md` into `docs/discovery/archive/<id>.md` files and delete the single file.
- Rewrite or downgrade self-cited entries: give each typed entry one external evidence token, or downgrade it to `[assumption]`.
- Regenerate each `Scope tokens:` header from the migrated entries.
- Trim entries over 240 characters by moving overflow to the archive file.
- `emoji_to_text` and `lecoursville` are offered opt-in but not migrated.

## Frontend/UI Requirements

None. There is no TUI, web, or rendered surface. The deliverable is committed Markdown plus standard-library Python.

## Production Risks And Mitigations

- Format break invalidates every existing entry. Mitigation: the migration in step 10 is part of the implementing change, and the validator fails loudly on the old format so nothing ships half-migrated.
- Vendored copies drift. Mitigation: one writer (`vendor-discovery-check.sh`), a committed sha256, and a `--check` gate in the curator sweep. Revisit the reusable-workflow path when a third repo opts in or the rules change often.
- Hooks are inert without `core.hooksPath`. Mitigation: the rollout runs `git config core.hooksPath .githooks` per clone and treats CI as the real gate.
- Longer lines after adding IDs. Mitigation: the ID costs 14 to 16 characters; overflow moves to the archive rather than expanding the cap.
- A larger archive raises read cost. Mitigation: the read contract opens `archive/<id>.md` only for a load-bearing hit; the index stays the scan surface.
- Archive orphans accrete. Mitigation: the validator warns on orphans and the curator deletes detail files whose entry is gone and shipped.
- Concurrent sessions on one index still conflict (the v1 open risk at `docs/specs/2026-10-03-progressive-discovery.md:201`). Mitigation: unchanged; append-only lines, IDs reduce ambiguity, the curator resolves. Remains an open risk.
- Command evidence cannot be verified. Accepted; it is documented intent, not proof of execution.

## Rollout Plan

1. Rewrite `scripts/check_discovery.py` and extend `scripts/test_check_discovery.py`; run `scripts/check.sh`.
2. Add `scripts/vendor-discovery-check.sh` and verify `--check` against the plugin repo.
3. Apply the skill, role, command, `AGENTS.md`, and `README.md` edits in section 8; regenerate `agents/generated/*.md`; run `scripts/check.sh`.
4. Add the superseded note to `docs/specs/2026-10-03-progressive-discovery.md`.
5. Migrate `opencode-agent-os/docs/discovery/` to the new format (section 10); delete its `ARCHIVE.md`; run the validator to green.
6. Vendor the validator into `opencode-agent-os` itself and add the hook and CI step; run `vendor-discovery-check.sh --check`.
7. In `Log_Builder`: vendor the validator, migrate `DISCOVERY.md` and split `ARCHIVE.md` into archive detail files, add the hook and CI step, set `core.hooksPath`; run the validator to green.
8. Offer opt-in to `emoji_to_text` and `lecoursville` at their next handoff (no forced change).
9. Record the v2 decisions as `[decision]` entries in `opencode-agent-os/docs/discovery/DISCOVERY.md`, each pointing at this spec.

Steps 7 and 8 touch other repositories and are separate commits the user runs.

## Test Plan

Single seam: `scripts/test_check_discovery.py`. Doc edits are covered by the existing budget and lint checks.

Update the shared fixture at `scripts/test_check_discovery.py:17` to the six-field format with an ID, and keep the pass/fail helper. Add these cases:

- `test_missing_id_flagged`: a five-field entry fails.
- `test_duplicate_id_flagged`: two entries share an ID; fails.
- `test_id_date_mismatch_flagged`: ID `D-20261004-01` with date `2026-10-05` fails.
- `test_malformed_id_flagged`: `D-2026-10-04-1` fails the grammar.
- `test_self_citation_only_flagged`: a `[find]` whose evidence is `docs/discovery/ARCHIVE.md` fails.
- `test_self_citation_with_external_passes`: a `[trap]` whose evidence is `docs/discovery/archive/D-20261009-01.md` plus `src/a.rb:3` passes.
- `test_url_is_external_evidence`: a `[find]` with a URL and no path passes.
- `test_backtick_command_is_external_evidence`: a `[decision]` with `` `gh release list` `` and no path passes.
- `test_assumption_without_external_evidence_passes`: an `[assumption]` naming what would settle it passes.
- `test_scope_undeclared_flagged`: an entry uses `plugin/new` while the header omits it; fails.
- `test_header_extra_scope_flagged`: the header lists `plugin/gone` with no entry; fails.
- `test_archive_header_mismatch_flagged`: `archive/D-20261009-01.md` starts `# D-20261009-02`; fails.
- `test_archive_oversize_allowed`: a 12 KB `archive/<id>.md` with a matching header exits 0.
- `test_orphan_archive_warns`: an archive file with no entry exits 0 and prints `orphan archive`.
- Keep and update: `test_missing_evidence_path_flagged`, `test_line_out_of_range_flagged`, `test_long_entry_flagged`, `test_oversized_file_flagged`, `test_url_and_command_tokens_ignored` (rename to external-evidence), `test_glob_token_ignored`, `test_evidence_resolves_against_target_repo_root`, `test_missing_evidence_in_target_repo_flagged`, `test_default_target_resolved_from_repo`, `test_missing_cli_path_flagged`.

Other checks:

- `python3 scripts/test_doc_budget.py` passes after the `log-discoveries` skill edit (it must stay under 200 lines; split rationale into a skill sibling if needed).
- `python3 scripts/lint-markdown.py .` passes on every changed Markdown file.
- `python3 scripts/check.sh` passes.
- `scripts/vendor-discovery-check.sh --check <repo>` exits 1 against a deliberately edited copy and 0 against a fresh vendor.

## Summary Of Changes

- [ ] `scripts/check_discovery.py` validates the six-field ID format, external-evidence classes, self-citation ban, scope-header truth, and archive naming, and validates the index and archive directory together.
- [ ] `scripts/test_check_discovery.py` gains the cases above and the updated fixture.
- [ ] `scripts/vendor-discovery-check.sh` writes a byte-identical vendored copy plus sha256, and `--check` detects drift.
- [ ] `skills/log-discoveries/SKILL.md` documents the ID format, self-citation ban, archive directory, directory read contract, delete-at-reconcile rule, header regeneration, and opt-in proposal.
- [ ] `ship-changes`, `write-handoff`, `capture-session`, `implement-spec`, and `create-spec` skills reference IDs, the directory read, and the opt-in proposal where section 8 lists them.
- [ ] `commands/engineer-prompt.md` and `commands/fix-bug.md` read the directory and cite by ID.
- [ ] `agents/roles/chief.md` and `agents/roles/context-curator.md` carry the directory read, ID references, the vendored `--check`, and the archive patrol; generated agents regenerated.
- [ ] `AGENTS.md` read rule points at `docs/discovery/`; `README.md` documents IDs, the archive directory, the vendored check, and the opt-in proposal.
- [ ] `docs/specs/2026-10-03-progressive-discovery.md` carries a superseded note for the affected rules.
- [ ] `opencode-agent-os` and `Log_Builder` indexes are migrated, their `ARCHIVE.md` files replaced by `docs/discovery/archive/<id>.md`, and both run the vendored validator green in CI.
- [ ] No database, no generated query index, and no glossary change ship in this spec.

## Verification Steps

Run from `/Users/e/mnt/bnk/cs/opencode-agent-os`:

```bash
python3 scripts/check.sh
python3 scripts/check_discovery.py
python3 scripts/vendor-discovery-check.sh --check .
```

Run from `/Users/e/mnt/bnk/cs/Log_Builder` after rollout:

```bash
python3 scripts/check_discovery.py
python3 scripts/vendor-discovery-check.sh --check .   # uses the plugin's copy path when vendored
```

- Confirm `python3 scripts/check_discovery.py` exits 1 on a temporary line whose only evidence is `docs/discovery/ARCHIVE.md`.
- Confirm every `docs/discovery/archive/*.md` filename stem equals its `# <id>` heading.
- Confirm no `docs/discovery/ARCHIVE.md` remains in an opted-in repo.
- Confirm the `Scope tokens:` header matches the scopes used in each index.

## Open Questions

- Command evidence cannot be proven to have run; accepted for now, revisit if false command evidence appears.
- Orphan archive files warn rather than fail; revisit if they accumulate.
- Concurrent sessions on one index still conflict (v1 open risk); unaffected by this spec.
- A generated, non-committed query index (JSON or SQLite) over the markdown remains deferred; trigger is a repeated cross-repo query need that grep does not satisfy.
- An out-of-repo usage-telemetry store remains deferred; trigger is a decision to measure reads, appends, and session value.
- Should the ID scheme extend to glossary terms or handoffs? Deferred; v2 covers the discovery index only.
