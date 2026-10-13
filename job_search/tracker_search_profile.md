# Job Tracker — Canonical Search Profile
_One search config, pasted into every alert tool so they all hunt for the same roles._
Derived from `master_profile.json`. Scope: **USA only, open to relocate anywhere.** Needs **H-1B sponsorship** (F-1 OPT).

---

## Target job titles (OR these)

**Embedded / Firmware**
- Firmware Engineer / Firmware Engineer I / Firmware Engineer II
- Embedded Software Engineer / Embedded SDE
- Embedded Systems Engineer
- Firmware Developer

**Robotics / Perception**
- Robotics Software Engineer
- Robot Perception Engineer / Perception Engineer
- Robotics Engineer
- Autonomy Engineer
- Controls Engineer (robotics)

**ML / Edge AI Systems**
- Machine Learning Engineer / ML Engineer
- ML Systems Engineer
- Edge AI Engineer
- Deep Learning Engineer
- Computer Vision Engineer
- Inference / Model Optimization Engineer
- GPU / CUDA Software Engineer

**New-grad qualifiers to add where the tool allows:** "New Grad", "University Graduate", "Early Career", "Entry Level", "I", "II".

---

## Keywords (skills from resume)
`C`, `C++`, `Python`, `CUDA`, `TensorRT`, `embedded C`, `bare-metal`, `RTOS`, `FreeRTOS`, `STM32`, `Cortex-M`, `firmware`, `ROS`, `ROS2`, `MoveIt`, `perception`, `computer vision`, `OpenCV`, `YOLO`, `Jetson`, `edge AI`, `inference`, `quantization`, `model optimization`, `PyTorch`, `UART`, `I2C`, `SPI`, `sensors`, `robotics`

---

## Exclude terms (kill the noise + the roles you can't take)
- Seniority you don't match: `Senior`, `Sr.`, `Staff`, `Principal`, `Lead`, `Manager`, `Director`, `5+ years`, `7+ years`, `10+ years`
- Hard-blockers for F-1 OPT: `US Citizen`, `citizens only`, `Green Card required`, `security clearance`, `Secret`, `TS/SCI`, `ITAR`, `must be a U.S. Person`
- Off-target: `Intern` (you want full-time), `Sales`, `Recruiter`, `Marketing`, `Manager`, `Technician`

---

## First2Apply — natural-language AI filter (paste verbatim)
> Show full-time entry-level or new-grad software roles in embedded/firmware, robotics/perception, or machine-learning/edge-AI, using skills like C/C++, Python, CUDA, embedded C, RTOS, ROS, computer vision, or model optimization. Exclude senior/staff/principal/lead/manager roles, internships, and any role requiring US citizenship, a security clearance, or ITAR/US-person status. USA locations only; remote is fine.

---

## Sponsorship
Wherever the tool supports it (Notify.careers does), turn **ON H-1B / visa-sponsorship filtering**. This front-loads the same hard-gate your fit-analysis already enforces.

---

## Tip: split by family
Where a tool allows multiple saved searches, make **three** (Embedded, Robotics, ML/Edge-AI) instead of one giant OR — cleaner alerts, easier to mute a family that's too noisy.

---

## Configured tracker setups (as built)

### Notify.careers (PRIMARY, paid) — configured 2026-07-18
- **Basic tab:** Emails ON · Frequency **Real-time** · Fields = **AI & Machine Learning, Electrical Engineering, Hardware Engineering, Software Engineering** (no Robotics/Embedded field exists — EE+HW+SW is the catch-net for firmware/robotics; drop Hardware Eng first if hardware-noisy) · Experience Levels = **Entry Level/New Grad + Junior** (Internship unchecked).
- **Posting tab:** Countries = **United States** · Locations empty (all US, relocate) · Workplace Type empty (all) · Contains/Doesn't-Contain keywords empty · Minimum Salary empty · **Salary Not Found = ON**.
- **Company tab:** **Visa Sponsorship = ON** (the key setting — H-1B sponsors only; front-loads the F-1 OPT gate; caveat: works off H-1B filing history so may miss would-sponsor startups) · all other company filters (IPO, funding, employee count, industries, HQ, year founded) left empty.

