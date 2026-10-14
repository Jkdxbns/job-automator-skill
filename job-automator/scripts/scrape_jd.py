#!/usr/bin/env python3
"""
scrape_jd.py — Scrapes a job description from an ATS URL.
Usage: python scrape_jd.py <url>
Prints raw JD text to stdout.

Exit codes: 0=success, 2=auth wall, 3=insufficient text
"""

import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCK_SIGNALS = ["authwall", "login", "signin", "challenge", "captcha", "checkpoint"]
NOISE_TAGS = ["nav", "footer", "header", "script", "style", "aside", "noscript", "iframe", "svg"]

ATS_SELECTORS = [
    {"id": "app_body"},                                          # Greenhouse
    {"class": "content"},                                        # Lever
    {"class": "ashby-job-posting-brief-description"},            # Ashby
    {"data-automation-id": "jobPostingDescription"},             # Workday
    {"class": "description__text"},                              # LinkedIn
    {"id": "jobDescriptionText"},                                # Indeed
    {"class": "job-description"},
    {"class": "posting-description"},
    {"id": "job-description"},
]


def scrape(url: str) -> str:
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
    except requests.RequestException as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    if any(s in r.url.lower() for s in BLOCK_SIGNALS) or r.status_code in (401, 403):
        print("BLOCKED", file=sys.stderr)
        sys.exit(2)

    soup = BeautifulSoup(r.text, "html.parser")

    for sel in ATS_SELECTORS:
        attr, val = list(sel.items())[0]
        el = soup.find(id=val) if attr == "id" else soup.find(attrs={attr: lambda v, val=val: v and val in str(v)})
        if el:
            for tag in el(NOISE_TAGS): tag.decompose()
            text = el.get_text(separator="\n", strip=True)
            if len(text) > 200:
                return text

    for tag in soup(NOISE_TAGS): tag.decompose()
    text = soup.get_text(separator="\n", strip=True)

    if len(text) < 100:
        print("INSUFFICIENT", file=sys.stderr)
        sys.exit(3)

    return text


if __name__ == "__main__":
    if sys.argv[1:2] in (['-h'], ['--help']):   # usage, no side effects
        print(__doc__)
        sys.exit(0)
    if len(sys.argv) < 2:
        print("Usage: python scrape_jd.py <url>")
        sys.exit(1)
    print(scrape(sys.argv[1]))
