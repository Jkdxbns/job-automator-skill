#!/usr/bin/env python3
"""Append a row to the submitted-jobs CSV log.

Usage:
  mark_submitted.py --company "Intrinsic (Google)" --role "Software Engineer, Simulation" \
      --session-id 6e96dd4c-337c-4d7e-8cc6-154966c352f8 [--job-dir /path/to/job/dir] \
      [--csv ~/job_search/submitted_log.csv]
"""
import argparse
import csv
import os
import sys
from datetime import date

FIELDS = ["date_submitted", "company", "role", "resume_cmd", "job_dir"]
DEFAULT_CSV = os.path.expanduser("~/job_search/submitted_log.csv")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--company", required=True)
    parser.add_argument("--role", required=True)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--job-dir", default="")
    parser.add_argument("--csv", default=DEFAULT_CSV)
    parser.add_argument("--date", default="")
    args = parser.parse_args()

    csv_path = os.path.expanduser(args.csv)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    row = {
        "date_submitted": args.date or date.today().isoformat(),
        "company": args.company,
        "role": args.role,
        "resume_cmd": f"claude-d --resume '{args.session_id}'",
        "job_dir": args.job_dir,
    }

    file_exists = os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"SAVED: {csv_path}")
    for k, v in row.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    sys.exit(main())
