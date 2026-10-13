#!/usr/bin/env python3
"""
log_fit.py — append a fit analysis to the GLOBAL slim index (A9, step 2).

Why this is a script and not an instruction: an audit on 2026-09-12 found 501
fit.json files on disk against only 167 rows in the global log. The loss was
concentrated on batch days — when many roles are analyzed at once, the per-role
global row gets skipped. F2's funnel report reads this log, so every missed row
understates the funnel. Scripting it removes the judgement call.

Usage:
  log_fit.py <fit.json | job_dir> [more ...]      # one or many; batch-safe
  log_fit.py --log <path> <fit.json ...>          # override the global log

Idempotent: re-running on the same job_dir REPLACES that row rather than
duplicating it, so re-analysis updates the index in place.

Exit codes:
  0 — every input logged
  1 — some inputs failed (details on stderr)
  2 — bad invocation
"""

import json
import os
import sys
from datetime import date

DEFAULT_LOG = os.path.expanduser("~/job_search/fit_analysis_log.json")


def resolve(arg: str) -> str:
    """Accept either a fit.json path or the job dir that contains logs/fit.json."""
    p = os.path.expanduser(arg)
    if os.path.isdir(p):
        p = os.path.join(p, "logs", "fit.json")
    return p


def load_log(path: str) -> list:
    if not os.path.exists(path):
        return []
    try:
        data = json.load(open(path))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        # Never destroy an unreadable log — refuse instead.
        print(f"ERROR: {path} exists but is not readable JSON; refusing to overwrite",
              file=sys.stderr)
        sys.exit(1)


def row_from_fit(fit: dict, job_dir: str, when: str) -> dict:
    llm = fit.get("llm_analysis") or {}
    verdicts = fit.get("verdicts") or {}
    return {
        "date": when,
        "company": fit.get("company", ""),
        "role": fit.get("role", ""),
        "job_dir": job_dir,
        "match_pct": fit.get("match_pct"),
        "seniority_fit": fit.get("seniority_fit"),
        "llm_match_pct": llm.get("llm_match_pct"),
        "llm_verdict": llm.get("llm_verdict"),
        "calibration_delta": llm.get("calibration_delta"),
        "matches": verdicts.get("matches"),
        "apply": verdicts.get("apply"),
        "role_category": fit.get("role_category"),
    }


def main() -> int:
    args = sys.argv[1:]
    log_path = DEFAULT_LOG
    if "--log" in args:
        i = args.index("--log")
        try:
            log_path = os.path.expanduser(args[i + 1])
        except IndexError:
            print("ERROR: --log needs a path", file=sys.stderr)
            return 2
        del args[i:i + 2]

    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    log = load_log(log_path)
    by_dir = {r.get("job_dir"): i for i, r in enumerate(log) if r.get("job_dir")}

    added = updated = failed = 0
    for arg in args:
        fit_path = resolve(arg)
        if not os.path.exists(fit_path):
            print(f"SKIP (not found): {fit_path}", file=sys.stderr)
            failed += 1
            continue
        try:
            fit = json.load(open(fit_path))
        except (json.JSONDecodeError, OSError) as e:
            print(f"SKIP (bad JSON): {fit_path} — {e}", file=sys.stderr)
            failed += 1
            continue

        # job_dir = the directory holding logs/fit.json
        job_dir = os.path.dirname(os.path.dirname(os.path.abspath(fit_path)))
        # Date the analysis by the fit.json's own mtime rather than "today": for a
        # fresh run they are the same, and it makes a historical backfill accurate.
        when = date.fromtimestamp(os.path.getmtime(fit_path)).isoformat()
        row = row_from_fit(fit, job_dir, when)

        if job_dir in by_dir:
            log[by_dir[job_dir]] = row
            updated += 1
            print(f"UPDATED: {row['company']} — {row['role']} ({row['match_pct']}%)")
        else:
            by_dir[job_dir] = len(log)
            log.append(row)
            added += 1
            print(f"LOGGED : {row['company']} — {row['role']} ({row['match_pct']}%)")

    # Write atomically so an interrupted run cannot truncate the index.
    tmp = log_path + ".tmp"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(tmp, "w") as f:
        json.dump(log, f, indent=2)
    os.replace(tmp, log_path)

    print(f"\n{added} added, {updated} updated, {failed} failed — {len(log)} rows total")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
