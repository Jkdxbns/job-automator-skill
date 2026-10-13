---
name: feedback-resume-defensibility
description: "Every résumé line is an attack surface; Justin's repeated interview failures are depth-probes on claims that outrun his evidence"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b3517308-bd3c-4152-a8c8-4d1c22446930
---

**Pattern across three interviews:** Justin loses at depth-probing on résumé claims he
can't defend cold.

- **NVIDIA:** listed a specific C++ standard version on résumé → asked what he used from it → couldn't
  answer. Also failed 2 other C++ questions. (Details available on request.)
- **TBC R3 (Mitch Gaines):** scenario sensor-selection question (underground/tunnel AV,
  GPS-denied) → couldn't reason to the answer. See [[project-tbc-pipeline]].
- **COFFIN framing only:** COFFIN's MCU is an Arduino Nano superloop, not STM32/FreeRTOS
  — see [[project-coffin-repo-landmines]]. **The Object Tracking Turret is NOT an example
  of this** — corrected 2026-09-10; its FreeRTOS/mutex/PWM claims are backed by seven
  verified CMPE 663 coursework projects. See [[feedback-master-profile-permission]].

**Why:** the through-line is claims outrunning evidence, not missing skills. His skill
coverage is ~94% on Edge AI; he loses on defensibility under hostile questioning.

**How to apply:**
1. Audit the résumé line by line — delete anything he can't defend cold. Every token is an
   attack surface; interviewers probe the weakest one. **"Defend" means explaining what he
   did and why (concepts, design choices, tradeoffs), not proving numbers** — interviewers
   never check his code or ask for metric provenance. See [[feedback-metrics-not-cross-checked]].
2. C++ depth is a real named gap (as of 2026-07-14). The inference engine project IS the
   fix — real RAII/templates/move-semantics/constexpr — then list only what he actually used.
3. **DSA** — start LeetCode NOW, in parallel, independent of projects; target roles have
   coding rounds.
4. **Sensor-tradeoff reasoning** is learnable, NOT "bad luck." Drill scenario questions
   (e.g. GPS-denied → LiDAR+IMU+wheel-odom+VIO). Perception interviewers ask this constantly.

Related: [[feedback-interview-prep-style]], [[project-ead-clock]].
