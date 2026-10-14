#!/usr/bin/env python3
"""
regression_check.py — replay past fixtures through the OLD and NEW code and assert that every
deterministic output Justin receives is byte-identical.

WHY
---
Token-saving changes to this skill are only acceptable if they change nothing he receives: the
fit verdict, match_pct, seniority_fit, the A7 report, the global log row. This script proves it
for the script layer, and proves for the instruction layer that no paragraph of the old skill text
was dropped or reworded unless that edit is listed (with its reason) in EXPECTED_TEXT_EDITS below.

WHAT IT CHECKS
--------------
Per fixture (every current-schema jobs/**/logs/fit.json, rebuilt into a payload, plus every stored
payload file), old code vs new code:
  1. score_fit.py <payload> --job-dir D              stdout + fit.json bytes
  2. score_fit.py --add-semantic <sem> --job-dir D   stdout + fit.json bytes (fixtures with a read)
  3. render_report.py <fit.json>                     stdout (Format 1)
  4. log_fit.py --log <tmp> <fit.json>               stdout + the row written
  5. NEW only, once score_fit.py has --report/--log: the one-call form must print exactly
     (1) + the old render_report output between the A7 markers + the old log_fit output,
     and write the same fit.json and log row.
  6. emploive results_table.py regexes read the same match/APPLY/semantic/seniority values.
Across fixtures:
  7. render_report.py on many fit.json at once (Format 2 batch table).
  8. print_refs.py packs: every file printed is byte-identical to the file on disk.
  9. Skill text: every paragraph of the old SKILL.md and references/*.md still exists verbatim
     (whitespace- and link-path-normalized) in the new SKILL.md + references/*.md.
 10. keyword_prefilter.py: same shortlist, scores and seniority flags; reports sponsorship_flag
     flips (expected: that is the comment-swallowing bug fix) and checks no comment text is parsed
     as a phrase.
 11. Every script answers --help (exit 0, usage on stdout) and writes nothing. mark_submitted.py,
     hunt_contacts.py and save_and_print_draft.py are never executed, only inspected.
 12. validate_skill.py passes on the new skill.

USAGE
-----
  python3 job-automator/scripts/regression_check.py [--base REF | --old DIR] [--limit N]
                                                    [--min N] [--workers N] [--keep]

  --base REF   git ref holding the OLD code (default: main). Extracted with `git archive`.
  --old DIR    use this directory as the old job-automator skill instead of git.
  --limit N    replay only the first N fixtures (default: all).
  --min N      fail unless at least N fixtures were replayed (default: 30).

Writes only under a temp dir (log_fit always gets --log <tmp>). Never touches ~/job_search.

EXIT CODES
  0 — all checks passed
  1 — a check failed (details printed)
  2 — bad invocation / old code unavailable
"""

import argparse
import concurrent.futures as cf
import difflib
import glob
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
NEW = os.path.dirname(SCRIPTS)                      # job-automator/
ROOT = os.path.dirname(NEW)                         # repo root
PY = sys.executable or "python3"

