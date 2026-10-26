# Handoff: Redteam Loop Token Cost

## State

- Redteam loop v2 is implemented in the working tree, uncommitted: `skills/redteam/SKILL.md`, `agents/roles/redteamer.md`, three regenerated `agents/generated/redteamer-*.md`.
- Check gate green this session: `bash scripts/check.sh` prints `all checks passed`.
- Design record: `docs/critique/2026-10-26_RedteamTokenCost.md` (29 findings, all settled).
- Benchmark record: `docs/critique/2026-10-26_PermissionsReplay.md` (19 findings, one round, user closed without shipping).

## What Changed

- Evidence pack before fan-out: one `code-locator` dispatch plus operator excerpts, 1,200-1,500 tokens, hard cap 2,000, HEAD-guarded, no conclusions.
- Lens set fixed at intake: `correctness` plus three, hard cap 4 per round, `testing` inside the 4, `maintainability` allowed, no specialist critic dispatch.
- Phase 3 is one consolidated rebuttal plus verifier commands; at most one builder, writing only under the run directory.
- Per-run redteamer budget 6: 4 diverge, 1 rebuttal, 1 un-ship.
- Models and effort unchanged; ledger schema, predicate, and caps unchanged.

## Benchmark

- Replay: permissions change from commit d3fc49d in a worktree at f7ca2ac, after applying the diff, with `docs/critique/` removed from the tree.
- Loop cost: 693,881 tokens across 8 dispatches (locator 58k, four lenses 356k, rebuttal 91k, verifier 119k, un-ship 51k, referee 19k).
- Old-loop estimate for the same shape: about 1.08M (four lenses at the 212k historical median, 40k referee, 190k verifier).
- Coverage: recovered the two real abuse highs (Downloads and symlink pivot, role bash allow overriding the global ask) plus new findings: harness rewrite via bash, merge-config force-merge, no permission-ordering test, unverified doc claims.
- Caveat: n=1, artifact smaller than the original, old run's session rows absent from the DB so the baseline is an estimate.

## Next Actions

1. Commit the working tree through `ship-changes` when ready; nothing is committed.
2. Optional: rerun the benchmark on a larger artifact to get a second data point.
3. Optional: decide whether the sample should ship read denies, the one open replay finding (C-20261026-05).

## Done After The Report

- Convergence clause 1 now judges surviving findings, not raw additions (`skills/redteam/SKILL.md:55`, mirrored in `agents/roles/referee.md`).
- `scripts/merge-config.py:31` seeds the `/tmp` allow once via `IF_ABSENT`; a user who removed it keeps it removed, with tests.
- The `~/Downloads/**` sample entry and its prose are gone; `**/mnt/**` stays per user decision.

## Verify

- `bash scripts/check.sh`
- `python3 scripts/check_critique.py docs/critique`
- `python3 scripts/apply-models.py --check`

## Risks

- The pack assumes all lens agents share the filesystem and can read `/tmp`; a sandboxed subagent would silently fall back to cold reads.
- Pack excerpts are verbatim; the secret grep is one pattern pass, not a guarantee.
- The benchmark was orchestrated by the same operator who knew the answer key; treat the recall result as directional only.
- Installed config at `~/.config/opencode` already carries the new skill and redteamer agents, copied this session.
