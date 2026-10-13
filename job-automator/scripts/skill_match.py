#!/usr/bin/env python3
"""
skill_match.py — the ONE place that decides "does Justin have this JD skill?"

Before this module there were three separate answers to that question, all by
raw string equality, all wrong in the same way: the profile says `STM32`, JDs
say `microcontrollers`.

  * score_fit.req_cov      -> capped 94.4% roles at 60 (Analog Devices)
  * tailoring score_item   -> ranked CUDA above STM32 for a firmware role
  * verify_coverage        -> reported 8 false CEILINGs on a role fully backed

All three now call match() here. Vocabulary lives in
references/skill_aliases.json (curated, survives rebuilds).

CREDIT reflects defensibility, not just presence — the point is an accurate
score, never an inflated one. A `working` skill is not worth the same as a
`strong` one in an interview, so it is not worth the same here.
"""

import json
import os
import re
import functools

_REFS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")
ALIAS_PATH = os.path.join(_REFS, "skill_aliases.json")

# MATCH CREDIT is binary on purpose. If the JD asks for C++ and Justin has C++,
# that is a match — depth is irrelevant to whether a keyword matches, and
# discounting it just made real matches look worse than they are.
# Only UNBACKED earns nothing: a skill with zero evidence in master_profile has
# no material to write a bullet from, so claiming it would be fabrication.
CREDIT = {"strong": 1.0, "working": 1.0, "exposure": 1.0, "unbacked": 0.0}

# WEIGHT is a different question: not "do we match" but "should this lead the
# resume". Leading with a weaker area steers the interview onto worse ground,
# so it is used ONLY for ordering in select_content.py — never for scoring.
WEIGHT = {"strong": 1.0, "working": 0.75, "exposure": 0.4, "unbacked": 0.0}

# Over-specific JD phrasings we MATCH but never mirror into the resume.
# Writing "C++17" instead of "C++" invites a standards-depth probe for no ATS
# gain — the NVIDIA lesson. Claim the skill, skip the decoration.
DECORATED = re.compile(
    r"c\+\+\s*\d{2}"                      # C++11 / C++17 / C++20
    r"|python\s*[23][\d.]*"                # Python 3.11
    r"|java\s*\d+"
    r"|\bc\s*(99|11|17)\b"
    r"|c\+\+\s*(0x|1x|2x)"
    r"|iso\s*26262|misra|autosar|do-?178|arinc|iec\s*61508"
    r"|modern\s*c\+\+|idiomatic|template\s*metaprogram|move\s*semantic|rvalue|raii"
    r"|expert|advanced|mastery|guru|deep\s+expertise|in-?depth",
    re.I)


def is_decorated(term):
    """True if mirroring this exact wording would manufacture an interview trap."""
    return bool(DECORATED.search(str(term or "")))

# JD phrasing that carries no skill meaning — stripped before comparison.
FILLER = {
    "strong", "solid", "good", "excellent", "basic", "working", "hands", "on",
    "proficiency", "proficient", "familiarity", "familiar", "understanding",
    "ability", "skills", "skill", "experience", "knowledge", "concepts",
    "concept", "fundamentals", "fundamental", "tools", "tool", "using", "use",
    "or", "and", "of", "in", "with", "the", "a", "an", "to", "for", "etc",
    "such", "as", "related", "equivalent", "preferred", "required", "plus",
    "similar", "including", "e.g", "i.e", "demonstrated", "practical",
    "relevant", "prior", "some", "exposure", "background", "expertise",
}


def norm(s):
    return re.sub(r"[^a-z0-9+#.]+", " ", str(s).lower()).strip()


def _sing(w):
    return w[:-1] if len(w) > 3 and w.endswith("s") and not w.endswith("ss") else w


def toks(s):
    return [_sing(w) for w in norm(s).split()]


def content(s):
    return [w for w in toks(s) if w not in FILLER]


@functools.lru_cache(maxsize=1)
def _table():
    """{normalized surface form: (canonical, depth)} — canonicals and aliases."""
    db = json.load(open(ALIAS_PATH))["skills"]
    t = {}
    for canon, spec in db.items():
        depth = spec.get("depth", "working")
        for form in [canon] + list(spec.get("aliases") or []):
            key = " ".join(toks(form))
            if key and key not in t:
                t[key] = (canon, depth)
    return t


@functools.lru_cache(maxsize=1)
def _unbacked():
    """Canonicals that skills_db.json says nothing in master_profile backs.
    They must not earn credit — that is how an inflated score starts."""
    db = os.path.join(_REFS, "skills_db.json")
    if not os.path.exists(db):
        return frozenset()
    try:
        return frozenset(s["canonical"] for s in json.load(open(db)).get("skills", [])
                         if not s.get("evidence"))
    except (json.JSONDecodeError, OSError, KeyError):
        return frozenset()


def _result(canon, depth, via, gate):
    if gate and canon in _unbacked():
        depth = "unbacked"
    return {"canonical": canon, "depth": depth, "credit": CREDIT[depth],
            "weight": WEIGHT[depth], "via": via}


def match(term, gate=True):
    """
    Resolve a JD skill phrase to a canonical skill Justin has.

    Returns {"canonical","depth","credit","via"} or None.
    """
    if not term or not str(term).strip():
        return None
    t = _table()
    whole = " ".join(toks(term))
    if not whole:
        return None

    # 1. the phrase itself is a known surface form
    if whole in t:
        canon, depth = t[whole]
        return _result(canon, depth, "exact", gate)

    # 2. drop JD filler and retry ("strong C programming skills" -> "c programming")
    stripped = " ".join(content(term))
    if stripped and stripped in t:
        canon, depth = t[stripped]
        return _result(canon, depth, "destuffed", gate)

    # 3. a known form appears as a whole-word phrase inside the JD term.
    #    Longest first so "embedded linux" wins over "linux".
    padded = f" {whole} "
    for key in sorted(t, key=len, reverse=True):
        if len(key) <= 2:
            continue  # short forms ("c", "ml") must match the whole term, not a fragment
        if f" {key} " in padded:
            canon, depth = t[key]
            return _result(canon, depth, f"contains:{key}", gate)

    # 4. every content word of the JD term is covered by one known form
    cw = set(content(term))
    if cw:
        for key, (canon, depth) in t.items():
            kw = set(content(key))
            if kw and cw <= kw:
                return _result(canon, depth, f"subset:{key}", gate)
    return None


def coverage(terms):
    """(credit_sum / len(terms), [(term, result_or_None)]) — the req_cov replacement."""
    terms = [t for t in (terms or []) if str(t).strip()]
    if not terms:
        return 1.0, []
    pairs = [(t, match(t)) for t in terms]
    return sum(r["credit"] for _, r in pairs if r) / len(terms), pairs


def canonical_set():
    return sorted({c for c, _ in _table().values()})


if __name__ == "__main__":
    import sys
    for a in sys.argv[1:]:
        r = match(a)
        print(f"{a!r:<42} -> {r}")
