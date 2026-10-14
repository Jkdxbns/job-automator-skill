---
name: job-automator
description: >
  Unified job application skill: job fit analysis, resume tailoring, cold
  outreach, logging submissions, outcome tracking. Triggers on: "analyze this
  job", "check job fit", "should I apply", "tailor my resume", "tailor", "draft
  cold email", "draft LinkedIn DM", "draft outreach", "follow up with X", "mark
  X sent", "mark submitted", "submitted", "X replied", "rejected by X", "how's
  my funnel", any job URL, OR a pasted block of job-description text (a role
  title with responsibilities or qualifications) even with no instruction verb —
  a bare JD paste means "analyze this job". Each request is ONE step: never
  chain to the next sub-workflow unasked. Always run fit analysis before
  tailoring; always show outreach drafts before sending (cold email becomes a
  Gmail draft, never auto-sent; a LinkedIn DM prints inline to copy).
---

# Job Automator — Unified Skill

Single entry point for the job application pipeline. Five sub-workflows — A, B, C, D, F — each its own step.

**Verdict authority — the rule governing everything below.** The keyword score decides APPLY. The semantic/LLM
read is informational only and has no path to the verdict, enforced in code (`scripts/score_fit.py`) rather
than by discipline.

**Standing output rule — every step.** Justin does not see Bash output; Claude Code collapses it to "ran N
shell commands." Any script output he should read — the A7 report, the B4.5 coverage report — must be **copied
into your message** in a fenced code block. Running a script is not showing him the result. Never say "above"
about a tool result.

**References load on demand** — each step names the file it needs. `scoring_rationale.md` holds the formulas,
backtests and audit history; read it only when changing a rule.


---

## S1 — Session start sweep (runs BEFORE any routing)

Once per session, before anything else, whatever was asked. Must stay above the routing table — buried inside
C it fired for ~5% of sessions and 21 of 22 drafts went past due.

1. Run it. This *is* the sweep:
   ```bash
   python3 ~/.claude/skills/job-automator/scripts/process_followups.py --count
   ```
   → `FOLLOWUPS=<n> DRAFTS=<n>`
2. If `FOLLOWUPS` > 0, print **one line**, then immediately continue with what was asked:
   > `note: {N} outreach messages past follow-up date — say "followups" to triage`

   **Do NOT ask, wait, or stall.** Once per session, then never again.
3. On "followups": `--obtain-pending` for the table, then `--get-notes <ids>` for only the people being
   drafted to. **One follow-up per contact** — `--set-status <ids> --status followed_up_1_sent` drops them out
   of pending. Route through **C1.5** (reply into the real thread, never a fresh first-touch draft).

`process_followups.py --help` is the authority on every other argument. It is the only thing that reads or
writes `outreach_log.json`, so that file never needs opening.
---

## Intent Routing

**Every request is ONE step.** Justin drives the sequence with short commands — paste a JD, then later
"tailor", then later "draft an email". He does **not** ask for combined runs, so there are no chained routes.
Run exactly the step asked for, then stop.

| User says | Run | Procedure |
|---|---|---|
| a pasted JD block (role + responsibilities/qualifications), **no verb** | **A** (default — never ask "what do you want?") | below |
| "analyze" / "check fit" / "should I apply" / a job URL | A | below |
| "tailor" / "tailor my resume" | **B** on the current job | below |
| "draft cold email" / "draft LinkedIn DM" / "draft outreach" | C | `references/workflow_c_outreach.md` |
| "follow up with X" / "mark X sent" | C1.5 / C6.5 | `references/workflow_c_outreach.md` |
| "mark submitted" / "submitted" / "done" | D | `references/workflow_d_submitted.md` |
| "draft recruiter emails" / "find recruiters" / "hunt contacts" (**submitted roles only**) | G | `references/workflow_g_recruiter_outreach.md` |
| "X replied" / "got an interview" / "rejected by X" / "offer from X" | F1 | `references/workflow_f_outcomes.md` |
| "how's my funnel" / "what's converting" | F2 | `references/workflow_f_outcomes.md` |

