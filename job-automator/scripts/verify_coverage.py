#!/usr/bin/env python3
"""
verify_coverage.py — ATS keyword coverage check for a tailored resume.

Answers the question the pipeline never asked: did the keywords we TOLD the
model to mirror actually land in the resume?

The useful part is the SPLIT of what's missing:
  - FIXABLE : the master profile backs this somewhere, but the tailored
              resume dropped it -> you can surface it.
  - CEILING : nothing in the master profile backs it -> this is your real
              ceiling for this role, worth knowing BEFORE you apply.

Usage:
  python3 verify_coverage.py <fit.json> <tailored.json> [--json]

Exit codes:
  0 — all keywords covered
  1 — some keywords uncovered (see report)
  2 — error (bad/missing input)
"""

import json
import os
import re
import sys

# Resolve this skill's own references/ dir from __file__ so the script works
# identically regardless of where the skill dir lives or is renamed to.
_REFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")

PROFILE_PATH = os.path.expanduser(
    os.path.join(_REFS, "master_profile.json")
)


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_match import match as skill_match  # noqa: E402


def norm(s: str) -> str:
    """Lowercase, strip punctuation/extra space, drop parenthetical asides."""
    s = s.lower()
    s = re.sub(r"\([^)]*\)", " ", s)          # "(not in profile)" etc.
    s = re.sub(r"[^a-z0-9+#./ -]", " ", s)    # keep c++, c#, ci/cd, node.js
    return re.sub(r"\s+", " ", s).strip()


def collect_text(obj) -> str:
    """Flatten every string in a nested JSON structure into one blob."""
    out = []

    def walk(o):
        if isinstance(o, str):
            out.append(o)
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(obj)
    return norm(" ".join(out))


# Well-known ATS equivalences. Deliberately small — only pairs that are
# genuinely the same skill, not a guessed thesaurus.
SYNONYMS = {
    "object-oriented": ["oop", "object oriented"],
    "oop": ["object-oriented", "object oriented"],
    "ci/cd": ["cicd", "continuous integration"],
    "k8s": ["kubernetes"],
    "kubernetes": ["k8s"],
    "ml": ["machine learning"],
    "machine learning": ["ml"],
}


def _match_one(k: str, blob: str) -> bool:
    if not k:
        return False
    if " " in k:                      # multi-word: contiguous substring
        return k in blob
    if len(k) >= 4:
        # Long single tokens may live inside a compound: rtos ⊂ freertos,
        # sql ⊄ ... . This is the common ATS case and its absence produced a
        # false "CEILING: RTOS" when the profile clearly had FreeRTOS.
        return k in blob
    # Short tokens (c, ai, ml, go) — strict boundary so 'c' ≠ 'cuda'.
    return re.search(rf"(?<![a-z0-9]){re.escape(k)}(?![a-z0-9])", blob) is not None


def covered(keyword: str, blob: str) -> bool:
    """True if the keyword — or a known synonym — appears in the blob."""
    k = norm(keyword)
    if _match_one(k, blob):
        return True
    return any(_match_one(norm(s), blob) for s in SYNONYMS.get(k, []))


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    as_json = "--json" in sys.argv
    if len(args) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    fit_path, tailored_path = args[0], args[1]
    for p in (fit_path, tailored_path):
        if not os.path.exists(p):
            print(f"ERROR: not found: {p}", file=sys.stderr)
            return 2

    try:
        fit = json.load(open(fit_path))
        tailored = json.load(open(tailored_path))
        profile = json.load(open(PROFILE_PATH))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # What the JD asked for. De-dupe case-insensitively, keep first spelling.
    wanted, seen = [], set()
    for k in (fit.get("top_ats_keywords") or []) + (fit.get("required_skills") or []):
        if isinstance(k, str) and k.strip() and norm(k) not in seen:
            seen.add(norm(k))
            wanted.append(k.strip())

    if not wanted:
        print("No ATS keywords in fit.json — nothing to verify.")
        return 0

    resume_blob = collect_text(tailored)
    profile_blob = collect_text(profile)

    # FIXABLE vs CEILING is decided by the canonical skills DB, not by whether
    # the profile text happens to contain the JD's exact wording. The old
    # string check called 8 Analog Devices keywords "CEILING — do NOT invent"
    # when every one of them was backed (Shell scripting->Bash,
    # debugging tools->oscilloscopes/logic analyzers, compiler->CMake). That
    # told Justin to stop at 58% on a role he fully matches.
    present, fixable, ceiling = [], [], []
    for k in wanted:
        if covered(k, resume_blob):
            present.append(k)
            continue
        m = skill_match(k)
        if (m and m["credit"] > 0) or covered(k, profile_blob):
            fixable.append({"keyword": k,
                            "have_as": (m or {}).get("canonical"),
                            "depth": (m or {}).get("depth")} if m else
                           {"keyword": k, "have_as": None, "depth": None})
        else:
            ceiling.append(k)          # genuinely unbacked

    pct = round(100 * len(present) / len(wanted))
    result = {
        "total": len(wanted), "covered": len(present), "coverage_pct": pct,
        "present": present, "fixable": fixable, "ceiling": ceiling,
    }

    if as_json:
        print(json.dumps(result, indent=2))
        return 0 if not (fixable or ceiling) else 1

    print(f"COVERAGE: {len(present)}/{len(wanted)} ATS keywords present ({pct}%)")
    if fixable:
        print(f"\n  🔧 FIXABLE ({len(fixable)}) — backed by master_profile, "
              f"but dropped from this resume:")
        for k in fixable:
            if k.get("have_as"):
                print(f"       • {k['keyword']:<38} you have it as: "
                      f"{k['have_as']} ({k['depth']})")
            else:
                print(f"       • {k['keyword']}")
        print("     → surface these: use the JD's wording for a skill you already have.")
    if ceiling:
        print(f"\n  🚧 CEILING ({len(ceiling)}) — nothing in master_profile backs these:")
        for k in ceiling:
            print(f"       • {k}")
        print("     → this is your real ceiling for this role. Do NOT invent them.")
    if not fixable and not ceiling:
        print("\n  ✅ Every ATS keyword is present in the tailored resume.")

    return 0 if not (fixable or ceiling) else 1


if __name__ == "__main__":
    sys.exit(main())
