#!/usr/bin/env python3
"""
prescreen_jd.py — the hard-blocker module: scan a JD for disqualifiers (A2.5),
record a blocker the regexes missed (A5), list the patterns.
Zero LLM calls. Zero tokens. The patterns live in references/hard_blockers.json,
never in this file, so neither the model nor a person edits code to teach it.

Usage:
  echo "<jd text>" | python3 prescreen_jd.py [--region auto|us|eu]     # check (A2.5)
  python3 prescreen_jd.py < jd.txt
  python3 prescreen_jd.py "<jd text as arg>"
  python3 prescreen_jd.py add --category <itar|clearance|citizenship|sponsorship>
          --regex '<python regex, matched on the lowercased JD>'
          --example '<the exact JD sentence it must catch>'
          --source '<Company, "Role", place, req id, YYYY-MM-DD>'
          [--note '<why the existing regexes missed it>']
          [--phrase '<wording to append to the candidate_context.md list>']
          [--dry-run]                                                    # record (A5)
  python3 prescreen_jd.py list [--notes]                                 # show patterns

Check exit codes:
  0 — clean, no blockers found, proceed with analysis
  1 — hard blocker found, print reason, STOP everything
  2 — no JD text

Check output on exit 1:
  BLOCK:<category>:<exact_match>
  e.g. BLOCK:Security Clearance:secret clearance

add — one call does what used to take a Read and an Edit of this script plus a
Read and an Edit of candidate_context.md:
  1. checks the regex compiles and matches --example (lowercased), and that no
     existing pattern already blocks --example (exit 3, nothing written);
  2. appends the regex, with a provenance note, to its category in
     hard_blockers.json;
  3. with --phrase, appends the phrase to that category's list in
     candidate_context.md (no_sponsorship_phrases, itar_ear_phrases,
     clearance_phrases, citizenship_phrases) and an "# Also caught manually:"
     note under the list, in the same style as the existing ones;
  4. re-scans --example and prints the BLOCK line it now produces.
Both files are written atomically, and only after every check passes.
add exit codes: 0 added (or would add, with --dry-run) · 2 bad input · 3 already blocked / duplicate

MAINTAINER NOTE — teach the scanner with `add`, not the analysis workflow:
  If a job slips through and is later found to be disqualifying (wrong visa,
  clearance, citizenship, or no-sponsorship), record it with `add`. This script
  runs before any LLM call — every phrase caught here saves a full analysis run.
"""

import argparse
import json
import os
import re
import sys
import textwrap

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCKERS_PATH = os.path.join(SKILL, "references", "hard_blockers.json")
CONTEXT_PATH = os.path.join(SKILL, "references", "candidate_context.md")


# ── Region detection (added 2026-09-23) ───────────────────────────────────────
# Justin now applies to EU/UK roles as well as US ones. The four HARD_BLOCKERS
# categories below were all written against US postings. Three of the
# "No Sponsorship" patterns are phrased generically enough that they also fire on
# ordinary EU/UK boilerplate ("must be legally authorised to work in Ireland"),
# which is exactly the permission an EU employer would be sponsoring him FOR.
# Those three are skipped when the posting is clearly EU/UK.
#
# Everything else still fires everywhere, deliberately:
#   - explicit "no sponsorship" / "sponsorship is not available" — a real block
#     in Dublin just as much as in Dallas
#   - "citizens only" — on an EU posting this means EU citizens, still a block
#   - ITAR / export control / security clearance — EU defence primes (Thales,
#     Saab, Leonardo, BAE) gate on EU/NATO nationality and clearance the same way
#
# Detection fails SAFE: relaxation applies only when there is positive EU/UK
# evidence AND no US marker. Anything ambiguous keeps the old strict behaviour.

def _load():
    with open(BLOCKERS_PATH, encoding="utf-8") as f:
        return json.load(f)


_DATA = _load()
EU_UK_HINTS = list(_DATA["eu_uk_hints"])
US_HINTS = list(_DATA["us_hints"])
# Patterns skipped when the posting is EU/UK. Must match HARD_BLOCKERS verbatim.
RELAXED_IN_EU_UK = set(_DATA["relaxed_in_eu_uk"])
HARD_BLOCKERS = {cat: [p["regex"] for p in pats] for cat, pats in _DATA["categories"].items()}


