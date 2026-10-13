#!/usr/bin/env python3
"""
Zero-LLM-token prefilter: scores a list of postings (from resolve_ats_roles.py
or paginate_scrape.py) against job-automator's keywords_only.json, and applies
the same hard-blocker / seniority checks as job-automator's A2.5/A4/A5, so only
plausible, eligible roles get passed on to expensive (even free-model) delegate
analysis at all.

Usage:
    python3 keyword_prefilter.py <postings.json> [--min-score N] [--top N]

<postings.json> must have a top-level "postings" list, each with at least
"title" and (ideally) "jd_text" — the output of resolve_ats_roles.py or
paginate_scrape.py works directly.

Output (stdout): JSON list of surviving postings, each augmented with:
  score, hard_blocked (bool), hard_block_reason, seniority_flag
sorted by score descending. Hard-blocked roles are EXCLUDED entirely (never
worth even a free-model call). Senior-titled roles are kept but flagged.

HARD-BLOCKER CHECK: delegates to prescreen_jd.py (same directory) rather than
maintaining its own phrase list. There used to be two separate implementations
of "detect ITAR/clearance/citizenship/no-sponsorship" here — this script's own
substring match against candidate_context.md, and prescreen_jd.py's regex list
(the one job-automator's SKILL.md actually names as canonical, A2.5, and the
one that gets updated when a new disqualifying phrase is caught live). Two
implementations of a safety-critical filter drift: a phrase added to
prescreen_jd.py's list did not protect this script's shortlist. Fixed by
calling the one true implementation instead of re-deriving it.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prescreen_jd import scan as prescreen_scan  # noqa: E402


SENIOR_TITLE_MARKERS = [
    "senior", "sr.", "staff", "lead ", "principal", "director", "manager",
    "vp ", "head of", "chief", "president",
]


def load_sponsorship_context(path: str) -> dict:
    """Only the soft sponsorship signal lives here now — a company-reputation
    check (known_sponsors) that prescreen_jd.py's phrase-only regex can't do.
    Explicit disqualifying phrases are prescreen_jd.py's job entirely.

    candidate_context.md is soft-wrapped prose, not valid INI (continuation
    lines aren't indented, so configparser.ConfigParser().read() throws
    ParsingError on it — a pre-existing bug this script never actually hit
    until tested end-to-end here). score_fit.py sidesteps this with its own
    regex line-scan; this does the equivalent for a comma-list value that may
    wrap across an unindented line, by capturing from the key up to the next
    blank line, `[section]` header, or new `key =` line."""
    text = open(path).read()
    def extract_list(key):
        m = re.search(
            rf"^{re.escape(key)}\s*=\s*(.+?)(?=\n\s*\n|\n\[|\n[A-Za-z_][A-Za-z0-9_]*\s*=|\Z)",
            text, re.MULTILINE | re.DOTALL,
        )
        if not m:
            return []
        raw = " ".join(m.group(1).split())  # collapse the embedded newline(s)
        return [s.strip().lower() for s in raw.split(",") if s.strip()]
    return {"no_sponsorship_phrases": extract_list("no_sponsorship_phrases")}


def score_posting(title: str, jd_text: str, core_keywords: list, broad_keywords: list):
    """Returns (core_hits, score). core_hits gates eligibility; score ranks.

    `all_keywords` in keywords_only.json is auto-extracted from resume prose and
    includes non-technical fragments ("Background", "Benchmarked", "Comfortable")
    that are harmless for an LLM classifier (job-automator's A4) but produce
    false-positive matches under blind substring counting. `core_keywords` (the
    actual named skills from master_profile.json's `skills` dict) is clean by
    construction, so it gates whether a role is even a candidate at all; the
    broader list only adds resolution among roles that already cleared that gate.
    """
    text = f"{title}\n{jd_text or ''}".lower()
    core_hits = sum(1 for kw in core_keywords if kw.lower() in text)
    broad_hits = sum(1 for kw in broad_keywords if kw.lower() in text)
    score = core_hits * 3 + broad_hits
    return core_hits, score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("postings_file")
    ap.add_argument("--keywords", default=None,
                     help="path to keywords_only.json (default: job-automator's)")
    ap.add_argument("--profile", default=None,
                     help="path to master_profile.json, for the curated core-skills gate")
    ap.add_argument("--context", default=None,
                     help="path to candidate_context.md (default: job-automator's)")
    ap.add_argument("--min-core-hits", type=int, default=2,
                     help="a role must hit at least this many CURATED skills to be eligible at all")
    ap.add_argument("--top", type=int, default=None, help="cap the shortlist to top N by score")
    args = ap.parse_args()

    keywords_path = args.keywords or os.path.expanduser(
        "~/.claude/skills/job-automator/references/keywords_only.json")
    profile_path = args.profile or os.path.expanduser(
        "~/.claude/skills/job-automator/references/master_profile.json")
    context_path = args.context or os.path.expanduser(
        "~/.claude/skills/job-automator/references/candidate_context.md")

    kw_data = json.load(open(keywords_path))
    broad_keywords = kw_data["all_keywords"]
    profile = json.load(open(profile_path))
    core_keywords = [s for group in profile["skills"].values() for s in group]
    ctx = load_sponsorship_context(context_path)

    data = json.load(open(args.postings_file))
    postings = data.get("postings", data if isinstance(data, list) else [])

    scored = []
    for p in postings:
        title = p.get("title", "")
        jd_text = p.get("jd_text", "") or ""
        full_text = f"{title}\n{jd_text}".lower()

        category, _pattern, matched = prescreen_scan(full_text)
        if category:
            continue  # hard-blocked roles are dropped entirely, never delegated

        sponsorship_flag = any(ph in full_text for ph in ctx["no_sponsorship_phrases"])
        senior_flag = any(m in title.lower() for m in SENIOR_TITLE_MARKERS)
        core_hits, score = score_posting(title, jd_text, core_keywords, broad_keywords)

        if core_hits < args.min_core_hits:
            continue

        scored.append({
            **p,
            "score": score,
            "core_hits": core_hits,
            "seniority_flag": senior_flag,
            "sponsorship_flag": sponsorship_flag,
        })

    scored.sort(key=lambda r: r["score"], reverse=True)
    if args.top:
        scored = scored[:args.top]

    print(json.dumps({"count": len(scored), "postings": scored}, indent=2))


if __name__ == "__main__":
    main()
