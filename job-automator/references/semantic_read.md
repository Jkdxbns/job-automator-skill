# A6.5 — Semantic deep-dive: anchors and output shape

Loaded when A6.5 triggers (`match_pct >= min_match_for_apply`).

**Standing constraint, restated because it is the whole point:** this read is **INFORMATIONAL ONLY**. It does
not override `matches` or `apply`. The keyword verdict from `score_fit.py` stays authoritative and there is no
code path from this output to the verdict. Why: `scoring_rationale.md` §2.

## Why the trigger is bound to `min_match_for_apply`

Not hardcoded: the semantic read exists to catch false-positive applies, so its trigger must never sit *above*
the apply bar — that would leave a band where the system recommends applying without ever verifying. Tying
them together makes that gap structurally impossible even if the threshold is retuned (`scoring_rationale.md`
§3).

## Inputs

Load the FULL `references/master_profile.json` — summary_pool, all experience bullets, all project bullets,
education. Not `keywords_only.json`.

## What to judge

Reason over the JD text directly (not the keyword list) against that full profile. Judge actual **skill and
domain depth**, not string presence:

- Are "have" keywords backed by real depth, or surface-only mentions?
- Are there responsibilities in the JD with no real backing anywhere in the profile, even adjacent?
- Conversely: does the profile show depth the keyword pass **missed or undersold** — a project that clearly
  demonstrates a JD responsibility even though the term never string-matched?

⚠️ **Do NOT deflate `llm_match_pct` for seniority or years of experience.** Track-record fit is handled by the
A5 experience check, which already feeds the verdict; penalising it here double-counts it. Note seniority
concerns in `real_gaps` as prose, but score **skill/domain fit only**.

## Scoring anchors

The number must follow from the definition, not from intuition. Use the full range; do not default to
multiples of 5 (43% of historical scores were multiples of 5, which is a tell that the anchors were being
ignored).

| Score | Meaning |
|---|---|
| 85–100 | Nearly every core responsibility has concrete, specific backing in the profile |
| 70–84 | Most core responsibilities backed; 1–2 genuine gaps, learnable on the job |
| 55–69 | Roughly half backed; several core responsibilities have no real backing |
| 40–54 | Minority backed; the role's core is largely unevidenced |
| < 40 | Fundamentally different domain — little transferable evidence |

## Output shape — produce exactly this

`llm_verdict` must be one of the three literals. No qualifiers, no parenthetical commentary appended — a
free-text verdict breaks downstream parsing.

```json
{
  "llm_match_pct": 0,
  "llm_verdict": "Strong Fit | Partial Fit | Weak Fit",
  "strengths": ["genuine depth matches, each with the bullet backing it"],
  "real_gaps": ["responsibilities with no real backing"],
  "overstated_by_keywords": ["counted Have/Adjacent but weaker in reality"],
  "understated_by_keywords": ["real depth the keyword pass MISSED"],
  "screening_gaps": ["exactly 3, ranked most disqualifying first"],
  "recommend_apply": true,
  "reasoning": "2-3 sentence plain-English synthesis"
}
```

### On `screening_gaps`

`real_gaps` lists everything missing — that is a study list. `screening_gaps` answers a different question:
**which three things would actually cause a recruiter or hiring manager to reject this application?** Rank by
how disqualifying they are, not by how many JD bullets mention them. A prioritised subset of `real_gaps`,
never a restatement of it.

This is the field that turns an analysis into a decision, and into a learning backlog. `render_report.py`
prints it as the "Would screen you out" list in the semantic block, and B-GATE prints it when it pauses.

## Handing it back

Write the dict to a JSON file and merge it into the existing fit.json — **do not re-run scoring**:
`python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic <semantic.json> --job-dir "$JOB_DIR"`.
It stores the block verbatim, computes `calibration_delta = match_pct − llm_match_pct` (keeps the keyword-vs-
semantic gap visible, historically ≈ +30, without letting it move the verdict) and clears `semantic_pending`.
Scoring runs once per job. **Do not hand-edit fit.json to
add it.**
