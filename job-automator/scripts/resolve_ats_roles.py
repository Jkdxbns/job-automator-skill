#!/usr/bin/env python3
"""
Reusable, zero-LLM-token fetch of a company's full open-role list, by hitting
known ATS JSON APIs directly instead of scraping the rendered career page.

Covers Greenhouse, Lever, Ashby, SmartRecruiters, Recruitee, Workable — the
common hosted-ATS backends behind most "JS-rendered" career pages (the JSON
API is what the page's own JS calls under the hood; this just calls it directly).

Usage:
    python3 resolve_ats_roles.py <slug_or_url> [--commitment "Full time"]

<slug_or_url> can be:
  - a bare ATS slug if you already know it (e.g. "field-ai")
  - a company career page URL (https://company.com/careers) — the script will
    derive slug candidates from the domain and try them across all ATS types

Exit codes:
  0 = found postings via a known ATS API, printed normalized JSON to stdout
  1 = no known ATS API responded — fall back to browser-based scraping
      (claude-in-chrome for a one-off page, or paginate_scrape.py for a
      generic paginated/custom site)

Output shape (stdout, exit 0):
{
  "source_ats": "greenhouse|lever|ashby|smartrecruiters|recruitee|workable",
  "slug_used": "...",
  "count": N,
  "postings": [
    {"title": "...", "url": "...", "location": "...", "department": "...",
     "team": "...", "commitment": "Full time"|"Part time"|...|null,
     "jd_text": "..." or null}   # populated when the API includes it inline
  ]
}
"""
import html
import json
import re
import sys
from urllib.parse import urlparse

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def slug_candidates(raw: str) -> list:
    """Derive plausible ATS slugs from a bare slug or a career-page URL."""
    if "://" in raw:
        host = urlparse(raw).netloc
    else:
        host = raw
    base = re.sub(r"^www\.", "", host)
    base = base.split(".")[0] if "." in base else base
    base = base.strip().lower()

    candidates = {base}
    candidates.add(base.replace("-", ""))
    candidates.add(base.replace("_", "-"))
    if "://" not in raw:
        # caller supplied a bare slug directly (not a URL) — trust it as-is first
        candidates = {raw.strip().lower()} | candidates
    return list(candidates)


def try_greenhouse(slug: str, session: requests.Session):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    r = session.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("jobs", [])
    if not jobs:
        return None
    postings = []
    for j in jobs:
        commitment = None
        for m in j.get("metadata") or []:
            if m.get("name") == "Employment Type" and m.get("value"):
                commitment = m["value"]
                break
        postings.append({
            "title": j.get("title"),
            "url": j.get("absolute_url"),
            "location": (j.get("location") or {}).get("name"),
            "department": ", ".join(d.get("name", "") for d in j.get("departments", [])) or None,
            "team": None,
            "commitment": commitment,
            "jd_text": _strip_html(j.get("content")) if j.get("content") else None,
        })
    return {"source_ats": "greenhouse", "slug_used": slug, "postings": postings}


def try_lever(slug: str, session: requests.Session):
    url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    r = session.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    if not isinstance(data, list) or not data:
        return None
    postings = []
    for j in data:
        cats = j.get("categories", {})
        jd_parts = []
        for l in j.get("lists", []):
            jd_parts.append(f"{l.get('text','')}\n{_strip_html(l.get('content',''))}")
        for extra_key in ("descriptionPlain", "additionalPlain"):
            if j.get(extra_key):
                jd_parts.insert(0, j[extra_key])
        postings.append({
            "title": j.get("text"),
            "url": j.get("hostedUrl"),
            "location": cats.get("location"),
            "department": cats.get("department"),
            "team": cats.get("team"),
            "commitment": cats.get("commitment"),
            "jd_text": "\n\n".join(jd_parts) if jd_parts else None,
        })
    return {"source_ats": "lever", "slug_used": slug, "postings": postings}


