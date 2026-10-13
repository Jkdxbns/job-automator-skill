# Interview Log

Post-mortems for every interview process. Append new rounds under the company section;
add a new `# COMPANY —` section for a new company. Keep the field names consistent so
this stays analyzable.

**Index:** [The Boring Company](#the-boring-company--rejected) · [NVIDIA](#nvidia--rejected) ·
[Amazon](#amazon--rejected) · [Zoox](#zoox--rejected) · [Dockware](#dockware--in-progress) ·
[Patterns](#cross-interview-patterns)

---

# CROSS-INTERVIEW PATTERNS

*Updated 2026-10-08 (TBC reclassified as perception; callback split corrected). This is the
section to read before any interview.*

| Process | Stage reached | Lost on | Category |
|---|---|---|---|
| The Boring Company *(titled Embedded Software Engineer; interviewed entirely as perception — robot systems, LiDAR, cameras, never firmware)* | R3 of 3 (cleared R1, R2) | Perception scenario reasoning | **Reasoning structure** |
| NVIDIA | Technical | Basic C++ under pressure + undefendable C++17 claim | **C++ fluency** |
| Amazon | OA | DSA / C++ | **C++ fluency** |
| Zoox | Cleared technical screen (2026-09-22); interview loop scheduled 2026-10-01/02 (how far it got is not logged) | **Rejected 2026-10-07, no reason given** | **Unscored** (no feedback). Testing & validation was the gap the interviewer flagged at the screen, but it did not block advancing. Do not infer a cause. |
| Dockware | Phone screen (2026-09-25) | — in progress, no gap identified | Answered the callback question (11 integration failures) generically instead of naming specific fixes — didn't block the call's flow, but worth flagging: see round notes |

**The pattern, stated plainly:**
- **Of the 3 losses with a known cause, 2 were C++ fluency**, not knowledge. Highest-priority
  fix, and it is daily reps, not a project.
- **1 of those 3 was reasoning structure** on an open scenario — reached for a component list
  instead of decomposing the problem.
- **Zoox (4th concluded process, rejected 2026-10-07) has no stated reason**, so it is not
  counted in the split above. Don't guess a cause.
- **0 of the 3 scoreable losses were caused by a missing domain skill.** The gaps that
  actually killed interviews were fluency and reasoning, both learnable and both cheap
  relative to a new project.
- **Callbacks come from perception/robotics roles, not firmware.** TBC was titled Embedded
  Software Engineer but the rounds were robot systems, LiDAR and cameras — never the firmware
  side. Dockware is robotics. Counted against `submitted_log.csv` as of 2026-10-08:
  robotics/perception **48 applications → 2 human interviews** (TBC, Dockware);
  embedded/firmware **93 applications → 1 human interview** (Zoox), plus Amazon, which ended
  at the OA with no human round. Perception is what opens the door; perception depth
  (TBC) and C++/DSA (NVIDIA, Amazon) are what close it.
  *This supersedes the earlier claim that "all 4 callbacks came from embedded/firmware roles
  (36 applications → 3 callbacks ≈ 8%)" — wrong on the family split and on the denominator,
  which has since grown from 36 to 93.*

**Standing prep list (drill before any technical round):**
1. C++ fundamentals + DSA, daily — the single acute wound.
2. Sensor/scenario decomposition (see the TBC post-mortem for the pattern).
3. Never list a résumé token you cannot defend cold (the C++17 lesson).

---

# THE BORING COMPANY — REJECTED

---

## Round 1 — Recruiter Screen

| Field | Details |
|---|---|
| **Company** | The Boring Company |
| **Role** | Embedded Software Engineer |
| **Stage** | Recruiter Screen |
| **Interviewer** | Alicia Scuderi (Recruiter) |
| **Date** | June 8, 2026 |
| **Time** | 1:00 PM – 1:30 PM |
| **Format** | Phone / Video call |
| **Location (role)** | Bastrop, TX (in-office) |
| **Resume sent** | `boringcompany_embedded-unified/resume_20260529_1244.pdf` |

### Notes
- Cold email sent May 26 → resume requested May 29 → call booked June 2
- Primary role: Embedded Software Engineer (92% match)
- Secondary mentioned in email: Embedded Perception Engineer (stretch, 5yr gap)
- Visa flag: F-1 OPT, EAD pending, H-1B sponsorship required long-term

### Outcome
- [x] Passed to technical round ✅

---

## Round 2 — Technical Interview

| Field | Details |
|---|---|
| **Stage** | Technical Interview |
| **Role title confirmed** | Associate Software Engineer |
| **Role context** | Autonomous systems — SWEs work with controllers, hardware-software integration |
| **Interviewer** | Zaphod Schmidt (Software Engineer, TBC Bastrop) |
| **Date** | TBD |
| **Time** | TBD |
| **Format** | TBD |

### Interviewer Profile
- Software Engineer at TBC, Bastrop TX (Jul 2025 – Present)
- Former TBC intern (May–Aug 2024, Bastrop) → converted to full-time
- 3 years CU Hyperloop: Software Engineer → Team Lead → President → Advisor
- Software Engineer at Good Speed Parking (computer vision for parking)
- Trimble Inc intern (hardware-software, surveying equipment)
- GitHub: `Marlin-KosselXL` — modified Marlin 3D printer firmware in C/C++ (motion control, stepper drivers, real-time ISR, safety watchdogs) — directly analogous to TBM embedded control

### What this signals
- Will go deep on embedded C/C++ — he's written motion control firmware himself
- CU Hyperloop background means he'll evaluate whether you understand tunnel/transport systems
- Was a new grad hire himself — knows the current interview format from both sides
- Expect: RTOS concepts, sensor integration, safety-critical patterns, hardware debugging, project deep-dives

### What was discussed
- Zaphod shared his work on camera streaming apps and LiDAR + camera systems at TBC
- Discussed the hardware-software-networking intersection at TBC
- He gave an honest perspective on day-to-day life at the company

### Outcome
- [x] Cleared technical round ✅

### Follow-up
- Sent LinkedIn connection note thanking him + noting hope to work together

---

## Round 3 — Senior Developer Interview

| Field | Details |
|---|---|
| **Stage** | Technical / Senior Developer round |
| **Interviewer** | Mitch Gaines (Embedded Software Engineer 2, TBC Austin) |
| **Format** | Video call |

### Interviewer Profile
- Embedded SW Engineer 2 at TBC (2.5 yrs); "Automation, Controls, Robotics Full Stack"
- B.S. Worcester Polytechnic Institute (WPI) — robotics
- Career: Farmblox (co-founder, IoT/LoRaWAN), Embue (building automation), Locus Robotics, Symbotic, Corista
- GitHub: deep embedded Linux — Yocto/OpenEmbedded, RAUC (A/B OTA updates), Mender
- 2 patents: Virtual Slide Stage (US 11,675,178, granted); Dynamic Pressure Sense/Redistribution (US 62/629,223, provisional)
- Focus: embedded Linux, modern C++, field reliability, robotics/controls, sensor→actuation loops

---

## OUTCOME — REJECTED ❌

- **Final result:** Rejected after Round 3 (senior developer interview with Mitch Gaines)
- Cleared Round 1 (recruiter) and Round 2 (technical, Zaphod) before this
- Role: Associate Software Engineer, autonomous systems, Bastrop TX

### Retrospective — Round 3 (filled 2026-09-09)

**The question (perception scenario):**
> An electric car drives through a tunnel that may have water accumulation. Stop the
> vehicle if water depth exceeds 1 ft — and the decision must be made *in advance*.

**What I answered:** localize the vehicle with wheel encoders, then use LiDAR and
cameras to detect water depth and distance to the water.
**Interviewer's hint:** "we do use LiDAR, but with protection."
**I stumbled at the start** and needed a prompt before answering.

**Stated rejection reason (via recruiter):** other candidates gave better answers.

**What actually went wrong — reached for components instead of decomposing the problem.**
The answer named hardware without engaging the measurement problem. Four things a
strong answer attacks:

1. **Depth is a *datum* problem, not a detection problem.** You never measure depth
   directly — you measure a water *surface*. Depth = surface elevation − floor
   elevation. So the real question is "where does my floor reference come from?"
   Answer: a prior map of the tunnel floor profile. That reframe is most of the answer.
2. **It is TBC's own tunnel — use the infrastructure.** Fixed water-level sensors at
   the known low points, broadcast to vehicles, beats estimating depth from a moving
   car. Solving on-vehicle what static instrumentation solves for $40 is the wrong
   instinct and interviewers notice.
3. **LiDAR physics on water** (this is what the "with protection" hint was circling).
   Water is specular and transparent to LiDAR — a puddle returns *nothing* (beam
   refracts away) or mirrors the ceiling. So water appears as a **void in the point
   cloud**, and that dropout *is* the detection signal when compared against the prior
   floor map. "LiDAR measures water depth" signals the return physics wasn't considered.
   Cameras add specular glare and polarization (real wet-surface technique).
4. **"In advance" is a requirement, not flavour text.** It sets lead distance =
   f(speed, braking distance). Asking "how fast, what braking distance, what lead time?"
   is itself worth marks.

**Fix:** not tunnel knowledge — a reasoning pattern:
`constraint → what must I measure → what is my reference datum → what does each
sensor's physics actually give me → what is the failsafe`. Drillable in a weekend.

**Honest read on the recruiter's reason:** "other candidates gave better answers" is
probably close to true rather than a brush-off — it is consistent with a stumble, a
prompt, then a component list. It is a *comparative* verdict, not a damning one.

**What went well:** cleared R1 (recruiter) and R2 (technical) against a real embedded
team, off a cold email with no referral.

---

<!-- Add future rounds below this line -->


---

# NVIDIA — REJECTED

| Field | Details |
|---|---|
| **Company** | NVIDIA |
| **Date** | June 2026 |
| **Stage reached** | Technical interview |
| **Outcome** | Rejected ❌ |

### What went wrong
- **Stumbled writing basic C++ code** during the interview. Self-assessed as lack of
  practice and confidence rather than a knowledge ceiling.
- **Listed "C++17" on the résumé and could not answer "what did you use from C++17?"**
  Also failed 2 further C++ questions.

### Diagnosis
Two distinct failures, both fixable:
1. **C++ fluency under pressure** — reps, not theory.
2. **An undefendable résumé token.** The gap did not fail the interview; *claiming past
   the gap* did. "I'd call myself intermediate, here's what I actually built" would have
   survived that question.

### Fix
Daily C++ reps. Audit the résumé line by line and delete anything not defendable cold.

---

# AMAZON — REJECTED

| Field | Details |
|---|---|
| **Company** | Amazon |
| **Date** | August 2026 |
| **Stage reached** | Online Assessment (DSA gate) |
| **Outcome** | Did not pass ❌ |
| **Context** | Generic req 3177934 + Embedded specialization routes to the embedded org |

### What went wrong
OA was hard; self-assessed as lack of C++/DSA practice.

### Diagnosis
Same root cause as NVIDIA — **C++/DSA fluency**. This is now 2 of 3 concluded losses
from the same single cause, which makes it the highest-ROI thing to fix in the whole
job search.

### Fix
Daily LeetCode/DSA in C++. Not optional, not a project — a habit.

---

# ZOOX — REJECTED

| Field | Details |
|---|---|
| **Company** | Zoox |
| **Role** | Embedded Software Engineer — **Body Systems** (pivoted from Drive Systems 2026-09-15; see Update below) |
| **Applied** | 2026-09-01 (Drive Systems) |
| **Stage** | Cleared technical screen (2026-09-22); interview loop scheduled 2026-10-01 and 2026-10-02. How far the process got before the rejection is not recorded here. |
| **Recruiter** | Mikel Pounds (corrected — previously logged as "Michael") |
| **Outcome** | **Rejected 2026-10-07. No reason given.** See "OUTCOME — REJECTED" at the end of this section. |

### Related applications
- Zoox — Embedded Software Engineer (2026-08-04)
- Zoox — Embedded Software Engineer, MCU Platforms (2026-08-05)
- Zoox — Embedded Software Engineer, Body Systems (2026-09-15, active — see Update below)

## Round 1 — Recruiter Screen (2026-09-09)

Full transcript: `~/Downloads/Zoox_Mikel_Pounds_Recruiter_09092026.txt`

| Field | Details |
|---|---|
| **Interviewer** | Michael (Recruiter) |
| **Format** | Phone/video, ~14 min |

### Company/role context given
- Zoox = fully electric, autonomous vehicle; Amazon subsidiary (independent) — "fast-paced
  startup feel, backed by Amazon." Launched Las Vegas + SF; ~200 vehicles → targeting ~2000
  by end of year. Became revenue-generating (~1 month before call) charging for LV rides.
- Role sits at the heart of vehicle motion: trajectory → actuator commands (motor/brake
  torque, steering), control-source arbitration, safety monitoring of trajectory execution
  + drive control ECUs. Also: sim/emulation/SIL/HIL infra, integrating supplier subsystems
  (steering, motoring, braking, active suspension). Day-to-day: SW requirements, design
  docs, test plans, cross-functional work.

### Confirmed 3-round process (this is new — wasn't known before this call)
1. **Technical screen** (Zoom) — hardware peripherals, communication interfaces, testing &
   documentation, **RTOS**, then live **C++ coding on CoderPad** with a firmware engineer,
   "grounded in real-world scenarios" (not abstract LC).
2. **Interview loop** — technical presentation + **five 1:1 interviews** (recruiter said
   he'll prep specifically for this one — the longest part of the process).
3. **Leadership round** — director of firmware engineering (mutual fit check), then
   **2 references** (a supervisor + a peer).

### New-grad bar, per recruiter (verbatim gist)
Hard skills expected to be trained on the job; screening mainly for **aptitude to learn**,
clear communication, ability to talk through a technical challenge, genuine interest in the
space, and curiosity (asking good questions). Debugging experience with oscilloscopes/logic
analyzers counted even without exact ISO/tooling checklist match — "wouldn't get too hung up
on the basic qualifications."

### Visa — confirmed no issue
Zoox sponsors all visa types. Wants 2+ years left on OPT/STEM-OPT (gives 2 chances at the
H1B lottery). Justin's OPT extension covers this — recruiter explicitly said "no issue there."

### Logistics
- Resume went to hiring manager same day (2026-09-09); feedback expected **by end of that
  week**. As of 2026-09-15 (6 days later) — **no update received, worth a follow-up nudge.**
- Comp question asked; Justin gave an open/flexible answer, no number pinned.

### Expected next round (if it comes)
Per recruiter + transcript: **hardware peripherals, comm interfaces (CAN/LIN likely), RTOS,
testing/documentation, then live embedded-flavored C++ on CoderPad.**

### Prep (given the cross-interview pattern above + this call's specifics)
1. **C++ reps daily — highest-priority, already cost 2 interviews.** CoderPad round is
   "real-world scenarios," not textbook DSA — embedded-flavored practice (bit ops, no-alloc
   design, ring buffers, state machines) outweighs LC hards here.
2. **RTOS fundamentals — currently a real gap, not covered anywhere in the C++ roadmap or
   the telemetry_gateway project.** Needs its own light pass (tasks, priorities, queues,
   semaphores, ISR-safe patterns) before the technical screen.
3. **Embedded fundamentals:** interrupt latency, priority inversion, CAN framing/arbitration,
   `volatile`, memory model.
4. **Sensor/scenario decomposition drill (TBC R3 pattern)** — "grounded in real-world
   scenarios" coding is exactly the shape that burned the TBC round (reached for components
   instead of decomposing the problem). Drill the `constraint → what to measure → reference
   datum → sensor physics → failsafe` pattern before this screen.

### Outcome notes
- [x] Recruiter round result: cleared, resume forwarded to hiring manager
- [x] Hiring-manager feedback: Drive Systems hiring manager passed (2026-09-15) — see Update below
- [ ] Technical round date:
- [ ] What was asked:
- [ ] What went wrong / well:

## Update 2026-09-15/16 — Drive Systems passed; pivoted to Body Systems; technical screen confirmed

Source: Gmail thread with Mikel Pounds (mpounds@zoox.com), read via Gemini export
(`~/Downloads/Zoox-Technical-Interview-Preparation.md`).

- **2026-09-15, ~14:48** — Mikel: "I just heard back from the hiring manager and they are not
  interested for this role; however, I have another role I think you would be a good fit for.
  It's a similar role but on our Body Systems team" (link to Lever posting). Drive Systems is
  now a closed loss for this specific req, not a rejection of Justin generally — same recruiter
  immediately re-routed him.
- **2026-09-15, ~13:24** — Justin confirmed interest in Body Systems.
- **2026-09-15, ~13:35** — Mikel: next step is the same **60-min Zoom technical screen** as
  originally described for Drive Systems — RTOS, hardware peripherals, communication interfaces,
  testing, documentation, then live coding on **CoderPad**, "grounded in real world scenarios."
  C++ preferred, C acceptable if flagged up front. Availability request sent.
- **2026-09-15, ~13:58** — Justin submitted availability.
- **2026-09-15, ~16:21–16:23** — Mikel: nothing further needed; coordinator **Michelle** will
  follow up once the technical screen is scheduled.

**Role scope change:** Body Systems ≠ Drive Systems. Body Systems = doors, latches, power
windows, exterior/interior lighting, HVAC, seat actuation, thermal sensors — not
trajectory→actuator-command/motor-torque/steering. Same CAN/LIN/RTOS/C++ technical core, same
screen format; **prep content should target Body Systems examples**, not Drive Systems ones.

**Study material built 2026-09-16:** `~/Desktop/interview_prep/Zoox_BodySystems/` — a 5-module,
from-zero study guide (Modern C++ → Peripherals → RTOS → CAN/LIN → CoderPad synthesis), PDF +
`START_HERE.md`. Built from a structured Gemini planning session plus live-verified public-forum
intel on this exact screen (not LeetCode-style; embedded data structures + write-your-own-tests;
volatile/stack-vs-heap trivia; "why Zoox" as their favorite behavioral question; 3–5 round on-site
loop + leadership round if this screen clears).

### Outcome notes (Body Systems)
- [x] Redirected to Body Systems after Drive Systems HM passed
- [x] Interest confirmed, availability submitted
- [x] Technical screen date: 2026-09-22 (held)
- [x] What was asked: see Round 2 below
- [x] What went wrong / well: see Round 2 below

## Round 2 — Technical Screen (2026-09-22)

Self-reported debrief (no transcript).

### What was asked
1. Name hardware peripherals + comm protocols worked with, where each is used, and which
   one is disliked. Justin answered: UART, SPI, I2C (protocols); timer, ADC, GPIO
   (peripherals).
2. Embedded Linux vs. RTOS vs. bare-metal — advantages/disadvantages of each.
3. Testing/handoff question: given code handed from one team to another, how would the
   receiving team debug and verify it works. **Could not answer at all.**
4. Live C++ coding, production-code-flavored debugging.
5. Class-size question: given a class with private data members + getters/setters, compute
   `sizeof`. Initially got it wrong, then recovered and explained padding — but referred to
   it as "packing" instead of padding (terminology slip, corrected in this debrief).
6. Black-box function synthesis: given 5 (x, y) pairs from an unknown function y = f(x),
   write code to iterate over the array and reproduce/apply the relationship. Fumbled this
   under pressure — interviewer explicitly attributed it to interview-stress "brain," not a
   knowledge gap.
7. What is a "serialization method" — asked by the interviewer, in the context of the
   testing/validation line of questioning.

### What went well
- Peripherals/protocols and RTOS-vs-bare-metal-vs-Linux fundamentals were solid.
- Recovered on the class-size question and got to padding once prompted.

### What went wrong (interviewer's explicit feedback)
- **Testing/validation experience is the stated gap.** Interviewer said Justin lacks
  debugging/testing experience and was expecting concrete answers on **integration testing,
  unit testing, and automated testing** — not just "it compiles and runs on hardware."
- The team-handoff debugging question (item 3) went unanswered — no framework for "how does
  someone else verify code they didn't write."
- Black-box array/function coding (item 6) — execution slip attributed to nerves, not
  concept gap; still worth drilling as a warm-up pattern next time.
- Serialization: term was raised in the testing context (likely re: serializing test
  data/messages for CAN/LIN payloads or logging, not general software serialization) —
  worth clarifying exact framing if it comes up again.

### Follow-up prep priority (before any next round)
1. **Testing & validation vocabulary + real examples**, mapped onto existing projects
   (COFFIN, STM32, ROS UR5e) — unit test vs. integration test vs. automated/regression test,
   and a concrete "code handed off between teams, how do you verify it" framework (unit
   tests at module boundary → integration test on target/HIL → code review → static
   analysis → CI). This was flagged as the clearest, most fixable gap.
2. Serialization in an embedded/automotive context — struct packing/marshaling for CAN/LIN
   frame payloads, byte order, versioning a wire format.
3. sizeof/padding drills — timed reps until padding math + terminology (padding, not
  packing) is automatic.
4. Warm-up drill for "black box input/output array → infer/apply function" style prompts to
   burn off first-questions nerves before it's asked live again.

## Update 2026-09-23 — Technical screen cleared; advancing to interview loop

Source: email from Mikel Pounds (mpounds@zoox.com), 2026-09-23.

**Result:** passed the 2026-09-22 technical screen — the testing/validation gap flagged by
the interviewer did not block advancement. Moving to the next stage of the process, which
per Round 1 notes is the **interview loop** (technical presentation + five 1:1 interviews),
followed by a leadership round + 2 references if that clears.

**Immediate asks from Mikel:**
1. Submit availability for upcoming interview-loop sessions via calendar link:
   `https://mloop.in/s/4brknmkNRk7`
2. Send a couple of times this week for a **15-minute prep call** with Mikel ahead of the
   loop.

### Outcome notes (Round 2 — Technical Screen)
- [x] Result: **cleared**, advancing to interview loop
- [ ] Availability submitted for interview-loop sessions
- [ ] Prep call with Mikel scheduled
- [ ] Interview loop date(s):

### Next prep priority
Loop = technical presentation + 5x 1:1s, the part the recruiter told Justin (Round 1) he'd
prep specifically for — treat the prep call as the place to get the real breakdown of format
and interviewers before building study material. Testing/validation prep items from Round 2
(above) still stand and should carry into loop prep once the format is known.

**Format, as understood 2026-09-23 (pre-prep-call, subject to confirmation):** ~5 hours,
single day, 5 interviewers — Justin's assumption is all five are 1:1s (matches Round 1
recruiter's "five 1:1 interviews" note), but exact mix (loop-only vs. + the technical
presentation folded into one of the five slots) TBD until the prep call with Mikel.

### External research on the onsite loop (2026-09-23)

Verified directly: Glassdoor's Zoox Software Engineer interview-stage breakdown (62 ratings)
lists "One on one interview" as an explicit stage (16%), consistent with a five-1:1 format.
Difficulty 3.1/5, 53% positive experience. Embedded Software Engineer-specific Glassdoor page
has only 3 ratings, no readable review text (gated/thin sample — low confidence on its own).
A 2023 Blind post (`zoox-onsite-interview-what-to-expect`) from a SWE candidate reports 6
rounds with no further detail visible (comments gated).

Lower-confidence (AI-aggregator sites — Dataford, Verve AI, InterviewKickstart, DesignGurus —
not primary candidate reports, but the same themes repeated independently across several of
them, so treated as directional signal, not verified fact):
- Onsite = full day, often remote, **5-6 rounds of 45-60 min each**.
- Recurring round types: coding/debugging, **system design** (embedded-scale, not web-scale —
  role context makes this "design a subsystem," e.g. a door-lock controller, not a
  distributed-systems design), a **math/logic/reasoning round** (geometry, spatial reasoning,
  probability, brain teasers — this is new, not in the current study guide at all), and a
  **behavioral/culture-fit session**, often with the hiring manager.
- "No LC gotcha interviews" — real-world scenario grounded, consistent with what Mikel already
  told Justin about the screen's coding style.
- Embedded-specific technical themes mentioned: RTOS basics, memory alignment, thread safety /
  memory barriers, OOP-style coding, CAN/LIN as a recurring qualification area.

**New prep item this surfaces:** a lightweight **math/logic/reasoning warm-up** (basic
geometry, spatial reasoning, probability, brain-teaser style) — not currently in any module of
the Zoox study guide and not part of the screen. Low time investment, but worth a pass since
it showed up independently across multiple sources.

### Domain/industry research (2026-09-23) — Body Systems electronics + EV industry process

Verified via web search (Embitel automotive-insights articles, Wikipedia BCM page, Promwad/
MathWorks/Eclipse ISO 26262 references):
- **Body Control Module (BCM):** the ECU class Body Systems work lives in — sensors/switches in,
  application-layer algorithms (remote-key decrypt, debounce, PWM actuator control, closed-loop
  HVAC/thermal control), relays/solenoids out. Communicates over CAN; also touches UDS/OBD-2 for
  diagnostics.
- **AUTOSAR-style layered architecture:** application layer on top of Base Software (BSW), often
  model-based (Simulink-generated C) — explains why "supplier integration" and portability matter
  so much in the JD.
- **V-model SDLC + ISO 26262 functional safety (ASIL A-D):** the V-model (requirements → design →
  implementation, mirrored by unit → integration → system/validation testing) is the same
  vocabulary as both the screen's testing question and the JD's "requirements capture → design →
  implementation → validation" phrasing — not a coincidence, it's the standard automotive
  development process this role operates inside.
- **OEM/Tier-1/supplier structure:** explains why supplier sub-system integration and heavy
  cross-functional collaboration (named explicitly in the JD: vehicle/controls/electrical/
  validation engineers) are core to this role, not incidental.

## Update 2026-09-25 — Prep call with Mikel (recruiter): full loop structure confirmed

Source: recorded call, Mikel Pounds, 2026-09-25 (~23 min). Transcribed locally
(faster-whisper). Recording: `~/Downloads/Zoox_Mikel_Ponds_Round2.mp4`.

**Confirmed structure — 6 sessions total (1 presentation + 5 interviews), not just 5x 1:1s:**

1. **Technical presentation** — usually scheduled first ("start on a strength"), but order
   can vary. Audience: hiring manager (**Beau**) + the 5 interviewers + possibly a few team
   members, 5–7 people on the call. Candidate presents ONE past project (school or
   internship, must be embedded SW/systems-related): what it was, requirements gathering,
   challenges/debugging, solution, outcome, specific individual contribution. **6–8 slide
   deck. 15–20 min talk + ~5 min Q&A.** Justin's choice, discussed live on the call: the
   **STM32 bare-metal temperature monitor** project (`03_stm32_baremetal.md`) — picked over
   the CV/robotics project because it's solo (clean attribution), already on resume, and the
   thermal-sensor angle ties directly to Body Systems. Mikel offered to route 2 project
   options to the hiring manager for a preference; Justin declined and picked STM32 himself.
2. **Coding interview #1 — 1 hour.** Opens with RTOS-familiarity questions + issues in
   multitasking software (race conditions, priority inversion — matches loop item 3). Then
   live C++ coding via CoderPad link — evaluated on C++ fundamentals AND
   development/testing thought process (both functionality and how the code is written,
   confirmed explicitly, not just "does it run").
3. **Coding interview #2 — 1 hour.** Hardware peripherals / firmware-for-hardware focus.
   Given a supplier datasheet for a simple sensor (Mikel: may be a genuinely messy/bad
   datasheet — saying so out loud is a fine signal) — extract specs, then write code. Core
   skill: **bitwise operators, counting individual bits.** Mikel's direct quote: "the STM32
   project is exactly what this interview is expecting." CoderPad link provided.
4. **System design — door control unit — 45 min, no coding.** Walkthrough of the door
   control unit's operation + available test assets, then candidate designs and tests the
   system live as a technical discussion. Time split shifts toward whichever the candidate
   is stronger at (testing/debugging vs. software architecture design) — confirms loop items
   1 (testing) and 5 (system design) both land here.
5. **Hiring manager interview (Beau) — 45 min, technical + behavioral.** Entire resume is
   fair game — projects, specific contributions, cross-functional collaboration. Confirmed
   behavioral question shape: "tell me about a time you received critical feedback" —
   Mikel's advice: source the story from school/project feedback, not personal life. Have a
   genuine "why Zoox" answer and thoughtful questions ready for him.
6. **Math & problem solving — 45 min, Zoox-specific.** Communication-based interview where
   math (algebra, geometry, probability) is just the subject matter — explicitly **not**
   testing math skill. What's graded: asking clarifying questions before solving, verbalizing
   every step (including anything written on paper), general information-gathering before
   diving in. Same "ask before you start" principle applies to the coding rounds and system
   design round too — Mikel repeated this as the single most important cross-cutting habit.

**Domain-specific knowledge — explicitly de-scoped beyond RTOS/peripherals:** asked directly
whether Body Systems domain questions (doors, dashboards) should be expected — Mikel: no,
outside of interview 1's RTOS/multitasking and interview 2's hardware-peripherals framing,
no deeper Body-Systems-specific quizzing is planned. "Wouldn't hurt" to skim recent Zoox news
casually, but this is optional color, not a prep item. **This meaningfully deprioritizes loop
item 8 (BCM/AUTOSAR/ISO 26262/V-model deep dive)** from the 2026-09-23 study plan — keep it
as light background only, don't invest further depth there.

**Drive Systems → Body Systems role change:** confirmed the only difference is team focus
area (body team works thermal, lighting, enclosure/closure systems) — nothing else about the
role or process changed.

**What the team is evaluating for (new-grad calibration):** primary hard skill = **C++**.
Soft skills weighted heavily: curiosity, inquisitiveness, asking thoughtful clarifying
questions, demonstrated hunger to learn. Mikel confirmed explicitly that interviewers know
Justin is a new grad with no production experience and are not expecting expert-level
performance — calibrate answers accordingly, don't overclaim seniority.

**Logistics confirmed:**
- Can split the loop across 2 days (recommended default: presentation + 2 interviews day 1,
  remaining 3 day 2) or do all 6 in one day — candidate's choice to request the split, but
  **cannot choose which specific interviews land on which day** (scheduler decides that).
- Give wide availability windows per day (e.g., "11am–5pm") rather than narrow slots.
- Turnaround after interviews: **~2–3 business days** for an update once actually scheduled;
  Mikel will respond immediately if nudged even without a firm answer yet.
- **Anti-cheating warning (told to every candidate, not Justin-specific):** Zoox has seen a
  rise in candidates using AI/Google or tab-switching during Zoom interviews — visible to
  interviewers and grounds for disqualification. Flagged specifically for the two CoderPad
  rounds. Justin asked about split-screen setup on a 14" laptop (CoderPad + Zoom in separate
  windows vs. two tabs in one window); Mikel had no firm recommendation — use discretion, but
  confirmed window/tab switches are visible and scrutinized. **Action: rehearse both coding
  rounds keeping CoderPad and the call in minimal, deliberate view — no ad hoc window
  hunting.**

### Outcome notes (Prep call)
- [x] Full loop structure obtained: presentation + 6 sessions (recruiter's "5 one-on-ones"
      language in earlier notes undercounted — it's 5 interviews + 1 presentation)
- [x] Presentation project chosen: STM32 bare-metal temperature monitor
- [ ] Availability submitted with 2-day split preference (11am–5pm target window, per Justin's
      own stated preference on the call)
- [ ] 6–8 slide presentation deck built
- [ ] Interview loop date(s) confirmed by scheduler

### Next prep priority (supersedes 2026-09-23 plan)
1. **Build the presentation deck** (new, not in the 2026-09-23 plan at all) — 6–8 slides on
   STM32 bare-metal temp monitor, rehearse to 15–20 min + anticipate Q&A from a 5–7 person
   technical audience including the hiring manager.
2. **"Ask clarifying questions before solving" as a drilled habit** — now confirmed as the
   single most-repeated piece of interviewer guidance, applies across coding, system design,
   AND the math/problem-solving round. Practice explicitly pausing to ask before touching
   keyboard/pen in every mock rep from here out.
3. Loop items 1 (testing/validation) and 5 (system design) both concentrate in the door
   control unit round — prioritize accordingly.
4. Loop item 3 (RTOS + CAN/LIN) — RTOS/multitasking confirmed as the literal opener of coding
   interview 1; keep as high priority.
5. Loop item 2 (C++ fluency) — confirmed as the explicit "main hard skill," both coding
   rounds graded on it directly.
6. Loop item 8 (deep Body Systems domain/industry knowledge) — deprioritize per the
   explicit de-scoping above; light background pass only.
7. Behavioral prep — now has a confirmed real prompt shape ("critical feedback" story) to
   rehearse specifically, sourced from school/project context.

Added as Zoox loop study plan item 8 in `~/Desktop/interview_prep/Zoox_BodySystems/START_HERE.md`.

## Update 2026-09-25 (later same day) — Interview loop SCHEDULED

Confirmation email received from Michelle Kim (Recruiting Coordinator), same day as the prep
call with Mikel. Split over 2 days, virtual via Zoom.

**Thursday, October 1, 2026 (CT):**
- 1:30–2:00 PM — Presentation
- 2:00–3:00 PM — Break
- 3:00–3:45 PM — Interview: Charlie Bulkeley (Staff Firmware Engineer) + Nehal Solanki
  (Manager, Firmware)
- 3:45–4:00 PM — Break
- 4:00–4:45 PM — Interview: Bo Gao (Staff Firmware Engineer)

**Friday, October 2, 2026 (CT):**
- 1:15–2:00 PM — Interview: Julio Velazquez (Senior Electrical Design Engineer)
- 2:00–3:00 PM — Break
- 3:00–4:00 PM — Interview: Felix Tsao (Software Engineer) + Victor Wang (Senior Firmware
  Engineer) — CoderPad: `app.coderpad.io/CM44XJ4W`
- 4:00–5:00 PM — Interview: John Tagliamento (Staff Firmware Engineer) + James Kim (Senior
  Firmware Engineer) — CoderPad: `app.coderpad.io/NXGMGPKT`

**Logistics:** Zoom link with passcode provided in the email; enter waiting room, interviewer
admits. If waiting >5 min past start, contact recruiting coordinator. NDA must be signed
before interviewing (name + signature). No GenAI tools permitted during the interview unless
explicitly stated otherwise. Candidate portal: `https://mloop.in/s/axMjC2EFthE`.

**Mapping to the 6-session structure confirmed on the prep call (presentation + 5 interviews):**
this schedule has exactly 6 blocks (1 presentation + 5 interviews), consistent with Mikel's
description. Round content wasn't labeled by name in the email, so the specific
mapping (which slot is RTOS/C++ coding, which is datasheet/bitwise coding, which is system
design/door control unit, which is the hiring-manager round, which is math/problem-solving) is
inferred, not confirmed:
- Thu 3:00 (Charlie Bulkeley + Nehal Solanki) and Thu 4:00 (Bo Gao) — most likely the two
  1-hour technical/coding rounds (not marked CoderPad in the email, but likely still live
  coding — go in prepared either way).
- Fri 1:15 (Julio Velazquez, Senior Electrical Design Engineer) — likely the
  hardware/datasheet-leaning or cross-functional technical round, given his electrical title.
- Fri 3:00 (Felix Tsao + Victor Wang) and Fri 4:00 (John Tagliamento + James Kim) — both
  explicitly marked with CoderPad links, confirmed live-coding rounds.
- Beau (hiring manager, named in the prep call) does not appear by name on this schedule —
  either one of the above panels includes him unlisted, or he's presentation-audience only.
  Not confirmed; don't block prep on resolving this.
- **Action for Justin:** ask a clarifying "what's the focus of this round?" in the first
  minute of each session rather than assuming from the interviewer's title alone — directly
  exercises the "ask clarifying questions first" habit Mikel flagged as the single
  most-emphasized cross-round behavior.

Full schedule and interviewer mapping also recorded in
`~/Desktop/interview_prep/Zoox_BodySystems/START_HERE.md`.

### Next action
Study timeline needs to be rebuilt anchored to these real dates (was previously built on a
placeholder deadline). See `~/Desktop/interview_prep/Zoox_BodySystems/study_timeline_2026-09-25_to_09-28.md`
— supersede once the new date-anchored version is agreed with Justin.

## OUTCOME — REJECTED ❌ (2026-10-07)

- **Final result:** Rejected 2026-10-07 (Body Systems req). Pipeline closed, no action pending.
- Justin emailed Mikel Pounds asking for a reason; **no reply as of 2026-10-07.**
- Earlier on this req: Drive Systems passed on by the hiring manager 2026-09-15 (CAN/LIN was a
  hard requirement there), redirected to Body Systems (CAN/LIN only a bonus), recruiter screen
  2026-09-09, technical screen 2026-09-22 (cleared), loop scheduled 2026-10-01/02.
- **Not recorded in this log:** whether the loop was completed, how each session went, and which
  stage the rejection came after. Fill these in if known.
- **Cause: unknown.** The only explicit feedback on file is from the 2026-09-22 screen: the
  testing/validation gap (integration/unit/automated testing, the team-handoff question) and
  the black-box-function fumble attributed to nerves. That feedback did not block advancing, so
  it cannot be treated as the reason for this rejection. Don't score it into the patterns above.
- If Mikel resurfaces with another req, log it as a new outcome chain (job-automator F1).

---

# DOCKWARE — IN PROGRESS

**Role:** Robotics Engineer (also posted as Software Operations Engineer — same JD body copy,
confirmed to be the same underlying opening via Bhavana B Rao, a Dockware robotics engineer
contacted via LinkedIn cold outreach). Applied via Josh Hathaway (CTO) referral path per
Bhavana's suggestion, plus a separate cold email to Conor Godfrey (Founder & CEO).

**Company context (from the call):** Three founders (2 ex-SpaceX, 1 ex-State Department),
started January 2025. Products: Dockware Scan (mobile app, original product), Vision
(ceiling-mounted computer vision sensor robots — 2 cameras + LiDAR + zoom camera, pitch/yaw
only, no translation, magnetically mounted to metal rafters), and an unreleased product
called Portal (light-pole camera rigs reading barcodes/damage on trucks passing through).
Mission: "the error free dock." Vision team is 5-6 people; Seth is the only non-robotics-
engineer on it (he's the sole EE/hardware lead, became "Product Responsible Engineer" for
Vision as the team grew).

## Round 1 — Phone Screen (Seth Hart, 2026-09-25)

**Interviewer:** Seth Hart — sole electrical/hardware engineer at Dockware, now also acting
as Product Responsible Engineer (PM-equivalent) for the Vision product line. Casual, friendly
tone throughout, consistent with Bhavana's advance warning that the first call wouldn't be
deeply technical.

**Format:** ~30 min phone call. Rapport/logistics questions (location, willingness to
relocate to Tulsa, background) → company/role overview → resume deep-dive on COFFIN capstone
→ one ML definition question → one open-ended system-design scenario (real unsolved company
problem) → why-Dockware → full-time-experience gap check → startup-workload check → candidate
questions → close.

**Resume deep-dive — COFFIN capstone, 11 integration failures:**
Seth explicitly asked to walk through the 11 integration failures named on the resume bullet,
what caused them, what the fix was, and how recurrence was prevented. **Answered generically**
— framed it as one overall "hardware not in sync with software" issue, with fixes described
as (1) quantizing the model for lower latency, (2) adding concurrency (separate threads for
robot control vs. AI), (3) adding delay between steps to reduce servo speed. This is plausible
and not wrong, but did not name any of the actual 11 specific failure→fix pairs (ToF range
gate for false positives, servo attach-before-write ordering, I2C mux retry logic, threaded
camera fix for stale frames, timeout fallback for grip sensor flakiness, etc.) despite having
been given that exact list in pre-call prep. **Lesson for next resume-bullet callback
question: answer with the named failure and the named fix, not a generalized summary** — this
is the same shape of gap as the TBC reasoning-structure loss (reaching for a general framing
instead of the specific, prepared detail).

**ML question:** "What is precision?" Answered "true positives over number of detections
made" — this is the textbook-correct definition (TP / (TP+FP), i.e. TP / all predicted
positives). Seth restated it as "true positives over all positives," which is closer to the
definition of recall (TP / (TP+FN), i.e. TP / all actual positives) — not corrected live, and
not worth revisiting with him, but noted here so the record is accurate: Justin's original
answer was right.

**System-design scenario — real, unsolved company problem (this is the standout moment of the
call):** Staging area is a fixed 40ft × 60ft rectangle, four Vision robots mounted at the
corners (ceiling-mounted, fixed position, pitch/yaw only — no translation, confirmed after
Justin initially assumed ground-mounted). Freight arrives via truck, is placed with 2"×2" QR
codes (~60% top-facing, ~40% on other/no-label sides), and can leave unpredictably any time
from 1 minute to 1 hour later via forklift, in random order. Goal: detect 100% of labels
before the freight leaves. **Justin's approach:** asked clarifying questions before answering
(mount restrictions, camera placement freedom) — correctly pivoted after learning the mount
constraint — proposed all-four-side coverage plus tracking the human labeler's walking pattern
to cluster probability of nearby pallets having labels, prioritizing side coverage before top
coverage. Seth confirmed there's no solved answer and the team is actively iterating (more
robots in the rafters vs. clustering/tracking vs. speeding up the zoom-scan cycle so tracking
matters less). **This is a real open problem — good to have a sharper, more developed answer
ready if it resurfaces in a later round**, since it's clearly core to what Dockware is
struggling with in production right now.

