# batch-delegate

A Claude Code skill that fans a "do this same analysis N times" task out to
free-tier delegate calls, run in parallel, instead of burning Anthropic-model
tokens on repetitive per-item work. `SKILL.md` is the instruction file the
orchestrating model reads; this README is for a human setting the skill up
or deciding whether to ship it somewhere.

## What it does

Give it a list of items (job postings, documents, rows of data — anything)
and a per-item task, and it:
1. Builds one self-contained prompt per item (no shared tool/skill access —
   delegates get everything inlined, since a free-tier model can't reliably
   call tools).
2. Runs them through a bounded worker pool of independent `claude-f` calls
   (OpenRouter-backed, not Anthropic-backed — this is the whole point).
3. Saves every item's full prompt and response to disk and streams live
   `PROGRESS i/N` updates as they complete.
4. Reports exactly what finished, what failed, and what was never attempted
   — no silent retries, no falling back to a paid model to "just finish it."

Optionally, for large runs (~30+ items), it can push into a live dashboard
Artifact instead of relying on chat to hold every report — see
`references/dashboard.md`.

## Before this works — setup requirements

**Required:**
- **A `claude-f` shell function.** This is the actual delegation mechanism,
  and it is **not part of this skill package** — it must exist independently
  in the shell environment (typically `~/.bashrc`), pointing at an OpenRouter
  API key:
  ```bash
  claude-f() {
      export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
      export ANTHROPIC_AUTH_TOKEN="<your OpenRouter API key>"
      export ANTHROPIC_API_KEY=""
      export ANTHROPIC_MODEL="<a free OpenRouter model id>"
      export CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1
      claude --dangerously-skip-permissions "$@"
  }
  ```
  **Never ship or commit your actual key.** If you're sharing this skill,
  share the function *shape* above, not your filled-in `~/.bashrc` snippet.
- **Your own OpenRouter account.** Recreating the function above still needs
  a real account and key behind it, and the specific free model you name
  needs to still exist under that id — free-tier listings change over time,
  so verify the model before relying on it.
- **bash and Python 3.10+.** `delegate.py` shells out via
  `subprocess.run(["bash", "-lc", ...])` (Linux/Mac natively; Windows needs
  WSL or Git Bash) and uses `str | None`-style type hints, which need a
  genuinely recent Python at runtime (no `from __future__ import
  annotations` is used to soften that).

**Not required, degrades gracefully:**
- **`Monitor`** (or an equivalent background-task/live-log tool) — `SKILL.md`
  recommends it for watching `delegate.py`'s progress live; without it, just
  read `results.jsonl` directly instead.
- **Artifact-tool access** — only needed for the optional dashboard
  (`references/dashboard.md`). Core delegation doesn't touch it.

## Install location note

`SKILL.md`'s command examples hardcode
`~/.claude/skills/batch-delegate/scripts/delegate.py`, i.e. a user-level
install. If you install this as a project-scoped skill instead, update those
paths to match — they are not location-agnostic as written.

## What's actually in the package

```
batch-delegate/
  SKILL.md                    orchestrator instructions (read by the model)
  README.md                   this file (read by a human)
  scripts/
    delegate.py                the entire delegation engine — pure stdlib,
                                zero job-domain knowledge, zero pip deps
  references/
    dashboard.html             optional live task-manager Artifact source
    dashboard.md                its setup/schema/push-mechanics docs
```

Nothing job-specific lives here. `SKILL.md` shows job-fit analysis as one
worked example (with pointers to job-automator's scripts, which live in
*that* skill, not this one) — the mechanics generalize to any
same-shape-many-times task.

## Verifying it works

```bash
echo '[{"id":"t1","prompt":"Output ONLY this JSON, nothing else: {\"n\":1}"}]' > /tmp/t.json
python3 ~/.claude/skills/batch-delegate/scripts/delegate.py /tmp/t.json --timeout 60 --workers 1
```
A successful run prints `OUT_DIR ...`, one `PROGRESS 1/1 OK id=t1` line, and
a final JSON summary with `"aborted": false`. If it fails immediately with
"claude-f: command not found," the shell function above isn't set up in the
environment `delegate.py`'s subprocess sees (`bash -lc` sources `~/.bashrc`
— confirm the function actually lives there and the shell that's running
isn't skipping rc-file loading).