**Read the named file in full before acting on a C / D / F route.** A and B are inline below.

**Rules**
- **Stop after the requested step. Never chain to the next unasked.** Standing preference; it overrides any
  suggestion to auto-run the pipeline. After A, report the fit and stop — do not offer to tailor or start
  tailoring. After B, report the PDF and stop.
- **A is a precondition, not a chain.** B and C read `$JOB_DIR/logs/fit.json`; if missing, run A silently
  first, then continue into the step actually asked for.
- C needs target person info (name + title + company) — ask if absent. D needs only company + role.
- Never spawn subagents without asking first (global CLAUDE.md → Subagents).
- If intent is genuinely unclear, ask which of the five steps he wants.

**HARD BLOCKER RULE — overrides everything, including explicit user instructions.** After A, check
`verdicts.hard_blocker_triggered`. If true:
- Print the blocker reason. **STOP.** Do not run B or C under any circumstances.
- Do not proceed even on "tailor anyway", "just do it", "I know the risk", or any other override. There is no
  popup and no marker file for this.
- Say: "This role has a hard disqualifier for F-1 OPT holders — [reason]. Tailoring is disabled for this job."
- The only allowed actions are logging and suggesting similar roles.

---

## Sub-workflow A — Job Fit Analysis

Inputs: job URL or pasted JD text · `references/candidate_context.md` · `references/keywords_only.json` ·
`references/skills_db.json` (canonical skills + aliases + depth; built by `build_skills_db.py` from
`master_profile.json` + the curated `references/skill_aliases.json`).

**A0 – A2.5 — setup, JD text, hard-blocker pre-screen.** Commands in
**[fit_payload.md](references/fit_payload.md)**: `build_keywords.py`, `build_skills_db.py`, `$JOB_CWD`/`$JOB_DIR`,
`keywords_only.json`, `skills_db.json`, `scrape_jd.py`, `prescreen_jd.py`.

**Skill vocabulary is centralised.** `scripts/skill_match.py` is the ONE place that answers "does Justin
have this JD skill?" — `score_fit.py` (req_cov), `select_content.py` (B1 ranking) and `verify_coverage.py`
all call it. It resolves JD prose ("microcontrollers", "version control (Git)") to canonical skills and
weights by defensible depth: strong 1.0 · working 0.75 · exposure 0.4 · **unbacked 0.0**. A canonical with
no evidence in `master_profile.json` earns nothing — that is the anti-inflation guard. Edit vocabulary in
`references/skill_aliases.json` (curated, survives rebuilds), never in the generated `skills_db.json`.

**Two scores, never conflated.** `fit.json/match_pct` is computed from `master_profile.json` vs the JD and
NEVER reads the tailored resume — it is the number Justin makes decisions on, so keyword-filling must not
be able to inflate it. `verify_coverage.py` measures the tailored resume against the JD's keywords and is
the number to maximise.

Two rules that must not be lost with the mechanics: career sites are JS-rendered, so **do not spend turns on
static scrapes** — use browser page-text extraction, and ask for a paste if it returns only boilerplate. If
`prescreen_jd.py` exits 1, print the ⛔ HARD BLOCK banner with the matched phrase and **STOP — no A3–A9, no B,
no C, and no override.**

**Batch variant — many roles at one company.** `resolve_ats_roles.py` (bulk scrape via a known ATS's JSON API
— Greenhouse/Lever/Ashby/SmartRecruiters/Recruitee/Workable) or `paginate_scrape.py` (Playwright fallback for
a custom career page) replace a one-off `scrape_jd.py` call when the task is "every open role at X," and
`keyword_prefilter.py` (calls `prescreen_jd.py` directly rather than a separate hard-blocker copy — don't
reintroduce that duplication) does the zero-token eligibility gate before any model sees a posting. Delegate
the per-role A3–A5 classification through `batch-delegate` rather than running this sub-workflow once per
role in the current session — see that skill's `SKILL.md` for the mechanics; this file owns the rubric, that
one owns the parallel execution.

