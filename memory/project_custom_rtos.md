---
name: project-custom-rtos
description: Flagship embedded project — preemptive RTOS from scratch on STM32 L476RG; scoped from the 68-role embedded job survey
metadata: 
  node_type: memory
  type: project
  originSessionId: 6139995c-bae5-47eb-9a29-6b3fda4597b8
---

Flagship embedded resume project, planned 2026-07-09. Full specs live at `~/Desktop/projects/rtos/` (README.md, docs/PROJECT_REPORT.md, docs/LEARNING_RESOURCES.md, docs/OPEN_DECISIONS.md). Read those before re-planning anything.

**Scoped by data:** survey of 68 analyzed embedded/firmware roles (`~/Desktop/jobs/*/logs/fit.json`) → 716 unique skills, 109 appearing in ≥2 roles. Project chosen to close the five biggest gaps: CAN bus (12 roles), HIL (8), JTAG (7), embedded unit testing (6), CI/CD (4). Histogram artifact at `~/job_search/embedded_skills_survey.html`.

**Decisions made:** L476RG primary (only board with onboard debugger + real bxCAN). BeagleBone Black is the Linux counterpart (SocketCAN peer, HIL host, and the RTOS-vs-Linux-vs-PREEMPT_RT jitter comparison), NOT a port target. Solo project — Maran is off the critical path; `port/riscv32/` stays a documented empty directory. Second port is POSIX host (needed for CI/unit tests anyway).

**Centerpiece artifact:** deliberately engineer a priority inversion, capture the missed deadline on a logic analyzer, enable priority inheritance, capture the met deadline. The Mars Pathfinder bug, reproduced and fixed. This is the thing that makes the project memorable — do not cut it.

**Language split (Justin asked; this is the settled answer):** ~60 instructions of ARM assembly (context switch + first-task launch only), ~3000 lines C, ~500 lines C++ RAII wrapper. Drivers are C, never C++. Reset handler and initial stack framing are C, not asm — Cortex-M hardware loads MSP from vector word 0.

**Timeline deliberately excluded from the report** at Justin's request; target was 6–8 weeks solo with AI in the loop.

**License landmine:** Samek's MiROS teaching kernel is GPLv3 — read to learn, never copy. FreeRTOS is MIT and safe to borrow patterns from.

Related: [[project-coffin-repo-landmines]] (COFFIN is the other flagship; drone runs ChibiOS), [[project-turret-virtual-build]] (being retired in favor of this).