def try_ashby(slug: str, session: requests.Session):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    r = session.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("jobs", [])
    if not jobs:
        return None
    postings = []
    for j in jobs:
        postings.append({
            "title": j.get("title"),
            "url": j.get("jobUrl"),
            "location": j.get("location"),
            "department": j.get("department"),
            "team": j.get("team"),
            "commitment": j.get("employmentType"),
            "jd_text": _strip_html(j.get("descriptionHtml")) if j.get("descriptionHtml") else None,
        })
    return {"source_ats": "ashby", "slug_used": slug, "postings": postings}


def try_smartrecruiters(slug: str, session: requests.Session):
    url = f"https://api.smartrecruiters.com/v1/companies/{slug}/postings"
    r = session.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("content", [])
    if not jobs:
        return None
    postings = []
    for j in jobs:
        loc = j.get("location", {})
        postings.append({
            "title": j.get("name"),
            "url": (j.get("ref") or {}).get("jobAd") or j.get("applyUrl"),
            "location": ", ".join(filter(None, [loc.get("city"), loc.get("region"), loc.get("country")])) or None,
            "department": (j.get("department") or {}).get("label"),
            "team": None,
            "commitment": (j.get("typeOfEmployment") or {}).get("label"),
            "jd_text": None,
        })
    return {"source_ats": "smartrecruiters", "slug_used": slug, "postings": postings}


def try_recruitee(slug: str, session: requests.Session):
    url = f"https://{slug}.recruitee.com/api/offers/"
    r = session.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("offers", [])
    if not jobs:
        return None
    postings = []
    for j in jobs:
        postings.append({
            "title": j.get("title"),
            "url": j.get("careers_url"),
            "location": j.get("location"),
            "department": j.get("department"),
            "team": None,
            "commitment": j.get("employment_type_code"),
            "jd_text": _strip_html(j.get("description")) if j.get("description") else None,
        })
    return {"source_ats": "recruitee", "slug_used": slug, "postings": postings}


def try_workable(slug: str, session: requests.Session):
    url = f"https://apply.workable.com/api/v1/widget/accounts/{slug}"
    r = session.get(url, headers=HEADERS, timeout=10)
    if r.status_code != 200:
        return None
    data = r.json()
    jobs = data.get("jobs", [])
    if not jobs:
        return None
    postings = []
    for j in jobs:
        postings.append({
            "title": j.get("title"),
            "url": j.get("url"),
            "location": j.get("location", {}).get("location_str") if isinstance(j.get("location"), dict) else j.get("location"),
            "department": j.get("department"),
            "team": None,
            "commitment": j.get("employment_type"),
            "jd_text": None,
        })
    return {"source_ats": "workable", "slug_used": slug, "postings": postings}


def _strip_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    text = html.unescape(raw_html)
    # some ATS APIs (Greenhouse) double-escape, so unescape twice defensively
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


ATS_TRIERS = [try_greenhouse, try_lever, try_ashby, try_smartrecruiters, try_recruitee, try_workable]


def main():
    if len(sys.argv) < 2:
        print("Usage: resolve_ats_roles.py <slug_or_url> [--commitment 'Full time']", file=sys.stderr)
        sys.exit(2)

    raw = sys.argv[1]
    commitment_filter = None
    if "--commitment" in sys.argv:
        commitment_filter = sys.argv[sys.argv.index("--commitment") + 1]

    session = requests.Session()
    candidates = slug_candidates(raw)

    for slug in candidates:
        for trier in ATS_TRIERS:
            try:
                result = trier(slug, session)
            except (requests.RequestException, ValueError, KeyError):
                continue
            if result and result["postings"]:
                if commitment_filter:
                    norm = lambda s: re.sub(r"[^a-z]", "", (s or "").lower())
                    result["postings"] = [
                        p for p in result["postings"]
                        if norm(p.get("commitment")) == norm(commitment_filter)
                    ]
                result["count"] = len(result["postings"])
                print(json.dumps(result, indent=2))
                sys.exit(0)

    print(json.dumps({
        "error": "no known ATS API responded",
        "slugs_tried": candidates,
        "ats_types_tried": [t.__name__.replace("try_", "") for t in ATS_TRIERS],
    }, indent=2), file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
