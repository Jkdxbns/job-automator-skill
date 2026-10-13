#!/usr/bin/env python3
"""
render_report.py — Deterministic A7 report renderer for job-automator.

TWO DISTINCT BLOCKS, NEVER MERGED
---------------------------------
Block 1 (always) — the KEYWORD read. This is the verdict of record. MATCHES and
APPLY come from here and from nowhere else.

Block 2 (only when the semantic read ran) — the SEMANTIC read, printed below and
explicitly labelled informational. It is a second opinion for the reader's own
judgment and it does not change the verdict above it.

The previous version merged the two into a single verdict line with a "semantic
overruled" annotation. That is what produced `seniority_fit: "Mismatch"` sitting
next to `apply: "Can Try"` with `Tailoring: recommended` underneath — three
statements the reader had to reconcile. One block owns the verdict now.

The `Tailoring:` line is derived from the authoritative APPLY verdict, never
from the semantic read, so it cannot disagree with the B-GATE.

Usage:
  python3 render_report.py <fit.json>                  # Format 1 — single role
  python3 render_report.py <fit1.json> <fit2.json>...  # Format 2 — batch table

Exit codes:
  0 — rendered
  2 — error (bad/missing input)

The model must NOT hand-render the report. Run this and print its stdout verbatim.
"""

import json
import os
import sys
import textwrap

WRAP = 72  # wrap width for the comma-separated skill lists


# ── shared helpers ─────────────────────────────────────────────────────────────

def load(path):
    with open(path) as f:
        return json.load(f)


def apply_tag(fit):
    """Map the stored keyword verdict to the four-state header tag."""
    v = (fit.get("verdicts") or {})
    apply_v = (v.get("apply") or "").strip().lower()
    if (fit.get("hard_blocker_triggered") or v.get("hard_blocker_triggered")
            or apply_v.startswith("hard block") or apply_v.startswith("blocked")):
        return "BLOCKED"
    if apply_v.startswith("yes"):
        return "APPLY"
    if apply_v.startswith("can try"):
        return "TRY"
    if apply_v.startswith("no"):
        return "SKIP"
    return "SKIP"   # unknown/free-text legacy verdict — fail safe, never recommend


def llm(fit):
    la = fit.get("llm_analysis")
    return la if isinstance(la, dict) else None


def sem_pct(fit):
    la = llm(fit)
    if la and la.get("llm_match_pct") is not None:
        return la["llm_match_pct"]
    return None


def seniority(fit):
    return fit.get("seniority_fit") or "—"


SKILL_KEYS = ("jd_skill", "term", "skill", "name", "jd_term")
GROUNDING_KEYS = ("you_have", "have", "backing", "evidence", "grounding", "source", "reason", "why")


def _dict_to_line(d: dict, sep: str) -> str:
    """A delegate's grounding-dict shape for have/adjacent entries is not
    consistent across calls (observed both {jd_skill, you_have} and
    {skill, backing} from the same prompt template on different roles — a
    free-tier model quirk, not a fixed schema). Try the known key-name pairs
    first; if none match, fall back to joining every string value in the dict
    rather than silently dropping the entry (which produced bare "," in the
    Have line for at least one role)."""
    skill = next((d[k] for k in SKILL_KEYS if d.get(k)), None)
    grounding = next((d[k] for k in GROUNDING_KEYS if d.get(k)), None)
    if skill or grounding:
        if skill and grounding:
            return f"{skill} {sep} {grounding}"
        return skill or grounding
    # unknown shape — join whatever string values exist so nothing is lost
    vals = [str(v) for v in d.values() if isinstance(v, str) and v.strip()]
    return " / ".join(vals) if vals else "(unlabeled)"


def adjacent_lines(fit):
    """Adjacent may be [str] or a grounding dict — normalize to strings."""
    out = []
    for a in fit.get("adjacent_skills") or []:
        if isinstance(a, dict):
            out.append(_dict_to_line(a, "→"))
        elif isinstance(a, str):
            out.append(a)
    return out


def have_lines(fit):
    """`have` is documented as [str], but a grounding-heavy delegate prompt can
    produce dict entries here too (the schema only names that shape for
    `adjacent`). Normalize defensively rather than let str(dict) or a dropped
    entry leak into the report — same shape-tolerance as adjacent_lines."""
    out = []
    for h in fit.get("have_skills") or []:
        if isinstance(h, dict):
            out.append(_dict_to_line(h, "—"))
        else:
            out.append(str(h))
    return out


def missing_lines(fit):
    """`missing` is documented as [str] too, but the same dict-leak pattern
    shows up here as {jd_skill, reason} — same defensive normalization."""
    out = []
    for m in fit.get("missing_skills") or []:
        if isinstance(m, dict):
            out.append(_dict_to_line(m, "—"))
        else:
            out.append(str(m))
    return out


def screen_out(fit):
    """The 3 ranked screening gaps, if the semantic read produced them."""
    la = llm(fit)
    if not la:
        return None
    gaps = la.get("screening_gaps")
    if isinstance(gaps, list) and gaps:
        return gaps[:3]
    rg = la.get("real_gaps")
    if isinstance(rg, list) and rg:
        return rg[:3]
    return None


