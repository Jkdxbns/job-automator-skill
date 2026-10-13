#!/usr/bin/env python3
"""One call for everything the orchestrator needs from its agent sessions.

usage: results_table.py [--keep] NAME [NAME ...]

Prints, in order:  the results table | TAILOR: names to type "tailor resume" into |
                   REJECT: names to rename+close | NOTES: one line per session with a flag.
So the orchestrator never reads an export, a screen or a log itself; it only reads this output.

Where the numbers come from (first that works):
  0. fit.json  the exact job folder is recovered from the session log (it records JOB_DIR), then
     ~/Desktop/jobs/<job>/logs/fit.json gives match_pct, verdicts, semantic %, seniority; resume status
     comes from resume_*.pdf + pdfinfo. No typing into the session at all.
  1. session log  (~/.claude/projects/*/<id>.jsonl; the name is its `custom-title` record). Used when
     there is no fit.json, e.g. a job stopped by the pre-screen hard block. No typing.
  2. /export  Claude Code draws in tmux's alternate screen, which keeps NO scrollback, so a long report
     scrolls its score lines out of reach of capture-pane. `/export <file>` writes the whole conversation
     to a file. It is typed only into an idle `claude` session; the file is DELETED after parsing
     (use --keep to leave it).
  3. the visible tmux screen (last resort).
A busy session is reported `running` and left untouched. Nothing is scored here; fit.json is only read, never written.

verdict: apply | can-try | no | blocked | error | running | waiting
"""
import glob, json, os, re, subprocess, sys, time

EXPORT_DIR = os.path.expanduser("~/Desktop/jobs/_batch/exports")
PROJECTS = os.path.expanduser("~/.claude/projects")
KEEP = False

def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None

def screen(name):
    return sh("tmux", "capture-pane", "-t", f"={name}:", "-p", "-S", "-")

def from_log(name):
    """Rebuild the conversation text from the newest session log titled NAME."""
    needle = f'"customTitle":"{name}"'
    files = sorted(glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")), key=os.path.getmtime, reverse=True)[:80]
    for f in files:
        try:
            if needle not in open(f, encoding="utf-8", errors="replace").read():
                continue
        except OSError:
            continue
        out = []
        for line in open(f, encoding="utf-8", errors="replace"):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            m = r.get("message") or {}
            c = m.get("content")
            if r.get("type") == "user":
                if isinstance(c, str):
                    out.append("❯ " + c.strip())
                elif isinstance(c, list):
                    for b in c:
                        if b.get("type") == "text":
                            out.append("❯ " + b["text"].strip())
                        elif b.get("type") == "tool_result":
                            x = b.get("content")
                            out.append(x if isinstance(x, str) else " ".join(i.get("text", "") for i in x if isinstance(i, dict)))
            elif r.get("type") == "assistant" and isinstance(c, list):
                for b in c:
                    if b.get("type") == "text":
                        out.append(b["text"])
                    elif b.get("type") == "tool_use" and b.get("name") == "Bash":
                        out.append("$ " + (b.get("input") or {}).get("command", ""))
        return "\n".join(out)
    return None

JOBS = os.path.expanduser("~/Desktop/jobs")

def find_jobdir(log_text):
    """last JOB_DIR=... in the agent's own Bash commands, resolved to an absolute path"""
    hits = re.findall(r"JOB_DIR=([^\s;'\"]+)", log_text or "")
    for h in reversed(hits):
        h = h.replace("$PWD", JOBS).replace("${JOB_CWD}", JOBS).replace("$JOB_CWD", JOBS)
        h = os.path.expanduser(h)
        if not os.path.isabs(h):
            h = os.path.join(JOBS, h)
        if os.path.isfile(os.path.join(h, "logs", "fit.json")):
            return h
    return None

def resume_state(jobdir, tailor_req):
    pdfs = sorted(glob.glob(os.path.join(jobdir, "resume_*.pdf")), key=os.path.getmtime)
    if pdfs:
        out = sh("pdfinfo", pdfs[-1]) or ""
        pages = re.search(r"Pages:\s*(\d+)", out)
        return "generated" if (pages and pages.group(1) == "1") else "generating..."   # >1 page = still being redrafted
    return "generating..." if tailor_req else "N/A"

def parse_fit(name, jobdir, log_text):
    d = dict(name=name, match="N/A", sem="N/A", verdict="waiting", resume="N/A", notes=[])
    f = json.load(open(os.path.join(jobdir, "logs", "fit.json")))
    v = f.get("verdicts") or {}
    tailor_req = bool(re.search(r"^❯\s*tailor resume", log_text or "", re.M))
    if v.get("hard_blocker_triggered") or v.get("apply") == "HARD BLOCK":
        d["verdict"] = "blocked"
        d["notes"].append("blocked: " + str(v.get("hard_blocker_reason") or "hard blocker")[:110])
        return d
    d["verdict"] = {"Yes": "apply", "Can Try": "can-try", "No": "no"}.get(v.get("apply"), "waiting")
    if f.get("match_pct") is not None:
        d["match"] = f"{f['match_pct']}%"
    sem = (f.get("llm_analysis") or {}).get("llm_match_pct")
    if sem is not None:
        d["sem"] = f"{sem}%"
    d["resume"] = resume_state(jobdir, tailor_req)
    if f.get("seniority_fit") == "Mismatch":
        d["notes"].append("seniority Mismatch (years requirement)")
    if f.get("production_scope_required"):
        d["notes"].append("production-scope ownership expected")
    if re.search(r"(?:redraft|Tailor anyway)[^\n]*\?", log_text or "", re.I) and tailor_req:
        d["notes"].append("asks: redraft/tailor question left unanswered")
    return d

def get_text(name):
    """returns (text, state): state is 'ok' | 'running' | 'closed'"""
    scr = screen(name)
    if scr is None:                                       # tmux session gone: the log is all that's left
        return (from_log(name) or ""), "closed"
    cmd = (sh("tmux", "display", "-p", "-t", f"={name}:", "#{pane_current_command}") or "").strip()
    if cmd in ("bash", "zsh", "sh", "fish"):              # claude exited
        return (from_log(name) or scr), "closed"
    if "esc to interrupt" in scr[-1800:]:
        return scr, "running"
    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, f"{name}.txt")
    if os.path.exists(path):
        os.remove(path)
    subprocess.run(["tmux", "send-keys", "-t", f"={name}:", f"/export {path}"])
    time.sleep(1)
    subprocess.run(["tmux", "send-keys", "-t", f"={name}:", "Enter"])
    for _ in range(15):
        time.sleep(1)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            time.sleep(0.5)
            text = open(path, encoding="utf-8", errors="replace").read()
            if not KEEP:
                os.remove(path)
            return text, "ok"
    return (from_log(name) or scr), "ok"                  # /export failed: session log, then the screen

