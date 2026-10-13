---
name: project_jobapplications_sheet
description: "JobApplications Google Sheet — mark-submitted also appends a styled row here; ID, columns, and styling conventions"
metadata: 
  node_type: memory
  type: project
  originSessionId: bce1115d-1116-4fc7-8dc5-43ce77805db8
  modified: 2026-08-27T19:05:11.189Z
---

On every "mark submitted" / "submitted" / "done", in addition to the CSV log ([[reference_interview_prep_files]] sits elsewhere), append one row to the **JobApplications** Google Sheet.

- **Spreadsheet ID:** `1p7c6m7kLcWg1Zc_O8DGM8Fc90PC3Ly0FP-vmEAayoQw` (owner jmascarenhas1998@gmail.com, gworkspace MCP).
- **Two separate tabs, not shared columns:** `Justin` (sheet id 0, 1000x26) and `France` (sheet id 1902739977, 31x14). Justin and France are two people independently tracking applications to motivate each other — each writes only to their own tab. Corrected 2026-07-20; an earlier version of this memory wrongly described one shared sheet with `Justin`/`France` as columns F/G — that layout does not exist.
- **Justin tab columns (A–F):** `Date | Company | Role | Job URL | Outreach | Match`. Header row 1; data rows appended below (verified live 2026-07-20: row 2 was an Amazon entry, Match stored as e.g. `"92.00%"`).
  - `Date` = submission date, `M/D/YYYY` (e.g. `7/20/2026`), written under Justin's own tab.
  - `Outreach` = "Submitted with referral" or "Submitted without referral" (plain text — connector has no data-validation API, so the dropdown was set up once by hand; keep writing the exact option strings so the chip stays valid).
  - `Match` = fit.json `match_pct`, formatted as text like `"62.50%"` to match the existing row style.
  - Job URL comes from chat (user pastes it before marking submitted). "With/without referral" inferred from whether outreach ran this session, unless the user states it directly (e.g. "didn't reach out" → without referral).
- **Styling per row:** all cells CENTER except the Date column (A) which is LEFT. Light-yellow `#FFF9C4` covers the full row `A:F` on the Justin tab (no France column to avoid within this tab).
- **Rejection styling:** when the user asks to reconcile Gmail rejections against the sheet, a row that turns out to be rejected gets its background changed from light-yellow `#FFF9C4` to light-red `#FFCDD2` (still full row `A:F`). Gmail label `Jobs/rejections` holds the rejection notices — match by req ID / exact role text in the email body, not just company name, since several companies (Field AI, KLA, NVIDIA, Amazon) have multiple rows in the sheet and only some reqs are rejected. A "withdrawn" notice (e.g. Amazon self-withdrawal) is not an employer rejection but still marks the row closed — flag it as a withdrawal to the user rather than silently treating it as identical.
- Before writing, always read the target tab's actual header row live (`Justin!A1:F1`) rather than trusting this memory's column list — confirm it still matches before appending.

Baked into the job-automator skill's Sub-workflow D (steps D3.5/D3.6) — mark-submitted writes the CSV log AND appends+styles this sheet row automatically. The skill's SKILL.md file still describes the old wrong single-sheet A–G layout as of 2026-07-20 and should be updated to match this tab-based structure.
