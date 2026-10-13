#!/usr/bin/env python3
"""
Delegates a batch of independent LLM calls to claude-f (the OpenRouter-backed
headless `claude` CLI defined in ~/.bashrc), run through a bounded worker pool
instead of one at a time.

Hard rules encoded here, not just in prose:
- Never falls back to any Anthropic-backed model. If claude-f is unavailable or
  fails, this script fails loudly rather than silently trying another backend.
  (Note: this only holds for the one-shot `claude -p` mode used here. A full
  interactive claude-f session — e.g. spawned for cross-session messaging —
  has been observed to silently fall back to the Anthropic-authenticated
  session instead of honoring the OpenRouter env override. Never build a
  delegate mechanism around interactive/peer-addressable claude-f sessions;
  one-shot `-p` subprocess calls are the only verified-free path.)
- Bounded concurrency via a thread pool (default 8 workers — these are I/O-bound
  subprocess calls, not CPU-bound, so a plain thread pool is sufficient; no
  process pool needed). Each item still gets exactly one retry (a fresh,
  independent call) before being counted as failed.
- Once any item fails twice, no NEW items are scheduled — but items already
  in flight are allowed to finish, since killing them mid-call wastes the work
  and provides no benefit. The report distinguishes completed / failed /
  never-attempted, and never-attempted is only items that hadn't started yet.
- Live progress: one line per item completion is printed to stdout as it
  happens (`PROGRESS i/N OK|FAIL id=...`), not just a final summary — so a
  Monitor watching this process's stdout sees the batch move in real time.
  A final `DONE ...` line summarizes.
- Full observability per item: every item's prompt and raw response are saved
  to their own file under --out-dir (default: a temp dir printed at start),
  so any item can be inspected in full at any time during or after the run —
  this is what "manage and view what's going on" resolves to for a delegate
  backend that cannot be chatted with mid-flight (see SKILL.md's Mechanism
  Note for why interactive claude-f sessions don't work for this).

Usage:
    python3 delegate.py <items.json> [--timeout SECONDS] [--workers N] [--out-dir DIR]

<items.json> is a JSON array: [{"id": "...", "prompt": "..."}, ...]
Each prompt must instruct the model to output ONLY a single JSON object.

Writes one line per item to <out-dir>/results.jsonl AS IT COMPLETES (not just
at the end), and prints PROGRESS lines to stdout for live monitoring. Prints a
single final JSON object to stdout:
    {"aborted": bool, "completed": [...], "failed": [...], "never_attempted": [...],
     "out_dir": "..."}
Exit code 0 = every item succeeded. Exit code 1 = one or more items failed
twice (whatever succeeded is still in "completed" and on disk).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, FIRST_COMPLETED, wait


def run_one_call(prompt: str, timeout: int, transcript_path: str) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write(prompt)
        prompt_path = f.name

    start = time.time()
    try:
        # claude-f is a bash function (~/.bashrc), not a binary on PATH — needs
        # a login/interactive-ish shell that sources it. Prompt goes through a
        # temp file + $(cat ...) to sidestep shell-quoting issues with the JD text.
        # --output-format json wraps the model's answer in an envelope carrying
        # real usage stats (tokens, duration, session_id, notional cost) — needed
        # for the task-manager dashboard, not just the answer itself.
        cmd = (f'shopt -s expand_aliases; source ~/.bashrc >/dev/null 2>&1; '
               f'claude-f -p --output-format json "$(cat {prompt_path})"')
        proc = subprocess.run(
            ["bash", "-lc", cmd],
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        _write_transcript(transcript_path, prompt, None, "timed out", None)
        return {"ok": False, "error": f"timed out after {timeout}s",
                "stats": {"wall_ms": int((time.time() - start) * 1000)}}
    finally:
        os.unlink(prompt_path)

    wall_ms = int((time.time() - start) * 1000)
    stats = {"wall_ms": wall_ms}
    envelope = None
    if proc.stdout.strip():
        try:
            envelope = json.loads(proc.stdout)
        except json.JSONDecodeError:
            envelope = None
    if envelope:
        usage = envelope.get("usage", {})
        stats.update({
            "session_id": envelope.get("session_id"),
            "duration_api_ms": envelope.get("duration_api_ms"),
            "duration_ms": envelope.get("duration_ms"),
            "ttft_ms": envelope.get("ttft_ms"),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "thinking_tokens": (usage.get("output_tokens_details") or {}).get("thinking_tokens"),
            "cost_usd_notional": envelope.get("total_cost_usd"),
            "stop_reason": envelope.get("stop_reason"),
            "is_error": envelope.get("is_error"),
        })

    _write_transcript(transcript_path, prompt, proc.stdout,
                       proc.stderr if proc.returncode != 0 else None, stats)

    if proc.returncode != 0:
        return {"ok": False, "error": f"exit {proc.returncode}: {proc.stderr.strip()[:500]}", "stats": stats}

    # the actual per-item answer is the envelope's "result" field (a JSON string);
    # fall back to scanning raw stdout for a brace-balanced object if envelope
    # parsing failed for any reason (e.g. --output-format json itself misbehaved)
    raw_answer = envelope.get("result") if envelope else None
    if raw_answer is None:
        match = re.search(r"\{.*\}", proc.stdout, re.DOTALL)
        raw_answer = match.group(0) if match else None
    if raw_answer is None:
        return {"ok": False, "error": f"no result found in output: {proc.stdout.strip()[:500]}", "stats": stats}

    match = re.search(r"\{.*\}", raw_answer, re.DOTALL)
    if not match:
        return {"ok": False, "error": f"no JSON object found in result: {raw_answer[:500]}", "stats": stats}

    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"malformed JSON ({e}): {match.group(0)[:500]}", "stats": stats}

    return {"ok": True, "result": data, "stats": stats, "raw_response": raw_answer}


def _write_transcript(path: str, prompt: str, stdout: str | None, stderr: str | None, stats: dict | None):
    with open(path, "w") as f:
        f.write("=== PROMPT ===\n")
        f.write(prompt)
        f.write("\n\n=== STDOUT ===\n")
        f.write(stdout or "(none)")
        if stderr:
            f.write("\n\n=== STDERR ===\n")
            f.write(stderr)
        if stats:
            f.write("\n\n=== STATS ===\n")
            f.write(json.dumps(stats, indent=2))


def process_item(item: dict, timeout: int, out_dir: str) -> dict:
    """Runs an item with one retry. Always writes its transcript(s) to out_dir,
    named by item id + attempt number, so both attempts are inspectable."""
    safe_id = re.sub(r"[^a-zA-Z0-9_.-]", "_", item["id"])
    queued_at = time.time()
    attempt1_path = os.path.join(out_dir, f"{safe_id}.attempt1.txt")
    outcome = run_one_call(item["prompt"], timeout, attempt1_path)
    if outcome["ok"]:
        return {"id": item["id"], "ok": True, "result": outcome["result"], "attempts": 1,
                "stats": outcome.get("stats"), "queued_at": queued_at, "prompt": item["prompt"],
                "raw_response": outcome.get("raw_response")}

    attempt2_path = os.path.join(out_dir, f"{safe_id}.attempt2.txt")
    retry = run_one_call(item["prompt"], timeout, attempt2_path)
    if retry["ok"]:
        return {"id": item["id"], "ok": True, "result": retry["result"], "attempts": 2,
                "stats": retry.get("stats"), "queued_at": queued_at, "prompt": item["prompt"],
                "raw_response": retry.get("raw_response")}

    return {
        "id": item["id"], "ok": False, "attempts": 2,
        "error": f"failed twice. first: {outcome['error']} | retry: {retry['error']}",
        "stats": retry.get("stats") or outcome.get("stats"), "queued_at": queued_at,
        "prompt": item["prompt"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("items_file")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--workers", type=int, default=8,
                     help="bounded concurrency for the thread pool (default 8)")
    ap.add_argument("--out-dir", default=None,
                     help="where per-item transcripts + results.jsonl are written "
                          "(default: a fresh temp dir, path is printed at start)")
    args = ap.parse_args()

    items = json.load(open(args.items_file))
    total = len(items)

    out_dir = args.out_dir or tempfile.mkdtemp(prefix="batch_delegate_")
    os.makedirs(out_dir, exist_ok=True)
    results_path = os.path.join(out_dir, "results.jsonl")
    print(f"OUT_DIR {out_dir}", flush=True)

    write_lock = threading.Lock()
    completed = []
    failed = []
    abort_new_submissions = threading.Event()
    done_count = 0

    def append_result(res: dict):
        nonlocal done_count
        with write_lock:
            done_count += 1
            with open(results_path, "a") as f:
                f.write(json.dumps(res) + "\n")
            status = "OK" if res["ok"] else "FAIL"
            st = res.get("stats") or {}
            tok = f" in={st.get('input_tokens')} out={st.get('output_tokens')} ms={st.get('wall_ms')}" if st else ""
            extra = "" if res["ok"] else f" error={res['error'][:200]}"
            print(f"PROGRESS {done_count}/{total} {status} id={res['id']}{tok}{extra}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {}
        it = iter(items)
        # Prime the pool up to `workers` in flight, then top up as each finishes —
        # this way abort_new_submissions actually stops new work from starting
        # instead of everything already having been submitted up front.
        def submit_next():
            try:
                item = next(it)
            except StopIteration:
                return None
            fut = ex.submit(process_item, item, args.timeout, out_dir)
            futures[fut] = item
            return fut

        for _ in range(min(args.workers, total)):
            submit_next()

        while futures:
            # wait() with FIRST_COMPLETED returns as soon as ANY future finishes —
            # unlike as_completed(), which must exhaust its whole input snapshot
            # before a caller can act on even the first result (that bug flattened
            # this pool to near-sequential: 1 of 8 workers active at a time).
            done, _pending = wait(list(futures.keys()), return_when=FIRST_COMPLETED)
            for fut in done:
                item = futures.pop(fut)
                res = fut.result()
                append_result(res)
                if res["ok"]:
                    completed.append(res)
                else:
                    failed.append(res)
                    abort_new_submissions.set()
                if not abort_new_submissions.is_set():
                    submit_next()

    attempted_ids = {r["id"] for r in completed} | {r["id"] for r in failed}
    never_attempted = [it["id"] for it in items if it["id"] not in attempted_ids]

    summary = {
        "aborted": len(failed) > 0,
        "completed": completed,
        "failed": failed,
        "never_attempted": never_attempted,
        "out_dir": out_dir,
    }
    print(json.dumps(summary, indent=2))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
