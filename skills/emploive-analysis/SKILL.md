---
name: emploive-analysis
description: >-
  Turn an Emploive job list into one Claude Code agent per job, each in its own tmux session
  shown in its own titled Ptyxis tab, each running the job-automator fit analysis (and
  "tailor resume" when the scores clear the gate), then report a compact table, and automatically rename + close the rejected ones (blocked, or
  initial match below 40). Use when I
  paste an emploive.com/home?... URL, or say "emploive", "analyze emploive jobs", "run
  emploive list", "go through the 2d jobs", "open each job in its own tab", "one session per
  job". Default scope is jobs posted 2d ago. Skips blocklisted companies (Anduril, Lockheed Martin, SpaceX, NASA, Actalent, US-citizen-only federal/defense). Do NOT use for a single pasted JD or one job
  URL (that is plain job-automator), or for 50+ jobs where only a verdict table is wanted
  (use batch-delegate).
---

# Emploive → one tab, one tmux session, one agent per job

I'm already logged in to Emploive in Chrome. Every job ends up in its **own named, resumable
Claude Code session**, shown in its **own terminal tab** so I can click between analyses and watch.
I am only the orchestrator: I open things, send the job link, and copy the outcome into a table.
Nothing else. No user setup is needed; I create the tmux sessions and tabs myself.

**Stop after the requested step.** Never chain into outreach, mark-submitted or recruiter
drafts. Ask before opening more than a handful of sessions (global rule: no unasked fan-out).

## How I'm invoked, and what the arguments mean

Usage: `/emploive-analysis "latest 2 jobs"`, `/emploive-analysis "posted < 24 h"`,
`/emploive-analysis "posted <= 2d"`. The skill alone creates the tmux sessions and tabs and manages
every agent; I never open tmux myself.

**Which Emploive URL to use** (first match wins):
1. A URL I gave explicitly: `URL: "<url>"`, `-url <url>`, `--url=<url>`, or an `emploive.com/home?...`
   link pasted anywhere in the prompt. Use it exactly as given.
2. Otherwise the **default URL** below (my saved filtered search; also kept in
   `references/emploive_url.txt`). Say which one I'm using in the one-line interpretation.

```
DEFAULT_URL="https://emploive.com/home?role_type=%5B%22Full-Time%22%5D&position_type=%5B%22AI+Engineer%22%2C%22Software+Engineer%22%2C%22Firmware+Engineer%22%2C%22Machine+Learning+Engineer%22%2C%22Robotics+Engineer%22%2C%22Electrical+Engineer%22%2C%22Systems+Engineer%22%2C%22Controls%2FAutomation+Engineer%22%2C%22CS%2FSWE%2FML+Research%22%2C%22Network+Engineer%22%2C%22QA%2FTest+Engineer%22%2C%22Solutions+Architect%22%5D&experience_level=%5B%22New+Grad+%280-1+YOE%29%22%2C%22Junior+%281-2+YOE%29%22%2C%22Mid+Level+%282-5+YOE%29%22%5D&continent=%5B%22Europe%22%5D&country=%5B%22United+States%22%2C%22United+Kingdom%22%5D&other=%5B%22AI%22%2C%22C%22%2C%22C%2B%2B%22%2C%22Hardware%22%2C%22Embedded+Systems%22%2C%22Machine+Learning%22%2C%22PyTorch%22%2C%22Python%22%2C%22Robotics%22%5D&title_keywords=%5B%22firmware%22%2C%22embedded%22%2C%22robot%22%2C%22perception%22%2C%22autonom%22%2C%22machine+learning%22%2C%22computer+vision%22%2C%22deep+learning%22%2C%22edge+ai%22%2C%22cuda%22%2C%22inference%22%2C%22ML+engineer%22%2C%22AI+engineer%22%2C%22rtos%22%2C%22real-time%22%2C%22driver%22%2C%22linux%22%2C%22systems+software%22%2C%22controls%22%2C%22mechatronics%22%5D"
```

The list is newest-first. Each row's right-most cell is its age label (`37m`, `1h`, `1d`, `2d`, ...).

