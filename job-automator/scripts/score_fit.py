#!/usr/bin/env python3
"""
score_fit.py — Deterministic scorer + verdict + fit.json writer (A4 + A6 + A8).

WHY THIS EXISTS
---------------
A4 (scoring math), A6 (verdict thresholds) and A8 (writing fit.json) used to be
pseudocode the model re-executed by hand on every analysis. That is how
`zoox_ds_pv/logs/fit.json` ended up with `seniority_fit: "Mismatch"` next to
`verdicts.apply: "Can Try"` — the prose said a Mismatch forces APPLY = No, and
the model silently skipped the step. A verdict computed in prose is a verdict
that can be skipped. This script removes the opportunity.

The model's remaining job is only what a script genuinely cannot do: read the
JD, classify each skill HAVE / ADJACENT / MISSING, and (if triggered) the
semantic read. The arithmetic and the verdict are no longer its business.

VERDICT AUTHORITY: KEYWORD-PRIMARY
----------------------------------
`match_pct` plus a single experience-mismatch flag decide APPLY. That is all.
The semantic read (A6.5) is recorded verbatim and is INFORMATIONAL ONLY — it
has no code path to `apply`, by construction, not by discipline. Per the
standing preference in memory `feedback_match_scoring_approach.md`: keyword
scoring is the default and stays authoritative.

`seniority_fit` is a richer restatement of the experience check (years required
AND senior/staff/principal/lead in the title or level). A "Mismatch" downgrades
Yes -> Can Try. It has NO independent veto: it can never by itself force
APPLY = No. Giving it that standalone power is exactly what broke.

USAGE
-----
  python3 score_fit.py <payload.json> [--job-dir DIR] [--print]
  cat payload.json | python3 score_fit.py - --job-dir "$JOB_DIR"

Writes <job_dir>/logs/fit.json and prints the resolved verdict to stdout.

PAYLOAD SHAPE (the model produces this; every key optional except jd/have/...)
------------------------------------------------------------------------------
{
  "jd": {                        # A3 extraction
    "company_name", "company_slug", "job_title", "job_slug",
    "required_skills": [], "preferred_skills": [], "ats_keywords": [],
    "required_experience_years": 0,
    "experience_level_stated": "intern|entry|junior|mid|senior|staff|not_stated",
    "key_responsibilities": [], "role_category": "...",
    "location": "...", "remote_ok": null
  },
  "have":     ["Python", ...],                     # classified HAVE
  "adjacent": [{"jd_skill": "JAX", "you_have": "PyTorch"}, ...] | ["JAX -> PyTorch"],
  "missing":  ["SQL", ...],
  "hard_blocker": {"triggered": false, "reason": null},
  "flags": {"no_sponsorship": false, "location_conflict": false},
  "production_scope_required": false,
  "semantic": null | { ...A6.5 output... }         # informational only
}

EXIT CODES
  0 — scored and written
  2 — bad input / unwritable job dir
"""

import argparse
import json
import os
import re
import sys

# ── thresholds ────────────────────────────────────────────────────────────────
# Read from references/candidate_context.md so the skill has ONE source of
# truth for these numbers. Falls back to the documented defaults.
_REFS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references")

DEFAULTS = {
    "min_match_for_apply": 60,
    "min_match_for_can_try": 40,
    "experience_threshold_years": 3,
}

SENIOR_TITLE_RE = re.compile(
    r"\b(senior|sr\.?|staff|principal|lead|architect|manager|head\s+of|"
    r"director|distinguished|fellow)\b", re.I)
SENIOR_LEVEL = {"senior", "staff", "principal", "lead"}
MID_LEVEL = {"mid", "mid-level", "midlevel"}


def load_thresholds():
    """Parse `key = value` lines out of candidate_context.md."""
    out = dict(DEFAULTS)
    path = os.path.join(_REFS, "candidate_context.md")
    try:
        text = open(path).read()
    except OSError:
        return out
    for key in DEFAULTS:
        m = re.search(rf"^\s*{key}\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*$", text, re.M)
        if m:
            out[key] = float(m.group(1)) if "." in m.group(1) else int(m.group(1))
    return out


# ── normalization helpers ─────────────────────────────────────────────────────

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from skill_match import match as skill_match  # noqa: E402


def norm(s):
    return re.sub(r"[^a-z0-9+#.]+", " ", str(s).lower()).strip()