**Other answers:** Why Dockware — systems-level ownership (hardware + perception + robotics
together) over narrow scope at a big company, deliberately targeting non-tiny/non-huge fast-
growing robotics companies. Full-time experience gap — handled honestly and without defensiveness
(just graduated); Seth explicitly said "not throwing rocks." Startup workload/ownership
question — handled well (growth-mindset framing, not scared of the responsibility).

**Weak spot — candidate questions:** re-asked substantially the same QR-labeling problem that
had just been discussed for ~10 minutes, rather than a fresh forward-looking question. Not
harmful (Seth answered warmly and gave more detail on the team's current approaches: more
robots in the rafters, labeler-tracking, speed-based scan cycles), but a wasted slot — **have
1-2 genuinely new questions ready for the next round** (e.g. team roadmap, how success is
measured on the Vision line) rather than reusing material already covered live.

### Outcome notes
- [x] Phone screen completed 2026-09-25, ~30 min, no red flags raised on either side
- [ ] Seth to discuss internally; will follow up via text/WhatsApp on Justin's phone number
- [ ] **Action:** if no reply by Tuesday 2026-09-29 close of business, Seth explicitly invited
      Justin to text/WhatsApp him directly as a nudge — this is pre-authorized, not a cold
      follow-up. Calendar reminder set for 2026-09-29 5:00 PM Central.

### Next prep priority
1. Rehearse the COFFIN 11-failures answer as explicit failure→fix pairs, not a generalized
   summary — this exact resume line will likely resurface in a technical round.
2. Develop a sharper answer to the QR-staging-area problem in case a later round returns to
   it — Seth confirmed this is a live, unsolved production problem, not a hypothetical.
3. Prepare 2 fresh, forward-looking candidate questions for the next round (avoid repeating
   material already covered).