# Every deliberate wording edit to the OLD skill text, as an exact substring replacement applied to
# the old file before comparing paragraphs. So the check proves that nothing else in the paragraph
# changed. Moved text needs no entry (it is found verbatim in its new file). An entry whose `old`
# no longer occurs in the old file fails the check (stale), and so does any old paragraph still
# missing after the replacements.
EXPECTED_TEXT_EDITS = [
    {"file": "SKILL.md",
     "old": 'score_fit.py /tmp/fit_payload.json --job-dir "$JOB_DIR"\n```\nIt computes',
     "new": 'score_fit.py /tmp/fit_payload.json --job-dir "$JOB_DIR" --report --log\n```\nIt computes',
     "why": "A6 command gains --report --log: A7 + A9 run in the same call once fit.json is final"},
    {"file": "SKILL.md",
     "old": ("never rebuild the payload:\n"
             ">    `python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic <semantic.json>"
             " --job-dir \"$JOB_DIR\"`\n"),
     "new": ("never rebuild the payload. Both in ONE\n"
             ">    Bash call: `cat > \"$JOB_DIR/logs/semantic.json\" <<'JSON'` … the read … `JSON`, then on the"
             " next line\n"
             ">    `python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic"
             " \"$JOB_DIR/logs/semantic.json\" --job-dir \"$JOB_DIR\" --report --log`\n"),
     "why": "A6.5 rule 5: write the read and merge it in one Bash call, with --report --log"},
    {"file": "references/semantic_read.md",
     "old": ("**do not re-run scoring**:\n"
             "`python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic <semantic.json>"
             " --job-dir \"$JOB_DIR\"`.\n"),
     "new": ("**do not re-run scoring**. One Bash\n"
             "call does both, and with `--report --log` it also prints the A7 report and writes the A9 log row:\n"
             "```bash\n"
             "cat > \"$JOB_DIR/logs/semantic.json\" <<'JSON'\n"
             "{ \"llm_match_pct\": 0, \"llm_verdict\": \"...\", \"...\": \"the full read, shape above\" }\n"
             "JSON\n"
             "python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic"
             " \"$JOB_DIR/logs/semantic.json\" --job-dir \"$JOB_DIR\" --report --log\n"
             "```\n"),
     "why": "A6.5 hand-back: same one-call write + merge (+ A7/A9) as SKILL.md rule 5"},
    {"file": "references/fit_payload.md",
     "old": "**A1 — Load candidate keywords.** Read `references/keywords_only.json`, not the full profile",
     "new": ("**A1 — Load candidate keywords.** Load `references/keywords_only.json`"
             " (`print_refs.py fit` prints it), not the full profile"),
     "why": "A1: keywords_only.json now arrives via print_refs.py fit (same bytes, no Read gutter)"},
    {"file": "references/hooks_and_errors.md",
     "old": "A third hook, installed from this skill's `hooks/` dir and **wired** in settings.json:",
     "new": "A third hook, kept in `~/.claude/hooks/` with the other two and **wired** in settings.json:",
     "why": "the duplicate hook copies in job-automator/hooks/ were removed; claude/hooks/ is the one copy"},
    {"file": "references/fit_payload.md",
     "old": ("# A0–A3 — setup, JD retrieval, and the score_fit.py payload\n\n"
             "## A0 – A2.5 — job dir, keywords, JD text, hard-blocker pre-screen\n"),
     "new": ("# A3 + A6 — the `jd` object and the score_fit.py payload\n\n"
             "The A0 – A2.5 commands (job dir, keywords, JD text, hard-blocker pre-screen) moved to SKILL.md,"
             " unchanged.\n"),
     "why": "A0–A2.5 moved verbatim into SKILL.md, so A0 no longer waits on reading this file; title updated"},
    {"file": "SKILL.md",
     "old": ("**A0 – A2.5 — setup, JD text, hard-blocker pre-screen.** Commands in\n"
             "**[fit_payload.md](references/fit_payload.md)**: `build_keywords.py`, `build_skills_db.py`,"
             " `$JOB_CWD`/`$JOB_DIR`,\n"
             "`keywords_only.json`, `skills_db.json`, `scrape_jd.py`, `prescreen_jd.py`.\n"),
     "new": ("**A0 – A2.5 — setup, JD text, hard-blocker pre-screen.** The commands are below.\n"
             "**[fit_payload.md](references/fit_payload.md)** holds the A3 `jd` schema and the A6 payload.\n"),
     "why": "pointer to fit_payload.md replaced: the A0–A2.5 commands now sit right below it"},
    {"file": "SKILL.md",
     "old": "   → `FOLLOWUPS=<n> DRAFTS=<n>`\n",
     "new": "   → `FOLLOWUPS=<n> DRAFTS=<n>`. Send it alongside the first step's commands, as a parallel call.\n",
     "why": "S1 runs in the same turn as the first step's commands instead of a turn of its own"},
    {"file": "SKILL.md",
     "old": '| "tailor" / "tailor my resume" | **B** on the current job | below |',
     "new": ('| "tailor" / "tailor my resume" | **B** on the current job |'
             ' B-GATE below, then `references/workflow_b_tailoring.md` |'),
     "why": "B0–B5 text moved to workflow_b_tailoring.md; the routing table names it"},
    {"file": "SKILL.md",
     "old": "**Read the named file in full before acting on a C / D / F route.** A and B are inline below.",
     "new": ("**Read the named file in full before acting on a B (after B-GATE) / C / D / F route.**"
             " A and B-GATE are\ninline below."),
     "why": "B joins the read-in-full routes; B-GATE itself stays inline"},
    {"file": "SKILL.md",
     "old": "Command in\n[workflow_b_tailoring.md](references/workflow_b_tailoring.md).\n",
     "new": "Command above.\n",
     "why": "B5 paragraph moved into workflow_b_tailoring.md, right after the command it names"},
    {"file": "references/workflow_b_tailoring.md",
     "old": ("Loaded during B, after B-GATE has cleared. The three rules that stay in SKILL.md itself — **B-GATE**,\n"
             "**B4-VERIFY**, and **B4.5's FIXABLE vs CEILING** — are enforcement and are not repeated here.\n"),
     "new": ("Loaded during B, after B-GATE has cleared. **B-GATE** stays in SKILL.md because it runs before this"
             " file is\nread. **B4-VERIFY** and **B4.5's FIXABLE vs CEILING** moved here from SKILL.md word for"
             " word; they are\nenforcement, not optional.\n"),
     "why": "header note: B4-VERIFY and B4.5 now live in this file"},
    {"file": "SKILL.md",
     "old": ("**B0 – B4 — cache check, tailor, generate.** Mechanics in\n"
             "**[workflow_b_tailoring.md](references/workflow_b_tailoring.md)**: the"),
     "new": "**B0 – B4 — cache check, tailor, generate.** Mechanics below: the",
     "why": "B0–B4 summary moved to the top of workflow_b_tailoring.md, so it points below, not at itself"},
    {"file": "references/workflow_b_tailoring.md",
     "old": '```bash\nRESULT=$(python3 ~/.claude/skills/job-automator/scripts/resume_cache.py check $JOB_DIR/logs/fit.json); EXIT=$?\n```\n',
     "new": '```bash\npython3 ~/.claude/skills/job-automator/scripts/resume_cache.py check $JOB_DIR/logs/fit.json; EXIT=$?; echo "CACHE_EXIT=$EXIT"\nif [ $EXIT -eq 1 ]; then   # CACHE_MISS: B1 runs in this same call\n  python3 ~/.claude/skills/job-automator/scripts/select_content.py $JOB_DIR/logs/fit.json --json \\\n    > $JOB_DIR/logs/selection.json && cat $JOB_DIR/logs/selection.json\nfi\n```\n',
     "why": "B0 runs B1's select_content.py in the same call on a cache miss and prints selection.json"},
    {"file": "references/workflow_b_tailoring.md",
     "old": '`fresh` (continue to B1). `EXIT=1` (CACHE_MISS) → continue to B1.\n',
     "new": "`fresh` (continue to B1). `EXIT=1` (CACHE_MISS) → continue to B1.\n\nOn CACHE_MISS that same call has already run B1's `select_content.py` and printed `selection.json`;\ndon't run it again. After `fresh` on a hit, run B1's command from tailoring_prompt.md.\n",
     "why": 'B0: says B1 already ran on a miss, and when to run it after `fresh`'},
    {"file": "references/workflow_b_tailoring.md",
     "old": 'python3 ~/.claude/skills/job-automator/scripts/generate_pdf.py $JOB_DIR/logs/tailored.json $JOB_DIR\n```\n',
     "new": 'python3 ~/.claude/skills/job-automator/scripts/generate_pdf.py $JOB_DIR/logs/tailored.json $JOB_DIR; GEN=$?; echo "GENERATE_EXIT=$GEN"\nif [ $GEN -eq 0 ]; then   # B4-VERIFY, then B4.5, in this same call\n  PDF=$(ls -t $JOB_DIR/resume_*.pdf 2>/dev/null | head -1)\n  if [ -z "$PDF" ] || [ ! -s "$PDF" ]; then\n    echo "NO PDF — resume did not build"\n  else\n    PAGES=$(pdfinfo "$PDF" | grep -i Pages); echo "$PAGES"     # must read "Pages: 1"\n    case "$PAGES" in *" 1")\n      python3 ~/.claude/skills/job-automator/scripts/verify_coverage.py $JOB_DIR/logs/fit.json $JOB_DIR/logs/tailored.json\n      echo "COVERAGE_EXIT=$?";;\n    esac\n  fi\nfi\n```\nOn exit 0 this one call also runs B4-VERIFY and, for a real single-page PDF, B4.5 — don\'t run them again.\nTheir rules below still apply in full: paste the coverage output, FIXABLE vs CEILING.\n\n',
     "why": 'B4 runs B4-VERIFY and, for a real single-page PDF, B4.5 in the same call'},
]