def detect_region(lowered: str) -> str:
    """'eu_uk' only on positive EU/UK evidence with no US marker; else 'us'."""
    if any(re.search(p, lowered) for p in US_HINTS):
        return "us"
    if any(re.search(p, lowered) for p in EU_UK_HINTS):
        return "eu_uk"
    return "us"


def scan(text: str, region: str | None = None) -> tuple[str | None, str | None, str | None]:
    """
    Returns (category, pattern, matched_text) if blocker found, else (None, None, None).
    Stops at first match.

    region: "us" | "eu_uk" | None (auto-detect). Callers that pass nothing keep
    the original behaviour on US postings; keyword_prefilter.py relies on this.
    """
    lowered = text.lower()
    if region is None:
        region = detect_region(lowered)
    for category, patterns in HARD_BLOCKERS.items():
        for pattern in patterns:
            if region == "eu_uk" and pattern in RELAXED_IN_EU_UK:
                continue
            m = re.search(pattern, lowered)
            if m:
                return category, pattern, m.group(0)
    return None, None, None


# ── add / list ────────────────────────────────────────────────────────────────

CATEGORY_ALIASES = {
    "itar": "ITAR / US Person",
    "clearance": "Security Clearance",
    "citizenship": "US Citizenship / PR Required",
    "sponsorship": "No Sponsorship",
}
CONTEXT_LIST = {
    "ITAR / US Person": "itar_ear_phrases",
    "Security Clearance": "clearance_phrases",
    "US Citizenship / PR Required": "citizenship_phrases",
    "No Sponsorship": "no_sponsorship_phrases",
}
KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*=")


def _resolve_category(name):
    if name in HARD_BLOCKERS:
        return name
    return CATEGORY_ALIASES.get((name or "").strip().lower())


def _context_with_catch(text, list_key, phrase, note_lines):
    """candidate_context.md with `phrase` appended to `list_key`'s comma list and
    `note_lines` inserted after the comment lines that follow that list. The list
    ends where keyword_prefilter.py's extract_list() ends it: at a blank line, a
    `#` line, a [section] or the next `key =` line."""
    lines = text.split("\n")
    start = next((i for i, l in enumerate(lines) if re.match(rf"^{re.escape(list_key)}\s*=", l)), None)
    if start is None:
        raise ValueError(f"{list_key} not found in candidate_context.md")
    end = start
    j = start + 1
    while (j < len(lines) and lines[j].strip() and not lines[j].lstrip().startswith("#")
           and not lines[j].startswith("[") and not KEY_RE.match(lines[j])):
        end = j
        j += 1
    if phrase:
        lines[end] = lines[end].rstrip() + ", " + phrase
    k = end + 1
    while k < len(lines) and lines[k].lstrip().startswith("#"):
        k += 1
    lines[k:k] = note_lines
    return "\n".join(lines)


