#!/usr/bin/env python3
"""
select_content.py — B1 content selection + keyword-fill hints.

Replaces the inline score_item() snippet, which substring-matched raw JD
keywords against bullet text. On a real Analog Devices firmware role that gave:

    'c'                -> matched 12/12 projects (the letter c)
    'ide'              -> matched 5/12 via "guided", "PySide", "override"
    'microcontrollers' -> matched 0/12   (profile says "STM32")
    8 of 15 keywords   -> matched nothing

...so a CUDA GPU project outranked the STM32 bare-metal project for a firmware
job. Selection now runs on canonical skills from skills_db.json, weighted by
depth, and the item -> canonical map comes from the DB's own evidence index.

Also emits KEYWORD FILL HINTS: where the JD's wording differs from the
profile's for a skill Justin genuinely has, so B3 can mirror the JD's term
instead of inventing anything. Hints are only ever produced for backed skills.

Usage:
  python3 select_content.py <fit.json> [--exp N] [--proj N] [--json]
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_match import match, toks, is_decorated  # noqa: E402

IDF = {}

_REFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")
PROFILE = os.path.join(_REFS, "master_profile.json")
DB = os.path.join(_REFS, "skills_db.json")


# where a JD term appeared says how much the employer cares about it
SOURCE_W = {"required_skills": 1.0, "top_ats_keywords": 0.8, "preferred_skills": 0.5}


def wanted_canonicals(fit):
    """JD terms -> {canonical: (weight, [jd surface forms])}. Backed skills only."""
    want = {}
    for field, sw in SOURCE_W.items():
        for t in (fit.get(field) or []):
            m = match(t)
            if not m or m["credit"] <= 0:
                continue   # unbacked: no material to write from
            w = m["weight"] * sw   # ordering weight, not match credit
            cur, forms = want.get(m["canonical"], (0.0, []))
            if t not in forms:
                forms.append(t)
            want[m["canonical"]] = (max(cur, w), forms)
    return want


def evidence_index(db):
    """canonical -> {'project:Name', 'experience:Title', ...} inverted to item -> canonicals."""
    item = {}
    for s in db.get("skills", []):
        if not s.get("evidence"):
            continue
        for ev in s["evidence"]:
            item.setdefault(ev, set()).add(s["canonical"])
    return item


def idf(idx, n_items):
    """A skill half your portfolio demonstrates cannot discriminate between
    those items. Python and Git otherwise outrank STM32 on a firmware role."""
    import math
    df = {}
    for canon_set in idx.values():
        for c in canon_set:
            df[c] = df.get(c, 0) + 1
    return {c: math.log(1 + n_items / d) for c, d in df.items()}


def rank(items, kind, want, idx, credits):
    out = []
    for it in items:
        label = f"{kind}:{it.get('name') or it.get('title') or '?'}"
        canon = idx.get(label, set())
        hit = canon & set(want)
        out.append({
            "label": label,
            "name": it.get("name") or it.get("title"),
            "score": round(sum(credits[c] * IDF.get(c, 1.0) for c in hit), 2),
            "matched": sorted(hit),
        })
    return sorted(out, key=lambda x: x["score"], reverse=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__, file=sys.stderr)
        return 2

    def opt(flag, default):
        return int(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else default

    n_exp, n_proj = opt("--exp", 4), opt("--proj", 5)
    fit = json.load(open(args[0]))
    profile = json.load(open(PROFILE))
    if not os.path.exists(DB):
        print("ERROR: skills_db.json missing — run build_skills_db.py", file=sys.stderr)
        return 2
    db = json.load(open(DB))

    want = wanted_canonicals(fit)
    credits = {c: v[0] for c, v in want.items()}
    idx = evidence_index(db)

    global IDF
    IDF = idf(idx, len(profile.get("experience", [])) + len(profile.get("projects", [])))

    exp = rank(profile.get("experience", []), "experience", want, idx, credits)
    proj = rank(profile.get("projects", []), "project", want, idx, credits)

    # keyword fill: the JD's wording for a backed skill, where it differs from ours
    prof_blob = " ".join(toks(json.dumps(profile)))
    hints = []
    for canon, (cred, forms) in sorted(want.items(), key=lambda kv: -kv[1][0]):
        for f in forms:
            key = " ".join(toks(f))
            if not key or f" {key} " in f" {prof_blob} ":
                continue
            if is_decorated(f):
                # match it, do not mirror it: "C++17" -> write "C++"
                hints.append({"use_jd_wording": canon, "for_skill": canon,
                              "instead_of": f, "note": "JD wording is over-specific; "
                              "claim the skill, skip the version/standard"})
            else:
                hints.append({"use_jd_wording": f, "for_skill": canon})
    unbacked = [t for t in (fit.get("required_skills") or []) if not (match(t) or {}).get("credit")]

    result = {"experience": exp[:n_exp], "projects": proj[:n_proj],
              "keyword_fill_hints": hints, "unbacked_jd_terms": unbacked}

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
        return 0

    print(f"JD wants {len(want)} canonical skills you have\n")
    print(f"TOP {n_exp} EXPERIENCE")
    for e in exp[:n_exp]:
        print(f"  {e['score']:>5}  {str(e['name'])[:48]:<48} {', '.join(e['matched'][:4])}")
    print(f"\nTOP {n_proj} PROJECTS")
    for p in proj[:n_proj]:
        print(f"  {p['score']:>5}  {str(p['name'])[:48]:<48} {', '.join(p['matched'][:4])}")
    print(f"\n  (dropped: {', '.join(str(p['name'])[:28] for p in proj[n_proj:])})")
    if hints:
        print(f"\nKEYWORD FILL — use the JD's wording for skills you have ({len(hints)}):")
        for h in hints[:14]:
            if h.get("instead_of"):
                print(f"  write \"{h['use_jd_wording']}\"  NOT \"{h['instead_of']}\"  ({h['note']})")
            else:
                print(f"  \"{h['use_jd_wording']}\"  -> you have it as: {h['for_skill']}")
    if unbacked:
        print(f"\nDO NOT INVENT ({len(unbacked)}) — nothing backs these:")
        for u in unbacked:
            print(f"  {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
