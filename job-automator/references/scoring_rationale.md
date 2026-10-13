# Scoring rationale & audit history

Background for the scoring, verdict, and logging rules in SKILL.md. Read this only when changing a formula, a
threshold, or the verdict authority — not on a routine analysis. SKILL.md states the rules; this file defends
them.

---

## 1. Why the A4 denominator is the whole classified set

Scoring only against a 2–4 item `required_skills` list produced **60 roles at exactly 100%** that were each
still missing ~4.6 skills — including roles with **zero** HAVE matches. A tiny denominator makes any coverage
look total.

Backtested against the roles carrying a semantic ground-truth read:

| Formula | Mean abs error | Bias |
|---|---|---|
| Old (`/ required` only, adjacency at full credit) | 26.7 | **+26.7** (over-scores) |
| `/ max(ats_list, classified)` | 22.6 | −20.0 |
| **Current (`/ classified set`, adjacency at 0.5)** | **14.5** | −11.9 |

⚠️ **That backtest is n=5** — the only roles carrying both `have_skills` and a semantic read. It is enough to
reject the old formula (its +26.7 bias is the documented failure) but **not** enough to fine-tune weights.

The 0.5 adjacency weight is the principled "half credit" default, not a fitted value. The residual ≈ −12 bias
suggests adjacency may be worth slightly more. **Do not hand-tune it** — let `calibration_delta` accumulate
and revisit once n ≥ 30.

### The two guard rails

1. **Zero-direct-match floor** (`raw_pct = min(raw_pct, 50)` when `|HAVE| == 0`) — adjacency alone is never a
   strong fit. A profile that merely resembles every ask, matching none of them, is not a 70% candidate.
2. **Required-skill gate** (`raw_pct = min(raw_pct, 60)` when `req_cov < 0.5`) — broad coverage of
   nice-to-haves cannot compensate for missing half the hard asks.

### Denominator hygiene

Do not pad `jd_ask` with boilerplate ("communication skills", "fast-paced environment") — the denominator must
be *skills*, or the score deflates. Equally, do not silently drop a demanded skill to shrink the denominator
and inflate the score. Both are ways of lying to the scorer.

---

## 2. Why the keyword verdict is authoritative (and the semantic read is not)

### The standing preference

Memory `feedback_match_scoring_approach.md`: *"Keyword-based scoring is default; only use LLM analysis if
explicitly requested."* Python matching is fast, deterministic, and good enough for day-to-day screening.

### What the semantic read is genuinely good for

The audit that motivated widening its trigger is real and still stands. Across 87 semantically-read roles:

- 64 had a Weak/Partial semantic read while the keyword verdict said Yes/Can Try.
- 11 of 13 explicit "Weak Fit" roles were still recommended.
- Keyword score ran a mean **+30 points** above the semantic read.

That is a real calibration gap, and it is why the semantic read still runs on every role at or above the apply
threshold, and why `calibration_delta` is recorded on every one.

### Why it was nevertheless demoted back to informational

The previous design made the semantic read *authoritative* — "gates the verdict", with downgrade/upgrade
branches in A6. That override logic was **prose the model executed freehand on every analysis**, and it failed
in production:

`~/Desktop/jobs/zoox_ds_pv/logs/fit.json` — `seniority_fit: "Mismatch"` with `verdicts.apply: "Can Try"`.
Under the rules as written, a Mismatch forced APPLY = No. The model skipped the step, wrote a
self-contradictory record, and the report then rendered `Tailoring: recommended` on top of it. A corpus scan
of 510 saved fit.json files found this contradiction in exactly 1 — which is the point: a rule that holds 509
times and silently fails once is a rule with no enforcement, not a rule with good odds.

Two independent problems were tangled together:

1. **Mechanism** — a verdict computed in prose can be skipped. Fixed by `scripts/score_fit.py`: the arithmetic
   and the verdict are now code.
2. **Authority** — a second, softer, model-generated signal with veto power over a deterministic one makes the
   whole verdict non-reproducible. Two different sessions reading the same JD could reach different verdicts,
   and neither could be audited. Fixed by removing the override branch entirely.

The semantic read keeps everything that was actually useful — the wider trigger, `screening_gaps`, the
anchor-scale scoring, `calibration_delta` — and loses only its power to change the number. It surfaces as its
own labelled block, and it drives the B-GATE *conversation*, not the verdict.

### Why `seniority_fit` has no veto

The prior rule was `seniority_fit == "Mismatch"` → APPLY = No, on the reasoning that a 4+ year / senior-titled
role is unwinnable at 0 full-time years. The reasoning is sound as a *signal* and wrong as a *veto*:

