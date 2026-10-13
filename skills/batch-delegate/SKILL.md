---
name: batch-delegate
description: >
  Generic batch-processing delegation layer. Use whenever a task involves running
  the SAME kind of analysis or classification across MANY independent items —
  many URLs, many rows of data, many documents, many job postings at a company
  — not a single one-off item. Triggers on: "go through this website", "fetch
  these many things", "batch process", "batch analyze", "process all the X",
  "run this across all of them". Delegates the per-item work, run in parallel
  through a bounded worker pool, to claude-f (OpenRouter-backed headless Claude
  Code, defined in ~/.bashrc) so the current session's Anthropic-model tokens
  (Sonnet/Haiku/Opus/Fable) are never spent on repetitive per-item work. A
  single item ("analyze this one thing") is NOT batch — handle it directly in
  the current session, no delegation.
---

# Batch Delegate

Generic delegation layer for "do this same thing N times" tasks. The current
session's model (whatever is active — Sonnet, Haiku, Opus, Fable) is the
**orchestrator only**. It never performs the repeated per-item work itself.
All per-item work is delegated to independent `claude-f` processes, run
concurrently through a bounded thread pool (`scripts/delegate.py --workers N`,
default 8) — not one at a time.

This skill owns exactly one script — `scripts/delegate.py`, the parallel
delegation engine — and nothing domain-specific. It does not know what a job
posting, a support ticket, or a PDF is. Fetching the batch, prefiltering it,
and scoring the results are the orchestrator's job every time, using whatever
tools fit the domain (see Step 1/2/5 below — job-fit analysis is one example
among many, not the default).

## Mechanism note — why this is subprocess calls, not peer sessions

It is tempting to reach for real Agent-tool subagents, or for a `claude-f`
session left running so it can be `SendMessage`d and chatted with mid-batch —
both would give better visibility than a subprocess call. **Both were tried
and rejected; do not re-attempt either without re-verifying first:**

- **Agent-tool subagents** run on an Anthropic-backed model (Sonnet by
  default) — there is no way to point the Agent tool at OpenRouter. Using it
  for batch work reintroduces the exact per-item token cost this skill exists
  to avoid.
- **A `claude-f`-launched interactive session** genuinely *does* register in
  the session-discovery mechanism (`~/.claude/sessions/<pid>.json` + a Unix
  socket) and shows up in `ListAgents`, addressable via `SendMessage` — this
  part works, confirmed by direct test. **But** when it actually processes a
  cross-session message, it silently replies using the real Anthropic session
  (Sonnet), not the OpenRouter model — confirmed by asking a probe session
  which model it was running on and getting `claude-sonnet-5` back, despite
  `claude-f`'s `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` override. The
  override only reliably holds for one-shot `claude -p` calls. A batch built
  on peer sessions would quietly spend real Sonnet tokens per item — worse
  than no visibility, because it fails silently.

The resolution: `scripts/delegate.py` gets real observability *without* a live
chat — every item's full prompt and raw response are saved to their own file
under `--out-dir`, live progress prints one line per completion, so you (or the
user) can inspect any item's exact reasoning at any point during or after the
run. You cannot send it a follow-up question, but you can watch it work and
read exactly what it said. If a genuinely free, chat-addressable backend ever
becomes available, revisit this — but re-verify the model-routing claim with a
fresh probe before trusting it, the way this note was produced.

## Hard rules

1. **Never use an Anthropic-backed model for the per-item work.** Not via the
   Agent tool, not via a peer `claude-f` session (see Mechanism note above),
   not via a fresh session, not as a "just this once" fallback. The
   orchestrator's job is: gather the batch, build prompts, delegate, parse,
   aggregate, report. Nothing else.
2. **Once any item fails twice, stop scheduling new items — but let items
   already in flight finish.** A failure is: non-zero exit, timeout, or output
   with no parseable JSON object. `scripts/delegate.py` gives a failed item
   exactly one retry (a fresh, independent `claude-f` call — covers cosmetic
   slips like a stray escaped quote breaking strict JSON) before counting it
   as failed. With a worker pool, "abort immediately" can't mean "stop
   everything mid-air" the way it could sequentially — killing an in-flight
   call wastes the work and helps no one. It means: no new item is submitted
   to the pool once a double-failure is seen. The final report has three
   buckets — `completed`, `failed`, `never_attempted` — and `never_attempted`
   is only the items that genuinely never started. Do not retry the whole
   batch, do not silently continue past a failure via a different mechanism,
   and above all do not fall back to Sonnet/Haiku/Opus/Fable to "finish the
   job." Report exactly what completed, what failed, and why.