def tailoring_rec(fit, tag):
    """
    Driven by the AUTHORITATIVE keyword verdict, so it can never contradict the
    B-GATE (which triggers on apply == "No").

    A weak semantic read does not flip this to "not recommended" — it is
    surfaced as a caveat inside block 2 instead, where it belongs.
    """
    if tag in ("SKIP", "BLOCKED"):
        return "not recommended"
    return "recommended"


def wrap_under(label, text):
    """Wrap a long comma list, indenting continuation lines under the value column."""
    indent = " " * (len(label) + 3)  # label + " : "
    if not text:
        return [f"│ {label} : "]
    wrapped = textwrap.wrap(text, width=WRAP,
                            break_long_words=False, break_on_hyphens=False)
    lines = [f"│ {label} : {wrapped[0]}"]
    for cont in wrapped[1:]:
        lines.append(f"│ {indent}{cont}")
    return lines


def wrap_numbered(i, text, bar="│"):
    """Wrap a numbered gap line, continuation indented under the text."""
    prefix = f"{bar}   {i}. "
    indent = f"{bar}      "
    wrapped = textwrap.wrap(str(text), width=WRAP,
                            break_long_words=False, break_on_hyphens=False)
    if not wrapped:
        return [prefix.rstrip()]
    lines = [prefix + wrapped[0]]
    for cont in wrapped[1:]:
        lines.append(indent + cont)
    return lines


def wrap_bullet(text, bar="│"):
    """Wrap a bulleted line, continuation indented under the text."""
    wrapped = textwrap.wrap(str(text), width=WRAP,
                            break_long_words=False, break_on_hyphens=False)
    if not wrapped:
        return [f"{bar}   •"]
    return [f"{bar}   • {wrapped[0]}"] + [f"{bar}     {c}" for c in wrapped[1:]]


def wrap_plain(text, bar="│", width=WRAP):
    wrapped = textwrap.wrap(str(text), width=width,
                            break_long_words=False, break_on_hyphens=False)
    return [f"{bar} {w}" for w in wrapped] or [bar]


# ── Block 1 — the keyword read (the verdict of record) ─────────────────────────

def render_keyword_block(fit):
    company = fit.get("company") or "?"
    role = fit.get("role") or "?"
    tag = apply_tag(fit)
    v = fit.get("verdicts") or {}

    have = have_lines(fit)
    adj = adjacent_lines(fit)
    miss = missing_lines(fit)

    kw = fit.get("match_pct")
    kw_str = f"{kw}%" if kw is not None else "—"

    labels = [f"✅ Have ({len(have)})",
              f"⚠️  Adjacent ({len(adj)})",
              f"❌ Missing ({len(miss)})"]
    w = max(len(x) for x in labels)
    labels = [x.ljust(w) for x in labels]

    out = [
        f"┌ {tag} · {company} — {role}",
        f"│ KEYWORD READ — verdict of record",
        f"│ match {kw_str}  ·  MATCHES {v.get('matches') or '—'}"
        f"  ·  APPLY {v.get('apply') or '—'}  ·  seniority {seniority(fit)}",
        "│",
    ]
    out += wrap_under(labels[0], ", ".join(have))
    out += wrap_under(labels[1], ", ".join(adj))
    out += wrap_under(labels[2], ", ".join(miss))
    out.append("│")

    # top missing skills — always from the keyword read, never the semantic one
    subs = [m for m in miss[:3]]
    if subs:
        out.append("│ Top keyword gaps:")
        for i, g in enumerate(subs, 1):
            out += wrap_numbered(i, g)
        out.append("│")

    # only print a constraint line if something actually fired
    fired = []
    cf = fit.get("constraint_flags") or {}
    if cf.get("no_sponsorship"):
        fired.append("sponsorship: JD states no sponsorship")
    if cf.get("location_conflict"):
        fired.append("location: conflicts with relocation constraints")
    if fit.get("production_scope_required"):
        fired.append("production-scope ownership expected (profile is "
                     "capstone/research/internship scope)")
    for f in fired:
        out.append(f"│ ⚑ {f}")
    if fired:
        out.append("│")

    if fit.get("experience_mismatch"):
        # Only claim a downgrade when the mismatch is what actually caused it:
        # match_pct cleared the apply bar but APPLY came out as Can Try. Below
        # the apply bar the Can Try comes from the score itself, and saying
        # "downgraded" there would be a second kind of contradictory report.
        th = fit.get("thresholds_used") or {}
        apply_t = th.get("min_match_for_apply")
        kw = fit.get("match_pct")
        caused = (isinstance(kw, (int, float)) and isinstance(apply_t, (int, float))
                  and kw >= apply_t and apply_tag(fit) == "TRY")
        if caused:
            out.append("│ ⚑ experience mismatch — cleared the apply bar but "
                       "downgraded Yes → Can Try")
        else:
            out.append("│ ⚑ experience mismatch — noted; the verdict above comes "
                       "from the score, not this flag")
        out.append("│")

    out.append(f"└ Tailoring: {tailoring_rec(fit, tag)}")
    return "\n".join(out)


