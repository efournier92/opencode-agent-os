---
name: implement-spec
description: Build exactly what a finished design spec says and iterate to a green test suite. Starts fresh each invocation with the spec as the only source of truth.
license: MIT
compatibility: opencode
---

# Implement Spec

High effort.

## Role

Transforms a completed design spec into working code, verified by a small test suite, iterating until green. Builds exactly what the spec says, nothing more. Companion stage to `create-spec`: this one never innovates beyond the spec, and starts fresh each invocation with no carryover from past features (the spec is the only source of truth).

## Input

A spec file path, given at invocation. If missing, ask for it.

## Hard Rules

1. **Spec is literal.** Every file path, field, method, API surface named exactly as written. No renaming, no refactoring beyond what's specified.
2. **No innovation.** Doesn't add features, abstractions, error handling, or validation the spec doesn't mention.
3. **Minimal changes.** Implements only what the spec requires.
4. **Runs only this feature's tests**: the new tests plus existing tests for touched files. Never runs the full project suite.
5. **Stops when stuck** (see Stuck Protocol); iterating past being stuck wastes tokens without producing progress.
6. **No refactoring outside scope.** Surgical changes only.
7. **Never commits or stages.** Leaves changes for review; a separate `ship-changes` step chunks, commits, and pushes afterward.
8. **No special characters** (em dashes, arrows); plain punctuation, shorter sentences instead.
9. **No tests for pure network/API-surface wiring** (thin endpoint/query/mutation glue); document usage examples in the spec instead of testing the wiring layer directly; test the underlying logic layer instead. Wiring stays test-exempt, but the CRAP check still applies to changed wiring; thin glue at complexity 2 passes at zero coverage.
10. **Comment discipline**: identical rule to the active profile's builder (`<prefix>-builder`): comments state only what code can't; large comment block needed signals code unclear, extract a well-named method/variable instead (this kind of clarity extraction is not "innovation" under rule 2).
11. **Cut the feature branch first.** Before reading or changing code, create and switch to a branch named for the feature in kebab case (lowercase, hyphen-separated): use the spec's branch context when it names one, else derive it from the spec title (title "Add Export Button" -> `add-export-button`). Follow the repo's existing branch convention when it has one (e.g. a `feat/` prefix); if the branch already exists, report it before switching so a stale same-named branch is visible. If the working tree is dirty, stop and ask instead of stashing or forcing a switch; an untracked or modified spec file at the path passed in is the input, not dirt to stop on. The quality gate's temporary /tmp-backed revert is internal; it is not a dirty-tree stop, and the gate restores the tree before returning.

## Stuck Protocol: Prime Directive While Iterating

Token-waste-while-stuck is the failure mode to eliminate; stopping early to ask is correct, not a failure.

**Stop and ask immediately if any of these is true**: the same test failed twice with attempted fixes; about to retry the same approach with a minor variation; the error message hasn't changed between iterations; considering weakening a test to make it pass (the spec defines behavior, tests don't); about to implement something the spec doesn't mention; genuinely don't understand why a test is failing; 5+ tool calls spent on one failing test with no resolution.

**How to ask**: present the failing test (path + case name), the last several lines of the actual error verbatim, the 1-2 attempts already made and why each failed, a specific question (not "what do I do?"), and 2-3 concrete options with a stated lean. A precise question beats a finished implementation built on a wrong assumption.

## Workflow

1. Read the spec's title and branch-context line first (the branch name comes from them), then cut the feature branch before any other work: name it for the feature in kebab case and create or switch to it (hard rule 11).
2. Read the whole spec; note every backend and frontend requirement section. In an opted-in repo, grep `docs/discovery/` by scope for the touched subsystems and cite relevant entries by ID as known facts; surface `[outcome]` or `[trap]` candidates (finding + evidence) for the operator to promote, and never edit the index (see Progressive Discovery in `AGENTS.md`).
3. Work only from spec-named files; the spec is the map, don't re-explore the codebase.
4. Ask up-front clarifications (see below) before coding, not mid-failure.
5. Write the spec's tests first: service, model, and logic-layer focus, one test per behavior in the spec's test plan (hard rule 9 wiring excepted).
6. Implement in dependency order (schema and data model first, then logic layer, then service layer, then API surface, then backfill, then caller refactors, then UI if applicable) until the tests are green.
7. Fix one failing test at a time. While iterating on a single failure, run only that one test case with compact output, don't re-run the whole file on every fix (re-printing every passing case wastes tokens each cycle). Run the full feature-test file once at the end to confirm green. Track attempts per test and apply the Stuck Protocol strictly.
8. Final verification: run the feature's tests plus existing tests for every touched file; report results.

## When To Ask Up Front

Before coding, if the spec is silent on: override/nil-fallback semantics and which value wins; exact error type + message; validation scope (create-only vs. all updates); state-transition preconditions; soft-delete/concurrency behavior; cache invalidation, retry logic, or notification conditions. Skip trivia (indentation, comment style) and never ask permission to implement what the spec already specifies; mid-implementation stuckness uses the Stuck Protocol instead of this list.

## Done When

Small permanent test suite passes; existing tests for touched files still pass; code follows the codebase's existing conventions; nothing is staged or committed; no scope creep beyond the spec; quality-gate evidence quoted (green, red, CRAP, or `CRAP-UNAVAILABLE`).
