---
name: project-master-profile-claim-audit
description: "Every master_profile.json claim that the interview-prep analyses flagged NOT FOUND was audited 2026-09-12 and CLEARED with evidence — do not re-raise them"
metadata:
  node_type: memory
  type: project
---

**Audited 2026-09-12. All eight flagged claims are legitimate. Do not re-open them,
and do not "helpfully" remove them from `master_profile.json`.**

The interview-prep analyses at `~/Desktop/interview_prep/projects/` contain claim-audit
tables marking several CV claims `NOT FOUND`. Cross-checking those against
`master_profile.json` produced 8 apparent overclaims. Every one resolved:

| Claim | Verdict | Evidence |
|---|---|---|
| "timer-triggered ADC scan conversions", "ADC1", "low-level I2C driver" (STM32 Bare-Metal Temp Monitor) | **VERIFIED** | `/mnt/e/Maal/_____Mera_____/smart_fan/` — TIM2 MMS=update→TRGO, `ADC1->CR2` EXTEN + EXTSEL=6 (TIM2 TRGO), scan mode `CR1 bit 8`, EOC interrupt `CR1 bit 5`, and a hand-written I2C driver (`i2c1_set_start/stop/send_addr/write/af_handler`, 23 direct `I2C1->` register writes) |
| VGG-16 U-Net backbone (Teesside) | **KEEP** | Justin's call: training VGG-19 implies VGG-16; transferable |
| medical imaging augmentation, accuracy-latency trade-offs (Teesside) | **KEEP** | Justin's call: not material |
| GitLab + JupyterHub (BARC Python Dev) | **VERIFIED** | Official BARC certificate `/mnt/e/_FCRIT_/__CERTIFICATIONS__/2023_BARC_GUI.pdf`, signed Dev Ranjan Das SO/G ATLAD BTDG: "He has learnt and used Gitlab and Jupyter hub during the project." Outranks a repo scan. |
| Mixed Reality headset / chroma keying (Planctech) | **KEEP** | Backed by `/mnt/e/_FCRIT_/Projects/MP2A/` (ARVR, CADS, Arduino, Python, claims docs, NDA). Bullet already says "concept". |
| PSNR of 65 (BARC Research) | **KEEP** | Justin's call |
| Object Tracking Turret (FreeRTOS/mutex) | **KEEP — never touch** | Backed by CMPE 663; see [[feedback-master-profile-permission]]. Analysis 01's "no FreeRTOS" applies to the COFFIN *arm firmware*, a different project. |

**Why the analyses said NOT FOUND:** each one is scoped to the specific repo it analyzes.
`03_stm32_baremetal.md` audited only the six CMPE 663 coursework projects and did not know
about `smart_fan`. A `NOT FOUND` there means "not in this repo", never "Justin cannot
defend it".

⚠️ **`03_stm32_baremetal.md` is now actively misleading for interviews.** Lines 303 and 377
instruct him to say *"I did not implement ADC in my course projects"* and line 339 marks
timer-triggered ADC `NOT FOUND`. That is true of CMPE 663 but **false overall** — smart_fan
does exactly this, at register level. Saying it in an interview would undersell real,
defensible work. That file needs a correction pointing at smart_fan.

Related: [[feedback-master-profile-permission]], [[feedback-resume-defensibility]].
