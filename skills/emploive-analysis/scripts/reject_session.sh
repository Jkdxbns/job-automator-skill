#!/usr/bin/env bash
# usage: reject_session.sh NAME
# Rename the Claude session AND the terminal tab to REJECTED, confirm the session rename took,
# then close the tmux session (which closes its tab). Only call this for a session whose verdict is final.
set -u
NAME=$1; T="=$NAME:"
tmux has-session -t "=$NAME" 2>/dev/null || { echo "no such session: $NAME"; exit 1; }
# only act on an idle Claude prompt
if tmux capture-pane -t "$T" -p | tail -12 | grep -q "esc to interrupt"; then echo "$NAME is still running, not rejecting"; exit 2; fi
tmux send-keys -t "$T" "/rename REJECTED"; sleep 1; tmux send-keys -t "$T" Enter
for i in $(seq 1 10); do sleep 1; tmux capture-pane -t "$T" -p | grep -q "REJECTED" && break; done
if ! tmux capture-pane -t "$T" -p | tail -6 | grep -q "REJECTED"; then echo "rename to REJECTED not confirmed for $NAME; leaving it open"; exit 3; fi
# rename the terminal TAB too: tmux forwards its title to the terminal when set-titles is on
SID=$(tmux display-message -p -t "=$NAME:" '#{session_id}')    # set-option rejects "=NAME"; the id is exact
tmux set-option -t "$SID" set-titles on
tmux set-option -t "$SID" set-titles-string "REJECTED"
tmux refresh-client -S 2>/dev/null
sleep 3     # let the tab title update visibly before it closes
tmux kill-session -t "=$NAME" && echo "rejected (session + tab renamed) and closed: $NAME"
