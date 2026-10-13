#!/usr/bin/env python3
"""
build_skills_db.py — joins the CURATED alias layer to the GENERATED evidence layer.

  references/skill_aliases.json  (curated, hand-maintained, survives rebuilds)
      canonical -> {aliases, depth}
  references/master_profile.json (source of truth)
      the bullets/skills that actually back each canonical
                |
                v
  references/skills_db.json      (generated, keyed by source_hash)

Why two files: regenerating wiped hand-written aliases when they lived in one
file. The curated layer is never written by this script.

Two reports, both of which are the point:
  ORPHAN  — a canonical with no evidence in the profile. Either the profile
            changed or the claim was never backed. Shown, never auto-deleted.
  UNMAPPED— a profile skill term no canonical covers. These are the DB holes
            that make a role look worse than it is.

Usage: python3 build_skills_db.py [--check]
  --check  exit 1 if stale, write nothing (for hooks/CI)

Exit: 0 ok/up-to-date · 1 stale under --check, or error
"""

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_match import match, norm, toks  # noqa: E402

_REFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")
PROFILE = os.path.join(_REFS, "master_profile.json")
ALIASES = os.path.join(_REFS, "skill_aliases.json")
OUT = os.path.join(_REFS, "skills_db.json")


def file_hash(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def combined_hash():
    return hashlib.sha256((file_hash(PROFILE) + file_hash(ALIASES)).encode()).hexdigest()


def evidence_for(canon, spec, profile):
    """Which profile items mention this canonical or any of its aliases."""
    forms = [canon] + list(spec.get("aliases") or [])
    keys = {" ".join(toks(f)) for f in forms if toks(f)}
    hits = []

    def scan(label, text):
        blob = f" {' '.join(toks(text))} "
        for k in keys:
            if k and f" {k} " in blob:
                hits.append(label)
                return

    for p in profile.get("projects", []):
        scan(f"project:{p.get('name','?')}", p.get("name", "") + " " + " ".join(p.get("bullets", [])))
    for e in profile.get("experience", []):
        scan(f"experience:{e.get('title','?')}", e.get("title", "") + " " + " ".join(e.get("bullets", [])))
    for cat, items in (profile.get("skills") or {}).items():
        scan(f"skills:{cat}", " ".join(items))
    return sorted(set(hits))


def main():
    check = "--check" in sys.argv
    for p in (PROFILE, ALIASES):
        if not os.path.exists(p):
            print(f"ERROR: missing {p}", file=sys.stderr)
            return 1

    want = combined_hash()
    if os.path.exists(OUT):
        try:
            if json.load(open(OUT)).get("source_hash") == want:
                print("CACHE_HIT")
                return 0
        except (json.JSONDecodeError, OSError):
            pass
    if check:
        print("STALE — run build_skills_db.py")
        return 1

    profile = json.load(open(PROFILE))
    curated = json.load(open(ALIASES))["skills"]

    skills, orphans = [], []
    for canon, spec in curated.items():
        ev = evidence_for(canon, spec, profile)
        if not ev:
            orphans.append(canon)
        skills.append({
            "canonical": canon,
            "depth": spec.get("depth", "working"),
            "aliases": spec.get("aliases") or [],
            "evidence": ev,
        })

    # profile skill terms no canonical resolves
    unmapped = []
    for cat, items in (profile.get("skills") or {}).items():
        for it in items:
            if not match(it):
                unmapped.append(f"{cat}: {it}")

    json.dump({
        "source_hash": want,
        "profile_hash": file_hash(PROFILE),
        "alias_hash": file_hash(ALIASES),
        "total_canonical": len(skills),
        "total_aliases": sum(len(s["aliases"]) for s in skills),
        "orphans": orphans,
        "unmapped_profile_terms": unmapped,
        "skills": skills,
    }, open(OUT, "w"), indent=2)

    print(f"REBUILT — {len(skills)} canonical skills, "
          f"{sum(len(s['aliases']) for s in skills)} aliases")
    if orphans:
        print(f"\n  ORPHAN ({len(orphans)}) — claimed but nothing in master_profile backs it:")
        for o in orphans:
            print(f"      {o}")
    if unmapped:
        print(f"\n  UNMAPPED ({len(unmapped)}) — profile skill no canonical covers "
              f"(JDs asking for these will read as a gap):")
        for u in unmapped:
            print(f"      {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
