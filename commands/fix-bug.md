---
description: Reproduce a bug, fix it red-green, and prove the fix. Invoke only as /fix-bug <bug>.
---

# Fix Bug

Turn `$ARGUMENTS` into a verified fix. This command is explicit-invocation only, so it costs nothing until you type it.

## Non-Negotiables

- Reproduce before fixing: a failing check must exist before any source edit.
- One bug per run: no refactors, no drive-by edits.
- The project's check is the gate; never claim green without running it this session.
- Keep maker and checker separate: `builder` always makes the fix, `verifier` always proves it; there is no self-granted trivial exemption.
- Freeze the red check: the fix diff must not touch it.
- Never commit, push, or merge; report done and stop.
- Plain punctuation: no em dashes, arrows, or smart quotes.
- If the invoker lacks `task` permission or its crew lacks a needed role, stop and report; never substitute an inline edit for a dispatched one.

## Step 1: Capture

Restate the bug as input, expected, and actual. If no bug followed the command or the repro is unclear, ask once and stop. If the expected behavior is not documented or intended, stop and report "feature request, not a bug", citing the source that defines it.

## Step 2: Reproduce (Red)

Locate the path via one `code-locator` recon dispatch; do not read broadly. In an opted-in repo, grep `docs/discovery/DISCOVERY.md` by scope first. Write the smallest failing check. When a test seam exists, the test must live in the project suite and be run by the project's check, not a scratch file; a scratch repro is a fallback and the hand-off must name the missing permanent guard. Require two independent red runs. If the first run passes, re-run up to five times and once from a clean state before concluding the repro is wrong, because a flaky bug is not a disproved one. Snapshot the project's full-check baseline, the exact failing set, before changing source. The check text is now frozen: the fix diff must not touch it.

## Step 3: Fix (Green)

Dispatch `builder` with the frozen check path marked forbidden in the diff; minimalist: reuse, stdlib, no new deps, smallest change. Run the targeted check, then the project's full check. Loop at most two `builder` re-dispatches, matching `builder`'s own stuck rule; on the third failure, abort: report the re-dispatch count and the last error, and revert the partial fix per `docs/rulebook/stash-discipline.md` so the tree is clean or the residue is named.

## Step 4: Mutation Proof

Revert the source fix only (stash per `docs/rulebook/stash-discipline.md`), rerun the frozen check, and require red; then re-apply the fix. A check that stays green proves it never caught the bug. Run the project's full check and diff its failing set against the Step 2 baseline; the only permitted change is the bug's failure disappearing.

## Step 5: Independent Proof

Per the `chief.md` verification routing, dispatch `verifier` to certify three claims: the repro fails before and passes after on re-derivation from the bug statement; the frozen check is untouched since Step 2; the full-check failures equal the baseline minus the bug. For a bug with no CLI-expressible repro, route `verify-in-browser` instead, or stop and report.

## Step 6: Hand Off

Report the same decisive command's red line and green line byte-exact, the root cause, the diff summary, the baseline versus final failure sets, and the verifier's verdict. Return a discovery candidate for any trap or non-obvious cause; never write the index. Never commit; offer `ship-changes`.