# emploive-analysis/scripts/results_table.py parses transcripts with these (copied verbatim).
EMPLOIVE_RES = {
    "match": r"match\s+([\d.]+)%",
    "apply": r"APPLY\s+(Yes|Can Try|No)\b",
    "sem": r"([\d.]+)%\s+skill/domain depth",
    "seniority": r"seniority\s+(Aligned|Stretch|Mismatch)",
}


# ── old code ──────────────────────────────────────────────────────────────────

def extract_old(base, dest):
    """git archive <base> job-automator → dest/job-automator."""
    try:
        tar = subprocess.run(["git", "-C", ROOT, "archive", "--format=tar", base, "job-automator"],
                             capture_output=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError) as e:
        err = getattr(e, "stderr", b"") or b""
        sys.exit(f"ERROR: cannot extract old code from git ref '{base}': "
                 f"{err.decode(errors='replace').strip() or e}")
    with tarfile.open(fileobj=io.BytesIO(tar)) as t:
        t.extractall(dest, filter="data")
    return os.path.join(dest, "job-automator")


# ── fixtures ──────────────────────────────────────────────────────────────────

def payload_from_fit(d):
    """Rebuild the score_fit.py payload a fit.json was produced from."""
    v = d.get("verdicts") or {}
    jd = {
        "company_name": d.get("company"), "company_slug": d.get("company_slug"),
        "job_title": d.get("role"), "job_slug": d.get("job_slug"),
        "required_skills": d.get("required_skills"), "preferred_skills": d.get("preferred_skills"),
        "ats_keywords": d.get("top_ats_keywords"),
        "required_experience_years": d.get("required_experience_years"),
        "experience_level_stated": d.get("experience_level_stated"),
        "key_responsibilities": d.get("key_responsibilities"),
        "role_category": d.get("role_category"), "location": d.get("location"),
    }
    return {
        "jd": jd, "have": d.get("have_skills"), "adjacent": d.get("adjacent_skills"),
        "missing": d.get("missing_skills"),
        "hard_blocker": {"triggered": v.get("hard_blocker_triggered"),
                         "reason": v.get("hard_blocker_reason")},
        "flags": d.get("constraint_flags"),
        "production_scope_required": d.get("production_scope_required"),
        "semantic": None,
    }


def semantic_from_fit(d):
    la = d.get("llm_analysis")
    if not isinstance(la, dict):
        return None
    return {k: x for k, x in la.items() if k != "calibration_delta"}


