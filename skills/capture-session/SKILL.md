---
name: capture-session
description: Distill everything relevant learned in the current session or work section into one terse, well-organized Markdown knowledge file a human or future agent can read standalone. Use when the user says "capture what we learned", "write up what we learned", "capture this", "debrief", "knowledge dump", "summarize findings", or "note down everything from this section".
license: MIT
compatibility: opencode
---

# Capture Session

User-invocable, low effort. Runs inline: it synthesizes the live session's context, which a subagent cannot see.

## Role

Distills what the current session or work section actually learned into one terse, well-organized Markdown file a human or future agent can read standalone. Knowledge-oriented (findings, decisions, traps, evidence), not resume-oriented. In an opted-in repo, every capture also lands as a one-line entry with an ID in `docs/discovery/DISCOVERY.md`, so it is discoverable without being loaded (see Progressive Discovery in `AGENTS.md`).

Distinct from `write-handoff`:

- `write-handoff` answers "how do I continue this work": current state, next actions, verify commands. Forward-looking, one file per work thread, overwritten in place.
- `capture-session` answers "what do we now know": findings, decisions, traps, evidence, open questions. Durable knowledge, one file per topic, new files accumulate over time.
- If both are wanted, write them separately and cross-link them; never merge into one file.

## When To Use

Trigger phrases are in the frontmatter description. Good moments to invoke:

- End of a recon or research pass.
- After an incident or root-cause fix.
- After landing a durable decision.
- Wrapping a long exploration.
- Before context gets compacted.

## Hard Rules

These come first because they decide whether a file should exist at all.

1. **Nothing to capture, no file.** If nothing non-rederivable was actually established, say so and stop. Never mint an empty or padded file to have output.
2. **Never write secrets or sensitive data.** No tokens, passwords, keys, or credentials; redact them. Flag PII (names, addresses, document numbers) and ask where it may live before writing it to a shared folder.
3. **Evidence or it did not happen.** Every non-obvious finding carries a location (`path:line`), a URL, or the command and its result. Label anything unverified as a hypothesis.
4. **Never invent facts.** Capture only what the session actually established. Unknown stays unknown; list it under open questions.
5. **One topic per file.** Split rather than bloat; cross-link related captures.
6. **Decide, do not ask, when reversible.** Folder, date, and label are decide-and-log. Ask only when the destination is genuinely ambiguous (no convention found and a new set) or the choice is irreversible.
7. **Style.** Follow the Markdown style rules in `docs/rulebook/markdown-style.md`: no em dashes, en dashes, arrows, ellipsis, or smart quotes; a blank line after every heading; title-cased titles and headings (capitalize every word); no sentence split across lines.

## Output Location And Naming

Resolve the folder in order and stop at the first that applies:

1. An explicit path in the argument.
2. The current directory, or the argument's parent, is already a set folder (`YYYY-MM_<Project_Label>/`) or already carries the set's `Project_Label`. Write directly into it; do not create a folder inside it.
3. An existing set folder elsewhere in the workspace whose name contains this `Project_Label`, or a recognized notes root: `flows/<Category>/`, `docs/notes/`, `notes/`, `docs/`, `memory/`. Write there; do not create a parallel tree.
4. Default: `docs/notes/` at the workspace root, created if absent.

Name every knowledge file with this pattern, the user's established convention:

```
YYYY-MM-DD_<Project_Label>_<Topic>.md
```

Segments:

- `YYYY-MM-DD`: ISO date, then a single underscore. Use today, or the date the content is about when that differs. The user forward-dates content about a future event; example: a file written `2026-03-11` about a `2026-03-12` release is named `2026-03-12_...`.
- `<Project_Label>`: the recurring context or project for the set, `Title_Case_With_Underscores`, reused verbatim across every file. Reuse the sibling files' label; never rename an established set. When no set exists, mint a noun-phrase label with no date, and if unsure reuse the workspace or project name.
- `<Topic>`: the subject of this file, `Title_Case_With_Underscores`, concise (one to four words). Name the thing, not the action: `Auth_and_Sessions`, `API_to_Service`, `PreLaunch_Checklist`.

Naming rules:

1. Separate segments and words with a single underscore.
2. Never use spaces. Hyphens appear only inside the ISO date, never as a word or segment separator.
3. Capitalize each word, but keep minor words lowercase: `to`, `and`, `of`, `for`, `the`, `a`, `in`. Examples: `API_to_Service`, `Auth_and_Sessions`, `PreLaunch_Tasks`.
4. Keep a compound that is one concept joined in camel case rather than split: `PreLaunch_Checklist`, not `Pre_Launch_Checklist`.
5. Order the set chronologically by filename. No sequence numbers, no version suffixes, no `-v2`; the date carries order.
6. Always end in `.md`.

