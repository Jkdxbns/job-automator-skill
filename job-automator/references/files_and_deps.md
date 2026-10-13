# Output files, join keys, and dependencies

## Files the pipeline writes

| File | Written by | Read by |
|---|---|---|
| `$JOB_DIR/logs/fit.json` | A6 (`score_fit.py`) | A7, A9, B, C, D, F |
| `$JOB_DIR/logs/tailored.json` | B | C, E |
| `$JOB_DIR/resume_{ts}.pdf` · `main_{ts}.tex` | B | — |
| `$JOB_DIR/logs/{email\|dm}_{ts}.json` · Gmail Drafts | C | — |
| `$JOB_DIR/{email\|linkedin_dm}_{ts}.txt` | C5b | C6.5 reminder description |
| `$JOB_DIR/logs/outreach.json` | C | S1, F |
| `$JOB_DIR/logs/.tailor_override` | B-GATE, on "Tailor anyway" | `gate_resume_build.py` |
| `~/job_search/fit_analysis_log.json` | A9 (`log_fit.py`) | F2 |
| `~/job_search/outreach_log.json` | C | S1, F1, F2 |
| `~/job_search/submitted_log.csv` | D (`mark_submitted.py`) | F2 |
| `references/resume_index.json` | B5 (`resume_cache.py index`) | B0 cache check |

## Join keys

- `job_dir` joins `~/job_search/fit_analysis_log.json` (the slim global index) back to
  `$JOB_DIR/logs/fit.json` (the full per-job record).
- `target_name` + `date_drafted` joins the job-specific and global outreach entries, and is how C6.5 and F1
  keep both copies in sync.
- `company` + `role` joins `submitted_log.csv` to a job dir for F2's funnel.

## Dependencies

```bash
pip install requests beautifulsoup4 reportlab pdfplumber python-docx --break-system-packages
```

`generate_pdf.py` additionally needs a working `pdflatex` (TeX Live) on PATH, and `B4-VERIFY` needs `pdfinfo`
(poppler-utils).
