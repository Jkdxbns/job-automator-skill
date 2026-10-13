# C1.5 — Follow-ups: find the real sent thread first

Loaded when the request is a follow-up ("follow up", "followup", "draft a follow up for X") or a
stale-followup offer accepted from the S1 sweep — **not** a first touch.

Do NOT jump into C2–C4 and do NOT create a standalone untethered draft. Find the real sent thread first. What
actually went out can diverge from whatever the local draft file or `outreach_log.json` says — hand edits
before sending, a different subject, a recipient added at send time. **Gmail sent mail is the ground truth,
not the local record.**

## 1. Search sent mail

```
ToolSearch: select:mcp__gworkspace__search_gmail_messages,mcp__gworkspace__get_gmail_thread_content
search_gmail_messages(query: 'in:sent {company_name} ({full_name} OR {first_name})')
```

If that returns nothing, retry with just `in:sent {company_name}` and scan the results for the right contact —
not every sent subject names them directly.

## 2. On a match, pull the full thread

```
get_gmail_thread_content(thread_id, include_analysis=true)
```

Read the actual `To`, `Subject`, and `Message-ID` of the **last message on the thread** — use these, not
anything from the local `.txt`/`.json` draft file, which may be stale.

If `analysis.ball_in_court_of` is `"us"` (they already replied), **STOP.** Do not draft a follow-up onto a
thread that already has a response from them. Tell the user there's a reply waiting and ask what they want to
do instead.

## 3. If no matching sent message exists

This contact was likely only reached on LinkedIn, or never actually emailed. Say so plainly — "no Gmail thread
found for X, was this sent via LinkedIn?" — and fall back to the normal C2–C5 flow for a standalone draft
rather than inventing a thread.

## 4. With a real thread, write the body directly

Skip C2–C4 — no need to re-derive a hook or re-pull bullets for a short nudge.

- Reference the original without repeating its full pitch (e.g. "I wanted to follow up on the note I sent
  about...").
- **One ask only**, same rule as any outreach message.
- Same formatting rules as C4 (`outreach_rules.md`: no hyphens or dashes, no numbers, plain uneven language) —
  but **skip the self-identification opener**, the thread already establishes who this is.
- **Short**: 50–80 words, well under the 120–170 word first-touch range.

## 5. Create it as a properly threaded reply, not a floating draft

```
draft_gmail_message(
  to:          <the real To address from the thread>,
  subject:     "Re: <the real subject from the thread>",
  thread_id:   <thread_id>,
  in_reply_to: <Message-ID of the thread's last message>,
  references:  <same Message-ID>,
  body:        <the follow up body>,
  include_signature: false
)
```

## 6. Log truthfully

Continue to C5b and C6 as normal, but record the **REAL** subject and recipient pulled from the thread — not
whatever an earlier local draft file said — so local records stay truthful to what Gmail actually shows. Set
`notes` on the log entry to `"Threaded reply in real Gmail thread {thread_id}"`.

Cap: two follow-ups per contact, then stop. Do not recommend a third.
