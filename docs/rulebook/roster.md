# Roster

Naming convention: agents are role nouns (`builder`, `critic`); skills are verbs/actions (`specify`, `commit`).
Role sources live in `agents/roles/`; each resolves to one generated agent per profile under `agents/generated/`, named `<role>-<profile>` (for example `builder-ds`).
New additions follow the same word-class split.

Two more layers sit alongside agents. Skills are named, fixed-procedure workflows invoked with the `skill` tool, while agents make judgment calls in a lane; a skill sometimes drives agents itself. A project agent lives outside the plugin and carries workspace-specific config the plugin format cannot express, such as an extra MCP server.

The live crew and skills are also listed by the `task` and `skill` tools; this table is the full catalog.

| Path | Kind | Job |
|---|---|---|
| `agents/roles/chief.md` | agent | operator: decides, decomposes, routes, verifies, writes handoffs |
| `agents/roles/builder.md` | agent | bounded implementation from an exact scope |
| `agents/roles/qa.md` | agent | PASS/FAIL verification, evidence = executed commands only |
| `agents/roles/critic.md` | agent | attacks handoffs/diffs/claims before they're trusted |
| `agents/roles/system-fixer.md` | agent | repairs the agent system itself; improvement mode for recurring failures |
| `agents/roles/context-curator.md` | agent | keeps instruction docs / memory / handoffs / discovery true and lean |
| `agents/roles/scout.md` | agent | external facts: docs, versions, APIs (cheap model) |
| `agents/roles/investigator.md` | agent | in-repo code locator: where X is defined, what calls Y (cheap model) |
| `agents/roles/compliance-officer.md` | agent | pre-filters spec/branch/PR for real regulatory/compliance questions |
| `agents/roles/product-manager.md` | agent | harsh product/UX critique of spec/branch/PR |
| `agents/roles/photo-generator.md` | agent | local AI photo-generation: rig setup, model downloads, identity-consistent image batches |
| `agents/roles/wordsmith.md` | agent | communicative language: formal writing, messages, speeches, talking points in an American Millennial voice |
| `agents/roles/visual-critic.md` | agent | holistic visual design sweep of print, PDF, and HTML deliverables |
| `agents/roles/visual-builder.md` | agent | applies visual fixes from `visual-critic` findings |
| `skills/specify/SKILL.md` | skill | turns a rough spec into an implementation-ready design doc |
| `skills/implement/SKILL.md` | skill | builds exactly what a finished spec says, iterating to green |
| `skills/commit/SKILL.md` | skill | organizes finished work into logical commits, never auto-commits |
| `skills/handoff/SKILL.md` | skill | writes a structured session handoff for fresh-session resume |
| `skills/capture/SKILL.md` | skill | distills session learnings into a terse, standalone knowledge file for a human or future agent |
| `skills/progressive-discovery/SKILL.md` | skill | writes and reads the opt-in discovery index (`docs/discovery/DISCOVERY.md`) |
| `skills/browser-verify/SKILL.md` | skill | proves a feature works end-to-end in a real browser, local stack only |
| `skills/ship-check/SKILL.md` | skill | parallel pre-ship quality gate on a branch |
| `skills/worktree/SKILL.md` | skill | manages grouped git worktrees with isolated ports/DBs |
| `skills/terse/SKILL.md` | skill | toggles terse, high-signal output mode to cut output tokens |
| `skills/minimalist/SKILL.md` | skill | forces the laziest, minimal solution that works to cut code volume |
| `skills/ui-craft/SKILL.md` | skill | sleek, distinctive frontend design: typography, palette, layout, anti-slop, verification checklist |
| `skills/burn/SKILL.md` | skill | deletes the current session from local history on quit, with confirmation |
