---
name: verify-in-browser
description: Prove a feature works end-to-end in a real browser against the local dev stack only. Delegates browser driving to a project-level verification subagent.
license: MIT
compatibility: opencode
---

# Verify In Browser

Drives a dedicated browser-verification project agent.

## Role

Proves a feature works end-to-end in a real browser against the local dev stack only; never a real/deployed environment. Delegates the actual browser driving to a separate project-level agent so page snapshots stay out of the main session's context.

## Steps

1. Parse the request into a feature description plus a role (defaults to the primary end-user role unless the request clearly names an admin/back-office role).
2. Only include specific route/component names in the dispatch if the feature description references code just changed AND the UI entry point is non-obvious. Otherwise don't explore the codebase at all before dispatching.
3. Use the `task` tool to spawn the browser-verification subagent in the foreground (its result is needed before continuing), with a prompt stating: feature to prove, role, and optional context (routes/components/expected UI text) only if actually known.
4. Relay the subagent's verdict block back to the user verbatim. On FAIL/BLOCKED, add one sentence suggesting the likely next step.

## Constraints

- Target is always the local dev stack's known port; never pass any other URL into the subagent prompt.
- One feature per invocation. Multiple features get multiple parallel dispatches, one each.
