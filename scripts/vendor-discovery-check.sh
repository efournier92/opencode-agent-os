#!/usr/bin/env bash
#
# Vendor the canonical discovery validator into an opted-in repo, or check the
# vendored copy for drift against the canonical source.
#
# Usage:
#   scripts/vendor-discovery-check.sh <repo-path>
#   scripts/vendor-discovery-check.sh --check <repo-path>
#
# Writes <repo-path>/scripts/check_discovery.py (byte-identical) plus
# <repo-path>/scripts/check_discovery.sha256. Never touches .githooks/ or CI.

set -euo pipefail

SELF="${BASH_SOURCE[0]}"
case "$SELF" in
  /*) SELF_DIR="${SELF%/*}" ;;
  */*) SELF_DIR="$PWD/${SELF%/*}" ;;
  *) SELF_DIR="$PWD" ;;
esac
CANONICAL="$SELF_DIR/check_discovery.py"

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

abs() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s\n' "$PWD/$1" ;;
  esac
}

usage() {
  echo "usage: ${0##*/} [--check] <repo-path>" >&2
  exit 2
}

snippets() {
  cat <<'EOF'
Per-repo hook, .githooks/pre-commit:
    python3 scripts/check_discovery.py
Activate it once per clone with:
    git config core.hooksPath .githooks

Per-repo CI step, added to the existing workflow:
    python3 scripts/check_discovery.py
EOF
}

if [ "${1:-}" = "--check" ]; then
  [ $# -eq 2 ] || usage
  REPO="$(abs "$2")"
  VENDORED="$REPO/scripts/check_discovery.py"
  expected="$(sha256 "$CANONICAL")"
  if [ ! -f "$VENDORED" ]; then
    echo "stale: vendored validator missing: $VENDORED" >&2
    echo "expected sha256: $expected" >&2
    exit 1
  fi
  actual="$(sha256 "$VENDORED")"
  if [ "$actual" != "$expected" ]; then
    echo "stale: vendored validator differs from canonical" >&2
    echo "expected sha256: $expected" >&2
    echo "actual sha256:   $actual" >&2
    exit 1
  fi
  echo "ok: vendored validator matches canonical ($expected)"
  exit 0
fi

[ $# -eq 1 ] || usage
REPO="$(abs "$1")"
TARGET_DIR="$REPO/scripts"
VENDORED="$TARGET_DIR/check_discovery.py"
mkdir -p "$TARGET_DIR"
if [ "$CANONICAL" -ef "$VENDORED" ]; then
  echo "already canonical: $VENDORED"
else
  cp "$CANONICAL" "$VENDORED"
fi
sha256 "$CANONICAL" > "$TARGET_DIR/check_discovery.sha256"
echo "vendored $CANONICAL -> $VENDORED"
snippets
