#!/usr/bin/env python3
"""
Turns delegate.py's results.jsonl into dashboard-ready item files + chunked
write_db batch metadata — the mechanical part of Step 5's dashboard push, so
"push everything to the dashboard" is a script call + N copy-pasteable
write_db calls, not something to freehand-construct and easy to skip.

This exists because the dashboard push failed silently three sessions in a
row when it depended on the orchestrator remembering to hand-build this
JSON during a long Monitor loop. Making it one mechanical step right after
delegate.py finishes (Step 5, which already always runs) is the fix — see
SKILL.md Step 5 and Hard Rule 8.

Usage:
    python3 prepare_dashboard_push.py <results.jsonl> --run-id <run_id> \
        [--extra <extra.json>] [--out-dir <dir>] [--chunk-size 40]

<results.jsonl> is delegate.py's output file (one JSON object per line:
id, ok, result, stats, prompt, raw_response, attempts, error).

--extra <extra.json> is OPTIONAL, task-specific display data this script
cannot derive on its own: {"<item_id>": {"title": ..., "outcome": ...,
"outcome_class": "positive"|"caution"|"negative"|"excluded"|"neutral",
"score": <number>, "summary": ...}, ...}. Any field omitted per-item, or the
whole file omitted, just leaves that dashboard field blank — the item still
gets pushed with its prompt/response/stats, it just won't have a nice title
or outcome label. Build this however fits the task (e.g. for job-fit
batches, from each role's title + score_fit.py verdict/match_pct).

Output (in --out-dir, default alongside results.jsonl):
  dashboard_items/<id>.json   — one file per item, ready for write_db's
                                  file_path
  dashboard_writes_N.json     — write_db 'batch' payloads, chunked to
                                  --chunk-size entries each (default 40, under
                                  the 50-per-call cap with headroom)
  dashboard_run_doc.json      — the run doc body for collection "runs"

Prints the exact sequence of write_db calls to make (run doc first, then
each chunk file's path) — read the chunk file and pass its array as `writes`
with db_op "batch".
"""
import argparse
import datetime
import json
import os
import re
import sys


def sanitize(item_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.~:@+-]", "_", item_id)[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_jsonl")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--extra", default=None)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--chunk-size", type=int, default=40)
    args = ap.parse_args()

    out_dir = args.out_dir or os.path.join(os.path.dirname(os.path.abspath(args.results_jsonl)), "dashboard_push")
    items_dir = os.path.join(out_dir, "dashboard_items")
    os.makedirs(items_dir, exist_ok=True)

    extra = {}
    if args.extra:
        extra = json.load(open(args.extra))

    seen = {}
    for line in open(args.results_jsonl):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        seen[r["id"]] = r  # last write wins (a retry overwrites the failed attempt)

    docs = []
    for item_id, r in seen.items():
        ex = extra.get(item_id, {})
        doc = {
            "id": item_id,
            "title": ex.get("title"),
            "team": ex.get("team"),
            "status": "done" if r.get("ok") else "failed",
            "outcome": ex.get("outcome"),
            "outcome_class": ex.get("outcome_class"),
            "score": ex.get("score"),
            "summary": ex.get("summary"),
            "prompt": r.get("prompt"),
            "raw_response": r.get("raw_response"),
            "error": r.get("error") if not r.get("ok") else None,
            "attempts": r.get("attempts"),
            "stats": r.get("stats"),
            "note": None,
            "note_status": None,
        }
        safe_id = sanitize(item_id)
        item_path = os.path.join(items_dir, f"{safe_id}.json")
        json.dump(doc, open(item_path, "w"))
        docs.append({"id": item_id, "path": item_path})

    # run doc
    n_done = sum(1 for r in seen.values() if r.get("ok"))
    n_failed = len(seen) - n_done
    run_doc = {
        "name": args.run_id,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total": len(seen), "status": "done" if n_failed == 0 else "done_with_failures",
    }
    run_doc_path = os.path.join(out_dir, "dashboard_run_doc.json")
    json.dump(run_doc, open(run_doc_path, "w"), indent=2)

    # chunked batch-write metadata
    chunk_paths = []
    for i in range(0, len(docs), args.chunk_size):
        chunk = docs[i:i + args.chunk_size]
        writes = [
            {"op": "set", "collection": f"runs/{args.run_id}/items", "doc_id": d["id"], "file_path": d["path"]}
            for d in chunk
        ]
        chunk_path = os.path.join(out_dir, f"dashboard_writes_{i // args.chunk_size}.json")
        json.dump(writes, open(chunk_path, "w"), indent=2)
        chunk_paths.append(chunk_path)

    print(json.dumps({
        "run_id": args.run_id,
        "item_count": len(docs),
        "run_doc_path": run_doc_path,
        "run_doc_write": {"db_op": "set", "collection": "runs", "doc_id": args.run_id, "file_path": run_doc_path},
        "item_write_chunks": [
            {"db_op": "batch", "writes_file": p, "note": "Read this file, pass its array as the `writes` param"}
            for p in chunk_paths
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
