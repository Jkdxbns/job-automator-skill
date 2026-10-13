---
name: feedback-outreach-research
description: "Recruiter response research (2026) — shorter emails, one ask, real hooks only, follow ups enforced"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 310d4370-4778-4b72-b290-2cf5c6839adb
---

Research done 2026-07-01 across recruiter blogs, an r/tech recruiter AMA writeup, and outreach survey data (couldn't access raw Reddit threads directly, this environment can't fetch reddit.com) converged on:

1. Emails perform best at 50 to 125 words, definitely under 200. The job automator skill previously targeted 200 to 280 words, which is longer than what gets replies. Now set to 120 to 170 words in [[feedback_outreach_style_rules]] territory.
2. Lead with who you are and the specific role in the first sentence, not buried in paragraph two.
3. One clear ask per message. Stacked asks (connect and referral and more roles) measurably hurt reply rates.
4. Generic "your recruiting background made you a good person to reach out to" style lines are NOT real personalization, they read as filler since they apply to any recruiter. Real hooks: a specific past employer overlap, a specific post, a specific shared detail from their actual profile. If no real hook exists, drop the hook line rather than fake one.
5. Fit must be stated explicitly against the JD's minimum qualifications, not left for the recruiter to infer.
6. Follow ups lift reply rates 50%+ but most candidates (including Justin, per the outreach log audit on 2026-06-30) log a followup_date and never actually send anything. Skill now has a C7 step requiring a stale followup scan at the start of each session.

**Why:** User asked for research into what recruiters actually want after reviewing a drafted Sandisk email, specifically pointing out the generic "recruiting background" hook line.

**How to apply:** Already folded into ~/.claude/skills/job-automator/SKILL.md (C2 hook rules, C4 length/ask rules, new C7 follow up enforcement step). See [[feedback_outreach_style_rules]] for the hyphen/numbers/plain language rules from the same session, and [[project_sandisk_test_engineer]] for the specific application this was applied to.