| Argument | Rows I take |
|---|---|
| `latest N jobs` | the top N rows, whatever their age |
| `posted < 24 h` | every row whose label is in minutes or hours (`m` / `h`), stopping at the first `1d` |
| `posted <= Nd` | every row up to and including the last `Nd` label (`<= 2d` = through the `2d` block) |
| nothing given | default to `posted <= 2d` |

Scroll the list container until the first row *past* the boundary appears (for `<= 2d`, the first
`3d`; for `< 24 h`, the first `1d`), so I know I have the whole block.

- **Volume rule:** up to **10** jobs run on my invocation alone. If the argument matches more than
  10, say how many it matched and ask before opening more (global rule: no unasked fan-out), then
  work in batches of 10, never more than ~10 agents running at once. Each is a full session on my model.
- 50+ jobs where I only want verdicts: suggest `batch-delegate`, then open sessions just for Can Try
  or better.
- State the interpretation in one line before starting (e.g. "posted < 24 h: 14 rows, taking the first 10").

## 1. Collect links (Claude in Chrome, the only browser work I do)

Load the Chrome tools in one ToolSearch call, call `tabs_context_mcp` (`createIfEmpty: true`; the
tab group is often gone between sessions), work in a **new tab**. Navigate to the resolved URL, wait
until rows appear (skeleton rows show first, ~10s).

The list scrolls inside a container, not the page. To reach an age block, scroll it with JS:

```js
const sc=document.querySelector('[class*="_listScroll_"]');
for(let i=0;i<40;i++){ sc.scrollTop=sc.scrollHeight; await new Promise(r=>setTimeout(r,1200));
  const hit=[...sc.querySelectorAll('*')].find(e=>e.children.length===0 && e.textContent.trim()==='2d');
  if(hit){hit.scrollIntoView({block:'center'});break;} }
```

Rows are newest-first, so the 2d block sits between the 1d and 3d rows. `outerHTML` and query
strings are blocked in the JS tool; return text only.

**Company blocklist, applied first.** Before clicking any row, take the company name shown under
each title and run it through the blocklist:

```bash
python3 ~/.claude/skills/emploive-analysis/scripts/filter_companies.py "Company A" "Company B" ...
```

`BLOCK` rows are dropped on the spot: I don't click them, don't read their Apply link, don't open a
tab, a session or a JD, and nothing gets analysed. The list is `references/blocked_companies.txt`
(Anduril, Lockheed Martin, SpaceX, NASA, Actalent, and US-citizen-only federal agencies and defense primes);
edit that file to change it. Blocked rows don't count toward "latest N": skip them and take the next
rows, so `latest 3` still yields 3 jobs. Say in one line what was skipped and why (e.g. "skipped 2
blocklisted: Anduril x2"). A role from an unlisted company that turns out to need a clearance is
still caught by the agent's own hard-block check.

For each target row: click it to open the detail panel, then `find` ("Apply link in job detail
panel (href) and the panel's job title") and check the title matches the row you clicked (the list
can shift). **Never click Apply.** If `find` returns a truncated href, ask for "the complete full
href". Keep per job: company, role title, the Apply href with any trailing `/application` removed
(that suffix is the form, the description is on the parent page), and the location Emploive shows
(it can differ from the ATS page, e.g. Munich vs Zurich; the agent trusts the ATS page).

I do **not** open the ATS pages, read descriptions, save JD files or paste text. job-automator
fetches the JD from the URL itself (`scrape_jd.py`, then Claude in Chrome page-text extraction,
then asks for a paste), so each agent does that for itself. Close my Emploive tab when done.

## 2. Orchestrator only

I do not run `score_fit.py`, `render_report.py`, `pdfinfo`, python readers or any analysis command,
I never open `fit.json`, exports or logs myself (the results script does, section 4), and I never answer a question an agent raises. Every fetch, scoring and
tailoring step happens inside the agent, driven by the `job-automator` skill (which I never edit).
Why: the analysis lives in that job's own resumable session, and my context stays small.

## 3. One tmux session + one Ptyxis tab per job

Session name = tab title = `<Company>_<Role>`, company first, hyphenated, no spaces/dots/colons
(tmux forbids `.` and `:`), e.g. `Cricut_Firmware-Engineer`. Tabs always open in
`/home/jkdxbns/Desktop/jobs` (`-d`). Never touch any session I didn't create (the user's own and old
`jobs-0` are off limits). It all runs visibly: the tab attaches the moment the session exists, so
there is no hidden background server.

