# Operator Detail

On-demand reference for the operator (chief). Read the relevant section when its trigger applies; never preload.

## Loop-Readiness Triage

Before promoting a manual workflow into a loop (skill, command, hook, or routing entry), all three must hold:

- It repeats often enough to be worth wiring.
- It has a done-check you can run automatically.
- A wrong attempt is cheap to discard.

Failing any, do it once by hand and do not wire it.

## Intake Gate: Goal, Effort, Verify

Run at Frame on any request that edits files or burns real time. Skip for a question, a lookup, or a one-line reversible edit.

- Goal: one line of what done looks like.
- Effort: how much work is justified, from one pass to a convergence loop.
- Verify: the exact command or review that proves it.

A missing or contradictory field gets one `question` call, one entry per missing field, the recommended default first, plus a clear accept-all option. Never a follow-up round on the same field.

Default instead of asking when the answer would not change the diff: effort is the cheapest shippable increment, verify is the project check resolved per `docs/rulebook/quality-gates.md`, goal is the single reading with the smallest diff. State the default you took in one line.

Verify never defaults silently on a done claim. When no command exists, the plan names the review pass instead (linter, critic, or a human read) and says so up front.

An unattended run with no user turn to answer (hook, cron, CI) does not block. State the three assumptions in one line and proceed, unless the action is irreversible or expensive, then stop.

Never gate twice: once the three are on the record, dispatch without re-asking.

## Memory And Handoffs

- **Durable decisions/preferences**: auto-memory index; never store what version control or project docs already record.
  - Format: `date | failure | root cause | patch | eval | next`, short and operational, no narrative.
  - A recurring failure gets an automated check, not a memory note.
- **Session handoff**: dated topic file with current state, decisions and why, next actions with exact paths, verify commands, and open risks; overwrite the same topic file as work progresses.
