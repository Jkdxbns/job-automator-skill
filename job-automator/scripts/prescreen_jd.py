#!/usr/bin/env python3
"""
prescreen_jd.py — Scans JD text for hard disqualifiers using regex.
Zero LLM calls. Zero tokens. Runs before any API call.

Usage:
  echo "<jd text>" | python prescreen_jd.py
  python prescreen_jd.py < jd.txt
  python prescreen_jd.py "<jd text as arg>"

Exit codes:
  0 — clean, no blockers found, proceed with analysis
  1 — hard blocker found, print reason, STOP everything

Output on exit 1:
  BLOCK:<category>:<exact_match>
  e.g. BLOCK:Security Clearance:secret clearance

MAINTAINER NOTE — update this script, not the analysis workflow:
  If a job slips through and is later found to be disqualifying (wrong visa,
  clearance, citizenship, or no-sponsorship), add the exact phrase or a regex
  pattern to the relevant HARD_BLOCKERS category below. This script runs before
  any LLM call — every phrase caught here saves a full analysis run.
  Example: found "continuous work authorization" slipped through → add it to
  "No Sponsorship" and commit. Do not handle new patterns inline in the workflow.
"""

import re
import sys


# ── Region detection (added 2026-09-23) ───────────────────────────────────────
# Justin now applies to EU/UK roles as well as US ones. The four HARD_BLOCKERS
# categories below were all written against US postings. Three of the
# "No Sponsorship" patterns are phrased generically enough that they also fire on
# ordinary EU/UK boilerplate ("must be legally authorised to work in Ireland"),
# which is exactly the permission an EU employer would be sponsoring him FOR.
# Those three are skipped when the posting is clearly EU/UK.
#
# Everything else still fires everywhere, deliberately:
#   - explicit "no sponsorship" / "sponsorship is not available" — a real block
#     in Dublin just as much as in Dallas
#   - "citizens only" — on an EU posting this means EU citizens, still a block
#   - ITAR / export control / security clearance — EU defence primes (Thales,
#     Saab, Leonardo, BAE) gate on EU/NATO nationality and clearance the same way
#
# Detection fails SAFE: relaxation applies only when there is positive EU/UK
# evidence AND no US marker. Anything ambiguous keeps the old strict behaviour.

EU_UK_HINTS = [
    r"\bunited kingdom\b", r"\bengland\b", r"\bscotland\b", r"\bwales\b",
    r"\bireland\b", r"\bnetherlands\b", r"\bgermany\b", r"\bsweden\b",
    r"\bdenmark\b", r"\bnorway\b", r"\bfinland\b", r"\bbelgium\b",
    r"\bczech\b", r"\bczechia\b", r"\bpoland\b", r"\bportugal\b",
    r"\bspain\b", r"\bfrance\b", r"\bitaly\b", r"\baustria\b",
    r"\bswitzerland\b", r"\bhungary\b", r"\bromania\b", r"\bestonia\b",
    r"\blithuania\b", r"\beuropean union\b", r"\beu/eea\b", r"\beea\b",
    # cities that carry his target employers
    r"\blondon\b", r"\bbristol\b", r"\bedinburgh\b", r"\bglasgow\b",
    r"\bmanchester\b", r"\bkings langley\b",
    r"\bdublin\b", r"\bcork\b", r"\blimerick\b", r"\bleixlip\b",
    r"\beindhoven\b", r"\bveldhoven\b", r"\bamsterdam\b", r"\bnijmegen\b",
    r"\bdelft\b", r"\benschede\b", r"\brotterdam\b", r"\butrecht\b",
    r"\bmunich\b", r"\bm(?:u|ue|\u00fc)nchen\b", r"\bstuttgart\b",
    r"\bberlin\b", r"\bhamburg\b", r"\bdresden\b", r"\bnuremberg\b",
    r"\blund\b", r"\bgothenburg\b", r"\bg(?:o|oe|\u00f6)teborg\b",
    r"\bstockholm\b", r"\bmalm(?:o|oe|\u00f6)\b", r"\bcopenhagen\b",
    r"\bbrno\b", r"\bprague\b", r"\bro(?:z|\u017e)nov\b",
    r"\bkrak(?:o|\u00f3)w\b", r"\bcracow\b", r"\bgda(?:n|\u0144)sk\b",
    r"\bwarsaw\b", r"\bwroc(?:l|\u0142)aw\b",
    r"\bporto\b", r"\blisbon\b", r"\bbraga\b", r"\bleuven\b",
    r"\bgrenoble\b", r"\bcambridge,\s*(?:uk|england|cambridgeshire)\b",
]

