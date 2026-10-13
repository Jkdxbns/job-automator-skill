---
name: feedback-master-profile-permission
description: Never edit master_profile.json without Justin's explicit permission; the Object Tracking Turret entry stays as written
metadata:
  node_type: memory
  type: feedback
---

**NEVER modify `~/.claude/skills/job-automator/references/master_profile.json` without
Justin's explicit, in-the-moment permission.** Not to fix a claim, not to re-home a
skill, not to "correct" framing — even when analysis suggests an entry is weak. Propose
the change, state the reasoning, and wait. He decides.

**Why:** it is the single source of truth for every tailored resume, so a silent edit
propagates into live applications. Justin owns that file.

**Standing decision (2026-09-10): the Object Tracking Turret entry STAYS as written.**
Do not suggest removing, renaming, or rewriting it again.

**Its actual backing — verified, so stop treating it as fabricated:** it accumulates
seven graded projects from **CMPE 663 Real-Time Embedded Systems** at
`/mnt/e/_RIT_/CMPE_663_RealTimeEmbeddedSystems/__Project__/`, each with a written report
under Justin's name:
- P0 bare-metal STM32L476RG · P1 Timing (FreeRTOS, PWM, timers, interrupts)
- P2 Servo control (PWM, task priority) · P3 Bank simulator (**FreeRTOS mutexes, queues**)
- P4 Game (EXTI, FreeRTOS, servo) · P5 Signals (**ADC, DMA**, queues)
- P6 Ultrasound speedometer (FreeRTOS, mutex, scheduler, PWM)

RIT does not allow listing six/seven micro-projects separately on a resume, so Justin
consolidated them into one mid-sized project entry. **He can explain and defend the
build**, because he did every component. The FreeRTOS/mutex/PWM/UART/ADC/DMA skills are
genuinely his and are backed by more evidence than most other resume bullets.

This **supersedes** the "synthesized / undefendable" framing in
[[project-turret-virtual-build]] and the turret line in
[[feedback-resume-defensibility]] — those undersold the coursework. The C++ standard-version lesson in
that memory still stands; the turret one does not.