def adj_pairs(adjacent):
    """Adjacent may be [str] or [{jd_skill, you_have}] — keep both, return
    (display_list, jd_side_terms)."""
    display, jd_side = [], []
    for a in adjacent or []:
        if isinstance(a, dict):
            jd = a.get("jd_skill") or a.get("term") or ""
            have = a.get("you_have") or a.get("have") or ""
            display.append({"jd_skill": jd, "you_have": have} if have else jd)
            jd_side.append(jd)
        else:
            display.append(a)
            # "JAX -> PyTorch" / "JAX → PyTorch": the JD side is before the arrow
            jd_side.append(re.split(r"->|→", str(a))[0])
    return display, jd_side


# ── A4: scoring ───────────────────────────────────────────────────────────────

def score(have, adjacent_jd, missing, required_skills):
    """
    Denominator is every term actually classified — not just required_skills.

    Scoring against a 2-4 item required list produced 60 roles at exactly 100%
    that were each still missing ~4.6 skills, some with ZERO direct matches.
    See references/scoring_rationale.md for the backtest.
    """
    n_have, n_adj, n_miss = len(have), len(adjacent_jd), len(missing)
    jd_ask_size = n_have + n_adj + n_miss

    if jd_ask_size == 0:
        return {
            "match_pct": 0.0, "have_count": 0, "adjacent_count": 0, "req_detail": [],
            "missing_count": 0, "jd_ask_size": 0, "req_cov": 1.0,
            "cap_applied": "no_skills_classified",
        }

    covered = 1.0 * n_have + 0.5 * n_adj      # adjacency is half credit, never full
    raw = covered / jd_ask_size * 100.0

    # required-skill coverage — via the canonical skills DB, not string equality.
    # The old version compared JD prose ("microcontrollers") to resume tokens
    # ("STM32") with `==`, so req_cov read ~0 on roles Justin fully matched and
    # guard rail 2 capped them at 60. Analog Devices: true 94.4 -> 60.0.
    # Each required term takes the BEST of (skills-DB credit, the LLM's own
    # HAVE/ADJACENT classification), so neither authority can silently
    # under-count the other.
    cap = None
    req_terms = [r for r in (required_skills or []) if norm(r)]
    if req_terms:
        have_n = {norm(h) for h in have}
        adj_n = {norm(a) for a in adjacent_jd}
        req_detail, total = [], 0.0
        for r in req_terms:
            m = skill_match(r)
            c_db = m["credit"] if m else 0.0
            c_llm = 1.0 if norm(r) in have_n else (0.5 if norm(r) in adj_n else 0.0)
            c = max(c_db, c_llm)
            total += c
            req_detail.append({
                "term": r, "credit": round(c, 2),
                "canonical": (m or {}).get("canonical"),
                "depth": (m or {}).get("depth"),
                "source": "skills_db" if c_db >= c_llm and m else ("llm" if c_llm else "none"),
            })
        req_cov = total / len(req_terms)
    else:
        req_cov, req_detail = 1.0, []

    # guard rail 1 — adjacency alone is never a strong fit
    if n_have == 0:
        raw = min(raw, 50.0)
        cap = "zero_have"

    # guard rail 2 — missing a hard requirement caps the ceiling
    if req_cov < 0.5:
        raw = min(raw, 60.0)
        cap = "low_required_cov" if cap is None else cap + "+low_required_cov"

    return {
        "match_pct": round(raw, 1),
        "have_count": n_have, "adjacent_count": n_adj, "missing_count": n_miss,
        "jd_ask_size": jd_ask_size, "req_cov": round(req_cov, 3),
        "cap_applied": cap, "req_detail": req_detail,
    }


# ── A5: the experience check (seniority folded in) ────────────────────────────

def experience_check(jd, thresholds):
    """
    ONE check, TWO outputs.

      seniority_fit     — the displayed signal: Aligned / Stretch / Mismatch
      experience_mismatch — the boolean the verdict consumes

    experience_mismatch is exactly (seniority_fit == "Mismatch"). A Mismatch
    downgrades Yes -> Can Try and nothing more. It is NOT a veto and has no
    path to force APPLY = No on its own.
    """
    years = jd.get("required_experience_years") or 0
    try:
        years = float(years)
    except (TypeError, ValueError):
        years = 0.0

    level = norm(jd.get("experience_level_stated") or "")
    title = jd.get("job_title") or ""
    thresh = thresholds["experience_threshold_years"]

    senior_signal = bool(SENIOR_TITLE_RE.search(title)) or level in SENIOR_LEVEL

    if years > thresh or senior_signal:
        fit = "Mismatch"
    elif years >= 2 or level in MID_LEVEL:
        fit = "Stretch"
    else:
        fit = "Aligned"

    return fit, (fit == "Mismatch"), senior_signal


# ── A6: the verdict — keyword-primary, no semantic branch ─────────────────────

