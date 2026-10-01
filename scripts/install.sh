#!/usr/bin/env bash
#
# Install the agent-team plugin into an OpenCode config directory.
#
# Usage:
#   scripts/install.sh [--config-dir DIR]
#
# Defaults to ~/.config/opencode, or $OPENCODE_CONFIG_DIR when set.
# Backs up anything it replaces and is safe to re-run.
#
# It installs generated agents, skills, the rulebook, seeds models.yaml on a
# fresh machine, seeds the sample config only when none exists, and merges the
# TUI keybinds that move agent switching to shift+tab.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}"

while [ $# -gt 0 ]; do
  case "$1" in
    --config-dir) CFG="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$CFG" ] || [ "$CFG" = "/" ]; then
  echo "refusing to install into '$CFG'" >&2
  exit 2
fi
if [ ! -d "$REPO/agents/generated" ]; then
  echo "missing $REPO/agents/generated; run 'python3 scripts/apply-models.py' first" >&2
  exit 2
fi

ts="$(date +%Y-%m-%d_%H%M%S)"
bak="$CFG/backup-$ts"
mkdir -p "$bak"

echo "repo:   $REPO"
echo "config: $CFG"
echo "backup: $bak"

# 1. Back up anything we replace.
for item in agents skills AGENTS.md models.yaml opencode.jsonc opencode.json tui.json; do
  if [ -e "$CFG/$item" ]; then
    cp -R "$CFG/$item" "$bak/$item"
  fi
done

# 2. Agents and skills (clear stale entries, then copy fresh).
rm -rf "$CFG/agents" "$CFG/skills"
mkdir -p "$CFG/agents" "$CFG/skills"
cp -n "$REPO"/agents/generated/*.md "$CFG/agents/"
cp -Rn "$REPO"/skills/* "$CFG/skills/"

# 3. Shared rulebook.
cp "$REPO/AGENTS.md" "$CFG/AGENTS.md"

# 4. models.yaml: seed a fresh install, never overwrite a customized copy.
if [ -f "$CFG/models.yaml" ]; then
  echo "kept existing models.yaml"
else
  cp "$REPO/models.yaml" "$CFG/models.yaml"
fi

# 5. Active config: seed only when absent. An existing config may hold providers,
#    MCP servers, or permissions we must not clobber; merge the sample by hand.
if [ -f "$CFG/opencode.jsonc" ] || [ -f "$CFG/opencode.json" ]; then
  echo "kept existing opencode config; merge $REPO/opencode.json.sample by hand"
else
  cp "$REPO/opencode.json.sample" "$CFG/opencode.jsonc"
fi

# 6. TUI keybinds: set agent switching to shift+tab only when the keys are
#    unset. A keybind a user chose is never overridden, and no other keybind is
#    touched (Tab is easy to hit and collides with input autocomplete).
if command -v python3 >/dev/null 2>&1; then
  CFG="$CFG" python3 - <<'PY'
import json, os
from pathlib import Path

path = Path(os.environ["CFG"]) / "tui.json"
try:
    data = json.loads(path.read_text()) if path.exists() and path.read_text().strip() else {}
    keybinds = data.setdefault("keybinds", {})
    before = dict(keybinds)
    keybinds.setdefault("agent_cycle", "shift+tab")
    keybinds.setdefault("agent_cycle_reverse", "none")
    if keybinds == before:
        print(f"keybinds already set; left {path} unchanged")
    else:
        path.write_text(json.dumps(data, indent=2) + "\n")
        print(f"keybinds -> {path}")
except Exception as exc:
    print(f"warning: could not update {path}: {exc}", file=os.sys.stderr)
PY
else
  echo "python3 not found; skipped tui.json keybind merge" >&2
fi

echo "agents: $(ls "$CFG/agents" | wc -l | tr -d ' ')"
echo "skills: $(ls "$CFG/skills" | wc -l | tr -d ' ')"
echo "done; restart OpenCode to load the new config"
