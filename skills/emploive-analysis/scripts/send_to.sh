#!/usr/bin/env bash
# usage: send_to.sh NAME "text" [--force]
# Types `text` into the Claude session NAME (text, 1s, Enter). Refuses if the session isn't running
# claude, or is busy (a busy agent would queue the text); --force overrides the busy check.
set -u
NAME=${1:-}; TEXT=${2:-}; FORCE=${3:-}; T="=$NAME:"
tmux has-session -t "=$NAME" 2>/dev/null || { echo "ERROR no such session: $NAME"; exit 2; }
[ "$(tmux display -p -t "$T" '#{pane_current_command}')" = "claude" ] || { echo "ERROR $NAME is not running claude"; exit 3; }
if [ "$FORCE" != "--force" ] && tmux capture-pane -t "$T" -p | tail -12 | grep -q "esc to interrupt"; then
  echo "BUSY $NAME, not sent"; exit 4
fi
tmux send-keys -t "$T" "$TEXT"; sleep 1; tmux send-keys -t "$T" Enter
echo "sent to $NAME: $TEXT"