H1 is a human title, not a mechanical transform of the filename. Hyphens and added words are correct here. Separate subjects with a pipe and spaces, the user's preference over a colon: `# Project Atlas | Kickoff Notes`. Verified examples: `PreLaunch_Checklist` -> `# 2026-03-09 Project Atlas Pre-Launch Checklist`; `Rollout_Risks` -> `# 2026-03-12 Project Atlas Rollout Risk Review`; `API_Design` -> `# 2026-03-06 Project Atlas API Design`. Older files may drop the date.

Set-level conventions:

- Group a multi-file topic set in a `YYYY-MM_<Project_Label>/` folder, e.g. `2026-03_Project_Atlas/`.
- Create that folder only when the parent is generic (`Misc/`, `notes/`, `docs/`) and no set folder exists yet. If the parent is already well-named for the set, or already names its `Project_Label`, write files straight into it. Never nest a set folder inside another set folder, and never create a subdirectory under a set folder unless the user asks.
- Once a set grows past a few files, keep one undated index named `<Project_Label>_Instructions.md`. Update it whenever a file is added: append a one-line entry for the new file, and refresh any state snapshot it holds. The index may be richer than a file list; follow what the existing index already does.
- A file that mirrors an external doc may be undated and outside the pattern, e.g. `Project_Atlas_Vendor_Deck.md` with H1 `# Project Atlas | Vendor Deck`. Leave such files alone.

Update versus create:

- Same topic and same event, a refinement: update that file in place, ignoring the date.
- Same topic but a new date or a new event: create a new dated file. This is what keeps date-ordering meaningful.
- Before minting, search the target folder for an existing file matching the `Project_Label` and `Topic` segments, ignoring the date.

## Content Contract

Include only what a reader cannot cheaply re-derive. Required sections; drop any that would be empty, and never pad to fill one.

- **Summary**: one or two lines: what this covers and why it matters.
- **Scope**: what was worked on, where (repos, paths, branch), and when.
- **Findings**: the core. Facts learned, each with its evidence: `path:line`, a URL, or the exact command and its result.
- **Decisions and why**: durable choices made, the reason, and the alternative rejected.
- **Traps and non-obvious behavior**: things that surprised you, footguns, order-dependent steps.
- **Evidence and artifacts**: commands run, outputs, links, files produced. Enough that a reader can re-run and verify.
- **Open questions**: what is still unknown or unresolved.
- **Next actions**: only if real. For resume-oriented planning, point at the `write-handoff` output instead of duplicating it.

Exclude: conversational narrative, restating the task, anything already in the project's own docs or version control, anything re-derivable by one grep or file read, and speculation not labeled as such.

Length: no hard cap, but a topic set can legitimately run long (a full rollout or migration plan can reach tens of kilobytes). Keep every line load-bearing; if a file pushes past roughly 300 lines, split by sub-topic instead of growing one file.

## Steps

1. **Guard.** If nothing non-rederivable was established, say so and stop.
2. **Scope.** From the argument or the session, fix the topic and the window (whole session, or one section).
3. **Resolve.** Pick the folder and filename using the rules above; locate any existing set folder or index first. Decide and log the folder, date, and label.
4. **Gather.** Pull the concrete evidence from the session: paths, commands run, results, decisions. Do not invent facts not actually established.
5. **Write** to the content contract, terse, with the H1 as a human title.
6. **Sync the index.** If the set has a `<Project_Label>_Instructions.md`, add this file's entry and refresh any snapshot it holds.
7. **Record discovery.** If the repo has opted in with a `docs/discovery/` directory, append a one-line entry with an ID to its `DISCOVERY.md` linking this file, so the capture is findable without loading it. The link is a path token and counts as external evidence only when the capture sits outside `docs/discovery/`; a typed entry still needs external evidence. Otherwise skip (the capture itself is the durable record).
8. **Verify**, then report.

## Verify

Run the Markdown linter from the plugin checkout (the plugin repo, not the installed config dir), for example `python3 <plugin-checkout>/scripts/lint-markdown.py <file>`, and fix every violation. If the checkout is not present, self-check the style rules manually, including the review-enforced title-case rule.

Content done-check before reporting:

- Every finding carries evidence.
- No required section is empty or padded.
- The index is updated.
- No secrets, and no unmarked PII.
- The H1 reads as a human title.

Report: the path, the section list, and any open question or PII that needs a human decision. If resume work remains, say so and offer `write-handoff`.