3. **Fetching the batch itself is not delegated, and is a domain-specific
   problem you solve in the current session — this skill has no opinion on
   how.** Getting the list of items to process runs directly in the current
   session, at near-zero token cost: a known API if one exists, a scrape if
   not, or data the user already handed you. Whatever the source, this cost
   is paid once per batch, never per item, and never handed to a delegate —
   free/non-Anthropic models are not reliable at tool-driven fetching (no
   computer-use fine-tuning), so delegates only ever do plain text-in/
   text-out reasoning, never browsing or API calls.

   If the batch happens to be job postings, don't rebuild this: job-automator
   owns, in its own scripts directory, `resolve_ats_roles.py` (bulk company
   scrape via known ATS JSON APIs — Greenhouse, Lever, Ashby, SmartRecruiters,
   Recruitee, Workable) and `paginate_scrape.py` (Playwright fallback for a
   custom career page). These used to live in this skill; they moved to
   job-automator because their logic — and their bundled hard-blocker/
   candidate-matching checks — is genuinely job-domain-specific, not generic
   batch mechanics. **A JD-text scrape that only captures a plain-text
   summary and misses the structured requirements list will silently inflate
   every downstream match score** — this happened in production (a
   90.9%/79.4%/70.6% batch of "APPLY" verdicts turned out to be
   43.8%/40.0%/35.7% once the real requirement bullets were pulled in) —
   `resolve_ats_roles.py` already pulls Lever's full `lists` field for
   exactly this reason; don't re-derive a weaker version by hand.
4. **Delegates cannot reliably call tools or skills themselves.** Never write a
   delegate prompt that says "use skill X" or "use tool Y" — a free/weak model
   is not reliably going to emit a correct tool_use block, which is exactly the
   failure mode this whole design exists to avoid. Instead, the orchestrator
   reads whatever rubric or reference material the task needs *before*
   building prompts, and bakes the specific logic into each delegate's prompt
   as complete, self-contained plain text. Delegates receive full
   instructions, never a pointer to go find them.
5. **A single item is not a batch.** "Analyze this one thing" / "score this
   one document" → handle it directly in the current session, no delegation
   at all. Delegation only activates once there are multiple independent
   items to process the same way.