# ── Block 2 — the semantic read (informational only) ──────────────────────────

def render_semantic_block(fit):
    la = llm(fit)
    if not la:
        return None

    lp = la.get("llm_match_pct")
    lv = la.get("llm_verdict") or "—"
    delta = la.get("calibration_delta")

    out = [
        "┌ SEMANTIC READ — INFORMATIONAL ONLY · does not change the verdict above",
        f"│ {lv}" + (f"  ·  {lp}% skill/domain depth" if lp is not None else ""),
    ]
    if delta is not None:
        out.append(f"│ keyword−semantic delta: {delta:+}")
    out.append("│")

    gaps = screen_out(fit)
    if gaps:
        out.append("│ Would screen you out:")
        for i, g in enumerate(gaps, 1):
            out += wrap_numbered(i, g)
        out.append("│")

    strengths = la.get("strengths")
    if isinstance(strengths, list) and strengths:
        out.append("│ Genuine strengths:")
        for s in strengths[:4]:
            out += wrap_bullet(s)
        out.append("│")

    reasoning = la.get("reasoning")
    if reasoning:
        out += wrap_plain(reasoning)
        out.append("│")

    ra = la.get("recommend_apply")
    if ra is False:
        out.append("│ ⚠️  Semantic read would NOT apply. The verdict above is "
                   "unchanged; this")
        out.append("│    is the caveat to weigh yourself, and it is what the "
                   "B-GATE surfaces.")
    elif ra is True:
        out.append("│ Semantic read agrees with applying.")
    out.append("└" + "─" * 3)
    return "\n".join(out)


def render_single(fit):
    tag = apply_tag(fit)
    if tag == "BLOCKED":
        company = fit.get("company") or "?"
        role = fit.get("role") or "?"
        v = fit.get("verdicts") or {}
        reason = (v.get("hard_blocker_reason")
                  or fit.get("hard_blocker_reason")
                  or "hard disqualifier for F-1 OPT")
        return "\n".join([
            f"BLOCKED · {company} — {role}",
            str(reason),
            "Ineligible for F-1 OPT. No tailoring, no further action.",
        ])

    parts = [render_keyword_block(fit)]
    sem = render_semantic_block(fit)
    if sem:
        parts.append("")
        parts.append(sem)
    else:
        parts.append("")
        if fit.get("semantic_pending"):
            parts.append("(SEMANTIC READ PENDING — match is at or above the apply bar but A6.5 was not run)")
        else:
            parts.append("(semantic read not run — below the apply threshold or hard blocker)")
    return "\n".join(parts)


# ── Format 2 — batch table ────────────────────────────────────────────────────

SEN_ABBR = {"Aligned": "OK", "Stretch": "STR", "Mismatch": "MIS"}


def render_batch(fits):
    rows = []
    n_apply = n_try = n_skip = n_blocked = 0
    for fit in fits:
        tag = apply_tag(fit)
        if tag == "APPLY":
            n_apply += 1
        elif tag == "TRY":
            n_try += 1
        elif tag == "BLOCKED":
            n_blocked += 1
        else:
            n_skip += 1
        sem = sem_pct(fit)
        gaps = screen_out(fit)
        blocker = (gaps[0] if gaps else (missing_lines(fit) or ["—"])[0])
        kw = fit.get("match_pct")
        rows.append({
            "role": f"{fit.get('company') or '?'} · {fit.get('role') or '?'}"[:38],
            "kw": f"{kw}%" if kw is not None else "—",
            "sem": f"{sem}%" if sem is not None else "—",
            "sen": SEN_ABBR.get(fit.get("seniority_fit"), "—"),
            "verdict": tag,
            "blocker": (str(blocker) or "—")[:34],
            "_sort": kw if kw is not None else 0,   # sort by the AUTHORITATIVE score
        })
    rows.sort(key=lambda r: r["_sort"], reverse=True)

    out = [f"{'ROLE':<40}{'KW':<6}{'SEM':<6}{'SEN':<5}{'VERDICT':<9}TOP BLOCKER"]
    for r in rows:
        out.append(f"{r['role']:<40}{r['kw']:<6}{r['sem']:<6}"
                   f"{r['sen']:<5}{r['verdict']:<9}{r['blocker']}")
    out.append("")
    summary = (f"{len(fits)} roles · {n_apply} APPLY · {n_try} TRY · "
               f"{n_skip} SKIP")
    if n_blocked:
        summary += f" · {n_blocked} BLOCKED"
    out.append(summary)
    out.append('KW is the verdict of record. SEM is informational only.')
    out.append('say "detail <company>" for the full read on any role')
    return "\n".join(out)


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        print(__doc__, file=sys.stderr)
        return 2
    for p in paths:
        if not os.path.exists(p):
            print(f"ERROR: not found: {p}", file=sys.stderr)
            return 2
    try:
        fits = [load(p) for p in paths]
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if len(fits) == 1:
        print(render_single(fits[0]))
    else:
        print(render_batch(fits))
    return 0


if __name__ == "__main__":
    sys.exit(main())
