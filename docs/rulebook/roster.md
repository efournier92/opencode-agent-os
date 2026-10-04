# Roster

Naming convention: agents are role nouns (`builder`, `verifier`); skills are verbs/actions (`create-spec`, `ship-changes`).
Role sources live in `agents/roles/`; each resolves to one generated agent per profile under `agents/generated/`, named `<role>-<profile>` (for example `builder-ds`).
New additions follow the same word-class split.

Two more layers sit alongside agents. Skills are named, fixed-procedure workflows invoked with the `skill` tool, while agents make judgment calls in a lane; a skill sometimes drives agents itself. A project agent lives outside the plugin and carries workspace-specific config the plugin format cannot express, such as an extra MCP server.

Commands are a third layer: user-invoked slash prompts that add no model context until run, which is why an explicit-only workflow belongs in a command, not a skill.

The live crew and skills are also listed by the `task` and `skill` tools; this table is the full catalog.

| Path | Kind | Job |
|---|---|---|
| `agents/roles/chief.md` | agent | operator: decides, decomposes, routes, verifies, writes handoffs |
| `agents/roles/builder.md` | agent | bounded implementation from an exact scope |
| `agents/roles/verifier.md` | agent | PASS/FAIL verification, evidence = executed commands only |
| `agents/roles/claim-critic.md` | agent | attacks handoffs/diffs/claims before they're trusted |
| `agents/roles/system-fixer.md` | agent | repairs the agent system itself; improvement mode for recurring failures |
| `agents/roles/context-curator.md` | agent | keeps instruction docs / memory / handoffs / discovery true and lean |
| `agents/roles/external-researcher.md` | agent | external facts: docs, versions, APIs (cheap model) |
| `agents/roles/code-locator.md` | agent | in-repo code locator: where X is defined, what calls Y (cheap model) |
| `agents/roles/compliance-officer.md` | agent | pre-filters spec/branch/PR for real regulatory/compliance questions |
| `agents/roles/product-critic.md` | agent | harsh product/UX critique of spec/branch/PR |
| `agents/roles/photo-generator.md` | agent | local AI photo-generation: rig setup, model downloads, identity-consistent image batches |
| `agents/roles/wordsmith.md` | agent | communicative language: formal writing, messages, speeches, talking points in an American Millennial voice |
| `agents/roles/phraser.md` | agent | riffing partner: ranked, distinct ways to rephrase a phrase, sentiment, or sentence, top pick flagged |
| `agents/roles/visual-critic.md` | agent | holistic visual design sweep of print, PDF, and HTML deliverables |
| `agents/roles/visual-builder.md` | agent | applies visual fixes from `visual-critic` findings |
| `skills/create-spec/SKILL.md` | skill | turns a rough spec into an implementation-ready design doc |
| `skills/implement-spec/SKILL.md` | skill | builds exactly what a finished spec says, iterating to green |
| `skills/ship-changes/SKILL.md` | skill | chunks unstaged work into commits and pushes; per-commit review by default, one pre-flight gate then unattended on an explicit autonomy cue |
| `skills/write-handoff/SKILL.md` | skill | writes a structured session handoff for fresh-session resume |
| `skills/capture-session/SKILL.md` | skill | distills session learnings into a terse, standalone knowledge file for a human or future agent |
| `skills/log-discoveries/SKILL.md` | skill | writes and reads the opt-in discovery index (`docs/discovery/DISCOVERY.md`) |
| `skills/verify-in-browser/SKILL.md` | skill | proves a feature works end-to-end in a real browser, local stack only |
| `skills/manage-worktrees/SKILL.md` | skill | manages grouped git worktrees with isolated ports/DBs |
| `skills/tighten-prose/SKILL.md` | skill | tightens output to terse, high-signal mode to cut output tokens (loads on "terse") |
| `skills/simplify-code/SKILL.md` | skill | forces the laziest, minimal solution that works to cut code volume |
| `skills/polish-ui/SKILL.md` | skill | sleek, distinctive frontend design: typography, palette, layout, anti-slop, verification checklist |
| `skills/burn-session/SKILL.md` | skill | deletes the current session from local history on quit, with confirmation |
| `commands/engineer-prompt.md` | command | user-invoked prompt engineering; adds no model context until run |
