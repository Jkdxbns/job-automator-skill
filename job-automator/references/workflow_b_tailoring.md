# Sub-workflow B — tailoring mechanics

Loaded during B, after B-GATE has cleared. The three rules that stay in SKILL.md itself — **B-GATE**,
**B4-VERIFY**, and **B4.5's FIXABLE vs CEILING** — are enforcement and are not repeated here.

## B0 — Resume cache check

```bash
RESULT=$(python3 ~/.claude/skills/job-automator/scripts/resume_cache.py check $JOB_DIR/logs/fit.json); EXIT=$?
```
`EXIT=0` (CACHE_HIT) → show the previous company/role, date, PDF and TEX paths, and the identical-keyword
count, then offer `reuse` (copy PDF and TEX into `$JOB_DIR` with a new timestamp, skip B1–B4, go to B5) or
`fresh` (continue to B1). `EXIT=1` (CACHE_MISS) → continue to B1.

The cache key is the sorted ATS keyword set **salted with a SHA-256 hash of `master_profile.json`**, so any
profile edit invalidates every cached resume — without it, removing an undefendable claim would keep serving
resumes that still carry it into live applications.


## B1 / B2 / B3 — Load context, pick a base summary, tailor.** The pre-filter snippet (top 4 experience
entries, top 5 projects by keyword hits), the `summary_pool` selection, and the verbatim system/user prompts
with the JSON return shape are all in [tailoring_prompt.md](tailoring_prompt.md) — use them as
written. No fit file → run Sub-workflow A first. The rules that matter most: never fabricate anything not in
master_profile; select and reorder rather than invent; a skill appears only if a bullet included in *this*
version demonstrates it; every bullet carries a metric or an ATS keyword; target one page.

⚠️ **Never edit `master_profile.json` without Justin's explicit in-the-moment permission** — it is the source
of truth for every tailored resume, so a silent edit propagates into live applications. Propose, state the
reasoning, wait.

## B4 — Generate PDF (1-page enforcement)
```bash
python3 -c "import json,sys; open('$JOB_DIR/logs/tailored.json','w').write(
  json.dumps(json.loads(sys.argv[1]),indent=2))" '<tailored_json>'
python3 ~/.claude/skills/job-automator/scripts/generate_pdf.py $JOB_DIR/logs/tailored.json $JOB_DIR
```
- Exit 0 → single page. Writes `resume_{ts}.pdf` and `main_{ts}.tex` into `$JOB_DIR`.
- Exit 2 → overflow. Read `OVERFLOW_LINES=N` from stdout.
- Exit 1 → **compile FAILED.** The script prints the pdflatex log tail to stderr and writes NO pdf. Do NOT
  report success, do NOT continue to B4.5/B5, and do NOT hand Justin a lone `.tex` as if it were the
  deliverable. Show the log tail, say the resume did not build, stop.


## On overflow (exit 2) — read `OVERFLOW_LINES=N` and shorten the tailored JSON inline using the redraft
prompt in [tailoring_prompt.md](tailoring_prompt.md): shorten the longest bullets first, then drop
the weakest bullet from the least-relevant entry, then drop the least-relevant project. Never remove the
summary, skills, or education, and never cut a bullet containing an ATS keyword from `top_ats_keywords`.
Re-run the generator; max 2 attempts, then save as-is and warn.


## B5 — Index + report
 Index for future reuse, then report the PDF path, the TEX path, the logs dir, the reuse keyword hash, the top
 5 ATS keywords injected, and `Pages: 1`.
```bash
python3 ~/.claude/skills/job-automator/scripts/resume_cache.py index $JOB_DIR/logs/fit.json $JOB_DIR \
  $JOB_DIR/resume_*.pdf $JOB_DIR/main_*.tex
```

---

