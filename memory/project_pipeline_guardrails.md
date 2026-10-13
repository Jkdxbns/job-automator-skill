---
name: project-pipeline-guardrails
description: "job-automator anti-drift guardrails: script-rendered A7 report, skill linter, and two enforcement hooks (resume-delete block + SKILL.md lint)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 60ac21ec-298b-46ac-9d63-ce358290a5f1
  modified: 2026-09-12T10:50:07.624Z
---

Guardrails added 2026-09-10 to stop the model drifting off the job-automator SKILL.md
pipeline. Do NOT bypass or duplicate these.

**Scripts (in `~/.claude/skills/job-automator/scripts/`):**
- `render_report.py` — the A7 fit report is rendered ONLY by this script (run it, print
  stdout verbatim). Hand-rendering the report is forbidden — that was the cause of the
  non-uniform-verdict complaint. Handles fit.json schema drift (adjacent as str or dict,
  missing seniority_fit / llm_analysis). One path = Format 1, many = Format 2 batch table.
- `log_fit.py` — A9's global-log row is written ONLY by this script, never by hand. Takes one
  or many `fit.json` paths (or job dirs); idempotent per job_dir, atomic write, dates rows by
  the fit.json mtime. Added 2026-09-12 after an audit found 501 fit.json on disk vs 167 logged
  rows, the loss concentrated on batch days. In batch mode pass every fit.json in one call.
- `validate_skill.py` — lints any skill: name/description hard caps (≤64 / ≤1024 chars),
  SKILL.md size vs the ~500-line/~5000-word progressive-disclosure guidance, and
  reference-integrity (every scripts//references/ path in SKILL.md must exist). Exit 1 =
  errors. Run `python3 validate_skill.py <skill_dir>` after editing any SKILL.md.

**Hooks (in `~/.claude/hooks/`, wired in `~/.claude/settings.json`):**
- `protect_resumes.py` (PreToolUse/Bash) — DENIES `rm` of .tex/.pdf/.docx or anything under
  ~/resumes, ~/Desktop/jobs, or the skill references dir. Escape hatch is `mv` to a `.trash/`
  dir (enforces the CLAUDE.md "Never Delete User Files" rule; needed because auto mode skips
  permission prompts). /tmp deletions are exempt.
- `lint_skill_on_edit.py` (PostToolUse/Edit|Write) — runs validate_skill.py whenever a
  SKILL.md is edited and injects the lint report if it finds errors (catches dangling
  references before they break the pipeline).

**Open audit warnings (not errors):** job-automator SKILL.md is ~9971 words (2× the
progressive-disclosure guidance) — a split into references/ is the recommended next step but
was NOT done (risk of breaking the pipeline; needs a focused pass). job-automator and pa
descriptions sit near the 1024-char cap. `references/resume.docx` / `cv.pdf` are absent
(user-supplied inputs; runtime uses master_profile.json, so not a break).

Related: [[feedback-master-profile-permission]], [[feedback-calendar-reminder-format]].
