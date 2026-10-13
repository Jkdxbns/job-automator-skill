# Sub-workflow D — Mark Submitted

Loaded on "mark submitted" / "submitted" / "done".

Logs a submitted application to TWO places: the local CSV, and the **JobApplications** Google Sheet. A plain
log write — no drafting, no verdicts.

**D1 — Resolve company + role.** From `$JOB_DIR/logs/fit.json` if it exists, else from what the user named,
else ask.

**D2 — Resolve session id.** Read `CLAUDE_CODE_SESSION_ID` directly — always the current session's own id, no
need to ask or inspect transcripts.

**D3 — Run the script.** Always. **Never hand-append a row to the CSV** — two malformed rows with the wrong
column count got in that way.
```bash
python3 ~/.claude/skills/job-automator/scripts/mark_submitted.py \
  --company "{company}" --role "{role}" \
  --session-id "$CLAUDE_CODE_SESSION_ID" --job-dir "${JOB_DIR:-}"
```
Appends one row to `~/job_search/submitted_log.csv` (`date_submitted, company, role, resume_cmd, job_dir`),
creating the file with a header if absent. `resume_cmd` is pre-built as `claude-d --resume '<session_id>'`
(`claude-d` is his alias for `claude --dangerously-skip-permissions`).

**D3.5 / D3.6 — Append + style the JobApplications sheet.** Procedure in
[submitted_sheet.md](submitted_sheet.md): the spreadsheet is **two separate tabs** (`Justin` and
`France`, not one shared sheet) and Justin only ever writes to `Justin`, whose columns A–F are Date, Company,
Role, Job URL, Outreach, Match. Read `Justin!A1:F1` live before writing to confirm the header. `Outreach` must
be exactly `Submitted with referral` or `Submitted without referral` (the dropdown has no data-validation API,
so any other string breaks the chip) — with referral if Sub-workflow C ran this session, unless the user says
otherwise. Append at row `n+1`, centre B–F, left-align A, background `#FFF9C4`. Do not re-resize columns.

**D4 — Confirm** what was logged to the CSV (the script's stdout) and to the sheet (company, role, row
number), with the link
`https://docs.google.com/spreadsheets/d/1p7c6m7kLcWg1Zc_O8DGM8Fc90PC3Ly0FP-vmEAayoQw/edit`.


**D5 — Offer recruiter outreach (Sub-workflow G), once.** After D4, and only after it: match ≥ 80 → 10
emails, 60–79 → 5, < 60 → do not offer at all. Ask once — *"Draft outreach for {company}? Match is
{match_pct}%, so that's {n} recruiter emails. Yes / No / a number."* — then stop. A number in the reply wins
("yes but 20" → `--n 20`). On a yes, follow
[workflow_g_recruiter_outreach.md](workflow_g_recruiter_outreach.md); on a no, nothing runs and no API credit
is spent.
---

