#!/usr/bin/env bash
# sync.sh pull — repo → local (code and config only; never overwrites live data)
# sync.sh push — local → repo (code, config, and a fresh snapshot of the data)
set -euo pipefail
R="$(cd "$(dirname "$0")" && pwd)"
X=(--exclude=.git --exclude=__pycache__ --exclude='*.pyc')
STAMP=$(date +%Y%m%d_%H%M%S)
# pull keeps a copy of every local file it replaces: <file>.bak_<stamp>
B=(--backup --suffix=".bak_$STAMP")

case "${1:-}" in
  pull)
    rsync -a "${X[@]}" "${B[@]}" "$R/job-automator/"             ~/.claude/skills/job-automator/
    rsync -a "${X[@]}" "${B[@]}" "$R/skills/emploive-analysis/"  ~/.claude/skills/emploive-analysis/
    rsync -a "${X[@]}" "${B[@]}" "$R/skills/batch-delegate/"     ~/.claude/skills/batch-delegate/
    rsync -a "${B[@]}" "$R/claude/hooks/"                         ~/.claude/hooks/
    rsync -a "${B[@]}" "$R/claude/settings.json" "$R/claude/CLAUDE.md" ~/.claude/
    rsync -a "${B[@]}" "$R/memory/" ~/.claude/projects/-home-jkdxbns-Desktop-jobs/memory/
    echo "pulled code + config. job_search/ and jobs/ are snapshots only — not copied back."
    ;;
  push)
    rsync -a "${X[@]}" --exclude=/hooks/ ~/.claude/skills/job-automator/ "$R/job-automator/"   # hooks live in claude/hooks only
    rsync -a "${X[@]}" ~/.claude/skills/emploive-analysis/        "$R/skills/emploive-analysis/"
    rsync -a "${X[@]}" ~/.claude/skills/batch-delegate/           "$R/skills/batch-delegate/"
    cp -p ~/.claude/hooks/*.py "$R/claude/hooks/"
    cp -p ~/.claude/settings.json ~/.claude/CLAUDE.md "$R/claude/"
    rsync -a ~/.claude/projects/-home-jkdxbns-Desktop-jobs/memory/ "$R/memory/"
    rsync -a ~/job_search/ "$R/job_search/"
    (cd ~/Desktop/jobs && find . -path '*/logs/*.json' -type f -print0 \
       | rsync -a --from0 --files-from=- ./ "$R/jobs/")
    echo "copied local → repo. Now: git -C $R add -A && git -C $R commit -m '...' && git -C $R push"
    ;;
  *) echo "usage: $0 pull|push" >&2; exit 2 ;;
esac
