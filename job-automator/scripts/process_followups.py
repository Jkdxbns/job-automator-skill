#!/usr/bin/env python3
"""
process_followups.py — the ONE place that touches ~/job_search/outreach_log.json.

The model must never read that file. It is 116+ entries / ~43k tokens, and every
question the skill asks of it is deterministic. The model passes arguments; this
script reads, filters, writes, and keeps outreach_index.json in step.

outreach_index.json holds only indexes, so S1 and the followup list never load
the log itself:

    {"next_index": 117, "drafted_only": [12, 44], "followups_pending": [7, 9],
     "needs_attention": [3]}

Everything is index driven: each arg takes indexes, placement follows the status
just written, and new entries take their index from next_index. Only
--rebuild-index ever scans the log by status.

Arrays are maintained ON WRITE. An entry enters followups_pending when its
status becomes sent/followup_due and leaves on any terminal status, so
"pending" is status-driven, never recomputed from followup_date.

STATUS MODEL
  drafted              written, not sent      -> drafted_only
  sent                 sent, awaiting reply   -> followups_pending
  followup_due         followup owed          -> followups_pending
  followed_up_1_sent   one followup sent      -> terminal (cap is one)
  replied              they answered          -> terminal
  cancelled_company_rejected                  -> terminal
  deleted              abandoned              -> terminal
Terminal statuses are dropped from both arrays and keep their log entry, so
reply-rate analysis still has its data.

USAGE
  --count                      S1 one-liner: prints FOLLOWUPS=<n> DRAFTS=<n>
  --obtain-pending             table of followups_pending (no notes)
  --obtain-drafts              table of drafted_only (no notes)
  --get-notes 7,9              notes for those indexes only (for drafting)
  --add '<json>'               append one entry, assign index, update arrays
  --set-status 7,9 --status sent
  --delete 7,9                 soft delete (status=deleted), keeps the entry
  --rebuild-index              recompute arrays from the log's statuses
"""
import argparse
import json
import os
import sys
from datetime import date

LOG = os.path.expanduser("~/job_search/outreach_log.json")
INDEX = os.path.expanduser("~/job_search/outreach_index.json")

DRAFTED = {"drafted"}
PENDING = {"sent", "followup_due"}
TERMINAL = {"followed_up_1_sent", "replied", "cancelled_company_rejected", "deleted"}
VALID = DRAFTED | PENDING | TERMINAL

# Every entry carries a followup_date so the schema is uniform; entries with no
# real date carry this placeholder. It is never treated as a date — it sorts
# last, prints as NO DATE, and puts the entry in needs_attention.
NO_DATE = "0000-00-00"


def has_date(e):
    fd = e.get("followup_date")
    return bool(fd) and fd != NO_DATE


def load_log():
    if not os.path.exists(LOG):
        return []
    with open(LOG) as f:
        return json.load(f)


def save_log(entries):
    tmp = LOG + ".tmp"
    with open(tmp, "w") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, LOG)


def save_index(idx):
    tmp = INDEX + ".tmp"
    with open(tmp, "w") as f:
        json.dump(idx, f, indent=2)
        f.write("\n")
    os.replace(tmp, INDEX)


def build_index(entries):
    """Arrays from statuses. An entry with no usable date lands in
    needs_attention too, so a broken row is visible instead of silently lost."""
    idx = {"next_index": 1, "drafted_only": [], "followups_pending": [],
           "needs_attention": []}
    for e in entries:
        i, st = e.get("index"), e.get("status")
        if i is None:
            continue
        idx["next_index"] = max(idx["next_index"], i + 1)
        if st in DRAFTED:
            idx["drafted_only"].append(i)
        elif st in PENDING:
            idx["followups_pending"].append(i)
            if not has_date(e):
                idx["needs_attention"].append(i)
    return idx


def load_index(entries=None):
    if os.path.exists(INDEX):
        with open(INDEX) as f:
            return json.load(f)
    idx = build_index(entries if entries is not None else load_log())
    save_index(idx)
    return idx


def by_index(entries):
    return {e.get("index"): e for e in entries if e.get("index") is not None}


def reindex(idx, touched, status, dated=True):
    """Place the touched indexes from the status just written. Nothing is
    re-derived by scanning the log — only --rebuild-index does that."""
    for i in touched:
        for k in ("drafted_only", "followups_pending", "needs_attention"):
            if i in idx.get(k, []):
                idx[k].remove(i)
        if status in DRAFTED:
            idx["drafted_only"].append(i)
        elif status in PENDING:
            idx["followups_pending"].append(i)
            if not dated:
                idx["needs_attention"].append(i)
    for k in idx:
        if k != "next_index":
            idx[k] = sorted(set(idx[k]))
    return idx


