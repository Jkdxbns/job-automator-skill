#!/usr/bin/env bash
# usage: wait_idle.sh [--timeout SECONDS] NAME [NAME ...]      (default timeout 600)
# Returns when every named agent has finished. An agent counts as done only after it was seen busy
# (or 30s passed, covering a very fast one) AND is quiet on two checks 5s apart, because it can go
# quiet briefly while a tool runs. A session no longer running claude counts as done.
# Exit 0 = all done, 1 = timeout (prints who is still running).
set -u
TO=600; [ "${1:-}" = "--timeout" ] && { TO=$2; shift 2; }
NAMES=("$@"); START=$(date +%s)
declare -A SEEN QUIET
busy(){ tmux capture-pane -t "=$1:" -p 2>/dev/null | tail -12 | grep -q "esc to interrupt"; }
while :; do
  PENDING=()
  for n in "${NAMES[@]}"; do
    if ! tmux has-session -t "=$n" 2>/dev/null || [ "$(tmux display -p -t "=$n:" '#{pane_current_command}')" != "claude" ]; then continue; fi
    if busy "$n"; then SEEN[$n]=1; QUIET[$n]=0; PENDING+=("$n"); continue; fi
    if [ -n "${SEEN[$n]:-}" ] || [ $(( $(date +%s) - START )) -gt 30 ]; then
      QUIET[$n]=$(( ${QUIET[$n]:-0} + 1 ))
      [ "${QUIET[$n]}" -ge 2 ] || PENDING+=("$n")
    else PENDING+=("$n"); fi
  done
  [ ${#PENDING[@]} -eq 0 ] && { echo "all idle"; exit 0; }
  [ $(( $(date +%s) - START )) -gt "$TO" ] && { echo "TIMEOUT still running: ${PENDING[*]}"; exit 1; }
  sleep 5
done
