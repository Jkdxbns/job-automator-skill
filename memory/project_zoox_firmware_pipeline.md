---
name: project_zoox_firmware_pipeline
description: "Zoox firmware pipeline CLOSED — Drive Systems rejected, redirected to Body Systems, rejected after technical screen with no reason given"
metadata: 
  node_type: memory
  type: project
  originSessionId: 38024202-014e-476f-9e01-9f2c5b5732d2
  modified: 2026-10-07T20:50:38.110Z
---

Recruiter Mikel Pounds (Zoox Technical Recruiter, firmware roles, joined Jun 2026, San Diego) is the single point of contact across multiple Zoox firmware reqs.

Timeline:
- 2026-09-01: Mikel reached out after the Embedded Software Engineer - Drive Systems application (`~/Desktop/jobs/zoox_embedded-swe-drive-systems`). Recruiter screen call booked for 2026-09-09.
- 2026-09-09: Recruiter screen call happened.
- 2026-09-15: Hiring manager passed on Drive Systems. Mikel redirected to a new, similar req: Embedded Software Engineer - Body Systems (`~/Desktop/jobs/zoox_embedded-swe-body-systems`, https://jobs.lever.co/zoox/46c23963-2be1-4037-8f1a-ce87bdccde6d). Justin accepted.
- 2026-09-15: 60-min technical screen scheduled (Zoom + CoderPad). Format confirmed by Mikel: opens with questions on RTOS, hardware peripherals, communication interfaces, testing, and documentation, then live coding grounded in real-world scenarios. C++ preferred; C allowed if requested.
- 2026-09-22 (3:00-4:00pm CT): Technical screen held with Stephen Hurd (Staff Firmware Engineer). NDA signed beforehand; no GenAI tools allowed during the screen.
- 2026-10-07: Rejected. Justin emailed Mikel asking for a reason — no reply as of this date. **Pipeline CLOSED, no further action pending.**

Fit comparison — Body Systems is a meaningfully better match than Drive Systems:
- Drive Systems required CAN/LIN as a hard requirement (total gap, killed defensibility).
- Body Systems lists CAN/LIN only as a bonus qualification; required skills (ARM/PowerPC microcontroller, C++/C+OOP, sensors/motors/actuators, hardware bring-up) map cleanly onto existing STM32/Cortex-M4, COFFIN, and Object Tracking Turret work. Keyword match 60% (Have 5/Adjacent 2/Missing 1 — only CAN/LIN missing), verdict MATCHES Yes / APPLY Yes.

No resume was tailored for Body Systems per Justin's explicit instruction ("no resume is needed, just update our logs") — only fit analysis + outcome logging were done on 2026-09-15.

**How to apply:** Pipeline is closed — no action pending. No rejection reason was obtained (recruiter didn't reply), so this cannot be scored into [[reference_interview_log]]'s cross-interview pattern with confidence; don't guess a cause. If Mikel resurfaces with yet another req, log the outcome chain the same way (F1 in job-automator) rather than starting a fresh untracked thread.

See [[feedback_resume_defensibility]] for why depth-probes matter going into the live coding round.
