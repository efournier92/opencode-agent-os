---
name: worktree
description: Create, list, or remove grouped git worktrees across every repo/service in the workspace at once, each with isolated network ports and its own database.
license: MIT
compatibility: opencode
---

# Worktree

User-invocable.

## Role

Creates, lists, or removes **grouped** git worktrees spanning every repo/service in the workspace at once, each with isolated network ports and its own database, so multiple branches of a multi-repo project can run side by side without colliding.

## Concept

A "worktree" here means one named working copy of *every* repo in the workspace, checked out to the same branch, sharing one slot number. The slot number derives a whole block of non-colliding ports (one base port per service, offset by `slot * 100` or similar) and a distinct container/network subnet, so several of these groups can run their own local stack concurrently.

## Operations

- **create `<branch>`**: validates inputs (target directory doesn't already exist, required per-repo env files exist to copy from), picks the lowest unused slot, cuts a worktree in every repo for that branch (creating the branch if it doesn't exist yet; warns if it exists in some repos but not others, since that implies diverged history), generates an override file for the container/port config (must force-override port lists rather than merge, or ports collide with the base stack) and a small per-worktree build-tool include file, patches copied env files with the slot-specific ports/DB name, records the new slot in a tracking file, and prints a summary with every service's assigned port plus first-run instructions. Any failure during worktree creation triggers full rollback (remove any worktrees already cut, delete the partial directory, do not record the slot).
- **list**: reads the tracking file and reports name/slot/branch/ports/path per entry, marking any whose directory is missing as stale.
- **remove `<branch>`**: stops the worktree's own container stack and removes its data volume, removes the worktree from every repo, deletes the directory, and drops the tracking-file entry. Branches themselves are kept (they may have unpushed work); never force-deletes a branch without asking first.

## Notes

- No file locking on slot assignment; fine for human-driven use; would need a lock if this were ever automated/concurrent.
- Each worktree gets its own database volume and runs its own migrations independently of the main checkout and of every other worktree.
