---
name: feedback-outreach-ask-type
description: "Match the outreach ask to the target's role (conversation vs document) and avoid run on/redundant asks"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 310d4370-4778-4b72-b290-2cf5c6839adb
---

For the single call to action in an outreach email or DM (see [[feedback_outreach_research]] for the one ask rule):

- **University/early career/mentor type recruiters** (title has "University Recruiter", "Early Careers", "Mentor", or their profile emphasizes coaching and relationship building) respond better to a **conversation ask** than a document ask. Example: "I would love a quick virtual coffee sometime, if you are open to it, to talk through how my background fits this role, whichever time works best for you." This costs the recruiter nothing to say yes to and signals genuine interest, versus a bare "take a look at my resume" ask which hands them a task.
- **Technical peers/engineers/hiring managers** are fine with a lighter document style ask, their bottleneck is reviewing technical fit, not conversation.
- Never write the ask as a run on sentence (two independent thoughts glued together with no punctuation).
- Never restate the same ask twice in a row in slightly different words in the same paragraph.

**Why:** User pushed back on a "quick look at my resume" ask for Diana Reyes Reis (Sandisk Senior University Recruiter, self described mentor and "passionate people promoter"), pointing out a conversation ask better signals genuine interest and doesn't just hand the recruiter more work. First draft of the conversation ask ("I'd appreciate a quick virtual coffee session sometime I would really like to talk through...") had a run on and restated the same intent twice; user caught it and asked for a fix.

**How to apply:** Baked into ~/.claude/skills/job-automator/references/outreach_examples.md as "The ask rule" with the Diana/Sandisk email as the canonical conversation ask template. Check target's title/profile against the recruiter type list above before choosing ask style in C4 of Sub-workflow C.
