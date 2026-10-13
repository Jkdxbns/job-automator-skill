# Sub-workflow F — Outcome tracking

Loaded on "X replied", "got an interview", "rejected by X", "offer from X", "how's my funnel".

Without outcomes the system cannot tell which match band, resume version, or outreach hook actually converts —
so it cannot improve, and neither can targeting ([scoring_rationale.md §6](scoring_rationale.md)).

| User says | Action |
|---|---|
| "got a reply from X" / "X replied" | F1 — record reply |
| "got an interview" / "screen scheduled" / "OA" | F1 — record interview stage |
| "rejected by X" / "ghosted" | F1 — record rejection |
| "offer from X" | F1 — record offer |
| "how's my funnel" / "what's converting" | F2 — funnel report |

**F1 — Record an outcome.** Resolve company + role (from `$JOB_DIR/logs/fit.json` if present, else ask). Write
to **every** record that exists for it: `$JOB_DIR/logs/fit.json` (add/update an `outcome` object) ·
`~/job_search/fit_analysis_log.json` (matching row, `job_dir` key) · `$JOB_DIR/logs/outreach.json` **and**
`~/job_search/outreach_log.json` (set `outcome` + `outcome_date`, if it came via outreach) ·
`~/job_search/submitted_log.csv` is the join if the role was submitted.

```json
"outcome": {
  "stage": "no_response | replied | screen | technical | onsite | offer | rejected | ghosted",
  "date": "YYYY-MM-DD",
  "channel": "application | outreach | referral",
  "notes": "free text — what was asked, why rejected if known"
}
```
- **Never infer an outcome.** Only record what the user states.
- `ghosted` only when he says so, or on request during an F2 sweep for applications older than ~30 days with
  no response.
- A rejection with a stated reason goes in `notes` — the highest-value field in this skill for improving
  targeting.

**F2 — Funnel report.** Read the global logs and print `analyzed → submitted → outreach sent → replies →
interviews → offers`, the conversion rate between each pair, and reply rate by `match_pct` band and by
`hook_used`. **State plainly when a rate rests on too few data points to mean anything (n < 10)** rather than
presenting it as signal.

---

