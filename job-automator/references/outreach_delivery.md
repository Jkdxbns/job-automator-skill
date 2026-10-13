# C5–C6.5 — Delivery, logging, and the follow-up reminder

Loaded after C4 has produced the draft JSON. Covers the two delivery channels, the local tracking save, the
dual log write, and the follow-up calendar event.

---

## C5 — Branch by delivery channel

Decide from `draft.type`, which was set by what the user actually asked for: "draft cold email" → `email`,
"draft LinkedIn DM" / "draft DM" → `dm`. Both branches run C5b afterward for tracking.

### C5-DM — print the draft inline (chat is the deliverable)

There is no DM API to save to, so chat is the deliverable — the user copies it into LinkedIn by hand. Use
plain ASCII dividers (no box-drawing Unicode). Paragraphs print as flowing prose, no mid-line hard wraps. The
user copies from the saved `.txt` file (C5b), not from terminal output.

```
----------------------------------------------------------------
LINKEDIN DM  |  {full_name}  @  {company}
----------------------------------------------------------------
{greeting}

{body paragraph 1 — full unwrapped prose}

{body paragraph 2 — full unwrapped prose}

{body paragraph 3 if present}

{sign_off}
----------------------------------------------------------------
Hook      : {hook_used}
Words     : {word_count}
Follow-up : {today + followup_days} if no reply
----------------------------------------------------------------
```

### C5-Email — create a Gmail draft

C1 should already have tried to capture `target_email`. Don't block the draft on it: Gmail drafts allow a
blank recipient and the user fills it in before sending.

```
ToolSearch: select:mcp__gworkspace__draft_gmail_message
```

`draft_gmail_message` with:
- `user_google_email`: `jmascarenhas1998@gmail.com`
- `to`: `target_email` if known, otherwise omit
- `subject`: `draft.subject`
- `body`: `greeting + "\n\n" + body (paragraphs joined with \n\n) + "\n\n" + sign_off`, as one plain-text
  string
- `body_format`: `"plain"`
- `include_signature`: `false` — `sign_off` already carries Justin's name and the portfolio site; a Gmail
  signature underneath would duplicate it

Then print a **short confirmation only** — not the full body, it is already in Gmail:

```
----------------------------------------------------------------
✅ Gmail draft saved  |  {full_name}  @  {company}
----------------------------------------------------------------
Subject   : {subject}
To        : {target_email, or "(not set — add a recipient before sending)"}
Hook      : {hook_used}
Words     : {word_count}
Follow-up : {today + followup_days} if no reply
----------------------------------------------------------------
Review and send from Gmail → Drafts.
```

If `draft_gmail_message` errors (auth, quota), fall back to the C5-DM inline print so the user isn't left
without the message, and say plainly that the Gmail save failed.

---

## C5b — Save draft files (both channels)

This is the tracking copy the C6.5 reminder points to, independent of where the live draft lives.

```bash
python3 ~/.claude/skills/job-automator/scripts/save_and_print_draft.py "$JOB_DIR" '<draft_json_string>'
```

```json
{
  "draft": {
    "type": "email or dm",
    "subject": "subject line or null",
    "greeting": "Hi [Name],",
    "body": "Paragraph one as a single long string with no hard wraps.\n\nParagraph two.\n\nParagraph three if present.",
    "sign_off": "Best,\nJustin Mascarenhas\njustinmascarenhas.com",
    "word_count": 0,
    "hook_used": "...",
    "followup_days": 5
  },
  "target": { "full_name": "...", "current_title": "...", "current_company": "...", "target_email": "... or null" },
  "meta":   { "company": "...", "role": "..." }
}
```

Saves `$JOB_DIR/logs/{email|dm}_{ts}.json` and `$JOB_DIR/{email|linkedin_dm}_{ts}.txt`.

⚠️ If two drafts land in the same session/minute, disambiguate the filename with the target's name (e.g.
`email_{ts}_{first}_{last}.json`) — the script does not dedupe on target, so a same-minute second call
silently overwrites the first.

---

## C6 — Log (two copies: job-specific + global)

Write the **same entry** to both. The per-job copy keeps the outreach next to the role it belongs to; the
global copy is what the S1 session-start sweep and any reply-rate analysis actually read.

1. **Job-specific** — `$JOB_DIR/logs/outreach.json` *(if there is no `$JOB_DIR` — outreach not tied to a
   specific role — skip this copy)*
2. **Global** — append to `~/job_search/outreach_log.json`

Both are JSON arrays; create if absent, append — **never overwrite**.

