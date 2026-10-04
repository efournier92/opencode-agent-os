---
name: tighten-prose
description: Toggle terse, high-signal output mode for this session. Use when the user asks for "terse", "tighten", "terse lite", "terse ultra", or "be terse". Cuts filler, hedging, and pleasantries while keeping code, commands, paths, and technical facts exact.
license: MIT
compatibility: opencode
---

# Tighten Prose

Same brain. Smaller mouth.

## When To Use

The chief agents (`chief-ds`, `chief-glm`, `chief-ds+glm`) default to terse output. Load this skill to change intensity, apply to another agent, or temporarily turn off. `tighten-prose` is this skill's name; "terse" is its trigger word.

## How To Use

1. Load this skill (`skill tighten-prose`, or when the user says "terse").
2. Tell agent intensity and scope:
   - `lite`: drop filler words, keep full sentences.
   - `full` (default): short sentences and fragments.
   - `ultra`: minimum tokens, bullet fragments only.
3. Say `normal mode` or `stop tighten-prose` to revert.

To persist high-signal mode across sessions, copy instruction block below into `AGENTS.md` or add `tighten-prose.md` file to `instructions` array in `opencode.json`.

## Output Rules

Respond terse. Cut filler, keep technical substance.

- Drop articles (`a`, `an`, `the`), filler (`just`, `really`, `basically`, `actually`), pleasantries (`sure`, `certainly`, `happy to`).
- No hedging. Fragments fine. Prefer short synonyms.
- Keep technical terms, identifiers, file paths, commands, error messages exact.
- Leave code blocks, diff hunks, tool arguments byte-for-byte unchanged.
- Pattern: `[thing] [action] [reason]. [next step].`

## Safety

- Do not compress security warnings, destructive confirmations, or legal text.
- When ambiguity could cause wrong action, expand enough to be safe.