**A3 — Parse the JD into structured fields** (model-side; no script). Produce the `jd` object — schema in
[fit_payload.md](references/fit_payload.md). Classify only what the JD actually asks for: `ats_keywords` are
what a screener searches on, `required_skills` are the hard asks; both drive the A4 denominator, so padding
them with boilerplate deflates the score.

**A4 — Classify each skill** (the judgment call; the arithmetic is A6's script). Compare
`profile.all_keywords` against `required_skills ∪ preferred_skills ∪ ats_keywords`, putting every term in
exactly one bucket:
- ✅ **HAVE** — exact or near-exact match
- ⚠️ **ADJACENT** — related skill present (JD wants JAX, profile has PyTorch)
- ❌ **MISSING** — no related skill found

That classified set is the scoring denominator. Do not pad it with boilerplate ("communication skills",
"fast-paced environment") and do not drop a demanded skill to shrink it. **You do not compute `match_pct`
yourself** — `score_fit.py` does, adjacency at half credit plus two guard rails (zero-HAVE floor 50,
required-coverage cap 60): [scoring_rationale.md §1](references/scoring_rationale.md).

**A5 — Constraint flags** (read `references/candidate_context.md`).

**Read the JD again yourself for blockers — a deliberate second pass, not duplication.** A2.5's regexes catch
known wordings; you catch the ones nobody has written a pattern for yet. **Judge meaning, not string match.**
Employers phrase these four endlessly differently, but one is almost always present somewhere: **no
sponsorship** (ever, incl. CPT/OPT/STEM-OPT) · **ITAR / export control** (US Person, EAR, deemed export) ·
**citizenship or PR required** · **security clearance** (any, active or obtainable — Secret/TS/SCI/DoD/public
trust). If you catch one A2.5 missed, set `hard_blocker.triggered = true`, `reason = exact sentence +
category`, **and** append the wording to the matching list in `candidate_context.md` so the regex layer learns
it.
- `defense_category_keywords` — 2+ matches AND sponsorship unknown → flag `⚠️ DEFENSE CATEGORY — verify
  citizenship requirement before applying`.

Soft flags (warn, overridable):

| Check | Logic |
|---|---|
| Sponsorship | **Explicit refusal** (`no_sponsorship_phrases`, "sponsorship is not available", etc.) is NOT a soft flag — it is a **hard blocker**: set `hard_blocker.triggered = true`, same as A2.5. Soft-flag only the unclear cases: nothing stated, conditional wording ("for the right candidate"), or company not in `known_sponsors` |
| Experience | see below |
| Location | `jd.remote_ok` vs `willing_to_relocate` |

**The experience check — one check, two outputs**, both derived by `score_fit.py` from
`jd.required_experience_years`, `jd.experience_level_stated` and the title: `seniority_fit` is the displayed
signal (`Aligned` entry/new-grad/0–1 yrs · `Stretch` 2–3 yrs or "mid" · `Mismatch` over
`experience_threshold_years`, or senior/staff/principal/lead/architect in the title or level), and
`experience_mismatch` is the boolean the verdict consumes — exactly `seniority_fit == "Mismatch"`.

A Mismatch downgrades **Yes → Can Try** and does nothing else. **It is a signal, not a veto — it can never by
itself force APPLY = No.** Standalone veto power is what broke the verdict before ([scoring_rationale.md
§2](references/scoring_rationale.md)).

Set `production_scope_required = true` when the JD centres on owning a production system at org scale — the
profile is capstone/research/internship scope, so that is a real gap even when keywords match. Reported, never
scored.


**A6 — Score + verdict + write fit.json (one script call).** A4's math, the verdict thresholds and the
fit.json write are **one deterministic script**. They were once pseudocode the model re-executed by hand,
which is how a role got recorded as `seniority_fit: "Mismatch"` *and* `apply: "Can Try"`. **Do not reimplement
any of it inline.** Build the payload from A3–A5 (shape in [fit_payload.md](references/fit_payload.md)) and
run:
```bash
python3 ~/.claude/skills/job-automator/scripts/score_fit.py /tmp/fit_payload.json --job-dir "$JOB_DIR" --report --log
```
It computes `match_pct`, `seniority_fit`, `experience_mismatch` and both verdicts, and writes
`$JOB_DIR/logs/fit.json` atomically. Verdict logic, first match wins:
```
hard_blocker (incl. explicit no-sponsorship) → MATCHES No,   APPLY HARD BLOCK
match_pct ≥ min_match_for_apply   + no exp mismatch → Yes,   APPLY Yes
match_pct ≥ min_match_for_apply   + exp mismatch    → Yes,   APPLY Can Try
match_pct ≥ min_match_for_can_try         → MATCHES Partial, APPLY Can Try
below min_match_for_can_try               → MATCHES No,      APPLY No
```
Thresholds come from `references/candidate_context.md`.

**`--report --log` (single role) fold A7 and A9 into this same call, but only once fit.json is final.** The
script prints render_report.py's exact output between the `=== A7 REPORT` marker lines and writes the
log_fit.py row. While `SEMANTIC    : REQUIRED` it does neither and says so; they run on the A6.5 merge
instead. For a batch, leave both flags off and run A7 and A9 once each over every role's fit.json.

**There is no semantic branch here, by construction** — `score_fit.py` has no code path from `llm_analysis` to
`verdicts.apply`. The semantic read is merged into the existing fit.json (A6.5) — it never triggers a second
scoring run. Never hand-edit fit.json.

**A6.5 — Semantic deep-dive (conditional, INFORMATIONAL ONLY, ONE PASS).**

> **THE MODEL MUST STRICTLY FOLLOW THIS — no exceptions, no shortcuts, no judgment calls.**
> 1. Run `score_fit.py` on the payload **exactly once**. That is the only scoring run for this job.
> 2. The trigger is a **fixed threshold of 60** — `min_match_for_apply`, read from `candidate_context.md`, never
>    hardcoded and never changed. The script decides, not you: it prints `SEMANTIC    : REQUIRED` (fit.json
>    `semantic_pending: true`) **if and only if** `match_pct >= 60` and no hard blocker fired.
> 3. **REQUIRED printed → the semantic read MUST be run.** Never skip it, never defer it, never replace it with
>    a prose opinion. Pasted JD text and URLs alike.
> 4. **REQUIRED not printed (match < 60, or hard blocker) → the semantic read MUST NOT be run.** Never run it
>    "to be thorough".
> 5. Save the read as JSON and merge it — **never re-run scoring** and never rebuild the payload. Both in ONE
>    Bash call: `cat > "$JOB_DIR/logs/semantic.json" <<'JSON'` … the read … `JSON`, then on the next line
>    `python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic "$JOB_DIR/logs/semantic.json" --job-dir "$JOB_DIR" --report --log`
> 6. Render A7 **only after** that merge (or immediately, if the read was not required). Never render A7 while
>    `semantic_pending` is true.

Procedure, anchors and output shape: **[semantic_read.md](references/semantic_read.md)**, read before
writing the read. Two constraints
stay here because they are what went wrong before: **do not deflate `llm_match_pct` for seniority or years**
(that is the A5 check's job), and **it does NOT override `matches` / `apply`** — it informs Justin and drives
the B-GATE conversation, never the number.

**A7 — Display report** — **runs AFTER A6 has written fit.json.**

Single role: the `--report` flag on A6 or on the A6.5 merge has already run this renderer. Its stdout is the
block between the `=== A7 REPORT` marker lines; that block is what you paste. Do not run render_report.py again
for the same fit.json. Run the command below for a batch, or to re-render on request.

> **HARD RULE — the report is script-rendered, then COPIED INTO YOUR REPLY.**
> ```bash
> python3 ~/.claude/skills/job-automator/scripts/render_report.py $JOB_DIR/logs/fit.json
> ```
> Two obligations; skipping the second means Justin sees nothing:
>
> 1. **Render it with the script** — never hand-write the report, and no reformatting, reordering, added
>    prose, or substituted layout. For a batch, pass every `fit.json` path in one call to get Format 2.
> 2. **Reproduce that stdout in your own message**, in a fenced code block, character for character. Paste it;
>    do not point at it.
>
> ❌ Never write "Above is the A7 report", "see the output above", or any other reference to the tool result —
> there is nothing above from his side. ❌ Never swap the report for a prose summary of the verdict. If your
> reply does not literally contain the box-drawn block, the step is incomplete.

**Two distinct blocks, never merged.** The script prints:

- **Block 1 — KEYWORD READ**, labelled *verdict of record*: the tag, `match_pct`, MATCHES, APPLY,
  `seniority_fit`, the full Have/Adjacent/Missing breakdown with counts, top keyword gaps, any constraint flag
  that fired, and `Tailoring:` — derived from the authoritative APPLY verdict, so it can never disagree with
  B-GATE.
- **Block 2 — SEMANTIC READ**, only when it ran, labelled *informational only · does not change the verdict
  above*: `llm_verdict`, `llm_match_pct`, `calibration_delta`, the three `screening_gaps`, strengths,
  reasoning, and a caveat when `recommend_apply == false`.

**Never collapse these into one verdict line** — the merged format is what let a Mismatch header sit above a
"recommended" footer. **Always print the skill breakdown**; a verdict with no skill data is an opinion.
`overstated_by_keywords`, `understated_by_keywords`, `req_cov` and cap notices stay in fit.json, printed only
on request. A hard blocker replaces the report entirely, single or batch.

**A9 — Log the global row** (never hand-write it)
```bash
python3 ~/.claude/skills/job-automator/scripts/log_fit.py $JOB_DIR/logs/fit.json
```
**In BATCH mode pass every role's fit.json in one call** — each gets its own row. Idempotent per `job_dir` (a
re-run updates, never duplicates) and atomic. Writes `~/job_search/fit_analysis_log.json`; F2's funnel reads
it, so a skipped row is lost funnel data ([scoring_rationale.md §4](references/scoring_rationale.md)).

Single role: the `--log` flag on A6 or on the A6.5 merge has already written this row (its `LOGGED` /
`UPDATED` line). Run log_fit.py yourself only in batch mode, or when the flag was not used.

Stop here unless this is part of a larger requested flow.

---

## Sub-workflow B — Resume Tailoring

Inputs: `$JOB_DIR/logs/fit.json` · `references/master_profile.json`.

**B-GATE — check before anything else in B**

Read `verdicts.apply` from `$JOB_DIR/logs/fit.json` — the gate triggers on the **authoritative keyword
verdict**, not the semantic read.

- `apply == "No"` → **STOP. Do not tailor yet.** Print the verdict, the `match_pct`, and (if the semantic read
  ran) its three `screening_gaps`. Then present the override through the **AskUserQuestion tool** — the native
  choice popup. Do **not** make Justin type a magic word like "override". One question, header `"Weak fit"`,
  two options:
  - `"Skip this role"` (Recommended) — "Don't spend a compile cycle or an application slot on this one."
  - `"Tailor anyway"` — "Proceed to B0 and tailor despite the verdict."

  Continue to B0 **only** on "Tailor anyway" (or an explicit typed go-ahead), and first write the override
  marker so the enforcement hook lets the build through:
  ```bash
  touch "$JOB_DIR/logs/.tailor_override"
  ```
  Any skip or decline → stop, tailor nothing.
- `apply == "HARD BLOCK"` → not a gate, a wall (see HARD BLOCKER RULE). No popup, no marker, no override.
- Semantic read says `Weak Fit` / `recommend_apply == false` but `apply != "No"` → **do not block.** Surface
  the caveat and the `screening_gaps`, then continue. It informs; it does not gate.
- No `llm_analysis` though `match_pct` cleared the trigger → the semantic read should have run; offer it
  first.

`hooks/gate_resume_build.py` enforces this at the Bash layer too, so a forgotten check is denied rather than
silently tailoring a rejected role.

**B0 – B4 — cache check, tailor, generate.** Mechanics in
**[workflow_b_tailoring.md](references/workflow_b_tailoring.md)**: the `resume_cache.py check` reuse offer
(its key is salted with a hash of `master_profile.json`, so a profile edit invalidates every cached resume),
the B1 pre-filter, B2 summary pick, the B3 prompt (in `tailoring_prompt.md`), and the `generate_pdf.py` call
with its exit codes. **Exit 1 means the compile FAILED and no PDF was written — show the pdflatex log tail,
say the resume did not build, and stop. Never hand Justin a lone `.tex` as if it were the deliverable.**

**Portfolio link — every resume.** The header is `phone | email | portfolio | location`; LinkedIn is
deliberately left off. `generate_pdf.py` picks the URL from `role_category`, printing `PORTFOLIO=<url>`:
embedded/firmware/hardware roles get `justinmascarenhas.com/embedded`, every other role gets
`justinmascarenhas.com/edge-ai`. Name the URL used when reporting the PDF in B5. Details and the one-job
override: [resume_format.md § Header](references/resume_format.md).

⚠️ **Never edit `master_profile.json` without Justin's explicit in-the-moment permission** — it is the source
of truth for every tailored resume, so a silent edit propagates into live applications. Propose, state the
reasoning, wait.

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

**On overflow (exit 2)** — read `OVERFLOW_LINES=N` and shorten the tailored JSON with the redraft prompt in
[tailoring_prompt.md](references/tailoring_prompt.md): longest bullets first, then the weakest bullet of the
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

**B5 — Index + report.** Index for reuse (`resume_cache.py index`), then report the PDF and TEX paths, logs
dir, reuse hash, top 5 ATS keywords injected, and `Pages: 1`. Command in
[workflow_b_tailoring.md](references/workflow_b_tailoring.md).

## Sub-workflows C, D, F, G · hooks · errors

Each is one self-contained step. **Read its file (named in the routing table) in full before acting.** Rules
outranking those files: **never auto-send** outreach (email → Gmail draft, DM → pasted inline); a follow-up
reminder only after Justin confirms it went out; **always** run `mark_submitted.py`, never hand-append a CSV
row; **never infer an outcome**.

**Portfolio link — every outreach message too.** Email and DM both close with the fixed sign-off `Best, /
Justin Mascarenhas / justinmascarenhas.com`, which **replaces** the old LinkedIn URL. Root domain only in
outreach: the `/embedded` and `/edge-ai` track pages belong to the resume and their hyphen breaks the no-dash
body rule. Full rule: [outreach_rules.md § Substance](references/outreach_rules.md).

**After D4 confirms a submission, offer Sub-workflow G — once, then stop.** Match ≥ 80 → 10 recruiter
emails, 60–79 → 5, < 60 → do not offer. Ask *"Draft outreach for {company}? Match is {n}%, so that's {n}
emails. Yes / No / a number."* — a number in the answer ("yes but 20") wins. Only on a yes does
`hunt_contacts.py` run, and it refuses outright unless the role is already in the submitted log. Recruiters
only, never a referral ask, drafts shown in the reply and **never sent**:
[workflow_g_recruiter_outreach.md](references/workflow_g_recruiter_outreach.md).

`protect_resumes.py`, `lint_skill_on_edit.py` and `gate_resume_build.py` (which makes B-GATE structural) are
all wired in `~/.claude/hooks/`. Details, error table, output-file map and the `validate_skill.py` check:
[hooks_and_errors.md](references/hooks_and_errors.md).
