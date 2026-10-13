---
name: project-resume-project-curation
description: "2026-09-14 master_profile project curation — which projects Justin kept despite quality critique, which were removed, and the open P7 WER question; do not re-raise the keep decisions"
metadata:
  type: project
---

**Curated 2026-09-14 with Justin's explicit permission.** Backup of the pre-edit profile:
`~/.claude/skills/job-automator/.trash/master_profile.before_P3_P14_P15_removal_20260914.json`;
removed entries saved verbatim in `.trash/removed_projects_P3_P14_P15_20260914.json`.

**Removed:** Quantization-Aware Training (tiny MLP, no result metric), ABB RobotStudio (course
sim, 6% usage), ImageSteganography package (used once). `RAPID` dropped from skills because
nothing backed it any more.

**Kept on Justin's call — do not re-propose removing them:**
- SLM Compression (TinyLlama int8) — he values the pynvml/psutil benchmarking and profiling, not just the quantization flag.
- GPT-2 from scratch — he is comfortable training transformers and can defend it.
- CUDA VGG16 — keep as is, including the 49.2/73.3/77.5 ms figures. Settled; never raise the project-report numbers again.
- MPI Neuron Sim + MPI Ray Tracer — both kept as separate entries; they are the only MPI/SLURM backing.
- Object Tracking Turret — never touch (see [[project-master-profile-claim-audit]]).

**Haptics project REMOVED 2026-09-14** (later the same day) — Justin's call: it is not
safety-critical and not test automation, and COFFIN already backs its remaining skills. Entry saved
verbatim at `.trash/removed_project_P2_thermal_illusion_20260914.json`. Do not re-propose it or argue
its unique keywords. History below kept only in case he restores it.

**(Superseded) Haptics project rewritten 2026-09-14** → now "Thermal Referral Illusion Study — Wearable Haptic
Wristband + PyQt6 App" (backup: `.trash/master_profile.before_P2_rewrite_20260914.json`). Framing
Justin set: he built the rig and the app from scratch to study a thermal referral illusion
(vibration makes Peltier heat/cold be felt elsewhere on the wrist); 1 Peltier + 3 vibrators
equally spaced on the band, Peltier positioned at the top, left, and right of the wrist
(Justin's statement — the app code's TOP/RIGHT/BOTTOM/LEFT labels don't override it), Arduino +
H-bridge driver; title approved; 4 bullets since 2026-09-14 keyword pass (HW/SW integration ·
safety-critical firmware · PyQt6 GUI/multithreading/test automation · user study) — for firmware
roles lead with the firmware bullet and drop the user-study one unless the JD is haptics/wearables/HCI.
Deliberately NOT claimed: functional safety (standards term — invites ISO 26262/IEC 61508 questions),
medical device, watchdog (none implemented), motor control, closed-loop control; 10 participants × (36 heating + 36
cooling) trials; ~50–55% felt it at both sites, 15–20% only at the vibrator, rest only at the
Peltier. **Never mention the HTML/Web Serial page, the "rebuild", or the web/LAN monitor** — he
defends Python and PyQt6, not HTML/CSS. Source: `~/Desktop/palash/`.

**ASR "15% WER" — settled, keep it.** Only the dataset wording was fixed (Hindi-English →
NPTEL 2020 Indian-English, so bullets 1 and 3 agree). The 15% WER stays as written; do not
question it again — see [[feedback-metrics-not-cross-checked]].

Related: [[feedback-resume-defensibility]], [[feedback-master-profile-permission]].