def _write_atomic(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def cmd_add(a):
    global _DATA, HARD_BLOCKERS
    cat = _resolve_category(a.category)
    if not cat:
        print(f"ERROR: unknown --category {a.category!r}; use one of "
              f"{', '.join(CATEGORY_ALIASES)} or a full name: {', '.join(HARD_BLOCKERS)}", file=sys.stderr)
        return 2
    try:
        rx = re.compile(a.regex)
    except re.error as e:
        print(f"ERROR: --regex does not compile: {e}", file=sys.stderr)
        return 2
    example = " ".join(a.example.split())
    if not rx.search(example.lower()):
        print("ERROR: --regex does not match --example (it is matched against the lowercased text)",
              file=sys.stderr)
        return 2
    if a.regex in HARD_BLOCKERS[cat]:
        print(f"ALREADY PRESENT: that exact regex is already in {cat}; nothing written")
        return 3
    hit_cat, hit_pat, hit = scan(example)
    if hit_cat:
        print(f"ALREADY BLOCKED: BLOCK:{hit_cat}:{hit} (pattern {hit_pat}); nothing written")
        return 3
    phrase = " ".join((a.phrase or "").lower().split())
    if phrase and ("," in phrase or "#" in phrase):
        print("ERROR: --phrase cannot contain a comma or # (the list is comma-separated)", file=sys.stderr)
        return 2
    note = f"Caught manually in A5: {a.source} — \"{example}\"" + (f" {a.note.strip()}" if a.note else "")

    data = _load()
    data["categories"][cat].append({"regex": a.regex, "note": note})
    new_json = json.dumps(data, indent=2, ensure_ascii=False) + "\n"

    list_key = CONTEXT_LIST[cat]
    context = open(CONTEXT_PATH, encoding="utf-8").read()
    new_context = None
    if phrase:
        listed = re.search(rf"^{re.escape(list_key)}\s*=(.*?)(?=\n\s*\n|\n\s*#|\n\[|\n[A-Za-z_]\w*\s*=|\Z)",
                           context, re.M | re.S)
        current = [p.strip().lower() for p in " ".join(listed.group(1).split()).split(",")] if listed else []
        text = (f"Also caught manually: {a.source} — \"{example}\""
                + (f" {a.note.strip()}" if a.note else "")
                + " Regex added to hard_blockers.json with prescreen_jd.py add.")
        note_lines = ["# " + w for w in textwrap.wrap(text, width=106, break_long_words=False,
                                                      break_on_hyphens=False)]
        new_context = _context_with_catch(context, list_key, "" if phrase in current else phrase, note_lines)

    print(f"category : {cat} (pattern #{len(data['categories'][cat])})")
    print(f"regex    : {a.regex}")
    if new_context is not None:
        print(f"context  : {list_key} += {phrase!r}" + (" (already listed; note only)" if phrase in current else ""))
    if a.dry_run:
        print("DRY RUN — nothing written")
        return 0
    _write_atomic(BLOCKERS_PATH, new_json)
    if new_context is not None:
        _write_atomic(CONTEXT_PATH, new_context)
    # reload and prove the new pattern catches the sentence
    _DATA = _load()
    HARD_BLOCKERS = {c: [p["regex"] for p in pats] for c, pats in _DATA["categories"].items()}
    c2, _, hit2 = scan(example)
    print(f"check    : BLOCK:{c2}:{hit2}" if c2 else "check    : NOT BLOCKED — investigate")
    return 0 if c2 else 1


def cmd_list(a):
    for cat, pats in _DATA["categories"].items():
        print(f"{cat} ({len(pats)})")
        for i, p in enumerate(pats, 1):
            relaxed = "  [skipped on EU/UK postings]" if p["regex"] in RELAXED_IN_EU_UK else ""
            print(f"  {i:>2}. {p['regex']}{relaxed}")
            if a.notes and p.get("note"):
                for w in textwrap.wrap(p["note"], width=100):
                    print(f"        {w}")
    return 0


def main():
    if sys.argv[1:2] in (["add"], ["list"]):
        ap = argparse.ArgumentParser(prog=f"prescreen_jd.py {sys.argv[1]}")
        if sys.argv[1] == "add":
            ap.add_argument("--category", required=True)
            ap.add_argument("--regex", required=True)
            ap.add_argument("--example", required=True)
            ap.add_argument("--source", required=True)
            ap.add_argument("--note")
            ap.add_argument("--phrase")
            ap.add_argument("--dry-run", action="store_true")
            sys.exit(cmd_add(ap.parse_args(sys.argv[2:])))
        ap.add_argument("--notes", action="store_true")
        sys.exit(cmd_list(ap.parse_args(sys.argv[2:])))

    # Accept JD text from stdin or as first argument.
    # --region auto|us|eu overrides detection; auto is the default.
    argv = sys.argv[1:]
    region = None
    for flag in ("--region", "-r"):
        if flag in argv:
            i = argv.index(flag)
            val = argv[i + 1] if i + 1 < len(argv) else "auto"
            region = {"eu": "eu_uk", "uk": "eu_uk", "eu_uk": "eu_uk",
                      "us": "us", "auto": None}.get(val.lower(), None)
            del argv[i:i + 2]
            break

    jd_text = argv[0] if argv else sys.stdin.read()

    if not jd_text.strip():
        print("ERROR: No JD text provided", file=sys.stderr)
        sys.exit(2)

    print(f"region={region or detect_region(jd_text.lower())}", file=sys.stderr)
    category, pattern, matched = scan(jd_text, region)

    if category:
        # Machine-readable line for the skill to parse
        print(f"BLOCK:{category}:{matched}")
        sys.exit(1)
    else:
        print("CLEAR")
        sys.exit(0)


if __name__ == "__main__":
    if sys.argv[1:2] in (['-h'], ['--help']):   # usage, no side effects
        print(__doc__)
        sys.exit(0)
    main()
