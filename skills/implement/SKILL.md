---
name: implement
description: Build exactly what a finished design spec says and iterate to a green test suite. Starts fresh each invocation with the spec as the only source of truth.
license: MIT
compatibility: opencode
---

# implement

High effort.

## Role

Transforms a completed design spec into working code, verified by a small test suite, iterating until green. Builds exactly what the spec says, nothing more. Companion stage to `specify`: this one never innovates beyond the spec, and starts fresh each invocation with no carryover from past features (the spec is the only source of truth).

## Input

A spec file path, given at invocation. If missing, ask for it.

## Hard rules

1. **Spec is literal.** Every file path, field, method, API surface named exactly as written. No renaming, no refactoring beyond what's specified.
2. **No innovation.** Doesn't add features, abstractions, error handling, or validation the spec doesn't mention.
3. **Minimal changes.** Implements only what the spec requires.
4. **Runs only this feature's tests**: the new tests plus existing tests for touched files. Never runs the full project suite.
5. **Stops when stuck** (see Stuck Protocol); iterating past being stuck wastes tokens without producing progress.
6. **No refactoring outside scope.** Surgical changes only.
7. **Never commits or stages.** Leaves changes for review; a separate commit-organizing step runs afterward.
8. **No special characters** (em dashes, arrows); plain punctuation, shorter sentences instead.
9. **No tests for pure network/API-surface wiring** (thin endpoint/query/mutation glue); document usage examples in the spec instead of testing the wiring layer directly; test the underlying logic layer instead.
10. **Comment discipline**: identical rule to the active profile's builder (`<prefix>-builder`): comments state only what code can't; large comment block needed signals code unclear, extract a well-named method/variable instead (this kind of clarity extraction is not "innovation" under rule 2).

## Stuck protocol: prime directive while iterating

Token-waste-while-stuck is the failure mode to eliminate; stopping early to ask is correct, not a failure.

**Stop and ask immediately if any of these is true**: the same test failed twice with attempted fixes; about to retry the same approach with a minor variation; the error message hasn't changed between iterations; considering weakening a test to make it pass (the spec defines behavior, tests don't); about to implement something the spec doesn't mention; genuinely don't understand why a test is failing; 5+ tool calls spent on one failing test with no resolution.

**How to ask**: present the failing test (path + case name), the last several lines of the actual error verbatim, the 1-2 attempts already made and why each failed, a specific question (not "what do I do?"), and 2-3 concrete options with a stated lean. A precise question beats a finished implementation built on a wrong assumption.

## Workflow

1. Read the whole spec; note every backend and frontend requirement section.
2. Work only from spec-named files; the spec is the map, don't re-explore the codebase.
3. Ask up-front clarifications (see below) before coding, not mid-failure.
4. Implement in dependency order (schema/data model first, then logic layer, then service layer, then API surface, then backfill, then caller refactors, then UI if applicable).
5. Write a small permanent test suite alongside: service/model/logic-layer focus, not UI-wiring tests (see hard rule 9).
6. Fix one failing test at a time. While iterating on a single failure, run only that one test case with compact output, don't re-run the whole file on every fix (re-printing every passing case wastes tokens each cycle). Run the full feature-test file once at the end to confirm green. Track attempts per test and apply the Stuck Protocol strictly.
7. Final verification: run the feature's tests plus existing tests for every touched file; report results.

## When to ask up front

Before coding, if the spec is silent on: override/nil-fallback semantics and which value wins; exact error type + message; validation scope (create-only vs. all updates); state-transition preconditions; soft-delete/concurrency behavior; cache invalidation, retry logic, or notification conditions. Skip trivia (indentation, comment style) and never ask permission to implement what the spec already specifies; mid-implementation stuckness uses the Stuck Protocol instead of this list.

## Done when

Small permanent test suite passes; existing tests for touched files still pass; code follows the codebase's existing conventions; nothing is staged or committed; no scope creep beyond the spec.