def last(pattern, text, flags=0):
    m = re.findall(pattern, text, flags)
    return m[-1] if m else None

def parse(name):
    scr = screen(name)
    if scr is not None and "esc to interrupt" in scr[-1800:]:          # busy: leave it alone
        return dict(name=name, match="N/A", sem="N/A", verdict="running", resume="N/A", notes=[])
    log_text = from_log(name)
    jobdir = find_jobdir(log_text)
    if jobdir:
        return parse_fit(name, jobdir, log_text)
    if log_text:                       # no fit.json (e.g. a pre-screen hard block): the log has the full text, no typing needed
        t = log_text
        cmd = (sh("tmux", "display", "-p", "-t", f"={name}:", "#{pane_current_command}") or "").strip() if scr is not None else ""
        state = "ok" if cmd == "claude" else "closed"
    else:
        t, state = get_text(name)      # last resorts: /export typed into the idle session, then the screen
    d = dict(name=name, match="N/A", sem="N/A", verdict="waiting", resume="N/A", notes=[])
    if state == "running":
        d["verdict"] = "running"
        return d
    blocked = bool(re.search(r"⛔\s*HARD BLOCK|HARD BLOCK:", t)) or last(r"APPLY\s+(HARD BLOCK)", t)
    match = last(r"match\s+([\d.]+)%", t)
    apply_ = last(r"APPLY\s+(Yes|Can Try|No)\b", t)
    sem = last(r"([\d.]+)%\s+skill/domain depth", t)
    seniority = last(r"seniority\s+(Aligned|Stretch|Mismatch)", t)
    k = t.rfind("tailor resume")
    tailor_req = bool(re.search(r"^❯\s*tailor resume", t, re.M))
    pdf = tailor_req and bool(re.search(r"PDF:|resume_\d{8}_\d{4}\.pdf|Pages:\s*1", t[k:]))
    err = re.search(r"Permission denied for reading page content|could not (?:fetch|scrape)|paste the JD", t, re.I)
    if blocked:
        d["verdict"] = "blocked"
        why = last(r"(?:BLOCK[^\n]*?[:\-]\s*)([^\n]{0,110})", t)
        d["notes"].append("blocked: " + (why or "hard blocker").strip())
    elif apply_:
        d["verdict"] = {"Yes": "apply", "Can Try": "can-try", "No": "no"}[apply_]
        d["match"] = f"{match}%" if match else "N/A"
        d["sem"] = f"{sem}%" if sem else "N/A"
        d["resume"] = "generated" if pdf else ("generating..." if tailor_req else "N/A")
    elif err or state == "closed":
        d["verdict"] = "error"
        d["notes"].append("no report found" if state == "closed" else "could not fetch the JD / permission denied")
    if seniority == "Mismatch":
        d["notes"].append("seniority Mismatch (years requirement)")
    if re.search(r"production-scope ownership", t):
        d["notes"].append("production-scope ownership expected")
    if re.search(r"(?:redraft|Tailor anyway)[^\n]*\?", t, re.I) and tailor_req:
        d["notes"].append("asks: redraft/tailor question left unanswered")
    return d

def num(x):
    try:
        return float(x.rstrip("%"))
    except ValueError:
        return None

def main():
    global KEEP
    args = sys.argv[1:]
    if "--keep" in args:
        KEEP = True
        args.remove("--keep")
    if not args:
        sys.exit(__doc__)
    rows = [parse(n) for n in args]
    hdr = ["session_name", "match_score", "semantic", "verdict", "resume status"]
    print("| " + " | ".join(hdr) + " |")
    print("|" + "---|" * len(hdr))
    for r in rows:
        print(f"| {r['name']} | {r['match']} | {r['sem']} | {r['verdict']} | {r['resume']} |")
    tailor = [r["name"] for r in rows if (num(r["match"]) or 0) > 60 and (num(r["sem"]) or 0) > 40
              and r["verdict"] in ("apply", "can-try") and r["resume"] == "N/A"]
    reject = [r["name"] for r in rows
              if r["verdict"] == "blocked" or (num(r["match"]) is not None and num(r["match"]) < 40)]
    print("\nTAILOR: " + (", ".join(tailor) or "none"))
    print("REJECT: " + (", ".join(reject) or "none"))
    notes = [f"- {r['name']}: " + "; ".join(r["notes"]) for r in rows if r["notes"]]
    if notes:
        print("NOTES:\n" + "\n".join(notes))

main()
