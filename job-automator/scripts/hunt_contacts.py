#!/usr/bin/env python3
"""
hunt_contacts.py — Sub-workflow G step G2: find hiring-side contacts at a company
via the Hunter.io API, verify their emails, and write them to the job dir.

HARD GATE: refuses to spend a single API credit unless the role is already in
~/job_search/submitted_log.csv. Justin's rule — the API is only used AFTER a job
is marked submitted. --force exists for re-runs, not for pre-submission hunting.

Usage:
  python3 hunt_contacts.py --job-dir $JOB_DIR [--n N] [--company "X"] [--domain x.com]
  python3 hunt_contacts.py --job-dir $JOB_DIR --quota      # just print quota, 0 credits

n (how many contacts) comes from fit.json's match_pct unless --n overrides:
  match >= 80 -> 10 · 60-79 -> 5 · < 60 -> 0 (exits, no API call)

Output: $JOB_DIR/logs/contacts.json  {company, domain, n_requested, contacts:[...]}
Each contact: first_name, last_name, position, email, confidence, verification,
rank_reason. Undeliverable emails are dropped before writing.

Exit codes: 0 ok · 1 error · 2 not submitted (gate) · 3 match too low · 4 quota
"""
import argparse, csv, json, os, re, sys, urllib.parse, urllib.request

API = "https://api.hunter.io/v2"
_HERE = os.path.dirname(os.path.abspath(__file__))
_REFS = os.path.join(os.path.dirname(_HERE), "references")
SUBMITTED_LOG = os.path.expanduser("~/job_search/submitted_log.csv")

# Title priority — who actually drives a hiring process, best first.
# Justin asks recruiters about the role/process; engineers get LinkedIn DMs instead.
RANK = [
    (re.compile(r"\btechnical recruit", re.I),                    1, "technical recruiter"),
    (re.compile(r"\b(sourcer|sourcing)\b", re.I),                 2, "sourcer"),
    (re.compile(r"\brecruit(er|ing)\b", re.I),                    3, "recruiter"),
    (re.compile(r"\btalent acquisition\b", re.I),                 4, "talent acquisition"),
    (re.compile(r"\b(university|campus|early career)\b", re.I),   5, "university/early-career"),
    (re.compile(r"\btalent\b", re.I),                             6, "talent"),
    (re.compile(r"\bpeople (ops|operations)\b", re.I),            7, "people ops"),
    (re.compile(r"\b(hiring manager|head of engineering|"
                r"engineering manager|director of engineering)\b", re.I), 8, "hiring manager"),
    (re.compile(r"\bhuman resources\b", re.I),                    9, "HR"),
]
# Never worth a credit: comp/benefits/payroll admin have no say in a specific req.
SKIP = re.compile(r"\b(benefits|payroll|compensation|total rewards|hris|"
                  r"immigration|workplace|facilities|learning)\b", re.I)


def api_key():
    k = os.environ.get("HUNTER_API_KEY")
    if k:
        return k.strip()
    path = os.path.join(_REFS, "hunter_key.txt")
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    sys.exit("ERROR: no Hunter API key. Set $HUNTER_API_KEY or write "
             f"{path} (one line, the key).")


def call(endpoint, **params):
    params["api_key"] = api_key()
    url = f"{API}/{endpoint}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try:
            body = json.load(e)
        except Exception:
            body = {"errors": [{"details": e.reason}]}
        return body
    except Exception as e:
        return {"errors": [{"details": str(e)}]}


# Legal-entity noise. Postings use registered names ("Amazon.com Services LLC",
# "Guidewire Software Solutions India Private Limited"); Hunter resolves brands.
_LEGAL = re.compile(r"\b(llc|l\.l\.c\.?|inc\.?|incorporated|ltd\.?|limited|corp\.?|"
                    r"corporation|co\.|company|gmbh|plc|pvt\.?|private|holdings?|"
                    r"group|lp|llp|s\.a\.|n\.v\.|a\.?g\.?|ab|sas|bv)\b", re.I)
