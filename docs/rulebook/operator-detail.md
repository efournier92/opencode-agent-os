# Operator Detail

On-demand reference for the operator (chief). Read the relevant section when its trigger applies; never preload.

## Loop-Readiness Triage

Before promoting a manual workflow into a loop (skill, command, hook, or routing entry), all three must hold:

- It repeats often enough to be worth wiring.
- It has a done-check you can run automatically.
- A wrong attempt is cheap to discard.

Failing any, do it once by hand and do not wire it.

## Memory And Handoffs

- **Durable decisions/preferences**: auto-memory index; never store what version control or project docs already record.
  - Format: `date | failure | root cause | patch | eval | next`, short and operational, no narrative.
  - A recurring failure gets an automated check, not a memory note.
- **Session handoff**: dated topic file with current state, decisions and why, next actions with exact paths, verify commands, and open risks; overwrite the same topic file as work progresses.