# Strong US markers only. State abbreviations are deliberately NOT used — ", in"
# and ", or" match ordinary prose and would silently re-strict EU postings.
US_HINTS = [
    r"\bunited states\b", r"\bu\.?s\.?a\.?\b", r"\bu\.?s\.?\s+person\b",
    r"\bus\s+work\s+authorization\b", r"\bin\s+the\s+u\.?s\.?\b",
    r"\bstem\s+opt\b", r"\bh-?1b\b", r"\bgreen\s+card\b",
]

# Patterns skipped when the posting is EU/UK. Must match HARD_BLOCKERS verbatim.
RELAXED_IN_EU_UK = {
    r"\bmust\s+be\s+(?:legally\s+)?authorized\s+to\s+work\b",
    r"\bmust\s+have\s+(?:and\s+maintain\s+)?(?:continuous\s+)?work\s+authorization\b",
    r"\bcontinuous\s+work\s+authorization\b",
}


def detect_region(lowered: str) -> str:
    """'eu_uk' only on positive EU/UK evidence with no US marker; else 'us'."""
    if any(re.search(p, lowered) for p in US_HINTS):
        return "us"
    if any(re.search(p, lowered) for p in EU_UK_HINTS):
        return "eu_uk"
    return "us"


HARD_BLOCKERS = {
    "ITAR / US Person": [
        r"\bu\.?s\.?\s+person\b",
        r"\bitar\b",
        r"\bear\s+compliance\b",
        r"\bexport\s+control\b",
        r"\bdeemed\s+export\b",
        r"\bitar[\/\s]ear\b",
        # Caught manually in A5: ASML J-00352651 "legally authorized to access such
        # controlled technology" citing the Export Administration Regulations (15 C.F.R. § 730)
        r"\bexport\s+administration\s+regulations\b",
        r"\bcontrolled\s+technology\b",
    ],
    "Security Clearance": [
        r"\bsecurity\s+clearance\b",
        r"\bsecret\s+clearance\b",
        r"\btop\s+secret\b",
        r"\bts\/sci\b",
        r"\bdod\s+clearance\b",
        r"\bclearance\s+required\b",
        r"\bactive\s+clearance\b",
        r"\bobtain\s+(?:a\s+)?clearance\b",
        r"\bpublic\s+trust\s+clearance\b",
        r"\bmust\s+(?:hold|have|obtain)\s+(?:a\s+)?(?:security\s+)?clearance\b",
    ],
    "US Citizenship / PR Required": [
        r"\bmust\s+be\s+a\s+u\.?s\.?\s+citizen\b",
        r"\bu\.?s\.?\s+citizens?\s+only\b",
        r"\bcitizens?\s+only\b",
        r"\bpermanent\s+residents?\s+only\b",
        r"\bu\.?s\.?\s+citizen\s+or\s+(?:permanent\s+resident|green\s+card|pr)\b",
        # Caught live: Niyam IT "US Citizenship with ability to successfully complete a federal
        # background investigation." — bare noun-phrase bullet, no "requires"/"must be" verb.
        r"\bu\.?s\.?\s+citizenship\s+with\s+ability\s+to\s+(?:successfully\s+)?complete\s+a\s+federal\s+background\s+investigation\b",
    ],
    "No Sponsorship": [
        r"\bno\s+sponsorship\s+(?:available|offered|provided)\b",
        r"\bwill\s+not\s+(?:sponsor|provide\s+sponsorship)\b",
        r"\bauthorized\s+to\s+work\s+(?:in\s+the\s+u\.?s\.?|without\s+sponsorship)\b",
        # Caught live: TP-Link "continuous work authorization in the US without the need for visa sponsorships"
        r"\bcontinuous\s+work\s+authorization\b",
        r"\bwithout\s+the\s+need\s+for\s+(?:visa\s+)?sponsorship",
        r"\bmust\s+have\s+(?:and\s+maintain\s+)?(?:continuous\s+)?work\s+authorization\b",
        r"\bno\s+visa\s+sponsorship\b",
        # Bare forms. candidate_context.md lists these and the regex layer must
        # agree with it, or A2.5 passes a JD that A5 would then have to catch.
        r"\bno\s+sponsorship\b",
        r"\bmust\s+be\s+(?:legally\s+)?authorized\s+to\s+work\b",
        r"\bwithout\s+(?:current\s+or\s+future\s+)?(?:visa\s+)?sponsorship\b",
        r"\bnot\s+(?:able|able\s+to|in\s+a\s+position)\s+to\s+(?:offer|provide)\s+(?:visa\s+)?sponsorship\b",
        # Caught live: Motorola "Employer work permit sponsorship is not available for this position"
        r"\bsponsorship\s+is\s+not\s+available\b",
        # Caught live: Caterpillar "Visa sponsorship is NOT provided for this position"
        r"\bsponsorship\s+is\s+not\s+(?:provided|offered)\b",
        # Caught live: Eaton "will not consider applicants for employment immigration
        # sponsorship or support... will not support any CPT, OPT, or STEM OPT plans"
        r"\bwill\s+not\s+consider\s+applicants\s+for\s+employment\s+immigration\s+sponsorship\b",
        r"\bwill\s+not\s+support\s+any\s+cpt,?\s*opt,?\s*(?:or\s+)?stem\s+opt\b",
        r"\bnot\s+support\s+(?:any\s+)?(?:cpt|opt|stem\s+opt)\s+plans?\b",
        # Caught manually in A5: Vertiv (all US reqs on egup.fa.us2.oraclecloud.com), 2026-09-21 —
        # "This is not a position for which sponsorship will be provided. Individuals with temporary
        # visas such as E, F-1, H-1... are not eligible for hire."
        r"\bnot\s+a\s+position\s+for\s+which\s+sponsorship\s+will\s+be\s+provided\b",
        r"\btemporary\s+visas?\s+such\s+as\b[^.]{0,60}\bf-?1\b[^.]{0,120}\bnot\s+eligible\b",
        # Caught manually in A5: Grainger Businesses (Embedded Systems Engineer, req 335303),
        # 2026-09-24 — "This position is not eligible for any form of sponsorship now or in
        # the future. Individuals requiring sponsorship (e.g. OPT or H1B visa status) should
        # not apply."
        r"\bnot\s+eligible\s+for\s+any\s+form\s+of\s+sponsorship\b",
        r"\bindividuals\s+requiring\s+sponsorship\b[^.]{0,60}\bshould\s+not\s+apply\b",
        # Caught manually in A5: Ford Motor Company (Embedded Software Engineer, Sunrise FL,
        # hybrid), 2026-09-30 — "This position does not support sponsorship." Bare
        # "does not support" phrasing; every prior pattern used offer/provide/available/eligible.
        r"\b(?:does|do|will)\s+not\s+support\s+(?:visa\s+|employment\s+|immigration\s+)?sponsorship\b",
        # Caught manually in A5: Blue River Technology / John Deere (Software Engineer, See & Spray,
        # Santa Clara CA), 2026-10-01 — "Visa sponsorship: Not available." Label-colon form, with
        # the negation AFTER "sponsorship"; earlier patterns all put the negation first or used "is".
        r"\bsponsorship\s*:\s*(?:not\s+available|none|no|not\s+(?:offered|provided))\b",
        # Caught manually in A5: IDEX / Advanced Flow Solutions (Software Engineer - Embedded
        # Systems, Oklahoma City OK / Remote USA, R-10076), 2026-10-08 — "This role is not
        # available for employment visa sponsorship." Subject is the ROLE, not sponsorship, so
        # every prior "sponsorship is not available" pattern missed it.
        r"\b(?:this\s+)?(?:role|position|job|opening|req(?:uisition)?)\s+is\s+not\s+available\s+for\b[^.]{0,60}\bsponsorship\b",
        r"\bnot\s+available\s+for\s+(?:employment\s+|work\s+|immigration\s+)?visa\s+sponsorship\b",
        # Caught manually in A5: CRABI (Robotics GNC Engineer, Medford MA), 2026-10-05 — "The company
        # will not consider candidates who require sponsorship for a work-authorized visa, now or in
        # the future." Verb is "will not consider ... who require sponsorship".
        r"\bwill\s+not\s+consider\s+(?:candidates|applicants)\s+who\s+require\s+sponsorship\b",
        # Caught manually in A5: Optimove (Machine Learning Engineer, Dundee, Scotland), 2026-10-04 —
        # "Must be eligible to work in the UK - we are unable to provide sponsorship at this time."
        # Existing pattern only matched "not able to provide"; "unable to" slipped through.
        r"\bunable\s+to\s+(?:offer\s+or\s+)?(?:offer|provide)\s+(?:visa\s+)?sponsorship\b",
        # Caught manually in A5: Bright Vision Technologies (Embedded AI Engineer, Remote US),
        # 2026-10-08 — "We are unable to sponsor new H-1B visa petitions for this position."
        # Verb is bare "sponsor" + H-1B object, not the noun "sponsorship".
        r"\bunable\s+to\s+sponsor\s+(?:new\s+)?(?:h-?1b|visa|work)\b",
    ],
}