**Use the bundled scripts, never hand-written tmux/ptyxis commands.** They exist because the inline
version cost ~8 tool calls per job (each re-reading the whole conversation) and is where mistakes came
from: a wrong `send-keys` target, and a prompt typed into a bare shell. Each script is one call:

```bash
S=~/.claude/skills/emploive-analysis/scripts
$S/launch_agent.sh NAME "<apply url>"     # tab + tmux session + claude-p + /model Sonnet + /effort medium + link
$S/wait_idle.sh --timeout 600 NAME1 NAME2 # returns when every agent has finished
$S/send_to.sh NAME "tailor resume"        # type into an idle agent; refuses if busy or not running claude
```

- `NAME` = tab title = tmux session = `<Company>_<Role>`: letters, digits, `_`, `-` only, company first
  (e.g. `Cricut_Firmware-Engineer`). Tabs open in `/home/jkdxbns/Desktop/jobs`. Never touch a session I
  didn't create (the user's own and old `jobs-0` are off limits). Everything is visible: the tab
  attaches the moment the session exists, so there is no hidden background server.
- `launch_agent.sh` starts `claude-p` (the user's `~/.bashrc` function: paid-subscription models, runs
  `--dangerously-skip-permissions`, so no prompts stall it), confirms Claude is really running before
  typing anything (it prints `ERROR claude did not start` and types nothing otherwise), pins
  `/model Sonnet` and `/effort medium` so analysis never runs on Fable or Opus, then sends **only the
  Apply link**. Open jobs one call after another so tab titles don't race.
- **Send nothing but the link.** A bare URL is all `job-automator` needs: it routes to fit analysis,
  fetches the JD itself, makes its own job dir, runs the prescreen, and stops after the A7 report. No
  instructions, formats, job dirs or location notes; the agent trusts the ATS page over Emploive's.
- `wait_idle.sh` counts an agent as done only after it was seen busy and is quiet on two checks 5s
  apart (it can go quiet while a tool runs). `TIMEOUT still running: ...` means some are still working;
  report them as `running`, don't poke them.
- If a session asks me anything (a redraft, a "Tailor anyway?" popup), leave it and flag it to the user.
- Typing by hand is allowed only for what the scripts don't cover; if I must, the tmux target is
  `-t "=NAME:"` (exact match with trailing colon; `-t "=NAME"` fails with `can't find pane`).

**Why I never read scores off the screen:** Claude Code draws in tmux's alternate screen, which keeps
no scrollback (`history_size=0`). A report longer than the pane (~46 rows) scrolls its `match` line
out of reach, which is how two Amazon scores went missing and the tailor step was skipped. So I never
scrape the screen. One script call reads the numbers from the agent's own files (see section 4).

**Tailor gate: apply it, never skip it.** The script's `TAILOR:` line lists every session with match
> 60, semantic > 40, no hard block, and no resume yet. Run `$S/send_to.sh NAME "tailor resume"` for each, wait with `wait_idle.sh`, then re-run the script so `resume status` becomes `generated`. If a
score can't be read, say so and stop on that row; never guess a value and never leave the gate
unapplied without telling the user. If a session asks me anything (a redraft, a "Tailor anyway?"
popup), leave it and flag it to the user.

## 4. Report

**Always answer with a table.** One call returns everything; paste its table into the reply:

```bash
python3 ~/.claude/skills/emploive-analysis/scripts/results_table.py NAME1 NAME2 ...
```

It prints the table, then `TAILOR:` (sessions to type `tailor resume` into), `REJECT:` (sessions to
rename + close, section 5) and `NOTES:` (one line per flagged session). I read only that output, never
an export, a screen or a log. Run it when the agents finish and again after tailoring.

Where it gets the numbers, first that works (a busy session is `running` and never touched):
1. **`fit.json`** — it finds the agent's job folder from the session log (which records `JOB_DIR`) and
   reads `~/Desktop/jobs/<job>/logs/fit.json`: match, APPLY verdict, semantic %, seniority. Resume
   status comes from `resume_*.pdf` and `pdfinfo` (`generated` only at `Pages: 1`). Nothing is typed
   into the session. This is exact and costs no tokens.
