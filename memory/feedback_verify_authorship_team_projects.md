---
name: verify-authorship-team-projects
description: "Before crediting code found in team/club project folders (e.g. ARC Robocon) as Justin's own work in a fit analysis or resume bullet, confirm authorship with him directly."
metadata:
  node_type: memory
  type: feedback
  originSessionId: ca377be2-4b9c-4464-91d6-71ed14bfe2e7
  modified: 2026-09-24T23:36:33.820Z
---

Never infer sole authorship of code found in a multi-person team/club repo (e.g. ARC Robocon, a
25-member club) just because it sits in a folder associated with Justin. Ask him explicitly which
files/functions he personally wrote before using them as "understated" evidence in a job-fit
semantic read or before drafting a resume bullet from them.

**Why:** During a RoboForce fit analysis, the model found mecanum holonomic-drive inverse-kinematics
code (0.7071 mixing coefficients) in the ARC folder and presented it as Justin's undersold work. He
corrected: he never wrote that IK (a teammate did) and hadn't even authored the third-party XBOXUSB.h
library he used for teleoperation (expected — using a library is normal, not a red flag). Separately,
he confirmed he DID personally write a different file's encoder-based quadrature odometry + gyro
heading-correction feedback loop, and a separate HSV object-detection script — both genuinely his and
usable. This ties directly into [[feedback_resume_defensibility]]: an undefendable claim surfaced in a
job-fit analysis is exactly the kind of thing that costs interviews later if it makes it onto a resume
bullet unverified.

**How to apply:** When mining an external project folder (script dumps, old club/team repos) for
undersold experience, use AskUserQuestion (or a direct question) to confirm per-file/per-function
authorship before including anything in `understated_by_keywords`, `strengths`, or a tailored resume
bullet. Third-party libraries (Arduino/Python libs, etc.) being unauthored is normal and not worth
flagging as a gap — only worth clarifying framing (e.g. "integrated X" not "built X's transport
stack").
