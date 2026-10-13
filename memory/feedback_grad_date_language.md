---
name: feedback-grad-date-language
description: "Check current date vs May 2026 grad date before using \"graduating\" vs \"graduated\" in resumes, emails, and DMs"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 310d4370-4778-4b72-b290-2cf5c6839adb
---

Justin's M.S. graduation date is May 2026. Any resume, cold email, or DM copy must compare the current session date against that date before choosing verb tense:
- Before May 2026 → "graduating May 2026" / "expected May 2026"
- May 2026 or later → "graduated May 2026" (past tense)

**Why:** Caught on 2026-07-01 when a drafted outreach email for the [[project_sandisk_test_engineer]] application said "I graduate ... in May 2026" — wrong tense since May 2026 had already passed. This is a recurring risk because the degree/grad date is hardcoded as a fact in ~/.claude/CLAUDE.md and in master_profile.json's summary_pool, so it's easy to copy that phrasing verbatim without checking today's date.

**How to apply:** Whenever job-automator (fit analysis summary, resume tailoring B3, or outreach drafting C4) generates text referencing the RIT M.S. graduation, cross-check the current date from context before writing "graduating" vs "graduated". Applies to resume summaries, email/DM bodies, and the "Message to Hiring Team" application-field drafts. Also check the "Dec 2025 - July 2026" eligibility window language in JDs the same way — once past July 2026, phrase differently (e.g., "graduated within the eligibility window" rather than restating the window as future).
