# Resume format reference

**`references/resume_template.tex` is the authority for all typography and layout.** `scripts/generate_pdf.py`
reads that template for the preamble and formatters, generates the body from `tailored.json`, and compiles it
with `pdflatex`. If you need to know a margin, a font size, or a section rule, read the template — not a prose
description of it, which is how this file previously drifted into describing a ReportLab generator that no
longer exists.

This file documents only the **content** decisions the tailoring step makes, which the template cannot
express.

## Engine

- LaTeX (`pdflatex`), driven by `references/resume_template.tex`
- Base class: `article`, `letterpaper`, `11pt`, `lmodern` font
- Output: `$JOB_DIR/resume_{ts}.pdf` + `main_{ts}.tex`
- A cover-letter generator no longer ships with this skill

## Page budget — exactly one page

**One page, always.** `generate_pdf.py` exits 2 on overflow and reports `OVERFLOW_LINES=N`; B4 redrafts (max 2
attempts) and B4-VERIFY asserts `pdfinfo` reads `Pages: 1` before anything may be reported as done. There is
no "2 pages acceptable for senior roles" exception — an earlier version of this file claimed one, and it
contradicted the enforcement in B4.

## Header

`phone | email | portfolio URL | location`, one line. **LinkedIn is not in the header**: with the portfolio
URL the line no longer fits on one line, and the site links LinkedIn (Justin's call, 2026-10-12).

The portfolio URL is chosen by `generate_pdf.py`, not by the tailoring step, from `fit.json` `role_category`:
embedded / firmware / hardware / ASIC roles get `justinmascarenhas.com/embedded`, every other role gets
`justinmascarenhas.com/edge-ai`. It prints `PORTFOLIO=<url>` on each build. To force the other page for one
job, set `_meta.portfolio_track` to `"embedded"` or `"edge-ai"` in `tailored.json`. Never put the **full
track URL** in `personal_info.website` by hand — `generate_pdf.py` overwrites that key on every build.

The **root domain** is a different thing and does live in the profile: `personal_info.website_root`
(`justinmascarenhas.com`), the single source of truth shared with the outreach sign-off
([outreach_rules.md § Substance](outreach_rules.md)). `resolve_portfolio()` reads it and appends the track,
falling back to its `PORTFOLIO` constant only if the key is missing. Change the domain in one place:
`master_profile.json`.

## Section order

`SUMMARY → SKILLS → EXPERIENCE → PROJECTS → EDUCATION`, then `AWARDS` only if it fits.

## Content rules per section

- **Summary** — 2–4 sentences, tightly scoped to the target role. Sentence 1 is degree + school. Never
  "passionate about", "excited to", "seeking opportunities", or "leverage".
- **Skills** — category label bold, items plain. Only categories relevant to this role; drop the rest. Most
  JD-relevant category first, ATS keywords first within each. A skill appears **only** if a bullet included in
  this specific tailored version demonstrates it.
- **Experience** — only roles with at least one relevant bullet. Every bullet carries a metric or a specific
  ATS keyword.
- **Projects** — selected by keyword match; lead with the metric/result bullet.
- **Education** — max 5 courses, relevant to this role only.

The full tailoring prompt that applies these is in [tailoring_prompt.md](tailoring_prompt.md).