def collect_fixtures(limit):
    items = []
    for f in sorted(glob.glob(os.path.join(ROOT, "jobs", "**", "logs", "fit.json"), recursive=True)):
        try:
            d = json.load(open(f))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or "score_detail" not in d or "thresholds_used" not in d:
            continue  # pre-score_fit.py schema: nothing to replay
        items.append({"src": os.path.relpath(f, ROOT), "payload": payload_from_fit(d),
                      "semantic": semantic_from_fit(d)})
    for pat in ("_fit_payload.json", "fit_payload.json", "payload.json"):
        for f in sorted(glob.glob(os.path.join(ROOT, "jobs", "**", "logs", pat), recursive=True)):
            try:
                d = json.load(open(f))
            except (OSError, ValueError):
                continue
            if isinstance(d, dict) and isinstance(d.get("jd"), dict):
                items.append({"src": os.path.relpath(f, ROOT), "payload": d, "semantic": None})
    return items[:limit] if limit else items


# ── one side of one fixture ───────────────────────────────────────────────────

def run(cmd, cwd=None):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr


def norm(text, work):
    return (text or "").replace(work, "<WORK>")


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return None


def replay(code, work, item):
    """Run the documented step sequence with the plain CLI. Mirrors what --report/--log does:
    render + log only once fit.json is final (no semantic pending)."""
    os.makedirs(work, exist_ok=True)
    s = os.path.join(code, "scripts")
    pj = os.path.join(work, "payload.json")
    json.dump(item["payload"], open(pj, "w"))
    job = os.path.join(work, "job")
    fit = os.path.join(job, "logs", "fit.json")
    log = os.path.join(work, "log.json")
    r = {}

    rc, out, err = run([PY, os.path.join(s, "score_fit.py"), pj, "--job-dir", job])
    r["score"] = (rc, norm(out, work))
    r["fit0"] = norm(read(fit), work)
    if rc != 0:
        r["err"] = err
        return r
    fit0 = json.loads(read(fit))
    blocked = (fit0.get("verdicts") or {}).get("hard_blocker_triggered")
    if not fit0.get("semantic_pending"):
        r["report0"] = run([PY, os.path.join(s, "render_report.py"), fit])[:2]
        rc2, out2, _ = run([PY, os.path.join(s, "log_fit.py"), "--log", log, fit])
        r["log0"] = (rc2, norm(out2, work))
    if item["semantic"] and not blocked:
        sp = os.path.join(work, "semantic.json")
        json.dump(item["semantic"], open(sp, "w"))
        rc3, out3, _ = run([PY, os.path.join(s, "score_fit.py"), "--add-semantic", sp, "--job-dir", job])
        r["merge"] = (rc3, norm(out3, work))
        r["fit1"] = norm(read(fit), work)
        r["report1"] = run([PY, os.path.join(s, "render_report.py"), fit])[:2]
        rc4, out4, _ = run([PY, os.path.join(s, "log_fit.py"), "--log", log, fit])
        r["log1"] = (rc4, norm(out4, work))
    r["log_rows"] = norm(read(log), work)
    r["fit_path"] = fit
    return r


def replay_flags(code, work, item):
    """NEW code, one-call form: score_fit.py ... --report --log <tmp> (and the same on the merge)."""
    os.makedirs(work, exist_ok=True)
    s = os.path.join(code, "scripts")
    pj = os.path.join(work, "payload.json")
    json.dump(item["payload"], open(pj, "w"))
    job = os.path.join(work, "job")
    fit = os.path.join(job, "logs", "fit.json")
    log = os.path.join(work, "log.json")
    r = {}
    rc, out, _ = run([PY, os.path.join(s, "score_fit.py"), pj, "--job-dir", job,
                      "--report", "--log", log])
    r["score"] = (rc, norm(out, work))
    r["fit0"] = norm(read(fit), work)
    if rc != 0:
        return r
    fit0 = json.loads(read(fit))
    blocked = (fit0.get("verdicts") or {}).get("hard_blocker_triggered")
    if item["semantic"] and not blocked:
        sp = os.path.join(work, "semantic.json")
        json.dump(item["semantic"], open(sp, "w"))
        rc3, out3, _ = run([PY, os.path.join(s, "score_fit.py"), "--add-semantic", sp,
                            "--job-dir", job, "--report", "--log", log])
        r["merge"] = (rc3, norm(out3, work))
        r["fit1"] = norm(read(fit), work)
    r["log_rows"] = norm(read(log), work)
    return r


def expected_flags(old, mod):
    """What the one-call form must print, built from the OLD plain-CLI outputs."""
    def block(report, log):
        return (f"{mod.REPORT_BEGIN}\n{report[1]}{mod.REPORT_END}\n{log[1]}")
    e = {"fit0": old["fit0"], "log_rows": old["log_rows"]}
    score_rc, score_out = old["score"]
    if "report0" in old:
        e["score"] = (score_rc, score_out + block(old["report0"], old["log0"]))
    else:
        e["score"] = (score_rc, score_out + mod.REPORT_PENDING + "\n")
    if "merge" in old:
        e["merge"] = (old["merge"][0], old["merge"][1] + block(old["report1"], old["log1"]))
        e["fit1"] = old["fit1"]
    return e


# ── checks ────────────────────────────────────────────────────────────────────

def diff(a, b, label):
    a = a if isinstance(a, str) else json.dumps(a, indent=1, ensure_ascii=False)
    b = b if isinstance(b, str) else json.dumps(b, indent=1, ensure_ascii=False)
    lines = list(difflib.unified_diff(a.splitlines(), b.splitlines(), f"old {label}",
                                      f"new {label}", lineterm="", n=1))
    return "\n".join(lines[:24])


