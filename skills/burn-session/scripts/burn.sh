#!/bin/sh
# burn.sh - purge the current OpenCode session once OpenCode exits.
#
# Session-only: deletes the session row from opencode.db; its messages and
# parts cascade. Never touches other sessions, logs, tool-output, shell
# history, or the database file itself.
#
#   burn.sh            resolve the current session and print a summary (dry run)
#   burn.sh --yes      arm deletion on OpenCode exit
#   burn.sh --cancel   cancel an armed deletion
#   burn.sh <ses_id>   target a specific session instead of the newest
#
# The current session is the newest row in the DB: it is the live one.
# Deletion is always deferred to process exit, because deleting a live
# session makes the running client error on its next write.
set -eu

DB="${OPENCODE_DB:-$HOME/.local/share/opencode/opencode.db}"
STATE="$HOME/.local/share/opencode/burn"
LOG="$STATE/burn.log"
mkdir -p "$STATE"

MODE=summary
SID=""
for a in "$@"; do
  case "$a" in
    --yes) MODE=arm ;;
    --cancel) MODE=cancel ;;
    *) SID="$a" ;;
  esac
done

if [ "$MODE" = cancel ]; then
  hit=0
  for f in "$STATE"/ses_*.pid; do
    [ -e "$f" ] || continue
    p=$(cat "$f")
    if kill -0 "$p" 2>/dev/null; then
      kill "$p" 2>/dev/null && echo "cancelled $(basename "$f" .pid) (watcher $p)"
    else
      echo "cleared stale watcher for $(basename "$f" .pid)"
    fi
    rm -f "$f"
    hit=1
  done
  [ "$hit" = 1 ] || echo "nothing armed"
  exit 0
fi

[ -f "$DB" ] || { echo "no opencode database at $DB" >&2; exit 1; }

if [ -z "$SID" ]; then
  SID=$(sqlite3 -readonly "$DB" "SELECT id FROM session ORDER BY time_updated DESC LIMIT 1;")
fi
case "$SID" in
  ses_*) ;;
  *) echo "could not resolve a session id (got: '$SID')" >&2; exit 1 ;;
esac

title=$(sqlite3 -readonly "$DB" "SELECT title FROM session WHERE id='$SID';")
dir=$(sqlite3 -readonly "$DB" "SELECT directory FROM session WHERE id='$SID';")
msgs=$(sqlite3 -readonly "$DB" "SELECT count(*) FROM message WHERE session_id='$SID';")
parts=$(sqlite3 -readonly "$DB" "SELECT count(*) FROM part WHERE session_id='$SID';")

echo "session : $SID"
echo "title   : $title"
echo "dir     : $dir"
echo "content : $msgs messages, $parts parts"
echo "cwd     : $PWD"

if [ "$MODE" = summary ]; then
  echo
  echo "dry run. re-run with --yes to arm deletion on quit."
  exit 0
fi

PID="${OPENCODE_PID:-}"
if [ -z "$PID" ] || ! kill -0 "$PID" 2>/dev/null; then
  echo
  echo "not inside a running OpenCode process; delete manually after quit:"
  echo "  opencode session delete $SID"
  exit 1
fi

OC=$(command -v opencode || true)
[ -n "$OC" ] || OC=opencode
PF="$STATE/$SID.pid"

nohup sh -c "while kill -0 $PID 2>/dev/null; do sleep 2; done; { echo \"[\$(date -u +%FT%TZ)] burn $SID\"; $OC session delete $SID; } >> '$LOG' 2>&1; rm -f '$PF'" >/dev/null 2>&1 &
wp=$!
echo "$wp" > "$PF"

echo
echo "armed: session $SID will be deleted when OpenCode (pid $PID) exits."
echo "watcher pid $wp; cancel with: sh $0 --cancel"
