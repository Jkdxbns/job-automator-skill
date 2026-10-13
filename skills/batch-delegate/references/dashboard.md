# Dashboard — reference

`references/dashboard.html` is the source for the live task-manager Artifact
("Delegate Ops"): a status grid over a `delegate.py` run, with a detail panel
per item (full prompt, full raw response, token/cost stats) and a note field
for flagging an item for a follow-up pass. Per Hard Rule 8 / Step 4a in
`SKILL.md`, publishing this (or reusing an existing instance) is the default
first thing that happens in every batch-delegate run, not an opt-in extra.
Chat still gets the same progress updates it always did — the dashboard is
additive, not a replacement for reporting in the conversation.

### Failure history — read this before changing dashboard behavior

Getting this right took five rounds across real test sessions, each fixing
one failure mode while leaving the next one in place. In order:

1. **"Offer it above ~30 items, ask first."** Failed because an offer
   phrased as a question is easy for the model to just not get around to
   asking — the dashboard was never mentioned at all in a fresh session.
2. **Unconditional publish, but push items only per-`Monitor`-tick.**
   Fixed (1) but the shell came up "online and live" with zero item data —
   pushing depended on remembering to do it repeatedly across a
   long-running loop, and nothing forced that habit to actually recur.
3. **Per-tick push replaced with a mandatory end-of-run script
   (`prepare_dashboard_push.py`, Step 5a).** Fixed (2) — a single
   mechanical action in a step that always runs, not an ongoing habit.
