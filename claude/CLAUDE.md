# Claude Code — Global Context
# ~/.claude/CLAUDE.md

---

## Who I Am

Name     : Justin Mascarenhas
Degree   : M.S. Computer Engineering — Rochester Institute of Technology, Rochester NY
Graduated: May 2026
Email    : jmascarenhas1998@gmail.com
LinkedIn : https://www.linkedin.com/in/justinmascarenhas/
GitHub   : https://github.com/Jkdxbns

---

## Resume & CV Files

Always use these when any job application skill runs, unless I provide a different path.

Single source of truth : ~/.claude/skills/job-automator/references/master_profile.json
Resume LaTeX template  : ~/.claude/skills/job-automator/references/resume_template.tex

There is no stored resume.docx or cv.pdf any more, and none is needed: every resume is
generated from master_profile.json through the template, always one page. If I say "my
resume" or "my CV" without a path, read master_profile.json.

---

## Installed Skills

Custom skills live in `~/.claude/skills/`. Each skill's own SKILL.md is authoritative for
its triggers and steps — this is an index, not a duplicate spec.

- **pa** — Personal assistant for Google Workspace (Tasks, Calendar, Docs, Sheets, Drive,
  Gmail read+draft only, Forms). Follow-up reminders are always 3-minute Calendar events,
  never Tasks.
- **job-automator** — Unified job application pipeline (fit analysis, resume tailoring,
  cold outreach, mark-submitted, outcome tracking) — one skill, sub-workflow routed
  internally. Each request is ONE step; it never chains unasked. Cold email → Gmail draft, never auto-sent. LinkedIn DM → printed inline to
  copy manually.
- **delegate** — Drafts a research prompt for another model's web UI and copies it to my
  clipboard. No API keys, no scraping. LM Studio has no live web access.
- **meeting** — Local live meeting transcription + copilot for the 6DOF arm project.
  Hands action items to **pa** as Google Tasks at wrap-up.

---

## MCP Servers

- **gworkspace** (loads every session): Google Workspace, powers **pa**. Every tool needs
  `user_google_email: jmascarenhas1998@gmail.com`. Tools are deferred — `ToolSearch` first.
  Gmail send/label/filter are hard-denied (read + draft only). App is in testing mode →
  ~weekly re-consent via a read call + authorization URL.
- Project-scoped MCPs are documented in each project's own CLAUDE.md, not here.
- Also available as claude.ai connectors: **Apollo.io** (credit-metered — always surface
  the `mcp_credits` cost/balance) and **claude-in-chrome** (call `tabs_context_mcp` first).

---

## Behaviour Rules
1. Always run fit analysis before tailoring — never tailor without a fit check.
2. Never fabricate experience, metrics, skills, or projects not in master_profile.json.
3. Never send emails or DMs automatically — always show draft and wait for approval.
4. A job URL or a pasted JD (role + responsibilities/qualifications) with no other
   context means "analyze this job" — never ask "what do you want me to do?" first.
5. If resume file not found at default path, ask — do not guess.
6. Log every action to the appropriate log file.
7. Keep output concise — structured reports and drafts, not explanations of what you're
   about to do.
8. Stop after each requested pipeline step — don't auto-chain the next one because it
   looks obvious. I drive the sequence with short commands.
9. Bypassing rules is not allowed unless says the password "BYPASS".

---

## Job Posting Scraping

Most target career sites (Apple, Tesla, Rivian, AeroVect, and Greenhouse/Workday/Lever
hosted pages) are JS-rendered. Do NOT spend turns on curl/WebFetch static scrapes. Go
straight to browser-based extraction and use page-text extraction, not screenshot
scrolling. If browser extraction returns only nav/footer boilerplate, ask me to paste
the JD instead of retrying.

---

## Never Delete User Files

Never `rm` any .tex, .pdf, .docx, or resume artifact without my explicit confirmation —
move to `.trash/` instead. This is hook-enforced for Bash `rm` (`protect_resumes.py`);
that hook does NOT cover overwriting a file via Edit/Write, so still check mtime yourself
before replacing anything that looks hand-edited.

---

## Subagents

**Always ask me before spawning subagents.** Never fan out Task agents on your own, even
when the work looks parallelisable or a report recommends it. Ask, wait for my yes, and
only then spawn — every agent gets one concrete, named assignment, no placeholders.

---

## Outreach Message Rules

For LinkedIn, WhatsApp and recruiter drafts: never mention visa, OPT, EAD or sponsorship
status unless I explicitly ask. Keep to two or three short sentences, one clear ask, no
combined multi-topic messages.

## Tone & Writing Style

Voice     : First person, direct, confident
Metrics   : Always exact numbers (1.5× speedup, ~25% reduction, 78% → 97.5%)
Forbidden : "passionate about", "excited to", "leverage", "synergy",
            "I hope this finds you well", "seeking opportunities"
Resume    : Achievement-first bullets, metric or ATS keyword in every bullet
Outreach  : See ~/.claude/skills/job-automator/references/outreach_examples.md
