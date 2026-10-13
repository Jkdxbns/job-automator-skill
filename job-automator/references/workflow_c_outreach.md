# Sub-workflow C — Cold Outreach Drafting

Loaded when the request is outreach: "draft cold email", "draft LinkedIn DM", "draft outreach", "follow up
with X", "mark X sent". Read this file in full before drafting.

Read **all of `outreach_examples.md`** — all three worked examples (including the conversation-ask example for
university / early-career recruiters) plus the Style Analysis rules. There is no line limit.

Inputs: target person info (user-provided) · `$JOB_DIR/logs/tailored.json` (top 3 bullets) ·
`$JOB_DIR/logs/fit.json` (company + role).

**C1 — Get target info.** Use what the user gave; no scraping, no API call:
```
full_name, first_name, current_title, current_company,
shared context (school, past employer, mutual connection, recent post),
role_type: recruiter | engineer | researcher | manager | other,
target_email: their address if given, else null
```
Ask for `target_email` only when the type is `email` (C5-Email needs it for the `to` field) — a DM has no use
for it. Don't block on it either: proceed with `null` and the Gmail draft is created with no recipient set.

**C1.5 — Follow-ups: search sent mail before drafting anything new**

For a follow-up ("follow up", "draft a followup for X", or an accepted S1 offer), do NOT jump into C2–C4 and
do NOT create a standalone untethered draft. Find the real sent thread first — what actually went out can
diverge from the local draft file or `outreach_log.json` (hand edits before sending, a different subject, a
recipient added at send time). **Gmail sent mail is the ground truth, not the local record.**

Full procedure in [followup_threads.md](followup_threads.md): the `in:sent` search and its fallback, reading
the real To/Subject/Message-ID off the thread, the **STOP** when `analysis.ball_in_court_of == "us"` (they
already replied — never follow up onto a thread with their response), the honest "no Gmail thread found, was
this sent via LinkedIn?" fallback, the threaded-reply `draft_gmail_message` call, and logging the real subject
and recipient. A follow-up body is 50–80 words, one ask, and skips the self-identification opener.

**C2 — Pick a personalization hook** (priority order)
1. Shared employer — Justin's past company matches theirs, or a company whose hardware/platform he has
   hands-on project experience with.
2. Same university (RIT or University of Mumbai).
3. Engineer/researcher in the same technical domain.
4. A recent post on a relevant topic.
5. Title relevance — why their specific role makes them the right person.

A line like "your recruiting background made you a good person to reach out to" is **not** a real hook — it
could apply to any recruiter and reads as filler. Only use a hook that references something specific to that
person. **If no specific hook exists, drop the hook line entirely** — no hook beats a fake one.

**C3 — Pull top 3 bullets.** From `$JOB_DIR/logs/tailored.json` (metric-bearing) when B has run for this role.
**If it has not, do not ask Justin for achievements** — the data is already on disk. Score
`master_profile.json`'s experience and project bullets against `fit.json`'s `top_ats_keywords` +
`key_responsibilities` (same scoring as B1) and take the top 3 metric-bearing ones. Only ask if neither
`tailored.json` nor `fit.json` exists, which means no role context at all.

**C4 — Draft outreach.** Match the tone, structure, and length of `outreach_examples.md` (first 80 lines)
exactly. Return JSON: `{ type, subject (null for dm), greeting, body, sign_off, word_count, hook_used,
followup_days }`.

**Read [outreach_rules.md](outreach_rules.md) before drafting** — it holds the hard rules: email 120–170 words
/ DM 120–180 with a ≤280-char opener; the fixed verbatim email closing-line pair; DM **one ask only**; and the
non-negotiable body formatting (no hyphens or dashes anywhere, no numbers in the body, no permission-granting
language, no mid-paragraph line breaks, plain uneven rhythm, a one-line self-identification opener, and never
mentioning visa/OPT/EAD unless Justin asks).

**C5 / C5b / C6 / C6.5 — Deliver, save, log, remind**

Full procedure in [outreach_delivery.md](outreach_delivery.md). The decisions and standing corrections that
must not drift:

- **Channel comes from `draft.type`**, set by what the user asked for. `dm` → **C5-DM**: print the full draft
  inline (no DM API exists, so chat is the deliverable; plain ASCII dividers, flowing prose, no mid-line
  wraps). `email` → **C5-Email**: create a **Gmail draft** via `draft_gmail_message` (`include_signature:
  false`) and print only a short confirmation — never the full body, it is already in Gmail. On a Gmail error,
  fall back to the inline print and say the save failed. **Never auto-send.**
- **C5b runs for both channels** — `python3 ~/.claude/skills/job-automator/scripts/save_and_print_draft.py
  "$JOB_DIR" '<draft_json>'` — the tracking copy the reminder points to. Add the target's name to the filename
  if two drafts land in the same minute; the script does not dedupe.
- **C6 dual-write.** The same entry goes to `$JOB_DIR/logs/outreach.json` **and**
  `~/job_search/outreach_log.json` — JSON arrays, create if absent, append, never overwrite. Only `drafted` /
  `sent` / `followup_due` are ACTIONABLE; `replied` / `cancelled_company_rejected` / `deleted` are terminal
  and S1 ignores them. Any later status or outcome update hits **both** copies, matched on `target_name` +
  `date_drafted`.
- **C6.5 asks, never assumes**: "Did you send this to {full_name}? (yes / not yet)". Anything short of a clear
  yes → **create NO reminder**, leave `status: "drafted"`. Standing user choice: unsent messages get no
  reminder.
- **The reminder event, on a clear yes**: 10am Google **Calendar event** (not a Task), timezone
  **`America/Chicago`**, **3 minutes** (10:00→10:03), **zero alerts** — `use_default_reminders = false`
  **and** `reminders = []`. Do NOT add the `pa` skill's popup overrides, and do NOT add "popup 10 min before +
  popup at start". ⚠️ **Standing user correction overriding both skills' defaults — do not let this regress to
  a 30-minute event with popups.** Merge into an existing same-company, same-day reminder when one exists.

**C7 — Follow-up enforcement.** The session-start sweep lives in **S1**, above the routing table, so it fires
every session regardless of sub-workflow. Cap remains two follow-ups per contact; accepted follow-ups route
through C1.5 — reply into the real thread, never a fresh first-touch draft.

---

