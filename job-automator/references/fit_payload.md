# A0–A3 — setup, JD retrieval, and the score_fit.py payload

## A0 – A2.5 — job dir, keywords, JD text, hard-blocker pre-screen

**A0 — Job directory + keyword cache**
```bash
python3 ~/.claude/skills/job-automator/scripts/build_keywords.py
python3 ~/.claude/skills/job-automator/scripts/build_skills_db.py
export JOB_CWD=$(pwd)
```
After A3 sets the slugs:
```bash
export JOB_DIR=${JOB_CWD}/${company_slug}_${job_slug}
mkdir -p ${JOB_DIR}/logs
```
`$JOB_DIR` is an exported env var, available to every later bash/Python step. Parallel sessions each get their
own — separate shell processes.

**A1 — Load candidate keywords.** Read `references/keywords_only.json`, not the full profile — A only needs
keywords. `profile.all_keywords` feeds A4; `master_profile.json` is loaded only in B and A6.5.

**A2 — Get JD text.** `python3 ~/.claude/skills/job-automator/scripts/scrape_jd.py "<url>"` — exit 2 or 3 →
ask the user to paste the JD. Most target career sites (Apple, Tesla, Rivian, Greenhouse/Workday/Lever) are
JS-rendered: do not spend turns on static scrapes — go straight to browser extraction using page-text
extraction, and if that returns only nav/footer boilerplate, ask for a paste (global CLAUDE.md).

**A2.5 — Hard blocker pre-screen** (regex, zero tokens)
```bash
RESULT=$(echo "$jd_text" | python3 ~/.claude/skills/job-automator/scripts/prescreen_jd.py); EXIT=$?
```
`EXIT=1` → parse `BLOCK:<category>:<matched_phrase>`, print the ⛔ HARD BLOCK banner with the matched phrase,
MATCHES/APPLY = No, and "F-1 OPT holders do not qualify." **STOP. Do not run A3–A9, B, or C.** Not
overridable. `EXIT=0` (CLEAR) → continue. Sponsorship regexes include the Eaton-derived CPT/OPT/STEM-OPT
phrasings — do not remove them.


---

Two schemas. A3 is what the model extracts from the JD; A6 is what it hands to `scripts/score_fit.py`, which
computes the score and verdict and writes fit.json.

---

## A3 — the `jd` object (model-side extraction, no script)

Read the JD and produce this. Every later step reads from it, and A0 needs `company_slug` + `job_slug` to
create `$JOB_DIR`. Slugs are lowercase and hyphenated (`bear-robotics`, `swe-ii`).

```json
{
  "company_name": "...", "company_slug": "...",
  "job_title": "...", "job_slug": "...",
  "required_skills": [], "preferred_skills": [], "all_keywords": [],
  "required_experience_years": 0,
  "experience_level_stated": "intern|entry|junior|mid|senior|staff|not_stated",
  "sponsorship_mentioned": false, "sponsorship_offered": null,
  "sponsorship_raw_text": null,
  "location": "...", "remote_ok": null, "clearance_required": false,
  "key_responsibilities": [], "ats_keywords": [],
  "role_category": "edge_ai_robotics|ml_systems|embedded_systems|hpc_cuda"
}
```

⚠️ **Classify only what the JD actually asks for.** `ats_keywords` are the terms a screener would search on;
`required_skills` are the hard asks. These two drive the A4 denominator, so padding them with boilerplate
deflates the score. Equally, do not silently drop a demanded skill to shrink the denominator and inflate the
score.

---

## A6 — the `score_fit.py` payload

```bash
cat > /tmp/fit_payload.json <<'JSON'
{
  "jd": { "...the A3 object..." },
  "have": ["Python", "Computer Vision"],
  "adjacent": [{"jd_skill": "JAX", "you_have": "PyTorch"}],
  "missing": ["SQL", "Spark"],
  "hard_blocker": {"triggered": false, "reason": null},
  "flags": {"no_sponsorship": false, "location_conflict": false},
  "production_scope_required": false,
  "semantic": null
}
JSON
python3 ~/.claude/skills/job-automator/scripts/score_fit.py /tmp/fit_payload.json --job-dir "$JOB_DIR"
```

Single role in the main session: SKILL.md A6 runs this with `--report --log` appended. Batch and delegate runs
keep the command exactly as written above.

- `have` / `missing` are lists of strings. `adjacent` accepts either `{"jd_skill": ..., "you_have": ...}`
  dicts (preferred — the report renders the arrow) or plain `"JAX -> PyTorch"` strings.
- `hard_blocker.reason` is the exact matched phrase plus its category (ITAR / Clearance / Citizenship / No Sponsorship). `flags.no_sponsorship = true` (explicit refusal) is promoted to a hard blocker by the script — it is not a soft flag.
- `semantic` is `null` on the single scoring run; the A6.5 read is merged afterwards with `score_fit.py --add-semantic <file> --job-dir "$JOB_DIR"` (no re-score). It is stored verbatim and gets a `calibration_delta`; it has no path
  to the verdict.

### What the script computes (do not compute any of it by hand)

`match_pct` (adjacency at half credit, denominator = the whole classified set, plus a zero-HAVE floor at 50
and a required-coverage cap at 60) · `score_detail` (counts, `jd_ask_size`, `req_cov`, `cap_applied`) ·
`seniority_fit` · `experience_mismatch` · `verdicts.matches` · `verdicts.apply` · `thresholds_used`. Then it
writes `$JOB_DIR/logs/fit.json` atomically.

Formula derivation and backtest: `scoring_rationale.md` §1.
