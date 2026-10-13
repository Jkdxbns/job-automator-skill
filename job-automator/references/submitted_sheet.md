# D3.5 / D3.6 — JobApplications Google Sheet append

Loaded by Sub-workflow D after `mark_submitted.py` has written the CSV row.

## The tab layout (read this before writing)

The spreadsheet is **TWO SEPARATE TABS**, `Justin` and `France` — *not* one shared sheet with per-person
columns. Justin only ever writes to the `Justin` tab; the `France` tab is entirely separate and untouched by
this workflow.

Columns A–F on the `Justin` tab:

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Date | Company | Role | Job URL | Outreach | Match |

This schema was corrected 2026-07-20, after the skill previously assumed a wrong single-shared-sheet A–G
layout that never existed. **Read `Justin!A1:F1` live before writing** to confirm the header still matches.

## D3.5 — Resolve the six values

- **Date** — today, `M/D/YYYY` to match existing row style (e.g. `7/20/2026`).
- **Company**, **Role** — from D1.
- **Job URL** — the job link the user pasted in chat before marking submitted. Standing convention: the URL is
  always in the conversation by this point. If genuinely absent, ask for it once.
- **Outreach** — exactly one of `Submitted with referral` / `Submitted without referral`, as plain text. The
  sheet's dropdown is a manual, one-time UI setup and the connector has no data-validation API, so always
  write one of these two exact strings or the dropdown chip goes invalid. Decide: if Sub-workflow C ran this
  session (outreach drafted/sent) → `Submitted with referral`; otherwise → `Submitted without referral`. If
  the user states referral status directly ("didn't reach out"), that overrides.
- **Match** — `match_pct` from `$JOB_DIR/logs/fit.json`, formatted as text like `"62.50%"` to match existing
  rows.

## D3.6 — Append + style

```
ToolSearch: select:mcp__gworkspace__read_sheet_values,mcp__gworkspace__modify_sheet_values,mcp__gworkspace__format_sheet_range
```

All calls use `user_google_email: jmascarenhas1998@gmail.com`, spreadsheet id
`1p7c6m7kLcWg1Zc_O8DGM8Fc90PC3Ly0FP-vmEAayoQw`, sheet name `Justin`.

1. `read_sheet_values` range `Justin!A1:A1000` → let `n` = number of non-empty rows; the new row index is `n +
   1`.
2. `modify_sheet_values` range `Justin!A{n+1}:F{n+1}` with the six D3.5 values.
3. `format_sheet_range` range `Justin!B{n+1}:F{n+1}` → `horizontal_alignment: "CENTER"`.
4. `format_sheet_range` range `Justin!A{n+1}` → `horizontal_alignment: "LEFT"` (keep the date left-aligned).
5. `format_sheet_range` range `Justin!A{n+1}:F{n+1}` → `background_color: "#FFF9C4"` (light yellow marks
   Justin's rows).

Column widths (Role / Outreach padding) are column-level and already set once — do **NOT** re-resize per
append.

If auth prompts, ask the user to complete Google sign-in, then retry from step 1.

Sheet link for the D4 confirmation:
`https://docs.google.com/spreadsheets/d/1p7c6m7kLcWg1Zc_O8DGM8Fc90PC3Ly0FP-vmEAayoQw/edit`
