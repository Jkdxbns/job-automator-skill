# Sub-workflow B — tailoring mechanics

Loaded during B, after B-GATE has cleared. **B-GATE** stays in SKILL.md because it runs before this file is
read. **B4-VERIFY** and **B4.5's FIXABLE vs CEILING** moved here from SKILL.md word for word; they are
enforcement, not optional.

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

**B4-VERIFY — assert the PDF exists before reporting done (mandatory).** Never trust the exit code alone:
```bash
PDF=$(ls -t $JOB_DIR/resume_*.pdf 2>/dev/null | head -1)
if [ -z "$PDF" ] || [ ! -s "$PDF" ]; then
  echo "NO PDF — resume did not build"
else
  pdfinfo "$PDF" | grep -i Pages     # must read "Pages: 1"
fi
```
If no non-empty `resume_*.pdf` exists, the build failed regardless of what any earlier message implied — stop
and say so. If `pdfinfo` reports more than one page, treat it as the exit-2 overflow path and redraft. Only a
real, existing, single-page PDF may be reported as done in B5.

## On overflow (exit 2) — read `OVERFLOW_LINES=N` and shorten the tailored JSON inline using the redraft
prompt in [tailoring_prompt.md](tailoring_prompt.md): shorten the longest bullets first, then drop
the weakest bullet from the least-relevant entry, then drop the least-relevant project. Never remove the
summary, skills, or education, and never cut a bullet containing an ATS keyword from `top_ats_keywords`.
Re-run the generator; max 2 attempts, then save as-is and warn.

**On overflow (exit 2)** — read `OVERFLOW_LINES=N` and shorten the tailored JSON with the redraft prompt in
[tailoring_prompt.md](tailoring_prompt.md): longest bullets first, then the weakest bullet of the
least-relevant entry, then the least-relevant project. **Never** cut the summary, skills, education, or a
bullet carrying an ATS keyword. Max 2 attempts, then save as-is and warn.

**B4.5 — Verify ATS keyword coverage (always run)**
```bash
python3 ~/.claude/skills/job-automator/scripts/verify_coverage.py $JOB_DIR/logs/fit.json $JOB_DIR/logs/tailored.json
```
Exit 0 = covered · 1 = gaps (expected and fine) · 2 = error. The B3 prompt *instructs* the model to mirror ATS
keywords; nothing ever confirmed they landed. **Reproduce the output in your reply** (A7 hard rule — Bash
output never reaches Justin). It splits what is missing into two very different things:

- **🔧 FIXABLE** — the master profile backs this skill but *this* resume dropped it. Offer to surface it by
  reordering or reselecting a bullet, or adding to skills. **Never invent a bullet — only surface what already
  exists.**
- **🚧 CEILING** — nothing in the master profile backs it. This is the honest ceiling for the role. **Do not
  invent it, and do not quietly add it to skills.** Knowing this *before* applying is the point.

If FIXABLE items exist, ask once whether to redraft. If only CEILING items remain, state the true coverage and
move on — that is the realistic ATS score for this application.

## B5 — Index + report
 Index for future reuse, then report the PDF path, the TEX path, the logs dir, the reuse keyword hash, the top
 5 ATS keywords injected, and `Pages: 1`.
```bash
python3 ~/.claude/skills/job-automator/scripts/resume_cache.py index $JOB_DIR/logs/fit.json $JOB_DIR \
  $JOB_DIR/resume_*.pdf $JOB_DIR/main_*.tex
```

**B5 — Index + report.** Index for reuse (`resume_cache.py index`), then report the PDF and TEX paths, logs
dir, reuse hash, top 5 ATS keywords injected, and `Pages: 1`. Command above.

**Portfolio link — every resume.** The header is `phone | email | portfolio | location`; LinkedIn is
deliberately left off. `generate_pdf.py` picks the URL from `role_category`, printing `PORTFOLIO=<url>`:
embedded/firmware/hardware roles get `justinmascarenhas.com/embedded`, every other role gets
`justinmascarenhas.com/edge-ai`. Name the URL used when reporting the PDF in B5. Details and the one-job
override: [resume_format.md § Header](resume_format.md).

---

