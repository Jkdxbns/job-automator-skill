# Hooks, error handling, and output files

## Hooks

Two live hooks wired in `~/.claude/settings.json` apply here. Do not bypass them.

- **`~/.claude/hooks/protect_resumes.py`** (PreToolUse/Bash) — DENIES `rm` of `.tex`/`.pdf`/`.docx`/`.doc`
  anywhere, and anything under `~/resumes`, `~/Desktop/jobs`, `~/job_search`, or the skill references dir.
  Escape hatch is `mv` to a `.trash/` dir; `/tmp` is exempt. Enforces CLAUDE.md "Never Delete User Files". It
  does **not** cover overwriting via Edit/Write — still check mtime before replacing anything that looks
  hand-edited.
- **`~/.claude/hooks/lint_skill_on_edit.py`** (PostToolUse/Edit|Write) — runs `validate_skill.py` on any
  edited SKILL.md and injects the report on errors. Generic: it resolves the skill dir from the edited path,
  so it covers this skill automatically.

A third hook, kept in `~/.claude/hooks/` with the other two and **wired** in settings.json:
**`~/.claude/hooks/gate_resume_build.py`** (PreToolUse/Bash) makes B-GATE structural — denies
`generate_pdf.py` / `resume_cache.py index` when the resolved job's fit.json says `apply == "No"` and no
`logs/.tailor_override` marker exists. A hard blocker is denied unconditionally, marker ignored. Fails open on
anything it cannot resolve.

Validate after any edit to this file (no argument = this skill):
```bash
python3 ~/.claude/skills/job-automator/scripts/validate_skill.py
```
`scripts/reflow_md.py <file> 110 --write` re-wraps prose to 110 columns when an edit leaves ragged lines. It
never touches code blocks, tables or headings, and it refuses to write if the content words change or if a
wrap would make a prose line start with `|` (markdown would read it as a table row).

---

## Shared Error Handling

| Error | Action |
|---|---|
| JD scrape blocked / JS-rendered page | Ask the user to paste the JD text |
| JSON parse fails | Retry: "Return ONLY a raw JSON object starting with {" |
| Resume file not found | Ask — do not guess the path |
| `logs/fit.json` missing | Run Sub-workflow A first |
| PDF generation error | Check `generate_pdf.py`; usually a missing import |
| Resume build denied by hook | B-GATE fired — present the popup, don't force it |

## Output Files & Dependencies

Every file the pipeline writes, the join keys between the logs, and the pip / pdflatex / poppler dependencies:
[files_and_deps.md](files_and_deps.md).

The two that matter most: `$JOB_DIR/logs/fit.json` is written **only** by `score_fit.py` and is the join key
source for everything downstream; `~/job_search/submitted_log.csv` is written **only** by `mark_submitted.py`.
