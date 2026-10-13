---
name: reference-batch-delegate-dashboard
description: "Live URL of Justin's \"Delegate Ops\" batch-delegate task-manager Artifact, and where its source/docs live"
metadata: 
  node_type: memory
  type: reference
  originSessionId: e13c05dc-e2cd-4146-9fb4-e047c9ee9c2b
  modified: 2026-09-15T06:24:03.083Z
---

The live batch-delegate task-manager dashboard ("Delegate Ops") is published
at: https://claude.ai/artifact/EYi3j2a1DSouwYSV7TZHoC

This is the **canonical URL** — use it from any working directory. It was
originally created by a session running from cwd `/home/jkdxbns` (whose own
memory scope also points here). A separate URL
(`Vc6ftnh8K4ph2rXGkgEnDe`, published from this session's own
`-home-jkdxbns-Desktop-jobs` memory scope) was a duplicate empty instance
created because Claude Code's memory is keyed per working directory — each
cwd gets its own memory files, so two different dashboards had been recorded
depending on where a batch-delegate run started. That duplicate is now
deprecated; do not resurrect it. Consolidating onto one URL here means any
session, from any cwd, that reads this memory file (or the equivalent file
in another project's memory scope) gets the same live dashboard.

**Verify this URL with `action: "read"` before reusing it** (Step 4a in
`batch-delegate/SKILL.md` requires this now). If it reads back "not found",
publish fresh (`Artifact.publish` with no `url`, `capabilities={"db":{}}`)
and overwrite this file (and the sibling copy in any other memory scope that
also tracks this dashboard) with the new URL immediately — don't propagate a
dead pointer forward, and don't let scopes diverge again.

This URL is account-specific — do not treat it as part of the
`batch-delegate` skill package itself, and never hand it to someone else's
session or copy it into a shipped skill. The shippable pieces are
`~/.claude/skills/batch-delegate/references/dashboard.html` (source) and
`references/dashboard.md` (setup + schema docs) — anyone receiving the skill
publishes their own instance from that source and gets their own URL.

Confirmed via direct `read_db` (2026-09-15) to contain 3 completed runs
(`kids-books-20260915`, `kids-books-summaries`, `run_9ab2e86744`), each with
25/25 item docs fully populated (prompt/raw_response/stats/summary) — the
push mechanism (Step 5a `prepare_dashboard_push.py` + Step 5b verification
gate) works correctly end to end.