6. **Every classification claim a delegate makes must cite the specific
   evidence backing it — never a bare label.** A free-tier model asked to
   classify items into buckets (have/adjacent/missing, relevant/irrelevant,
   whatever the task's categories are) will sometimes invent plausible-
   sounding support that isn't actually in the source material (observed in a
   job-fit batch: several delegates credited "personal Docker/k3s/CI-CD
   exposure" that does not appear anywhere in the candidate's actual profile).
   The delegate prompt must require each classification to name the specific
   line, section, or fact it's grounded in, not just assert the label. This
   doesn't eliminate hallucination but makes it checkable — an ungrounded
   claim is a visible red flag in the output instead of an invisible one.
7. **A hard constraint and a soft/quality signal are different fields — never
   let a delegate conflate them.** If the task has any absolute-exclusion
   category (a hard constraint that must categorically drop an item — legal
   ineligibility, an out-of-scope category, a policy violation) alongside a
   softer quality/fit signal (a score, a confidence level, a seniority/tier
   mismatch), keep them as separate fields with separate semantics, and say
   so explicitly in the delegate prompt with a negative example. Observed
   failure in a job-fit batch: 22 of 53 delegate outputs set
   `hard_blocker.triggered = true` with a reason that was actually just
   "title says Senior, candidate is new-grad" — a soft seniority mismatch,
   not a real hard blocker (visa/citizenship/clearance). A model left to
   infer the boundary between "must exclude" and "worth flagging" will
   sometimes collapse the two categories on its own; state the negative
   example (a plausible-looking wrong classification, called out as wrong)
   rather than just listing the categories and trusting it to stay disjoint.
   When in doubt, spot-check a sample of hard-constraint-triggered outputs
   against the actual category list before trusting the batch — that's
   exactly how the 22/53 error above was caught.
8. **Push to the live dashboard by default, per item, as each one completes
   — not just at the end.** Unconditional, not gated on batch size, never a
   permission question. Publish/reuse in 4a (verify a remembered URL first),
   push each item live in 4b as it finishes (mandatory now, not a bonus —
   the point is a reviewable live feed the user can redirect mid-batch),
   then 5a/5b do a final sweep + verification. Took six rounds to get right,
   including a client-side rendering bug hiding correct data; full history
   in [references/dashboard.md](references/dashboard.md) — read before
   changing dashboard behavior. Skip only if the user says not to, or the
   Artifact tool is unavailable.

## Mechanics

### Step 1 — Resolve the batch (current session, zero or near-zero tokens)
Produce a list of items to process — however that's done for this task
(an API call, a scrape, data the user provided). Save it to a scratch JSON
file. See Hard Rule 3 for the job-postings case specifically.

### Step 2 — Deterministic pre-filter (script, zero tokens, optional)
Before spending any model call — even a free one — cut obviously irrelevant
items with a cheap deterministic check, if the domain has one. This is what
keeps the delegated batch small and relevant instead of running analysis on
hundreds of items that were never going to match. Skip this step entirely if
there's no cheap eligibility signal for the task — not every batch has one.

For job-fit batches: job-automator's `keyword_prefilter.py` scores postings
against the candidate's curated skills list and drops anything
`prescreen_jd.py` (job-automator, the canonical hard-blocker check —
`keyword_prefilter.py` calls it directly rather than maintaining a separate
copy, after exactly that duplication caused drift once) flags as a hard
blocker.

### Step 3 — Build one self-contained prompt per surviving item
For each item, write a prompt that:
- States the exact task and the exact JSON output shape required — the shape
  is entirely task-dependent (a fit-score payload, a classification label, an
  extracted-fields object, whatever the batch needs).
- Includes whatever reference material and the item's full content the task
  needs (full context is fine here, it's free).
- Applies Hard Rule 6 (grounding) and Hard Rule 7 (hard-constraint vs. soft
  signal, if the task has both) explicitly, inline, with a negative example
  included verbatim — don't just link to it.
- Ends with: "Output ONLY the JSON object. No markdown fences, no other text."
- Does NOT tell the model to use any tool or skill — the instructions above
  already are the task's logic, inlined.

Write all `{id, prompt}` pairs to a JSON file for `delegate.py`.

**Job-fit example:** mirror job-automator's A3+A4+A5 payload shape (see its
own `fit_payload.md` reference doc) so `score_fit.py` can consume it
directly — `jd`, `have`, `adjacent`, `missing`, `hard_blocker`, `flags`,
`production_scope_required`. Don't ask the delegate to compute a verdict or
a percentage itself; `score_fit.py` is the sole source of the authoritative
score (per the standing preference in memory
`feedback_match_scoring_approach.md`) — the delegate's job is classification
input, not arithmetic.

### Step 4 — Publish the dashboard, then delegate (parallel)

**4a — Dashboard, first, unconditionally (Hard Rule 8).** Before launching
`delegate.py`:
1. Check memory for a known dashboard URL (`reference_batch_delegate_dashboard.md`
   or similar — it may not exist, or may belong to a different project's
   memory scope than this session's `cwd`; don't block on not finding one).
2. **If a URL was found, verify it before trusting it** —
   `action: "read"` on it first. A remembered URL can go dead (an artifact
   can be deleted independently of this skill — confirmed happening in
   practice, and it silently broke a run that assumed the saved URL still
   resolved). If it reads back fine, reuse it:
   `Artifact.publish(file_path="~/.claude/skills/batch-delegate/references/dashboard.html", url="<the saved URL>")`.
   If it's missing, or no URL was found in memory at all, publish fresh:
   same call without `url`, plus `capabilities={"db": {}}`, a `favicon`, and
   `icon="console"` — this makes a *new* URL. Either way a fresh URL was
   just created, **immediately update memory with it** (overwrite the old
   record, don't append) so the next session doesn't inherit a dead pointer
   again.
3. Write the run doc (`write_db` / `set`, collection `"runs"`, a fresh
   `doc_id`) so the page has something to show immediately.
4. Tell the user the URL in one line — "pushing this batch live to
   <url>" — as an FYI, not a question to wait on.

Full schema and push mechanics: **[references/dashboard.md](references/dashboard.md)**.

**4b — Run the pool, pushing each item live as it completes:**
```bash
python3 ~/.claude/skills/batch-delegate/scripts/delegate.py <items.json> \
  --timeout 120 --workers 8 --out-dir <scratch-dir>/delegate_run
```
Prints `OUT_DIR <path>` immediately, then one `PROGRESS i/N OK|FAIL id=...`
line per item as it completes (in whatever order the pool finishes them, not
input order). Pipe this through `Monitor` filtering on
`PROGRESS|OUT_DIR|aborted|Error`. **On every `PROGRESS` notification, before
waiting again: read the newly-appended line(s) in `<out-dir>/results.jsonl`
and push that item now** — `write_db` `set` on
`runs/<run_id>/items/<id>` with whatever's known yet (id/status/prompt/
raw_response/stats; outcome/title/score get filled in at Step 5a once
available). This is what makes the dashboard usable *during* the run — a
live transcript feed to review and redirect from — not just a summary after
everything's done. It is no longer optional/best-effort; skipping it just
defers all visibility to the end, defeating the point. Item schema and a
per-item push example: [references/dashboard.md](references/dashboard.md).
Every item's full prompt + raw response is also saved directly at
`<out-dir>/<id>.attempt1.txt` (and `.attempt2.txt` on retry).

At the end it prints one final JSON object:
```json
{"aborted": bool, "completed": [...], "failed": [...], "never_attempted": [...], "out_dir": "..."}
```
`aborted: false` → every item completed, proceed to Step 5.
`aborted: true` → report to the user:
- How many completed (`completed`), with their ids
- Which item(s) failed and why (`failed`, each with its `error`)
- Which were never attempted (`never_attempted`) — genuinely not started, not
  in-flight-and-discarded
Point at the failed items' transcript files in `out_dir` so the user (or you)
can see exactly what went wrong. Do not attempt the remaining items with any
other model. Ask the user how they want to proceed (retry later, skip and
continue manually, investigate the error) — do not decide for them.

### Step 5 — Aggregate, push to the dashboard, and report
Merge delegate results with whatever deterministic data you already have
into one table, in whatever shape the task calls for.

For job-fit batches: run each result through job-automator's `score_fit.py`
to get the authoritative `match_pct`/verdict (never compute it by hand — see
Step 3), write each as a `fit.json` under its own job dir, append to
`~/job_search/fit_analysis_log.json` via `log_fit.py`, and render the batch
table via `render_report.py` — reproduce its stdout verbatim, per
job-automator's own A7 hard rule.

**5a — Push to the dashboard:**
```bash
python3 ~/.claude/skills/batch-delegate/scripts/prepare_dashboard_push.py \
  <out-dir>/results.jsonl --run-id <the run_id from Step 4a>
```
Optional `--extra <extra.json>` for display data the script can't derive
(title/outcome/score per item — see `references/dashboard.md`); omit it and
items still push, just without a nice label. Run the `write_db` calls the
script prints (run doc, then each chunk file as `writes` with
`db_op: "batch"`) even if Step 4b's per-tick pushes already ran (`set` is
idempotent).

