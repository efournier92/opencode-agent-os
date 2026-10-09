---
description: Engineer a messy idea into a destination-shaped, grounded, verifiable prompt. Invoke only as /engineer-prompt <idea>.
---

# Engineer Prompt

Turn `$ARGUMENTS` into one ready-to-use prompt. This command is explicit-invocation only, so it costs nothing until you type it.

## Non-Negotiables

- Read-only on the repo; delegate all fact-finding to `task`.
- Never pin a model; polish is model-agnostic.
- One prompt out; write a file only when asked.
- Plain punctuation, no em dashes, arrows, or smart quotes.

## Step 1: Classify The Destination

Pick exactly one, because shape follows it.

- Subagent dispatch.
- Skill invocation.
- Operator plan or handoff.
- User-facing LLM prompt.

If no idea followed the command, or the idea is already a finished prompt for one destination, say so and stop.

## Step 2: Ground The Facts

Dispatch up to two low-tier recon agents via `task`, resolving bare role names against the `task` crew list (for example `code-locator-ds+glm`): `code-locator` for in-repo facts, `external-researcher` for external facts. Cap each at roughly 20 tool calls. Each dispatch carries shell discipline, what NOT to re-report, and a `NEED-INPUT` clause per the Delegation Contract. Require "location plus one-line fact, no prose." In an opted-in repo, grep the `docs/discovery/` directory first and cite matches by ID. Spot-read every cited fact before using it.

## Step 3: Ask Only Material Questions

Facts are the agent's job; decisions are the user's. Open the whole frontier in a single `question` tool call, one entry per decision, each with 2-4 options, the recommended one first and labeled `(Recommended)`; keep headers within 30 characters and option labels to 1-5 words, and never add an "Other" option. Every question to the user goes through the tool, never prose; the tool's built-in custom answer covers anything the options miss. A question earns a slot only if its answer changes a requirement. Log everything else as an assumption. Stop asking once the prompt is unambiguous.

## Step 4: Shape

Fill the template for the destination.

- Subagent dispatch: scope/location, goal, exact paths, output shape ("fact plus location, no prose"), what NOT to re-report, shell discipline, and a `NEED-INPUT` clause.
- Skill invocation: exact skill name, its argument, and the expected exit claim.
- Operator plan or handoff: ordered phases, each with a done-check; link existing skills instead of restating them.
- User-facing prompt: role, task, constraints, output format, and an observable success condition.

## Step 5: Verify

Run the structural checklist: destination classified, template complete, every load-bearing claim carries a `file:line` or named source, no model pinned. If the prompt is read-only, confirm via the `question` tool before spending one smoke-test call, then run the engineered prompt verbatim via `task` and record the result. If it mutates state, stop at the checklist and mark the unverified corner with an `engineer-prompt:` comment.

## Step 6: Hand Off

Print the prompt. If it is a recurring workflow, suggest routing it to `create-spec` or `customize-opencode`. For cross-session work, suggest the `write-handoff` skill. Name load-bearing decisions for the operator to index by ID; never write the `docs/discovery/` index yourself.
