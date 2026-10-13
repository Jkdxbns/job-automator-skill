---
name: reference-interview-log
description: Master interview post-mortem log — all processes, what was asked, what went wrong, and the cross-interview failure pattern
metadata:
  node_type: memory
  type: reference
---

**File:** `~/Desktop/jobs/interview_log.md` — read the CROSS-INTERVIEW PATTERNS section
at the top before any interview prep. Append new rounds there; do not re-derive.

**The pattern as of 2026-09-09 (4 processes, 3 concluded):**
- **2 of 3 losses were C++ fluency**, not knowledge — NVIDIA (stumbled on basic C++ live,
  plus an undefendable C++-standard-version résumé token) and Amazon (OA/DSA). Highest-ROI fix in the
  entire job search, and it is daily reps not a project.
- **1 of 3 was reasoning structure** — TBC R3 perception scenario (tunnel water depth).
  Reached for a component list instead of decomposing. Full worked post-mortem with the
  correct reasoning pattern is in the file.
- **0 losses were caused by a missing domain skill.**
- **All callbacks came from embedded/firmware** (36 apps → 3 callbacks ≈ 8%, vs ~4% for
  edge-AI). Firmware opens doors; depth closes them.

**Reasoning pattern for sensor/scenario questions** (from the TBC post-mortem):
`constraint → what must I measure → what is my reference datum → what does each sensor's
physics actually give me → what is the failsafe`.

**Live:** Zoox — Embedded SWE, Drive Systems. Recruiter round 2026-09-09. Next round
likely C++ fundamentals + embedded basics (memory, interrupts, volatile, RTOS, CAN).

Related: [[feedback-resume-defensibility]], [[project-tbc-pipeline]],
[[project-amazon-embedded-pipeline]].