```json
{
  "date_drafted": "YYYY-MM-DD",
  "target_name": "...", "target_title": "...", "target_company": "...",
  "role_applied": "...", "company_applied": "...", "job_dir": "$JOB_DIR",
  "type": "email|dm", "subject": "...",
  "body_preview": "first 120 chars...",
  "hook_used": "...",
  "status": "drafted",
  "date_sent": null,
  "followup_date": "YYYY-MM-DD",
  "reminder_event_id": null,
  "outcome": null,
  "outcome_date": null,
  "notes": ""
}
```

### Status vocabulary

```
status ∈ drafted | sent | followup_due | followed_up_1_sent
       | replied | cancelled_company_rejected | deleted
```

`drafted` → `sent` on C6.5 confirmation. Only **drafted / sent / followup_due** are ACTIONABLE; `replied`,
`cancelled_company_rejected`, `deleted` are terminal and S1 ignores them — counting terminal entries inflates
the stale number.

Keep the two copies in sync: any later status or outcome update (C6.5, F) must be applied to **both** the
job-specific and the global entry, matched on `target_name` + `date_drafted`.

---

## C6.5 — Confirm sent, then set a 10am follow-up reminder

Runs right after C6 logs the draft. This is the ONLY place a follow-up reminder is created. Sub-workflow C
only.

### Step 1 — Ask, never assume

> "Did you send this {email / DM} to {full_name}? (yes / not yet)"

- Anything that is not a clear "yes" ("not yet", "no", "about to") → **STOP. Create NO reminder.** Leave the
  log entry at `status: "drafted"`. Tell the user they can say "mark {name} sent" later and you'll set the
  reminder then. **Standing user choice: unsent messages get no reminder.**
- A clear "yes" → continue.

### Step 2 — Update the log entry

Set `status: "sent"` and `date_sent` to today. Recompute `followup_date = date_sent + followup_days` so it
counts from the **actual send date**, not the draft date.

### Step 3 — Load calendar tools

```
ToolSearch: select:mcp__gworkspace__manage_event,mcp__gworkspace__get_events
```

All calls use `user_google_email: jmascarenhas1998@gmail.com`, calendar `primary`, timezone
**`America/Chicago`**. Reminders are 10am **Calendar events**, not Google Tasks — Tasks are date-only and
never fire a timed popup.

### Step 4 — Merge check (same company, same follow-up day)

Before creating, scan `outreach_log.json` for any OTHER entry with the same `company_applied` AND the same
`followup_date` that already has a `reminder_event_id`. If unsure it still exists, confirm with `get_events`
on that day.

- **Match found → MERGE.** `manage_event` (action `update`) on that event id:
  - Title → "Followup with {name1} and {name2} at {company}" (for 3+, use "{name1}, {name2}, and {name3}").
  - Description → append this contact's block (name, hook, draft path).
  - Store that same `reminder_event_id` on this contact's log entry.
- **No match → CREATE** (Step 5).

### Step 5 — Create the event

`manage_event` (action `create`) on `primary`:

- **Title:** "Followup with {first_name} on {channel} — {company}" (channel = "LinkedIn" for a DM, "email" for
  an email).
- **Start:** `{followup_date}T10:00:00` · **End:** `{followup_date}T10:03:00`, timezone `America/Chicago`. **A
  3-minute event.**
- **Reminders: none at all** — `use_default_reminders = false` **and** `reminders = []`. Do NOT add the `pa`
  skill's popup overrides (popup 10 min / 2 hr / 12 hr / email 1 day), and do NOT add "popup 10 min before +
  popup at start" either. This is a 3-minute, zero-alert marker event.

  ⚠️ **Standing user correction — it overrides both skills' stated defaults.** Justin explicitly asked to
  update every existing followup reminder to 3 minutes with all before-event alerts stripped. Do not let this
  regress to a 30-minute event with popups. Scoped to these follow-up marker events only; real meetings/calls
  still use normal duration and the `pa` defaults.

- **Description** (one item per line):
  - "Follow up on {email/DM} to {full_name} ({target_title}, {company}) re: {role}. Send only if no reply
    yet."
  - "Hook: {hook_used}"
  - "Draft: {saved .txt path from C5b}"
  - "Resume this Claude Code session: claude-d --resume '{session_id}'" (read `CLAUDE_CODE_SESSION_ID`; if
    unset, use the current session directory name).
- Capture the returned event id into this entry's `reminder_event_id`.

### Step 6 — Confirm to the user

State the event title, the date, and 10am, and whether it was a new reminder or merged into an existing
same-company one.