def compare(old, new, keys):
    bad = []
    for k in keys:
        if old.get(k) != new.get(k):
            bad.append((k, diff(old.get(k), new.get(k), k)))
    return bad


def emploive_values(text):
    out = {}
    for k, pat in EMPLOIVE_RES.items():
        m = re.findall(pat, text or "")
        out[k] = m[-1] if m else None
    return out


def paragraphs(text):
    return [p for p in re.split(r"\n\s*\n", text) if p.strip()]


def norm_para(p):
    p = re.sub(r"\]\((?:\.\./)?(?:references/)?([^)\s]+)\)", r"](\1)", p)  # link path moved files
    return re.sub(r"\s+", " ", p).strip()


def text_corpus(skill_dir):
    files = [os.path.join(skill_dir, "SKILL.md")]
    files += sorted(glob.glob(os.path.join(skill_dir, "references", "*.md")))
    return {os.path.relpath(f, skill_dir): open(f, encoding="utf-8").read() for f in files}


def check_text(old_dir):
    """Every old paragraph must survive verbatim somewhere in the new skill text, after applying
    only the substitutions listed in EXPECTED_TEXT_EDITS."""
    old = text_corpus(old_dir)
    new = text_corpus(NEW)
    applied, stale = [], []
    for e in EXPECTED_TEXT_EDITS:
        if e["file"] in old and e["old"] in old[e["file"]]:
            old[e["file"]] = old[e["file"]].replace(e["old"], e["new"])
            applied.append(e)
        else:
            stale.append(e)
    new_blob = "\n\x00\n".join(norm_para(p) for t in new.values() for p in paragraphs(t))
    old_blob = "\n\x00\n".join(norm_para(p) for t in old.values() for p in paragraphs(t))
    missing = [(f, norm_para(p)[:160]) for f, t in old.items() for p in paragraphs(t)
               if norm_para(p) not in new_blob]
    added = [(f, norm_para(p)[:160]) for f, t in new.items() for p in paragraphs(t)
             if norm_para(p) not in old_blob]
    return missing, applied, added, stale


def check_print_refs():
    path = os.path.join(SCRIPTS, "print_refs.py")
    if not os.path.exists(path):
        return None, []
    problems, checked = [], 0
    for pack in ("fit", "semantic"):
        rc, out, err = run([PY, path, pack])
        if rc != 0:
            problems.append(f"print_refs.py {pack} exited {rc}: {err.strip()}")
            continue
        for m in re.finditer(r"^===== (\S+) — verbatim, (\d+) chars.*=====\n", out, re.M):
            rel, n = m.group(1), int(m.group(2))
            body = out[m.end():m.end() + n]
            disk = open(os.path.join(NEW, rel), encoding="utf-8").read()
            checked += 1
            if body != disk:
                problems.append(f"{pack}: {rel} printed text differs from the file on disk")
            if len(out) > 30000:
                problems.append(f"{pack}: output is {len(out)} chars, over the 30000-char Bash cap")
    return checked, problems


# Never executed by this harness, not even with --help (user rule): checked statically instead.
NEVER_RUN = {"mark_submitted.py", "hunt_contacts.py", "save_and_print_draft.py"}


def tree_state(dirs):
    state = {}
    for d in dirs:
        for dp, _, fs in os.walk(d):
            if "__pycache__" in dp:
                continue
            for f in fs:
                p = os.path.join(dp, f)
                st = os.stat(p)
                state[p] = (st.st_size, st.st_mtime_ns)
    return state


def check_help():
    """Every script answers -h/--help with exit 0 and usage text, and writes nothing."""
    watched = [os.path.join(NEW, "references"), os.path.join(ROOT, "job_search"),
               os.path.join(NEW, "scripts")]
    before = tree_state(watched)
    problems, ran, static = [], 0, 0
    for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
        name = os.path.basename(path)
        if name in NEVER_RUN:
            src = open(path).read()
            if "argparse" not in src and "['-h'], ['--help']" not in src:
                problems.append(f"{name}: no --help handling")
            static += 1
            continue
        rc, out, err = run([PY, path, "--help"], cwd=tempfile.gettempdir())
        ran += 1
        if rc != 0 or not out.strip():
            problems.append(f"{name} --help: exit {rc}, {len(out)} chars of stdout {err.strip()[:120]}")
    after = tree_state(watched)
    changed = sorted(p for p in set(before) | set(after) if before.get(p) != after.get(p))
    problems += [f"--help wrote {os.path.relpath(p, ROOT)}" for p in changed]
    return ran, static, problems


GATE_HOOK = os.path.join(ROOT, "claude", "hooks", "gate_resume_build.py")
GEN = "python3 ~/.claude/skills/job-automator/scripts/generate_pdf.py"