def table(entries, indexes, title):
    m = by_index(entries)
    rows = sorted((m[i] for i in indexes if i in m),
                  key=lambda e: (not has_date(e), e.get("followup_date") or "",
                                 e.get("index") or 0))
    if not rows:
        print(f"{title}: none")
        return
    print(f"{title} ({len(rows)})")
    print(f"{'IDX':>4}  {'NAME':<24}{'COMPANY':<26}{'TYPE':<20}{'SENT':<12}{'FOLLOWUP':<12}")
    print("-" * 100)
    for e in rows:
        print(f"{e.get('index'):>4}  "
              f"{str(e.get('target_name') or '?')[:23]:<24}"
              f"{str(e.get('target_company') or '?')[:25]:<26}"
              f"{str(e.get('type') or '')[:19]:<20}"
              f"{str(e.get('date_sent') or e.get('date_drafted') or '-'):<12}"
              f"{(e.get('followup_date') if has_date(e) else 'NO DATE'):<12}")


def parse_ids(s):
    out = []
    for part in str(s).replace("[", "").replace("]", "").split(","):
        part = part.strip()
        if part:
            out.append(int(part))
    return out


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--count", action="store_true")
    p.add_argument("--obtain-pending", action="store_true")
    p.add_argument("--obtain-drafts", action="store_true")
    p.add_argument("--get-notes")
    p.add_argument("--add")
    p.add_argument("--set-status")
    p.add_argument("--status")
    p.add_argument("--delete")
    p.add_argument("--rebuild-index", action="store_true")
    a = p.parse_args()

    entries = load_log()

    if a.rebuild_index:
        idx = build_index(entries)
        save_index(idx)
        print(f"REBUILT {INDEX}")
        for k, v in idx.items():
            print(f"  {k}: {v if k == 'next_index' else len(v)}")
        return 0

    idx = load_index(entries)

    if a.count:
        print(f"FOLLOWUPS={len(idx.get('followups_pending', []))} "
              f"DRAFTS={len(idx.get('drafted_only', []))}")
        return 0

    if a.obtain_pending:
        table(entries, idx.get("followups_pending", []), "FOLLOWUPS PENDING")
        na = idx.get("needs_attention", [])
        if na:
            print(f"\n{len(na)} have no real followup_date (indexes: "
                  f"{','.join(map(str, na))}) — set one with --set-status")
        return 0

    if a.obtain_drafts:
        table(entries, idx.get("drafted_only", []), "DRAFTED, NOT SENT")
        return 0

    if a.get_notes:
        m = by_index(entries)
        for i in parse_ids(a.get_notes):
            e = m.get(i)
            if not e:
                print(f"[{i}] NOT FOUND")
                continue
            print(f"[{i}] {e.get('target_name')} @ {e.get('target_company')} "
                  f"({e.get('status')}, {e.get('type')})")
            print(f"  role    : {e.get('role_applied')}")
            print(f"  subject : {e.get('subject')}")
            print(f"  hook    : {e.get('hook_used')}")
            print(f"  notes   : {e.get('notes')}")
            print()
        return 0

    if a.add:
        e = json.loads(a.add)
        if e.get("status") and e["status"] not in VALID:
            print(f"ERROR: bad status {e['status']!r}; one of {sorted(VALID)}", file=sys.stderr)
            return 2
        e.setdefault("status", "drafted")
        e.setdefault("date_drafted", date.today().isoformat())
        nxt = idx.get("next_index") or 1
        e = {"index": nxt, **{k: v for k, v in e.items() if k != "index"}}
        entries.append(e)
        idx["next_index"] = nxt + 1
        save_log(entries)
        e.setdefault("followup_date", NO_DATE)
        save_index(reindex(idx, [nxt], e["status"], has_date(e)))
        print(f"ADDED index={nxt} status={e['status']} "
              f"{e.get('target_name')} @ {e.get('target_company')}")
        return 0

    if a.set_status:
        if not a.status:
            print("ERROR: --set-status needs --status", file=sys.stderr)
            return 2
        if a.status not in VALID:
            print(f"ERROR: bad status {a.status!r}; one of {sorted(VALID)}", file=sys.stderr)
            return 2
        ids, m = parse_ids(a.set_status), by_index(entries)
        missing = [i for i in ids if i not in m]
        if missing:
            print(f"ERROR: no such index: {missing}", file=sys.stderr)
            return 2
        for i in ids:
            m[i]["status"] = a.status
            if a.status == "sent":
                m[i].setdefault("date_sent", date.today().isoformat())
            if a.status == "followed_up_1_sent":
                m[i]["followup_sent_date"] = date.today().isoformat()
        save_log(entries)
        save_index(reindex(idx, ids, a.status, all(has_date(m[i]) for i in ids)))
        print(f"SET status={a.status} for {ids}")
        return 0

    if a.delete:
        ids, m = parse_ids(a.delete), by_index(entries)
        missing = [i for i in ids if i not in m]
        if missing:
            print(f"ERROR: no such index: {missing}", file=sys.stderr)
            return 2
        for i in ids:
            m[i]["status"] = "deleted"
        save_log(entries)
        save_index(reindex(idx, ids, "deleted"))
        print(f"DELETED (soft, entry kept) {ids}")
        return 0

    p.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