### Google Alerts (startup funding/launch signals) — configured 2026-09-17
Purpose: catch 1-10 person startups *before* they even have a careers page, via funding/launch
announcements — not a job-board scraper (that's Notify.careers/RefereeAI's job). No sponsorship
filter (tiny startups rarely have H-1B history; screen manually). All delivered to
jmascarenhas1998@gmail.com, "At most once a day".

1. `("embedded software engineer" OR "firmware engineer") ("seed funding" OR "series a" OR "raises $")`
2. `("robotics engineer" OR "perception engineer" OR "autonomy engineer") ("seed round" OR "series a" OR "raises $")`
3. `("machine learning engineer" OR "edge ai engineer" OR "computer vision engineer") startup ("seed" OR "series a" OR "raises $")`
4. `("RTOS" OR "bare-metal" OR "embedded C") startup ("seed funding" OR "series a" OR "raises $")` — Sources: News, Blogs
5. `("embedded software engineer" OR "firmware engineer") ("we're hiring" OR "is hiring" OR "join our team") startup`
6. `("embedded" OR "firmware") ("stealth startup" OR "emerges from stealth") hiring`
7. `("embedded" OR "firmware" OR "hardware engineer") ("YC W26" OR "YC S26" OR "Y Combinator") hiring`
8. `("hardware startup" OR "robotics startup" OR "IoT startup") ("seed" OR "series a" OR "raises $") embedded`

### Wellfound + YC Work at a Startup — NOT yet configured (2026-09-17)
Justin has both accounts already; not automated (no login on the automation browser profile).
To do manually: set saved search/alerts on both to the same 3 role families above, no sponsorship
filter, Wellfound "actively hiring" filter on if available.

### Emploive (FREE, testing) — configured 2026-07-18, **reconfigured & CLOSED 2026-09-18**
- Position Types (8): CS/SWE/ML Research, Electrical Engineer, Firmware Engineer, Machine Learning Engineer, Software Engineer, Systems Engineer, Robotics Engineer, **Controls/Automation Engineer** (dropped both UI/UX — those forwarded to a friend separately).
- Location = USA · Role Type = full-time · Experience = **Junior + New Grad** · Email delivery = **6-hour periodic** (backup tool, batch & evaluate).
- Job Title keywords: originally empty; a keyword set was added 2026-09-18. **Justin confirmed the tracker
  is configured and this item is closed.** The exact final keyword list was not captured in that session
  (an earlier browser attempt was lost before saving), so this file does not mirror it — read the live
  settings at https://emploive.com/trackers if the list is ever needed.
- Coverage caveat measured 2026-09-17: title keywords are OR-matched ("matches any job whose title
  contains one of these keywords"), and the then-current set caught only ~60% (220/361) of his Yes/Can-Try
  roles. Widen the keyword list rather than the position types if alert volume looks thin.
- No visa/sponsorship filter exists on Emploive — fit-analysis pipeline still gates those.

### Emploive "Unified Keywords" tracker — created 2026-09-28
Keyword-driven, everything optional left unspecified (Emploive forces Position type, Location, Role type).
- Role type = Full-Time · Locations = United States, United Kingdom, Europe · Experience/Work model/Company/Industry/Funding/Size/Tags = unset · Notifications = Real-time · reposts not included.
- Position types (8): AI Engineer, Software Engineer, Firmware Engineer, Machine Learning Engineer, Robotics Engineer, Electrical Engineer, Systems Engineer, Controls/Automation Engineer.
- Job title keywords (20, OR-matched substrings): firmware, embedded, robot, perception, autonom, machine learning, computer vision, deep learning, edge ai, cuda, inference, ML engineer, AI engineer, rtos, real-time, driver, linux, systems software, controls, mechatronics.
- Emploive UI: title keywords = type + Enter; position type/location/role type = manual clicks (Enter does nothing).
- Other live trackers on the account (as of 2026-09-28): "tracker_v1" (formerly My Tracker; CS/SWE/ML Research + Controls, New Grad/Junior/Mid, tag-based) and "New Grad" (9 position types, entry-level title keywords, tags).