4. **A remembered URL from memory got reused without checking it still
   existed.** The artifact had been deleted independently of anything the
   skill did (confirmed via `action: "read"` returning "not found" — an
   artifact-lifecycle event outside the skill's control, not a bug in it),
   so the reuse `write_db` calls had nothing to write to and the run
   silently had no dashboard, again.
5. **Step 5a was still just an instruction to execute, with nothing
   checking it actually ran.** After (1)-(4) were all fixed on paper, the
   dashboard was still found empty with no way to tell, from outside the
   session that ran the batch, whether the push was skipped, errored
   unsurfaced, or wrote to a different URL. The pattern across all four
   prior rounds was the same shape: "do X" instructions in a long
   multi-tool-call task are followed probabilistically, not
   deterministically, no matter how emphatically worded — a *different*
   thing kept breaking each time, not the same thing recurring, which is
   the signature of "the instruction works most of the time" rather than
   "the instruction is wrong." Fixed by Step 5b: a verification gate, not
   another instruction to remember — `read_db` the run + item count and
   compare against what actually completed, *before* the task is allowed
   to be reported done. This ties the dashboard to the model's own "am I
   actually finished" judgment instead of a side-task easy to silently
   drop.

6. **The page itself silently crashed on real data.** All five fixes above
   were verified via `read_db` — a server-side check that the data landed —
   and never by actually loading the dashboard in a browser. The bug:
   `boot()`'s snapshot handler did `var v = d.data(); v.id = d.id;` on the
   object a live-data subscription returns. That object is frozen (not
   extensible), and the whole file runs under `"use strict"` — so the
   assignment threw a `TypeError`, silently aborting the handler right after
   it had already called `setLive(true)`. Net effect: dashboard showed
   "live", data was correct and complete in the database, and the table
   stayed permanently blank — indistinguishable from a working page with
   the wrong URL loaded, or a working empty run. Confirmed only by opening
   the page with `claude-in-chrome` and reading the page's console/DOM
   directly. Fixed by building a new object (`Object.assign({}, d.data(),
   {id: d.id})`) instead of mutating the snapshot's. **Lesson: `read_db`
   confirms the data pipeline; it does not confirm the page renders it.**
   Any future "user says the dashboard is empty but read_db shows data"
   report should go straight to loading the actual page, not back through
   the write path again.

Current state, fixing all six: publish/reuse is unconditional and
FYI-only (1), items push live per-completion in Step 4b — not just a
remembered habit — with Step 5a/5b as a final sweep + verification rather
than the first time data lands (2, 3), Step 4a reads a remembered URL back
before trusting it (4), Step 5b checks the push actually landed before the
batch can be called done (5), and a page-load check (not just `read_db`)
is the way to confirm the UI itself actually works (6). If a seventh
failure mode ever surfaces, add it to this list before touching the
mechanics — treat "it broke a new way" as expected until proven otherwise,
not as a sign the whole approach is wrong.

**This file ships with the skill. A live dashboard does not.** An Artifact is
a hosted page under a specific claude.ai account, not a file — publishing
`dashboard.html` creates a URL owned by whoever publishes it. Shipping this
skill to someone else hands them the recipe (this file + the instructions
below), not your running instance. They publish their own.

## First-time setup (once per account/workspace)

Publish the file as a new Artifact with the `db` capability:

```
Artifact.publish(file_path="~/.claude/skills/batch-delegate/references/dashboard.html",
                  capabilities={"db": {}}, favicon="📡", icon="console")
```

This returns a URL. **Write that URL down somewhere persistent** — nothing in
the skill package tracks it, because it's account-specific. The natural place
is a `reference`-type memory entry (see the auto-memory system, if this
session has one) so a future session already knows which dashboard to push
into instead of publishing a fresh one every time. If there's no persistent
memory available, ask the user where they want the URL recorded, or just
publish fresh per session and accept the duplication.

To reuse an existing dashboard instead of creating a new one, pass its URL
back: `Artifact.publish(file_path=..., url="<the saved URL>")` — omitting
`url` always creates a *separate* artifact, even with identical content.

## Data model

Two collections, `runs` and `runs/<run_id>/items`:

```
runs/<run_id>                              (doc)
  { name, created_at, total, workers, timeout_s, status, note? }

runs/<run_id>/items/<item_id>              (doc, one per delegate item)
  { id, title, team?,
    status:        "queued" | "running" | "done" | "failed",
    outcome:        <any short label the batch uses — free text>,
    outcome_class:  "positive" | "caution" | "negative" | "excluded" | "neutral",
    score:          <number, optional — any 0-100-ish metric the batch produces>,
    summary:        <one-line human-readable result, optional>,
    prompt:         <the exact prompt sent to the delegate>,
    raw_response:   <the delegate's raw stdout/answer text>,
    error:          <set only if status is "failed">,
    attempts:       1 | 2,
    stats:          <delegate.py's per-item stats object, verbatim — see below>,
    note:           <user or orchestrator note, optional>,
    note_status:    "open" | null }
```

`outcome`/`outcome_class`/`score` are **generic by design** — this is the
piece that was job-fit-specific in an earlier version and got fixed. A job-fit
batch might write `outcome: "Can Try"`, `outcome_class: "caution"`,
`score: 57.3`. A classification batch might write `outcome: "spam"`,
`outcome_class: "negative"`, `score: 0.92` (a confidence). A summarization
batch with no natural pass/fail concept can leave `outcome_class` unset — it
defaults to neutral in the UI, which is a legitimate state, not a placeholder.
The filter dropdown and the outcome-distribution chart in the dashboard build
themselves from whatever `outcome` strings actually appear in the data; there
is nothing to configure for a new batch type.

`stats` (present once `delegate.py` was run with `--output-format json`,
which is the default since it was added — absent/null for older runs, which
the dashboard renders as an empty stats block, not an error):
```
{ input_tokens, output_tokens, thinking_tokens, wall_ms, duration_ms,
  ttft_ms, cost_usd_notional, session_id, stop_reason, is_error }
```
`cost_usd_notional` is OpenRouter's own reported figure for a nominally-free
model — informative for relative comparison between items, not a real
charge. Stored per item but not rendered in the UI (removed from both the
left-pane aggregate and the per-item panel on request) — still readable via
`read_db` if ever needed.

## Pushing data live, per item (Step 4b — mandatory)

This is a **manual push by the orchestrating model** — a background script
has no way to call the Artifact tool, `delegate.py` included. Every time a
`Monitor`'d `PROGRESS` line arrives, before waiting again: read the new
line(s) `delegate.py` just appended to `results.jsonl` (each is
`{id, ok, result, stats, prompt, raw_response, attempts, error}`), and issue
one `write_db` `set` on `runs/<run_id>/items/<id>`:
```
{ id, status: ok ? "done" : "failed",
  prompt, raw_response, error: ok ? null : error, attempts, stats,
  // title/outcome/outcome_class/score/summary: fill in whatever you can
  // derive from `result` right now; leave the rest null — Step 5a's pass
  // fills in anything task-specific that needed post-processing.
  note: null, note_status: null }
```
This is what makes the page a *live* feed instead of a summary that only
appears once the whole batch is done — the reason the dashboard exists at
all is so the user can watch it and redirect the orchestrator mid-run.
Earlier versions of this skill treated per-tick pushes as optional and it
silently regressed every time (see failure round 2/3 above); it no longer is.

## Pushing data — the final sweep (Step 5a)

Once `delegate.py` finishes, `scripts/prepare_dashboard_push.py` turns
`results.jsonl` into ready-to-write item files and pre-chunked `write_db`
batch payloads — a mechanical re-push that fills in any `--extra` display
data (title/outcome/score) not available during the live per-item pushes,
and catches any item a live push failed to land for:
```bash
python3 ~/.claude/skills/batch-delegate/scripts/prepare_dashboard_push.py \
  <out-dir>/results.jsonl --run-id <run_id> --extra <extra.json>
```
`--extra` is optional — `{"<item_id>": {"title", "outcome", "outcome_class",
"score", "summary"}, ...}`; omit it and items still push with
prompt/response/stats, just no nice label. The script prints the exact calls
to make: one `set` for the run doc, then one `batch` call per chunk file
(`--chunk-size 40` by default, under the 50-per-call cap with headroom) —
read each chunk file and pass its array as `writes`. Chunks use `file_path`
per entry rather than inline `data`, since the inline-payload size cap is
smaller than the per-document 256 KiB limit and long prompts/responses need
the room. Run this even if every item already got a live push in 4b — `set`
is idempotent, and this is the pass Step 5b verifies against.

## Reading it back

`db.collection("runs/<run_id>/items").orderBy("id", "asc").limit(1000)` is
what the page itself subscribes to — live, updates as new writes land, no
polling needed on the page's side. From the orchestrator's side (outside the
page), `action: "read_db"` with `db_op: "query"` or `"get"` against the same
`url` reads the current state the same way — useful for checking whether a
user flagged any items with a note (`note_status: "open"`) before starting a
follow-up pass, without having to re-derive that from `results.jsonl`.

## When to skip this

Only when the user explicitly says not to use it, or the Artifact tool isn't
available in this environment. There's no longer a size threshold — see
Hard Rule 8's note above for why the size-gated version didn't hold up in
practice. The run doc + a handful of `write_db` batch calls is cheap enough
that gating it on batch size wasn't buying much anyway; the earlier "skip
below ~20" reasoning underweighted how often the threshold logic itself was
the thing that silently failed.
