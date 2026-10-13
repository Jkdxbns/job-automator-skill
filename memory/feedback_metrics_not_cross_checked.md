---
name: feedback-metrics-not-cross-checked
description: "Interviewers never check Justin's codebase or ask him to prove numbers — stop flagging metric/source mismatches in master_profile or asking him to verify figures"
metadata:
  type: feedback
---

**Do not question, verify, or flag the numbers in Justin's résumé or `master_profile.json`.**
That includes mismatches against a project report or notebook, metrics a code scan couldn't
find, and "unverified" figures.

**Why (Justin, 2026-09-14):** from his own interview experience —
1. No interviewer ever cross-checks his codebase.
2. Interviewers never ask for the real numbers or proof of them. They ask what he did and why.
3. What wins is a correct theoretical explanation and justification of the approach. Whether
   the exact figure matches a report does not matter to anyone in the room.

He called repeated questions about this "badgering" and "silly questions that don't make sense".

**How to apply:**
- When auditing or tailoring, judge a project by whether he can **explain what he built and
  why** (design choices, tradeoffs, theory), never by whether its metrics reproduce from source.
- Do not raise report-vs-résumé number gaps (e.g. CUDA VGG16 49.2 ms vs report 54.7 ms, ASR
  15% WER) or treat `NOT FOUND` / `PARTIAL` metric rows in interview-prep analyses as issues.
- Do not ask him to mount drives or dig up sources just to confirm a number.
- Still valid and still worth raising: a **self-contradiction inside the résumé itself** (two
  bullets stating different facts, like the Hindi-English vs Indian-English fix), and his
  standing rule not to introduce metrics that aren't already in `master_profile.json`.
- Interview prep should drill the **why** behind each number (what it means, what drove it,
  what tradeoff it reflects), not its provenance.

Related: [[feedback-resume-defensibility]], [[project-resume-project-curation]],
[[project-master-profile-claim-audit]].
