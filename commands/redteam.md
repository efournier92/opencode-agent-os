---
description: Pressure-test a goal through many adversarial lenses, converge on evidence, and walk through only human-only decisions. Invoke only as /redteam <goal>.
---

# Redteam

Turn `$ARGUMENTS` into an evidence-converged, safe-to-ship solution by loading and running the `redteam` skill. This command is explicit-invocation only, so it costs nothing until you type it.

## Non-Negotiables

- No nesting: every dispatch is one level deep, and no subagent receives `task`; the operator routes findings to builders.
- Plain punctuation: no em dashes, arrows, or smart quotes.
- If the invoker lacks `task` or `question` permission, or its crew lacks `redteamer` or `referee`, stop and report; never substitute an inline review for a dispatched one.

## Step 1: Validate

If no goal followed the command, ask once and stop. Confirm the repo has a git working tree and a `docs/` directory, and that your crew lists `redteamer` and `referee`; otherwise stop and report the missing prerequisite.

## Step 2: Run

Load the `redteam` skill and follow its Phases 0 to 8 exactly. The skill owns the loop; this command adds nothing to it.

## Step 3: Hand Off

Report the ledger path, the convergence verdict, the walkthrough outcome, and the discovery IDs appended in Phase 8. Return the relevant evidence lines byte-exact. Never commit; offer `ship-changes` only through the skill's ship gate.