def verdict(match_pct, experience_mismatch, hard_blocker, no_sponsorship,
            thresholds):
    """
    First match wins. There is deliberately NO semantic/LLM branch here: the
    semantic read cannot reach this function's inputs.
    """
    if hard_blocker or no_sponsorship:
        # An explicit no-sponsorship statement is a hard blocker, same as
        # prescreen_jd.py's A2.5 "No Sponsorship" category — one rule, one outcome.
        return "No", "HARD BLOCK"

    apply_t = thresholds["min_match_for_apply"]
    try_t = thresholds["min_match_for_can_try"]

    if match_pct >= apply_t:
        matches = "Yes"
        apply_v = "Can Try" if experience_mismatch else "Yes"
    elif match_pct >= try_t:
        matches, apply_v = "Partial", "Can Try"
    else:
        matches, apply_v = "No", "No"
    return matches, apply_v


# ── main ──────────────────────────────────────────────────────────────────────

def build(payload, thresholds):
    jd = payload.get("jd") or {}
    have = list(payload.get("have") or [])
    missing = list(payload.get("missing") or [])
    adj_display, adj_jd = adj_pairs(payload.get("adjacent"))

    hb = payload.get("hard_blocker") or {}
    hb_trig = bool(hb.get("triggered"))
    hb_reason = hb.get("reason")

    flags = payload.get("flags") or {}
    no_spon = bool(flags.get("no_sponsorship"))
    if no_spon and not hb_trig:
        # Promote to a hard blocker so fit.json, the report and the build gate hook
        # (which read hard_blocker_triggered) all agree with the verdict.
        hb_trig = True
        hb_reason = hb_reason or "No Sponsorship: explicit refusal stated in the JD"

    sd = score(have, adj_jd, missing, jd.get("required_skills"))
    sen_fit, exp_mismatch, senior_signal = experience_check(jd, thresholds)
    matches, apply_v = verdict(sd["match_pct"], exp_mismatch, hb_trig, no_spon,
                               thresholds)

    semantic = payload.get("semantic")
    if not isinstance(semantic, dict):
        semantic = None
    if semantic is not None:
        # calibration_delta keeps the keyword-vs-semantic gap visible without
        # letting it touch the verdict.
        lp = semantic.get("llm_match_pct")
        semantic = dict(semantic)
        semantic["calibration_delta"] = (
            round(sd["match_pct"] - lp, 1) if isinstance(lp, (int, float)) else None)

    # Eligible for the A6.5 semantic read but none supplied: flag it so the gap is
    # visible in fit.json, the script output and the report instead of silent.
    semantic_pending = (semantic is None and not hb_trig
                        and sd["match_pct"] >= thresholds["min_match_for_apply"])

    return {
        "company": jd.get("company_name"), "company_slug": jd.get("company_slug"),
        "role": jd.get("job_title"), "job_slug": jd.get("job_slug"),
        "match_pct": sd["match_pct"],
        "score_detail": {
            "have_count": sd["have_count"],
            "adjacent_count": sd["adjacent_count"],
            "missing_count": sd["missing_count"],
            "jd_ask_size": sd["jd_ask_size"],
            "req_cov": sd["req_cov"],
            "cap_applied": sd["cap_applied"],
        },
        "seniority_fit": sen_fit,
        "experience_mismatch": exp_mismatch,
        "senior_title_signal": senior_signal,
        "production_scope_required": bool(payload.get("production_scope_required")),
        "have_skills": have,
        "adjacent_skills": adj_display,
        "missing_skills": missing,
        "top_ats_keywords": jd.get("ats_keywords") or [],
        # Persisted so B4.5 (verify_coverage.py) can check the JD's HARD asks,
        # and so the verdict is recomputable from fit.json alone.
        "required_skills": jd.get("required_skills") or [],
        "preferred_skills": jd.get("preferred_skills") or [],
        "required_experience_years": jd.get("required_experience_years"),
        "experience_level_stated": jd.get("experience_level_stated"),
        "key_responsibilities": jd.get("key_responsibilities") or [],
        "role_category": jd.get("role_category"),
        "location": jd.get("location"),
        "constraint_flags": flags,
        "verdicts": {
            "matches": matches,
            "apply": apply_v,
            "decided_by": "keyword",   # never "semantic" — see module docstring
            "hard_blocker_triggered": hb_trig,
            "hard_blocker_reason": hb_reason,
        },
        "thresholds_used": thresholds,
        "llm_analysis": semantic,      # INFORMATIONAL ONLY
        "semantic_pending": semantic_pending,
    }