**5b — Verify it landed; this is the actual guarantee, not 5a.** "Do X" was
tried five ways in this skill's history and X kept silently not happening —
full account in `references/dashboard.md`. `read_db` the run doc and item
count, compare against what `delegate.py` actually completed. Mismatch
(including zero, including the run doc missing) → re-run 5a, re-check.
**Do not report the batch complete without this check passing** — pushing
is a claim about intent, this confirms the data is actually there.

## Example: batch job-fit analysis for a company

This is one worked example, not the skill's default mode — see Steps 1, 2, 5
above for where each piece is job-automator-specific vs. generic.

1. `resolve_ats_roles.py <slug>` (job-automator) → full postings with real JD
   text (Step 1).
2. `keyword_prefilter.py` (job-automator) against the curated skills list,
   hard-blocked roles dropped via `prescreen_jd.py` → shortlist (Step 2).
3. For each shortlisted role, build a prompt inlining job-automator's A3–A5
   rubric (skill classification + constraint flags, grounded, hard-blocker
   vs. seniority separated) + the role's real JD text + the candidate's full
   profile (Step 3).
4. Publish/reuse the dashboard, write the run doc (Step 4a) — then
   `delegate.py --workers 8` runs the pool, live progress, per-item
   transcripts (Step 4b).
5. `score_fit.py` per role for the authoritative verdict, `log_fit.py` to the
   funnel, `render_report.py` for the batch table — reproduce it verbatim —
   then `prepare_dashboard_push.py` (with an `--extra` built from each
   role's title + verdict/match_pct) and the `write_db` calls it prints
   (Step 5a), then `read_db` to confirm the item count landed before
   calling the batch done (Step 5b — this is the part that's non-negotiable).
6. Present the table. Tailoring/outreach for any role the user picks proceeds
   through job-automator's normal Sub-workflow B/C in the current session —
   those stay on Sonnet, by design, since by then the volume is small.
