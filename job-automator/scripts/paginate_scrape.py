#!/usr/bin/env python3
"""
Generic fallback for a company's open-role list when resolve_ats_roles.py finds
no known ATS API — a fully custom career page. Uses headless Playwright (zero
LLM tokens) to load the page and, optionally, click through pagination.

This is a template, not a one-size-fits-all scraper: custom career pages don't
share a common structure, so it needs a CSS selector for the job links and
(optionally) a selector for a "next page" control. Get these once per site by
inspecting the page (read_page/find in claude-in-chrome, or view-source), then
this script is reusable for that site going forward (e.g. re-checking for new
postings weekly) without re-deriving the selectors each time.

Usage:
    python3 paginate_scrape.py <url> --link-selector "a.job-link" \\
        [--next-selector "button.next-page"] [--max-pages 20] [--wait-ms 1500]

Output (stdout): JSON {"count": N, "postings": [{"title": "...", "url": "..."}]}
Exit 0 on success, 1 if the page never rendered any matching links at all
(wrong selector, or the page needs a different scrape approach entirely —
fall back to a one-off claude-in-chrome read for this specific site).
"""
import argparse
import json
import sys
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


def scrape(url: str, link_selector: str, next_selector: str | None,
           max_pages: int, wait_ms: int) -> list:
    postings = []
    seen_urls = set()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)

        for page_num in range(1, max_pages + 1):
            page.wait_for_timeout(wait_ms)
            links = page.query_selector_all(link_selector)
            new_this_page = 0
            for link in links:
                href = link.get_attribute("href")
                title = (link.inner_text() or "").strip()
                if not href or not title:
                    continue
                full_url = urljoin(page.url, href)
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                postings.append({"title": title, "url": full_url})
                new_this_page += 1

            if not next_selector:
                break  # single page, no pagination requested

            next_btn = page.query_selector(next_selector)
            if not next_btn or not next_btn.is_enabled() or new_this_page == 0:
                break  # no more pages, or button disabled, or stalled (no new items)

            next_btn.click()
            page.wait_for_timeout(wait_ms)

        browser.close()

    return postings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--link-selector", required=True,
                     help='CSS selector for job posting links, e.g. "a.job-link"')
    ap.add_argument("--next-selector", default=None,
                     help='CSS selector for the "next page" control, if paginated')
    ap.add_argument("--max-pages", type=int, default=20)
    ap.add_argument("--wait-ms", type=int, default=1500,
                     help="Wait time after each nav/click for content to render")
    args = ap.parse_args()

    try:
        postings = scrape(args.url, args.link_selector, args.next_selector,
                           args.max_pages, args.wait_ms)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)

    if not postings:
        print(json.dumps({
            "error": "no links matched the given selector — verify it against "
                     "the live page (read_page/find in claude-in-chrome) before retrying",
        }), file=sys.stderr)
        sys.exit(1)

    print(json.dumps({"count": len(postings), "postings": postings}, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