- It sat above the score in the evaluation order, so it silently discarded keyword evidence entirely — a 95%
  keyword match on a role titled "Senior" was rejected without the score ever being consulted.
- "Lead" and "II" appear in plenty of titles that are open to new grads.
- It duplicated a check A5 already performed against `experience_threshold_years`, so the same fact was
  applied twice by two different mechanisms with different outcomes.

Now folded into the A5 experience check as one signal with one effect: a Mismatch downgrades Yes → Can Try,
exactly as the archived design did. It is still computed, still stored, still displayed on the report line —
it just cannot veto.

### Why the verdict was never a good candidate for "verdict-primary" scoring

The argument for making the semantic verdict primary was that on 89 historical reads the verdict separates
cleanly (Strong 78–90, Partial 40–78, Weak 20–55) while the number is compressed and round-clustered (78% of
scores fall in 45–80, 43% are multiples of 5). Both halves of that are true. But it argues for *not trusting
the semantic number*, which is a reason to keep the semantic read out of the verdict — not a reason to promote
its label above a deterministic score.

---

## 3. Why the A6.5 trigger is bound to `min_match_for_apply`

The original trigger was `URL input AND match_pct > 90`. Audited against 473 analyzed roles, it:

- left **83% of roles structurally ineligible** for a semantic read, and skipped the entire band where the
  apply decision is actually made;
- fired only where keyword was already near-perfect, so it could only ever revise a score **downward** — never
  surface a role keywords *undersold*;
- ignored pasted-JD input entirely, which is how most roles arrive.

The trigger is bound to `min_match_for_apply` rather than hardcoded because the semantic read exists to catch
false-positive applies, so its trigger must never sit *above* the apply bar — that would create a band where
the system says "apply" without ever verifying. Tying them together makes that gap structurally impossible
even if the apply threshold is retuned later.

Coverage at 60 is ~48% of target-track roles. Roles below the apply bar stay keyword-only: the verdict is
already Can Try or No, so there is no false-positive apply to catch.

---

## 4. Why A7 is script-rendered and A9 is script-logged

**A7 (`render_report.py`).** The report used to be hand-written by the model on every analysis, so no two
reports looked alike and the score and skill breakdown were hard to find. Hand-rendering is the direct cause
of the non-uniform-verdict complaint. It is also how the zoox contradiction reached the screen: the renderer
derived `Tailoring:` from the semantic read while the header derived the verdict from keywords, so the two
halves of one report disagreed. `Tailoring:` now derives from the authoritative APPLY verdict.

**A9 (`log_fit.py`).** The old path `~/job-automator/fit_analysis_log.json` was wrong — that directory does
not exist, so the global log silently captured only 109 of 484 analyses (23%). A re-audit on 2026-09-12 found
**501 fit.json on disk vs 167 logged rows**, with the loss concentrated on high-volume batch days: the
per-role row was being skipped when many roles were analyzed at once. That is why the step is a script call
and not a "write the row" instruction. F2's funnel reads this log; a skipped row is lost funnel data.

---

## 5. Why S1 sits above the routing table

The stale-followup sweep declares "at the start of any session", but it previously lived inside Sub-workflow
C. Sessions that ran A/B/E never reached it, so it never fired: **21 of 22 drafted outreach entries went past
due with nothing sent.** It must stay above the routing table to work.

---

## 6. Why outcome tracking (F) exists

Across 484 analyses, 79 submissions and 47 outreach drafts, exactly **one** reply was ever recorded and no
interview result was ever fed back. Without outcomes the system cannot tell which match band, resume version,
or outreach hook actually converts — so it cannot improve, and neither can targeting.

A rejection with a stated reason in `outcome.notes` is the highest-value field in the whole skill for
improving targeting.

---

## 7. Outreach length and format evidence

- **Email 120–170 words.** Recruiter response data shows 50–125 word emails perform best and reply rates drop
  sharply past ~150 words. The old 200–280 target was too long.
- **One ask only.** Stacked asks measurably hurt reply rates on LinkedIn.
- **No generic hooks.** "Your recruiting background made you a good person to reach out to" reads as filler
  because it could apply to any recruiter. A message with no hook line beats a message with a fake one.
- **No permission-granting language** ("no worries if it got buried", "no rush on your end"). Justin is the
  one asking for a favor, not the one who gets to grant absolution.

See `references/outreach_examples.md` for the worked examples and `feedback_outreach_research.md` /
`feedback_outreach_style_rules.md` in memory.
