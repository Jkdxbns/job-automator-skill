---
name: reference_job_alert_tools
description: "Justin's job-alert tool stack (Notify.careers paid, RefereeAI free, First2Apply, Emploive) + the canonical search profile they all share"
metadata: 
  node_type: memory
  type: reference
  originSessionId: bce1115d-1116-4fc7-8dc5-43ce77805db8
  modified: 2026-09-18T02:51:08.205Z
---

Justin's real-time job-alert stack — these surface job URLs that then feed the fit-analysis pipeline ([[project_jobapplications_sheet]]).

- **Notify.careers** — PAID ($5/mo Active tier). Primary tool. Monitors 5,600+ company career pages, within-minutes alerts. Has an **H-1B / visa-sponsorship filter** (key for his F-1 OPT gate). notify.careers
- **RefereeAI** (refereeai.us) — FREE, Discord notifications, ~4 hr refresh. Despite the name it does NOT do referrals — just a career-page aggregator that links to the official apply page. Backup net. **CONFIGURED & ACTIVE 2026-07-18** — Discord user `justkiddin_haha`, H-1B Sponsor filter ON, Entry Level, Any Degree, one keyword (free limit = 1 alert/account; a 2nd free signup with a different keyword would add a family).
- **First2Apply** (first2apply.com) — **DROPPED 2026-07-18.** Was installed & running on the Fedora desktop (extracted amd64 `.deb`), but Justin abandoned it because it requires logging into LinkedIn/Indeed *inside* the third-party Electron app — not comfortable sharing job-board sessions with it. Installation fully removed; the `.deb` may still sit in ~/Downloads. Don't re-suggest it. Board coverage replaced by **first-party native alerts**: LinkedIn "Create job alert" + Indeed saved-search email alerts (his own accounts, no third party).
- **Emploive** (emploive.com) — FREE, unproven (bare landing page, no reviews). Testing only; don't pay.

**Canonical search profile** (titles + keywords + exclude terms + First2Apply AI-filter prompt) lives at `~/job_search/tracker_search_profile.md`. Scope: **USA only, open to relocate anywhere**; families = Embedded/Firmware + Robotics/Perception + ML/Edge-AI; exclude senior/staff/clearance/citizenship/intern; sponsorship filter ON. Paste the same profile into every tool to keep them in sync.

**Startup layer added 2026-09-17** (1-10 person startups, no sponsorship filter — cast wide,
screen manually; Justin's explicit call since tiny startups rarely have H-1B filing history):
- **Google Alerts (9 active)** — funding/launch-signal alerts, NOT job-board scraping (redundant
  with Notify.careers/RefereeAI for that). Full query list in `tracker_search_profile.md`. Heavily
  weighted toward embedded per Justin's "especially embedded" ask: RTOS/bare-metal, stealth-startup,
  YC-batch, and general hardware/robotics/IoT funding queries, plus the original 3 role-family
  funding alerts. "At most once a day", Sources = mostly Automatic (one set to News+Blogs).
- **AngelList is NOT a separate job board** — it split from Wellfound in Nov 2022; AngelList today
  is only venture-fund investing. **Wellfound = AngelList Talent renamed.** Don't set up "AngelList"
  as if distinct from Wellfound.
- **Wellfound + YC's Work at a Startup** — Justin already has both. NOT automated (this Chrome
  profile isn't logged into Wellfound; didn't attempt login — that's his to do). Still open: set
  saved-search/alerts on both to the same 3 role families, no sponsorship filter, "actively hiring"
  filter on Wellfound if available.
- **HN "Who is Hiring" monthly thread** — no alert exists for this (small startups post directly in
  comments, nothing else catches it). Recurring Google Calendar reminder created for the 2nd of
  every month, 3 min, zero alerts pop-ups: "Check HN 'Who is Hiring' thread (embedded/firmware/robotics keywords)".
