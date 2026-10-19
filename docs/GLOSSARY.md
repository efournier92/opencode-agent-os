# Glossary

Project-specific domain terms for the agent-os plugin. One entry per term: bold term, blank line, what the concept is, then an _Avoid_ list of rejected synonyms.

**Quality gate**

One command run per behavior-changing implementation task, bundling green proof, red proof, and CRAP check. _Avoid_: rail, guardrail, bare "the gate".

**Green proof**

Targeted tests pass on the final tree. _Avoid_: test pass, green run.

**Red proof**

The same targeted tests fail when the change is absent, proving the tests constrain the change. _Avoid_: failing test, red run.

**CRAP check**

Per-function risk score `comp^2 * (1 - cov)^3 + comp`, gated at 8 on changed functions. _Avoid_: crap score, complexity check.

**Redteamer**

A read-only critic dispatched with one assigned attack lens against a candidate solution; it returns evidence-backed findings and never fixes. _Avoid_: adversary, devil's advocate, reviewer.

**Referee**

The read-only convergence gate that classifies ledger findings as settled-by-evidence or human-only and emits the minimal walkthrough agenda. _Avoid_: adjudicator, synthesizer, summarizer, judge.

**Redteam**

The operator-run adversarial loop that pressure-tests a goal through diverse lenses and converges on evidence. _Avoid_: grill, adversarial review.

**Critique ledger**

The committed per-run record of findings, with IDs, severities, statuses, and rebuttals, that is the loop's shared state. _Avoid_: findings doc, notes, log.

**Round**

One full diverge-attack-rebut cycle of the loop. _Avoid_: iteration, pass, cycle.

**Walkthrough**

The interactive final stage where the operator puts only human-only decisions to the user through the `question` tool. _Avoid_: review, sign-off, approval.

**Convergence**

The state where a round adds no new high-severity finding and every high or medium finding is settled with evidence. _Avoid_: done, finished.

**Local profile**

The profile named `local`, whose every role pins `ollama/qwen3.6:35b-a3b` so the whole crew runs on-device and no local-profile agent is pinned to a remote model provider. _Avoid_: offline mode, local mode.