def gate_cases(d):
    """(label, command, hook-input extras, expected decision) for the B-GATE hook.
    d maps: no (APPLY No, no marker), ovr (APPLY No + .tailor_override), yes (APPLY Yes),
    blk (HARD BLOCK + a marker, which must be ignored)."""
    no, ovr, yes, blk = d["no"], d["ovr"], d["yes"], d["blk"]
    write = ("python3 -c \"import json,sys; open('$JOB_DIR/logs/tailored.json','w').write(\n"
             "  json.dumps(json.loads(sys.argv[1]),indent=2))\" '{\"a\": 1}'\n")
    chain = (f"export JOB_DIR={no}\n{write}{GEN} $JOB_DIR/logs/tailored.json $JOB_DIR; GEN=$?;"
             " echo \"GENERATE_EXIT=$GEN\"\nif [ $GEN -eq 0 ]; then\n  PDF=$(ls -t $JOB_DIR/resume_*.pdf | head -1)\n"
             "  pdfinfo \"$PDF\" | grep -i Pages\nfi\n")
    return [
        ("generate, absolute paths", f"{GEN} {no}/logs/tailored.json {no}", {}, "deny"),
        ("documented B4 block: write, then generate on the next line",
         write.replace("$JOB_DIR", no) + f"{GEN} {no}/logs/tailored.json {no}", {}, "deny"),
        ("write; generate on one line", f"python3 -c \"print(1)\" '{{\"a\":1}}'; {GEN} {no}/logs/tailored.json {no}",
         {}, "deny"),
        ("export JOB_DIR=… && generate $JOB_DIR", f"export JOB_DIR={no} && {GEN} $JOB_DIR/logs/tailored.json $JOB_DIR",
         {}, "deny"),
        ("B4 chain with if/then", chain, {}, "deny"),
        ("if/then wrapper", f"if true; then {GEN} {no}/logs/tailored.json {no}; fi", {}, "deny"),
        ("bash -c payload", f"bash -c \"{GEN} {no}/logs/tailored.json {no}\"", {}, "deny"),
        ("resume_cache index with line continuation",
         f"python3 ~/.claude/skills/job-automator/scripts/resume_cache.py index {no}/logs/fit.json {no} \\\n"
         f"  {no}/resume_1.pdf {no}/main_1.tex", {}, "deny"),
        ("relative paths, session cwd = job dir", f"{GEN} logs/tailored.json .", {"cwd": no}, "deny"),
        ("$JOB_DIR set only in an earlier Bash call (transcript)", f"{GEN} $JOB_DIR/logs/tailored.json $JOB_DIR",
         {"transcript": no}, "deny"),
        ("HARD BLOCK ignores the override marker", f"{GEN} {blk}/logs/tailored.json {blk}", {}, "deny"),
        ("APPLY Yes", f"{GEN} {yes}/logs/tailored.json {yes}", {}, "allow"),
        ("APPLY Yes, B4 chain", chain.replace(no, yes), {}, "allow"),
        ("APPLY No + Tailor-anyway marker", f"{GEN} {ovr}/logs/tailored.json {ovr}", {}, "allow"),
        ("grep that names the script", "grep -rn generate_pdf.py .", {"cwd": no}, "allow"),
        ("echo that names the script", f"echo \"next: {GEN} {no}/logs/tailored.json {no}\"", {}, "allow"),
        ("heredoc that quotes the build", f"cat <<'EOF'\n{GEN} {no}/logs/tailored.json {no}\nEOF", {}, "allow"),
        ("comment that names the build", f"ls {no}  # then {GEN} {no}/logs/tailored.json {no}", {}, "allow"),
        ("resume_cache check (not index)",
         f"python3 ~/.claude/skills/job-automator/scripts/resume_cache.py check {no}/logs/fit.json", {}, "allow"),
        ("A6.5 heredoc + merge", f"cat > {no}/logs/semantic.json <<'JSON'\n{{\"llm_match_pct\": 50}}\nJSON\n"
         f"python3 ~/.claude/skills/job-automator/scripts/score_fit.py --add-semantic {no}/logs/semantic.json"
         f" --job-dir {no} --report --log", {}, "allow"),
    ]


def check_gate_hook(old_hook, tmp):
    """New hook must match every expected decision; it must also allow everything
    expected-allow that the old hook allowed (no new false denials)."""
    base = os.path.join(tmp, "gate")
    d = {}
    for key, apply_v, marker in (("no", "No", False), ("ovr", "No", True), ("yes", "Yes", False),
                                 ("blk", "HARD BLOCK", True)):
        jd = os.path.join(base, key)
        os.makedirs(os.path.join(jd, "logs"), exist_ok=True)
        json.dump({"company": "X", "role": key, "match_pct": 50,
                   "verdicts": {"apply": apply_v, "hard_blocker_triggered": key == "blk",
                                "hard_blocker_reason": "ITAR" if key == "blk" else None}},
                  open(os.path.join(jd, "logs", "fit.json"), "w"))
        if marker:
            open(os.path.join(jd, "logs", ".tailor_override"), "w").close()
        d[key] = jd
    rows, problems = [], []
    env = {k: v for k, v in os.environ.items() if k != "JOB_DIR"}
    for label, cmd, extra, want in gate_cases(d):
        inp = {"tool_name": "Bash", "tool_input": {"command": cmd}, "cwd": extra.get("cwd", tmp)}
        if "transcript" in extra:
            tp = os.path.join(base, "transcript.jsonl")
            rec = {"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Bash",
                 "input": {"command": f"export JOB_DIR={extra['transcript']} && mkdir -p $JOB_DIR/logs"}}]}}
            open(tp, "w").write(json.dumps(rec) + "\n")
            inp["transcript_path"] = tp
        got = {}
        for side, hook in (("old", old_hook), ("new", GATE_HOOK)):
            p = subprocess.run([PY, hook], input=json.dumps(inp), capture_output=True, text=True,
                               env=env, cwd=tmp)
            got[side] = "deny" if '"deny"' in p.stdout else "allow"
        rows.append((label, got["old"], got["new"], want))
        if got["new"] != want:
            problems.append(f"{label}: new hook says {got['new']}, expected {want}")
        if want == "allow" and got["old"] == "allow" and got["new"] != "allow":
            problems.append(f"{label}: newly denied")
    return rows, problems