_TAIL = re.compile(r"\b(services?|solutions?|technologies|technology|software|"
                   r"systems|labs?|india|usa|america|north|global|international)\b", re.I)


def name_variants(company):
    """Progressively simpler names to try. A 0-result search costs no credit, so
    trying a few is free; the first that resolves wins."""
    out, seen = [], set()

    def add(x):
        x = re.sub(r"[,&]", " ", x or "")
        x = re.sub(r"\s+", " ", x).strip(" -–—.")
        if x and x.lower() not in seen:
            seen.add(x.lower())
            out.append(x)

    add(company)
    stripped = _LEGAL.sub(" ", company or "")
    add(stripped)
    add(_TAIL.sub(" ", stripped))
    first = (stripped.strip().split() or [""])[0]
    add(first)
    if "." in first:                      # amazon.com -> amazon
        add(first.split(".")[0])
    return out


def _core_tokens(company):
    """Significant words of a company name, legal + descriptive noise removed."""
    s = _TAIL.sub(" ", _LEGAL.sub(" ", company or ""))
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 1}


def resolution_is_sane(company, org, domain):
    """Guard against the ladder resolving to a different company entirely.
    'Physical Intelligence' stripped to 'Physical' resolves to physical.pt, whose
    organization is literally 'Physical' — a naive name check passes it and we would
    draft mail to strangers. Require EVERY significant token to appear in the
    resolved org or domain."""
    core = _core_tokens(company)
    if not core:
        return True
    hay = re.sub(r"[^a-z0-9]", "", f"{org or ''} {domain or ''}".lower())
    return all(t in hay for t in core)


def quota():
    d = call("account").get("data", {}).get("requests", {})
    return (d.get("searches", {}).get("remaining", 0),
            d.get("verifications", {}).get("remaining", 0))


_ROLE_NOISE = {"i", "ii", "iii", "iv", "senior", "sr", "jr", "junior", "staff",
               "the", "and", "of", "for", "a", "an", "new", "grad", "engineer",
               "engineering", "software"}


def _toks(s):
    return {w for w in re.findall(r"[a-z0-9+#]+", (s or "").lower())
            if w not in _ROLE_NOISE and len(w) > 1}


def _same_role(a, b):
    """Role titles drift between fit.json and the log ('Robotics Systems Engineer,
    Tech Deployment' vs 'Robotics Systems Engineer II, RDPI Technology Deployment').
    Company is the hard key; the role only has to overlap."""
    ta, tb = _toks(a), _toks(b)
    if not ta or not tb:
        return True
    return len(ta & tb) / min(len(ta), len(tb)) >= 0.5


def is_submitted(company, role):
    """True if this company+role already has a row in the submitted log."""
    if not os.path.exists(SUBMITTED_LOG):
        return False
    c = (company or "").lower().strip()
    with open(SUBMITTED_LOG, newline="") as f:
        for row in csv.DictReader(f):
            rc = (row.get("company") or "").lower().strip()
            if rc == c and _same_role(role, row.get("role")):
                return True
    return False


def n_from_match(pct):
    if pct is None:
        return 0
    if pct >= 80:
        return 10
    if pct >= 60:
        return 5
    return 0


