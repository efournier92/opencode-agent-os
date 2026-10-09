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
