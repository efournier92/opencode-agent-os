#!/usr/bin/env bash
#
# Tag a release with today's date, YYYY-MM-DD.
#
# Usage:
#   scripts/release.sh [remote]
#
# One release per day. Running it again the same day moves today's tag to the
# current HEAD, replacing the earlier tag locally and on the remote. Tags for
# any other date are never touched. Pushes the current branch, then the tag.

set -euo pipefail

REPO="${RELEASE_REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
REMOTE="${1:-origin}"
TAG="$(date +%Y-%m-%d)"

if [ -n "$(git -C "$REPO" status --porcelain)" ]; then
  echo "working tree is dirty; commit or stash first" >&2
  exit 1
fi

BRANCH="$(git -C "$REPO" branch --show-current)"
if [ -z "$BRANCH" ]; then
  echo "detached HEAD; check out a branch first" >&2
  exit 1
fi

git -C "$REPO" push "$REMOTE" "$BRANCH"

if git -C "$REPO" rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "moving $TAG to $(git -C "$REPO" rev-parse --short HEAD)"
  git -C "$REPO" tag -d "$TAG" >/dev/null
else
  echo "tagging $TAG at $(git -C "$REPO" rev-parse --short HEAD)"
fi

git -C "$REPO" tag -a "$TAG" -m "Release $TAG"
git -C "$REPO" push --force "$REMOTE" "refs/tags/$TAG"

echo "released $TAG -> $(git -C "$REPO" rev-parse --short HEAD)"