def build_postings(items):
    posts = []
    for i, it in enumerate(items):
        jd = it["payload"].get("jd") or {}
        parts = []
        for k in ("key_responsibilities", "required_skills", "preferred_skills", "ats_keywords"):
            v = jd.get(k)
            if isinstance(v, list):
                parts += [str(x) for x in v]
        parts.append(str(jd.get("location") or ""))
        posts.append({"id": i, "title": str(jd.get("job_title") or ""), "jd_text": "\n".join(parts)})
    return {"postings": posts}


def check_prefilter(old_code, items, tmp):
    pf = os.path.join(tmp, "postings.json")
    json.dump(build_postings(items), open(pf, "w"))
    res = {}
    for side, code in (("old", old_code), ("new", NEW)):
        refs = os.path.join(code, "references")
        rc, out, err = run([PY, os.path.join(code, "scripts", "keyword_prefilter.py"), pf,
                            "--keywords", os.path.join(refs, "keywords_only.json"),
                            "--profile", os.path.join(refs, "master_profile.json"),
                            "--context", os.path.join(refs, "candidate_context.md")])
        if rc != 0:
            return {"error": f"{side} keyword_prefilter.py exited {rc}: {err.strip()[:300]}"}
        res[side] = json.loads(out)["postings"]
    strip = lambda ps: [{k: v for k, v in p.items() if k != "sponsorship_flag"} for p in ps]
    flips = sum(1 for a, b in zip(res["old"], res["new"])
                if a.get("sponsorship_flag") != b.get("sponsorship_flag"))
    sys.path.insert(0, SCRIPTS)
    from keyword_prefilter import load_sponsorship_context  # noqa: E402  (new code)
    phrases = load_sponsorship_context(os.path.join(NEW, "references", "candidate_context.md"))
    phrases = phrases["no_sponsorship_phrases"]
    return {
        "survivors": len(res["new"]),
        "same_shortlist": strip(res["old"]) == strip(res["new"]),
        "flips": flips,
        "old_flagged": sum(1 for p in res["old"] if p.get("sponsorship_flag")),
        "new_flagged": sum(1 for p in res["new"] if p.get("sponsorship_flag")),
        "phrases": len(phrases),
        "comment_phrases": [p for p in phrases if "#" in p or "caught" in p],
    }


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--base", default="main")
    ap.add_argument("--old")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min", type=int, default=30)
    ap.add_argument("--workers", type=int, default=max(2, (os.cpu_count() or 4)))
    ap.add_argument("--keep", action="store_true", help="keep the temp dir")
    a = ap.parse_args()

    tmp = tempfile.mkdtemp(prefix="ja_regress_")
    try:
        old_code = os.path.abspath(a.old) if a.old else extract_old(a.base, os.path.join(tmp, "old_src"))
        if not os.path.exists(os.path.join(old_code, "scripts", "score_fit.py")):
            print(f"ERROR: no scripts/score_fit.py under {old_code}", file=sys.stderr)
            return 2
        sys.path.insert(0, SCRIPTS)
        import score_fit as new_score_fit  # noqa: E402
        flags = hasattr(new_score_fit, "REPORT_BEGIN")

        items = collect_fixtures(a.limit)
        print(f"old code : {a.old or 'git ' + a.base}")
        print(f"fixtures : {len(items)} "
              f"({sum(1 for i in items if i['src'].endswith('fit.json'))} rebuilt from fit.json, "
              f"{sum(1 for i in items if not i['src'].endswith('fit.json'))} stored payloads, "
              f"{sum(1 for i in items if i['semantic'])} with a semantic read)")

        failures, counts = [], {"score": 0, "merge": 0, "report": 0, "log": 0, "flags": 0}

        def one(idx):
            it = items[idx]
            o = replay(old_code, os.path.join(tmp, "o", str(idx)), it)
            n = replay(NEW, os.path.join(tmp, "n", str(idx)), it)
            keys = ["score", "fit0", "report0", "log0", "merge", "fit1", "report1", "log1", "log_rows"]
            bad = compare(o, n, keys)
            f = None
            if flags and "err" not in o:
                f = replay_flags(NEW, os.path.join(tmp, "f", str(idx)), it)
                bad += [("flags:" + k, d) for k, d in compare(expected_flags(o, new_score_fit), f,
                                                              ["score", "fit0", "merge", "fit1",
                                                               "log_rows"])]
                old_txt = "\n".join(x[1] for x in (o.get("report0"), o.get("report1")) if x)
                new_txt = "\n".join(x[1] for x in (f.get("score"), f.get("merge")) if x)
                if emploive_values(old_txt) != emploive_values(new_txt):
                    bad.append(("emploive", f"{emploive_values(old_txt)} != {emploive_values(new_txt)}"))
            return idx, o, n, f, bad

        olds, news = {}, {}
        with cf.ThreadPoolExecutor(a.workers) as ex:
            for idx, o, n, f, bad in ex.map(one, range(len(items))):
                olds[idx], news[idx] = o, n
                counts["score"] += 1
                counts["merge"] += "merge" in o
                counts["report"] += ("report0" in o) + ("report1" in o)
                counts["log"] += ("log0" in o) + ("log1" in o)
                counts["flags"] += f is not None
                for k, d in bad:
                    failures.append(f"[{items[idx]['src']}] {k}\n{d}")

        # Format 2 batch table on the final fit.json of every fixture that scored
        ok_idx = [i for i in range(len(items)) if olds[i]["score"][0] == 0][:60]
        if len(ok_idx) >= 2:
            ob = run([PY, os.path.join(old_code, "scripts", "render_report.py")]
                     + [olds[i]["fit_path"] for i in ok_idx])[:2]
            nb = run([PY, os.path.join(NEW, "scripts", "render_report.py")]
                     + [news[i]["fit_path"] for i in ok_idx])[:2]
            if ob != nb:
                failures.append("[batch] render_report Format 2\n" + diff(ob[1], nb[1], "batch"))

        print(f"replayed : score_fit {counts['score']} · semantic merges {counts['merge']} · "
              f"reports {counts['report']} (+1 batch of {len(ok_idx)}) · log rows {counts['log']} · "
              f"one-call --report/--log {counts['flags'] if flags else 'n/a (not in this code yet)'}")

        checked, pr_problems = check_print_refs()
        if checked is None:
            print("print_refs: n/a (script not present yet)")
        else:
            print(f"print_refs: {checked} files compared byte-for-byte")
            failures += [f"[print_refs] {p}" for p in pr_problems]

        missing, applied, added, stale = check_text(old_code)
        print(f"skill text: {len(missing)} old paragraphs missing · {len(applied)} listed wording edits · "
              f"{len(added)} new paragraphs")
        for e in applied:
            print(f"   edited  {e['file']}: {e['why']}")
        for f_, p in added:
            print(f"   added   {f_}: {p[:110]}")
        for e in stale:
            failures.append(f"[text] EXPECTED_TEXT_EDITS entry not found in old {e['file']}: "
                            f"{e['old'][:80]!r}")
        for f_, p in missing:
            failures.append(f"[text] {f_}: old paragraph missing from the new skill text:\n   {p}")

        pf = check_prefilter(old_code, items, tmp)
        if "error" in pf:
            failures.append(f"[prefilter] {pf['error']}")
        else:
            print(f"prefilter : {pf['survivors']} survivors, shortlist identical: {pf['same_shortlist']} · "
                  f"sponsorship_flag old {pf['old_flagged']} → new {pf['new_flagged']} "
                  f"({pf['flips']} flips) · {pf['phrases']} phrases parsed")
            if not pf["same_shortlist"]:
                failures.append("[prefilter] shortlist / scores / seniority flags changed")
            if pf["comment_phrases"]:
                failures.append(f"[prefilter] comment text parsed as phrases: {pf['comment_phrases'][:5]}")

        old_hook = os.path.join(tmp, "old_gate_resume_build.py")
        try:
            src = subprocess.run(["git", "-C", ROOT, "show", f"{a.base}:claude/hooks/gate_resume_build.py"],
                                 capture_output=True, check=True).stdout
            open(old_hook, "wb").write(src)
        except (subprocess.CalledProcessError, OSError):
            old_hook = GATE_HOOK
        rows, gate_problems = check_gate_hook(old_hook, tmp)
        closed = sum(1 for _, o, n, w in rows if o != w and n == w)
        print(f"gate hook : {len(rows)} commands · {sum(1 for r in rows if r[2] == r[3])} as expected · "
              f"{closed} gap(s) the old hook let through now closed")
        for label, o, n, w in rows:
            if o != n:
                print(f"   {label}: old {o} → new {n} (expected {w})")
        failures += [f"[gate hook] {p}" for p in gate_problems]

        ran, static, help_problems = check_help()
        print(f"--help    : {ran} scripts run with --help, {static} checked statically (never run), "
              f"{len(help_problems)} problem(s)")
        failures += [f"[--help] {p}" for p in help_problems]

        rc, out, _ = run([PY, os.path.join(NEW, "scripts", "validate_skill.py")])
        print(f"validate  : {out.strip().splitlines()[-1] if out.strip() else 'no output'}")
        if rc != 0:
            failures.append("[validate_skill] " + out.strip())

        if len(items) < a.min:
            failures.append(f"only {len(items)} fixtures replayed (need {a.min})")

        print()
        if failures:
            for f_ in failures[:40]:
                print("FAIL", f_)
            if len(failures) > 40:
                print(f"... {len(failures) - 40} more")
            print(f"\nFAIL — {len(failures)} difference(s)")
            return 1
        print("PASS — old and new outputs are identical")
        return 0
    finally:
        if a.keep:
            print(f"(kept {tmp})")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