2. **The session log** (`~/.claude/projects/*/<id>.jsonl`; the name is its `custom-title` record). Used
   when there is no `fit.json`: a job stopped by the pre-screen hard block leaves an empty folder.
   Still no typing.
3. **`/export`** typed into the idle session, parsed, and the export file is **deleted after use**.
   Only if the first two both fail.
4. The visible screen, last resort.
A session renamed `REJECTED` loses its name in the log, so it can't be looked up afterwards; that's fine
because rejected jobs are never reported again.

| session_name | match_score | semantic | verdict | resume status |
|---|---|---|---|---|

- `verdict` is exactly one of: **`apply`** (APPLY Yes), **`can-try`** (APPLY Can Try),
  **`blocked`** (the `⛔ HARD BLOCK` banner; add the matched phrase in the note under the table).
  Also possible: `no` (APPLY No), `error` (JD fetch or permission failure), `running` (still
  working), `waiting` (stopped without a verdict, e.g. on a question).
- `match_score` and `semantic` come from the `KEYWORD READ` / `SEMANTIC READ` boxes; `N/A` when
  blocked or the semantic read didn't run (it only runs at match >= 60).
- `resume status`: `N/A`, `generating...` while tailoring runs, `generated` once the PDF shows
  `Pages: 1`.

Anything an agent flags that needs a human decision (a soft sponsorship note such as "may not
interview without PR", a redraft question, a seniority mismatch, the blocked reason) goes in one
short line under the table. Do not resolve it myself. If the script prints a wrong or `waiting` row,
look at that session's screen before reporting; don't guess.

## 5. Reject sweep (automatic, part of every run)

Runs on its own at the end of every run, right after the table. Do not ask first; the thresholds
below are the user's standing rule.

**REJECTED = `blocked`, OR initial `match_score` below 40.** Judge by the keyword match only, never
the semantic score. `error`, `running` and `waiting` rows are never rejected; leave those tabs open.
A job at exactly 40 or above stays open (APPLY Can Try territory). Anything that cleared the gate and
was tailored stays open too.

```bash
S=~/.claude/skills/emploive-analysis/scripts
for n in <names on the REJECT: line>; do $S/reject_session.sh "$n"; done
```

`reject_session.sh NAME` does, in order: renames the Claude session with `/rename REJECTED` and
confirms it took; sets the terminal **tab title to `REJECTED`**; waits ~3s so the new title shows;
then closes the tmux session, which closes its tab. (`Ctrl-b x` then `y` only kills a pane and
needs a keystroke; `kill-session` does the same for this one-pane session and is reliable.) It
refuses to act if the session is still running or the rename isn't confirmed.

Report the table first, then one line naming the rejected sessions that were closed. The closed
sessions stay resumable by name (`/resume`), but they will all read `REJECTED`; the note under the
table is what records which job each one was.

## Known pitfalls

- **Scores differ between sessions.** The same role scored 53.6% in one session and 64.3% in
  another because DSP was classified adjacent vs have, which flipped the 60 threshold. The DSP
  instruction in the prompt exists for this; mention it if a result looks borderline.
- **EU/UK/Switzerland roles are not hard blockers** for me (willing to relocate, applying in
  parallel). A `location: conflicts with relocation constraints` flag on these is noise.
- Sponsorship/ITAR/clearance blocks still apply everywhere; the agent's pre-screen handles them.
  Soft wording ("may elect not to interview candidates without citizenship or PR") can slip past
  as a non-blocker, so surface it under the table for me to judge.
- Claude in Chrome can deny page reading per site (`Permission denied for reading page content on
  this domain`). That happens inside the agent, which says so on screen; report it as `ERROR:`, and
  don't work around it.
- Duplicate Emploive rows (same Apply href twice, e.g. Anduril) are one job: dedupe, say so, and
  don't double-run it.
- Ptyxis `--tab` lands in the active Ptyxis window. A `select-window` inside `-x` is ignored,
  which is why this design uses one session per tab instead of window groups.