def rank(contacts):
    out = []
    for e in contacts:
        pos = e.get("position") or ""
        if SKIP.search(pos):
            continue
        tier, why = 99, None
        for pat, t, label in RANK:
            if pat.search(pos):
                tier, why = t, label
                break
        if why is None:
            continue                      # no hiring-side signal in the title
        out.append((tier, -(e.get("confidence") or 0), e, why))
    out.sort(key=lambda x: (x[0], x[1]))
    return [(e, why) for _, _, e, why in out]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--job-dir", default=os.environ.get("JOB_DIR", ""))
    p.add_argument("--company")
    p.add_argument("--domain")
    p.add_argument("--n", type=int)
    p.add_argument("--no-verify", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="skip the submitted-log gate (re-runs only)")
    p.add_argument("--quota", action="store_true", help="print quota and exit")
    a = p.parse_args()

    if a.quota:
        s, v = quota()
        print(f"searches remaining: {s} · verifications remaining: {v}")
        return

    fit = {}
    fit_path = os.path.join(a.job_dir, "logs", "fit.json") if a.job_dir else ""
    if fit_path and os.path.exists(fit_path):
        fit = json.load(open(fit_path))
    company = a.company or fit.get("company")
    role = fit.get("role", "")
    if not company:
        sys.exit("ERROR: no company (pass --company or point --job-dir at a fit.json)")

    # ---- GATE: submitted only ------------------------------------------------
    if not a.force and not is_submitted(company, role):
        print(f"NOT SUBMITTED: '{company} — {role}' is not in {SUBMITTED_LOG}.\n"
              "Hunter.io is only used after a job is marked submitted. "
              "Run mark_submitted.py first (or --force to re-run a hunt).")
        sys.exit(2)

    n = a.n if a.n is not None else n_from_match(fit.get("match_pct"))
    if n <= 0:
        print(f"MATCH TOO LOW: match_pct={fit.get('match_pct')} → n=0. "
              "No API call made. Pass --n to override.")
        sys.exit(3)

    searches, verifs = quota()
    need_v = 0 if a.no_verify else n
    if searches < 1 or verifs < need_v:
        print(f"QUOTA: {searches} searches / {verifs} verifications remaining; "
              f"this run needs 1 search and {need_v} verifications.")
        sys.exit(4)

    # ---- G2a: resolve domain + fetch HR contacts (1 search credit) -----------
    data, tried = {}, []
    if a.domain:
        res = call("domain-search", domain=a.domain, department="hr", limit=10)
        if "errors" in res:
            sys.exit("Hunter error: " + json.dumps(res["errors"]))
        data = res.get("data", {})
    else:
        for variant in name_variants(company):
            tried.append(variant)
            res = call("domain-search", company=variant, department="hr", limit=10)
            if "errors" in res:
                sys.exit("Hunter error: " + json.dumps(res["errors"]))
            d = res.get("data", {})
            if d.get("domain") and d.get("emails"):
                if not resolution_is_sane(company, d.get("organization"), d.get("domain")):
                    print(f"  (rejected '{variant}' -> {d.get('domain')} "
                          f"[{d.get('organization')}]: not the same company)")
                    continue
                data = d
                if variant.lower() != (company or "").lower():
                    print(f"(resolved '{company}' via '{variant}')")
                break
    domain = data.get("domain")
    if not domain:
        print(f"Could not resolve a domain for '{company}' "
              f"(tried: {', '.join(tried)}). Re-run with --domain company.com.")
        sys.exit(1)
    ranked = rank(data.get("emails", []))
    if not ranked:
        print(f"No hiring-side contacts found at {domain or company}.")
        sys.exit(1)

    # ---- G2b: verify each (1 verification credit each) -----------------------
    contacts = []
    for e, why in ranked[:n]:
        email = e.get("value")
        status = "not_verified"
        if not a.no_verify and email:
            v = call("email-verifier", email=email).get("data", {})
            status = v.get("status", "unknown")
            if status in ("invalid", "undeliverable"):
                continue                 # never draft to a bouncing address
        contacts.append({
            "first_name": e.get("first_name"), "last_name": e.get("last_name"),
            "position": e.get("position"), "email": email,
            "confidence": e.get("confidence"), "verification": status,
            "linkedin": e.get("linkedin"), "rank_reason": why,
        })

    out = {"company": company, "role": role, "domain": domain,
           "match_pct": fit.get("match_pct"), "n_requested": n,
           "found": len(contacts), "contacts": contacts}
    if a.job_dir:
        os.makedirs(os.path.join(a.job_dir, "logs"), exist_ok=True)
        dest = os.path.join(a.job_dir, "logs", "contacts.json")
        tmp = dest + ".tmp"
        with open(tmp, "w") as f:
            json.dump(out, f, indent=2)
        os.replace(tmp, dest)
        print(f"Wrote {dest}")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
