# job-automator — skill + everything it uses

Snapshot of the job-automator Claude Code skill and every file it reads, writes or depends on, so the
whole system can be edited from Claude Code on the web.

## Repo path → local path

| Repo path | Local path | What it is |
|---|---|---|
| `job-automator/` | `~/.claude/skills/job-automator/` | The skill: `SKILL.md`, `scripts/`, `references/`, `hooks/` |
| `skills/emploive-analysis/` | `~/.claude/skills/emploive-analysis/` | Skill that runs job-automator per Emploive job |
| `skills/batch-delegate/` | `~/.claude/skills/batch-delegate/` | Batch layer used by job-automator's batch variant |
| `claude/hooks/` | `~/.claude/hooks/` | Live hooks: `protect_resumes.py`, `gate_resume_build.py`, `lint_skill_on_edit.py` |
| `claude/settings.json` | `~/.claude/settings.json` | Wires the hooks (PreToolUse/Bash, PostToolUse/Edit\|Write) |
| `claude/CLAUDE.md` | `~/.claude/CLAUDE.md` | Global rules the skill relies on |
| `memory/` | `~/.claude/projects/-home-jkdxbns-Desktop-jobs/memory/` | Project memory (outreach, resume, scoring feedback) |
| `job_search/` | `~/job_search/` | Global logs: `fit_analysis_log.json`, `outreach_log.json`, `outreach_index.json`, `submitted_log.csv` |
| `jobs/<company_role>/logs/*.json` | `~/Desktop/jobs/<company_role>/logs/` | Past `fit.json` / `tailored.json` per job — use as regression fixtures |

PDFs and `.tex` outputs under `~/Desktop/jobs` are not included.

## Working on the web

Scripts and `SKILL.md` use absolute paths (`~/.claude/skills/job-automator/...`, `~/job_search/...`).
In a cloud session, either run scripts from `job-automator/scripts/` directly, or symlink first:

```bash
mkdir -p ~/.claude/skills && ln -sfn "$PWD/job-automator" ~/.claude/skills/job-automator
ln -sfn "$PWD/job_search" ~/job_search
```

Not available on the web: gworkspace MCP (Sheets, Gmail drafts), Claude in Chrome, pdflatex (unless
installed), live hooks. Lint after any skill edit: `python3 job-automator/scripts/validate_skill.py`.

## Syncing

`./sync.sh pull` copies code and config (skills, hooks, settings, CLAUDE.md, memory) from the repo onto the
local paths, after `git pull`. Every replaced local file is kept as `<file>.bak_<timestamp>`. It never
copies `job_search/` or `jobs/` back — those are snapshots, and the local copies are the live data.
`./sync.sh push` copies the local paths (including a fresh data snapshot) into the repo, then commit and push.