def scan(text: str, region: str | None = None) -> tuple[str | None, str | None, str | None]:
    """
    Returns (category, pattern, matched_text) if blocker found, else (None, None, None).
    Stops at first match.

    region: "us" | "eu_uk" | None (auto-detect). Callers that pass nothing keep
    the original behaviour on US postings; keyword_prefilter.py relies on this.
    """
    lowered = text.lower()
    if region is None:
        region = detect_region(lowered)
    for category, patterns in HARD_BLOCKERS.items():
        for pattern in patterns:
            if region == "eu_uk" and pattern in RELAXED_IN_EU_UK:
                continue
            m = re.search(pattern, lowered)
            if m:
                return category, pattern, m.group(0)
    return None, None, None


def main():
    # Accept JD text from stdin or as first argument.
    # --region auto|us|eu overrides detection; auto is the default.
    argv = sys.argv[1:]
    region = None
    for flag in ("--region", "-r"):
        if flag in argv:
            i = argv.index(flag)
            val = argv[i + 1] if i + 1 < len(argv) else "auto"
            region = {"eu": "eu_uk", "uk": "eu_uk", "eu_uk": "eu_uk",
                      "us": "us", "auto": None}.get(val.lower(), None)
            del argv[i:i + 2]
            break

    jd_text = argv[0] if argv else sys.stdin.read()

    if not jd_text.strip():
        print("ERROR: No JD text provided", file=sys.stderr)
        sys.exit(2)

    print(f"region={region or detect_region(jd_text.lower())}", file=sys.stderr)
    category, pattern, matched = scan(jd_text, region)

    if category:
        # Machine-readable line for the skill to parse
        print(f"BLOCK:{category}:{matched}")
        sys.exit(1)
    else:
        print("CLEAR")
        sys.exit(0)


if __name__ == "__main__":
    if sys.argv[1:2] in (['-h'], ['--help']):   # usage, no side effects
        print(__doc__)
        sys.exit(0)
    main()
