#!/usr/bin/env bash
#
# Single quality gate for the plugin tree: skill budget, unit suite, markdown lint.
#
# Usage:
#   scripts/check.sh
#
# Exit code 0 = all checks passed. Wired into .githooks/pre-commit and CI.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO"

echo "== doc budget =="
python3 scripts/test_doc_budget.py

echo "== unit tests =="
python3 -m unittest discover -s scripts -p 'test_*.py'

echo "== markdown lint =="
python3 scripts/lint-markdown.py .

echo
echo "all checks passed"
