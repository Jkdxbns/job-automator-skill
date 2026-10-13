#!/usr/bin/env bash
# usage: launch_agent.sh NAME [APPLY_URL]
# One call replaces ~8: opens a Ptyxis tab in ~/Desktop/jobs attached to tmux session NAME, starts
# `claude-p -n NAME`, CONFIRMS Claude is up (never types anything into a bare shell), pins
# /model Sonnet and /effort medium, then sends the Apply link (if given).
# NAME: letters, digits, _ and - only (tmux forbids . and :), e.g. Cricut_Firmware-Engineer
set -u
NAME=${1:-}; URL=${2:-}; T="=$NAME:"; DIR=/home/jkdxbns/Desktop/jobs
[[ $NAME =~ ^[A-Za-z0-9_-]+$ ]] || { echo "ERROR bad session name: '$NAME'"; exit 2; }
tmux has-session -t "=$NAME" 2>/dev/null && { echo "ERROR session $NAME already exists"; exit 2; }
ptyxis --tab -T "$NAME" -d "$DIR" -x "tmux new-session -A -s $NAME"
for i in $(seq 1 15); do tmux has-session -t "=$NAME" 2>/dev/null && break; sleep 1; done
tmux has-session -t "=$NAME" 2>/dev/null || { echo "ERROR tab/session did not open: $NAME"; exit 3; }
tmux send-keys -t "$T" "claude-p -n $NAME" Enter
for i in $(seq 1 40); do sleep 2; tmux capture-pane -t "$T" -p | grep -q '^❯' && break; done
if ! tmux capture-pane -t "$T" -p | grep -q 'Claude Code'; then
  echo "ERROR claude did not start in $NAME (nothing else was typed)"; exit 3
fi
for cmd in "/model Sonnet" "/effort medium"; do
  tmux send-keys -t "$T" "$cmd"; sleep 1; tmux send-keys -t "$T" Enter; sleep 3
done
if [ -n "$URL" ]; then
  tmux send-keys -t "$T" "$URL"; sleep 1; tmux send-keys -t "$T" Enter
fi
sleep 1
echo "started $NAME${URL:+ with link}"