def merge_semantic(job_dir, sem_path):
    """A6.5 one-pass merge: attach the semantic read to an existing fit.json.

    Scoring ran exactly once, so nothing is re-scored and no payload is rebuilt.
    The verdict fields are never touched — the semantic read stays informational.
    """
    out = os.path.join(os.path.expanduser(job_dir), "logs", "fit.json")
    try:
        fit = json.load(open(out))
        semantic = json.load(open(sem_path))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read fit.json / semantic file: {e}", file=sys.stderr)
        return 2
    if not isinstance(semantic, dict):
        print("ERROR: semantic file must be a JSON object", file=sys.stderr)
        return 2
    if fit.get("verdicts", {}).get("hard_blocker_triggered"):
        print("ERROR: hard blocker fired — no semantic read applies", file=sys.stderr)
        return 2
    lp = semantic.get("llm_match_pct")
    semantic["calibration_delta"] = (
        round(fit["match_pct"] - lp, 1) if isinstance(lp, (int, float)) else None)
    fit["llm_analysis"] = semantic            # INFORMATIONAL ONLY
    fit["semantic_pending"] = False
    try:
        tmp = out + ".tmp"
        with open(tmp, "w") as f:
            json.dump(fit, f, indent=2)
        os.replace(tmp, out)                  # atomic
    except OSError as e:
        print(f"ERROR: cannot write fit.json: {e}", file=sys.stderr)
        return 2
    print(f"fit.json    : {out}")
    print(f"semantic    : {semantic.get('llm_verdict')} ({lp}%) merged — informational, "
          f"delta {semantic['calibration_delta']}; verdict unchanged "
          f"(APPLY {fit['verdicts']['apply']})")
    return 0


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("payload", nargs="?",
                    help="payload JSON file, or - for stdin (omit with --add-semantic)")
    ap.add_argument("--job-dir", default=os.environ.get("JOB_DIR", ""))
    ap.add_argument("--add-semantic", metavar="SEMANTIC_JSON",
                    help="merge the A6.5 semantic read into the existing fit.json "
                         "(no re-scoring)")
    ap.add_argument("--print", action="store_true",
                    help="also print the fit.json to stdout")
    a = ap.parse_args()

    if a.add_semantic:
        if not a.job_dir:
            print("ERROR: no --job-dir and $JOB_DIR unset", file=sys.stderr)
            return 2
        return merge_semantic(a.job_dir, a.add_semantic)
    if not a.payload:
        ap.error("payload is required unless --add-semantic is given")

    try:
        raw = sys.stdin.read() if a.payload == "-" else open(a.payload).read()
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read payload: {e}", file=sys.stderr)
        return 2

    thresholds = load_thresholds()
    fit = build(payload, thresholds)

    job_dir = os.path.expanduser(a.job_dir or "")
    if not job_dir:
        print("ERROR: no --job-dir and $JOB_DIR unset", file=sys.stderr)
        return 2
    logs = os.path.join(job_dir, "logs")
    try:
        os.makedirs(logs, exist_ok=True)
        out = os.path.join(logs, "fit.json")
        tmp = out + ".tmp"
        with open(tmp, "w") as f:
            json.dump(fit, f, indent=2)
        os.replace(tmp, out)          # atomic
    except OSError as e:
        print(f"ERROR: cannot write fit.json: {e}", file=sys.stderr)
        return 2

    v = fit["verdicts"]
    print(f"fit.json    : {out}")
    print(f"match_pct   : {fit['match_pct']}%  "
          f"(have {fit['score_detail']['have_count']} / "
          f"adj {fit['score_detail']['adjacent_count']} / "
          f"miss {fit['score_detail']['missing_count']}, "
          f"denominator {fit['score_detail']['jd_ask_size']})")
    if fit["score_detail"]["cap_applied"]:
        print(f"cap applied : {fit['score_detail']['cap_applied']}")
    print(f"seniority   : {fit['seniority_fit']} "
          f"(experience_mismatch={fit['experience_mismatch']})")
    print(f"MATCHES     : {v['matches']}")
    print(f"APPLY       : {v['apply']}   [decided by keyword score only]")
    if fit["llm_analysis"]:
        print(f"semantic    : {fit['llm_analysis'].get('llm_verdict')} "
              f"({fit['llm_analysis'].get('llm_match_pct')}%) — informational, "
              f"delta {fit['llm_analysis'].get('calibration_delta')}")
    if fit.get("semantic_pending"):
        print("SEMANTIC    : REQUIRED - match >= "
              f"{fit['thresholds_used']['min_match_for_apply']}, no semantic read supplied. "
              "Run A6.5 (references/semantic_read.md), save it as JSON, merge it with "
              "`--add-semantic <file> --job-dir $JOB_DIR` (no re-scoring), and only "
              "then render the report.")
    if a.print:
        print()
        print(json.dumps(fit, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
