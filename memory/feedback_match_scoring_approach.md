---
name: feedback-match-scoring-approach
description: Preference for keyword-based match scoring vs LLM analysis in job fit workflow
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1a9439c-b533-4534-9019-a763c227ba47
  modified: 2026-09-03T19:12:51.887Z
---

Keyword-based (Python string matching) match scoring is fine as the default. Only switch to LLM-based skill analysis if the user explicitly asks for it, OR a standing auto-trigger condition fires (see exception below).

**Why:** Python matching is fast, deterministic, and good enough for day-to-day screening. LLM analysis is reserved for when deeper reasoning about skill depth is needed — but a high keyword score can hide real depth/seniority gaps, so a >90% match is exactly the case where blind trust in keywords is riskiest.

**How to apply:** In Sub-workflow A4, do not add LLM calls or suggest upgrading to AI-based matching unless the user says something like "give me a deeper analysis" or "use AI to score this."

**SUPERSEDED 2026-08-28 — the old exception was measured and found broken.** The
previous rule (URL input AND `match_pct > 90`, informational-only) was audited
against 473 analyzed roles:
- It left **83% of roles structurally ineligible** for a semantic read, and skipped
  the entire 70–90 band where the apply decision is actually made.
- Because it only fired where keyword was already near-perfect, it could only ever
  revise a score **downward** — never surface a role keywords undersold.
- Keyword score ran a mean **+30 points** above the semantic read. In **64 of 87**
  roles the semantic read said Weak/Partial while the verdict still said Yes/Can Try
  (11 of 13 explicit "Weak Fit" roles were still recommended), because the semantic
  result was informational-only.

**Current rule (Sub-workflow A6.5):** run the semantic deep-dive whenever the
keyword match reaches the apply threshold (`match_pct >= min_match_for_apply`,
currently 60), regardless of whether the JD arrived as a URL or pasted text.
Bound to `min_match_for_apply` deliberately (2026-09-03) rather than hardcoded: the
semantic read exists to catch false-positive applies, so its trigger must never sit
*above* the apply bar or a band appears where the system says "apply" without ever
verifying. Coverage ~48% of target-track roles. Roles below the apply bar stay
keyword-only — the verdict is already Can Try or No, so there is no false-positive
apply to catch. **It now gates the verdict**, verdict-primary: `Weak Fit`
downgrades one step, `Strong Fit` can upgrade Can Try -> Yes, and `llm_match_pct <= 35`
is a hard floor forcing APPLY = No. Any change is stated in the report. It records `calibration_delta` so the keyword-vs-semantic gap
keeps accumulating.

Keyword scoring remains the sole method **below the apply threshold**. So the
original preference still holds for most roles; it is overridden only where the
system is about to recommend applying, which is where the data showed keyword-only
scoring was costing real applications.
