---
name: project-turret-virtual-build
description: "Object Tracking Turret interview-defense strategy — keep CV as-is, master missing skills via virtual build"
metadata: 
  node_type: memory
  type: project
  originSessionId: 266d76f0-e1c5-44f8-a902-25810ba0ed0e
---

Object Tracking Turret is a CV claim Justin never built as an integrated device — it synthesizes 3 real projects: COFFIN (YOLO on Jetson + VL53L0X via TCA9548A mux on Arduino), STM32 real-time coursework on L476RG (FreeRTOS + mutexes + multi-servo PWM + UART-RX interrupt + EXTI buttons), and smart_fan temperature monitor on F401RE (bare-metal hand-written I2C1 driver + SSD1306 OLED + TIM2-triggered 1Hz ADC).

**Decision (2026-06-08):** Keep the CV/resume bullet exactly as written. Do NOT physically build. Instead, close every missing skill (the ❌ integration gaps) through a "virtual build" so Justin genuinely understands and could build/defend each claim. Goal: project becomes a complete set of transferable + learned skills.

**Risk read:** TBC (Embedded SW Eng) = HIGH exposure — deep rounds probe exactly the STM32 integration gaps. NVIDIA (TensorRT) = LOW exposure — they care about the Jetson/YOLO/inference half (real, from COFFIN), not the firmware. For NVIDIA the turret is a footnote; lead with COFFIN TensorRT/CUDA.

**Guardrail:** Never quote measured metrics (reliability %, latency, deterministic rate) for the *integrated turret* — those don't exist. Individual subsystem metrics (COFFIN, smart_fan 1 Hz) are fine.

**Architecture chosen:** L476RG as turret brain (already hosts FreeRTOS + servos + UART-IT + EXTI — 4 of 6 embedded ✅ live here); ADD the I2C subsystem (VL53L0X + OLED). I2C knowledge transfers from the F401 bare-metal driver.

**Gap-closing curriculum (dependency order):** Phase0 I.1 board decision (done→L476). Phase1 I2C sensing: VL53L0X driver on STM32 (3.2/I.3), OLED distance (3.5), OLED+ToF on one bus under FreeRTOS (3.9/I.2). Phase2 link: Jetson→STM32 protocol + UART-RX parse (1.5/1.8/I.4), pixel→angle→CCR (1.9). Phase3 control: track↔override arbitration (2.4/I.5), unified FreeRTOS schedule (2.9/I.6), vTaskDelayUntil no-drift (3.8). Phase4 Jetson-side: YOLOv8 version (1.2), TensorRT-vs-FP16 nuance (1.4).

See [[project-tbc-pipeline]] [[reference-interview-prep-files]] [[reference-jetson-ssh]].

---

## CORRECTION (2026-09-10) — the "synthesized / CV claim he never built" framing was wrong

Verified against `/mnt/e/_RIT_/CMPE_663_RealTimeEmbeddedSystems/__Project__/`: **seven
graded projects** with written reports under Justin's name cover FreeRTOS scheduling,
mutexes, queues, task priorities, PWM/servo, UART, EXTI, ADC and DMA (P0-P6, incl. a
bank simulator built on mutex-protected shared state and a DMA-fed ADC signals project).

RIT resume norms don't allow listing seven micro-projects, so he consolidated them into
one entry. **He built every component and can defend the build.** Treat the turret as
BACKED, not fabricated.

**Standing decision: the entry stays as written. Do not propose changing it again.**
See [[feedback-master-profile-permission]] — master_profile.json is never edited without
explicit permission.
