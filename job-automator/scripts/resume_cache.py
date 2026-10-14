#!/usr/bin/env python3
"""
resume_cache.py — Keyword-hash based resume reuse system.
Checks if a resume already exists for a given set of ATS keywords.
Indexes new resumes after generation.

Usage:
  python resume_cache.py check  <fit_analysis.json>
  python resume_cache.py index  <fit_analysis.json> <job_dir> <pdf_path> <tex_path>
  python resume_cache.py list

Exit codes (check):
  0 — CACHE_HIT  : matching resume found, path on stdout
  1 — CACHE_MISS : no matching resume, proceed with tailoring
  2 — error

Exit codes (index):
  0 — indexed successfully
  1 — error
"""

import json
import sys
import os
import hashlib
import shutil
from datetime import datetime

# Resolve this skill's own references/ dir from __file__ so the script works
# identically regardless of where the skill dir lives or is renamed to.
_REFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")

INDEX_PATH = os.path.expanduser(
    os.path.join(_REFS, "resume_index.json")
)
PROFILE_PATH = os.path.expanduser(
    os.path.join(_REFS, "master_profile.json")
)


# Bump when generate_pdf.py changes what every resume renders (e.g. the header), so cached PDFs built with
# the old layout stop matching. v2 (2026-10-12): portfolio URL replaces LinkedIn in the header.
LAYOUT_VERSION = "v2-portfolio-header"


def profile_hash() -> str:
    """
    Hash the current master_profile.json contents.

    Folded into the cache key so ANY edit to the profile invalidates every
    cached resume. Without this, editing the profile (e.g. removing an
    undefendable claim, adding a new project) would silently keep serving
    resumes built from the OLD profile — shipping the removed claim into a
    live application.
    """
    try:
        with open(PROFILE_PATH, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        # No profile readable → unique value so nothing can cache-hit.
        return "noprofile"


def keyword_hash(keywords: list[str]) -> str:
    """
    Hash a list of ATS keywords TOGETHER WITH the current master profile.
    Sort + lowercase + join → SHA256, salted with the profile hash.
    Same keyword set + same profile always produces the same hash.
    """
    normalized = sorted(set(k.strip().lower() for k in keywords if k.strip()))
    joined = " | ".join(normalized) + " || profile:" + profile_hash() + " || layout:" + LAYOUT_VERSION
    return hashlib.sha256(joined.encode()).hexdigest()[:16]  # 16 chars is enough


def load_index() -> dict:
    if not os.path.exists(INDEX_PATH):
        return {"entries": {}}
    try:
        return json.load(open(INDEX_PATH))
    except (json.JSONDecodeError, OSError):
        return {"entries": {}}


def save_index(index: dict):
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)


def get_keywords_from_fit(fit_path: str) -> list[str]:
    fit = json.load(open(fit_path))
    # Use ATS keywords + required skills that were matched (Have + Adjacent)
    # These define what the resume needs to contain
    keywords = (
        fit.get("top_ats_keywords", []) +
        fit.get("missing_skills", [])   # include these so near-matches count
    )
    return [k for k in keywords if k.strip()]


def cmd_check(fit_path: str):
    if not os.path.exists(fit_path):
        print(f"ERROR: fit analysis not found: {fit_path}", file=sys.stderr)
        sys.exit(2)

    keywords = get_keywords_from_fit(fit_path)
    if not keywords:
        print("CACHE_MISS (no keywords in fit analysis)")
        sys.exit(1)

    h = keyword_hash(keywords)
    index = load_index()

    if h not in index["entries"]:
        print(f"CACHE_MISS (hash: {h})")
        sys.exit(1)

    entry = index["entries"][h]
    pdf   = os.path.expanduser(entry["pdf_path"])
    tex   = os.path.expanduser(entry["tex_path"])

    # Verify the files still exist
    if not os.path.exists(pdf):
        print(f"CACHE_MISS (indexed resume no longer exists: {pdf})")
        del index["entries"][h]
        save_index(index)
        sys.exit(1)

    # Print machine-readable match info
    print(f"CACHE_HIT")
    print(f"HASH={h}")
    print(f"PDF={pdf}")
    print(f"TEX={tex}")
    print(f"COMPANY={entry['company']}")
    print(f"ROLE={entry['role']}")
    print(f"DATE={entry['timestamp'][:10]}")
    print(f"KEYWORDS={len(entry['keywords'])}")
    sys.exit(0)


def cmd_index(fit_path: str, job_dir: str, pdf_path: str, tex_path: str):
    if not os.path.exists(fit_path):
        print(f"ERROR: fit analysis not found: {fit_path}", file=sys.stderr)
        sys.exit(1)

    fit      = json.load(open(fit_path))
    keywords = get_keywords_from_fit(fit_path)

    if not keywords:
        print("SKIP (no keywords to index)")
        sys.exit(0)

    h     = keyword_hash(keywords)
    index = load_index()

    entry = {
        "hash"      : h,
        "keywords"  : sorted(set(k.strip().lower() for k in keywords)),
        "pdf_path"  : os.path.expanduser(pdf_path),
        "tex_path"  : os.path.expanduser(tex_path),
        "job_dir"   : os.path.expanduser(job_dir),
        "company"   : fit.get("company", ""),
        "role"      : fit.get("role", ""),
        "timestamp" : datetime.now().isoformat(),
    }

    index["entries"][h] = entry
    save_index(index)
    print(f"INDEXED (hash: {h}, {len(keywords)} keywords)")
    sys.exit(0)


def cmd_list():
    index = load_index()
    entries = index.get("entries", {})
    if not entries:
        print("No resumes indexed yet.")
        return

    print(f"\n{'─'*64}")
    print(f"  RESUME INDEX  ({len(entries)} entries)")
    print(f"{'─'*64}")
    for h, e in sorted(entries.items(), key=lambda x: x[1]["timestamp"], reverse=True):
        pdf_exists = "✅" if os.path.exists(os.path.expanduser(e["pdf_path"])) else "❌ missing"
        print(f"  {e['timestamp'][:10]}  {e['company']} — {e['role']}")
        print(f"  Hash: {h}  Keywords: {e.get('keywords_count', len(e['keywords']))}  PDF: {pdf_exists}")
        print(f"  {e['pdf_path']}")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    cmd = sys.argv[1]

    if cmd == "check" and len(sys.argv) >= 3:
        cmd_check(sys.argv[2])

    elif cmd == "index" and len(sys.argv) >= 6:
        cmd_index(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])

    elif cmd == "list":
        cmd_list()

    else:
        print(f"ERROR: unknown command or missing args", file=sys.stderr)
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    if sys.argv[1:2] in (['-h'], ['--help']):   # usage, no side effects
        print(__doc__)
        sys.exit(0)
    main()
