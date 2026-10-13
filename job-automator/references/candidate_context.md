# Candidate Context
# Edit this file to match your personal situation.

[identity] name = Justin Mascarenhas degree = M.S. Computer Engineering school = Rochester Institute of
Technology graduation = May 2026 experience_level = new-grad # options: student | new-grad | junior | mid |
senior

[experience] full_time_years = 0 internships = 6 # total internship count description = Fresher with 0 years
full-time experience but 7 internships across ML, embedded, research, and robotics domains.

[location] current = Arlington, TX, USA willing_to_relocate = true preferred_locations = any # comma-separated
cities, or "any" remote_ok = true

[visa] status = F-1 OPT # e.g. F-1 OPT | H1B | Green Card | US Citizen requires_sponsorship = true # true if
you need H1B sponsorship long-term ead_pending = true # true if EAD not yet approved notice_period_weeks = 4 #
weeks before you can start

[sponsorship_policy]
# Companies known to sponsor H1B for new grads (high confidence)
known_sponsors = Google, Meta, Microsoft, Amazon, Apple, NVIDIA, Qualcomm, Intel, IBM, Salesforce, Adobe,
Uber, Lyft, Airbnb, Stripe, Databricks, OpenAI, Anthropic, Waymo, Tesla, Palantir, Two Sigma, Jane Street,
Citadel, Bloomberg, Oracle, SAP, Cisco, Broadcom, AMD, Applied Materials, Lam Research, KLA

# Red flag phrases in JD that signal no sponsorship
no_sponsorship_phrases = must be authorized to work, no sponsorship, us citizen or permanent resident, must
have work authorization, visa sponsorship is not provided, not a position for which sponsorship will be provided, individuals with temporary visas such as f-1 are not eligible for hire, sponsorship is offered exclusively for principal-level roles, sponsorship offered exclusively for principal-level, roles below the principal level require candidates to possess unrestricted u.s. work authorization, not eligible for any form of sponsorship now or in the future, individuals requiring sponsorship (e.g. opt or h1b visa status) should not apply, this position does not support sponsorship, visa sponsorship: not available, we are unable to provide sponsorship, this role is not available for employment visa sponsorship, not available for employment visa sponsorship
# Also caught manually: CRABI, "Robotics GNC Engineer", Medford, MA, 2026-10-05 — "The company will not
# consider candidates who require sponsorship for a work-authorized visa, now or in the future." Regex
# missed it (verb "will not consider ... who require sponsorship"); pattern now added to prescreen_jd.py.
# Also caught manually: Optimove, "Machine Learning Engineer", Dundee, Scotland, 2026-10-04 — "Must be
# eligible to work in the UK - we are unable to provide sponsorship at this time." Explicit refusal in an EU/UK
# posting, so the region relaxation does not apply. Regex had "not able to provide" only; "unable to" added.
# First caught (exact phrase not in prior list): Medtronic, "Embedded Software Engineer II (Christine)",
# Lafayette, CO, R78076, 2026-09-23 — tiered sponsorship policy: H-1B/TN/J offered only at Principal level
# and above; this is a Level II role, so sponsorship is explicitly excluded. Caught only on the manual A5
# second pass, not the A2.5 regex — the phrasing ties sponsorship to seniority rather than using a flat
# "no sponsorship" statement.
# Also caught manually: Grainger Businesses, "Embedded Systems Engineer", Santa Ana, CA, req 335303,
# 2026-09-24 — "This position is not eligible for any form of sponsorship now or in the future.
# Individuals requiring sponsorship (e.g. OPT or H1B visa status) should not apply." Regex now added
# to prescreen_jd.py.
# Also caught manually: Ford Motor Company, "Embedded Software Engineer", Sunrise FL, hybrid,
# 2026-09-30 — "This position does not support sponsorship." listed as a required qualification.
# Regex missed it: every prior pattern keyed on offer/provide/available/eligible, none on the bare
# "does not support" verb. Pattern now added to prescreen_jd.py. Note this supersedes the
# 2026-06-30 analysis of the same req, which recorded sponsorship as CONTRADICTORY.
# Also caught manually: Copeland, "Teamcenter Developer", Sidney, OH, JR117566, 2026-10-05 — "We are not
# able to provide relocation assistance or visa sponsorship for this role at this time." Regex missed it:
# sponsorship sits in a coordinated "relocation assistance or visa sponsorship" clause after "not able to provide".
# Also caught manually: IDEX / Advanced Flow Solutions, "Software Engineer - Embedded Systems",
# Oklahoma City OK / Remote USA, R-10076, 2026-10-08 — "This role is not available for employment
# visa sponsorship." Regex missed it because the subject of "is not available" is the ROLE, not
# sponsorship; every prior pattern keyed on "sponsorship is not available". Two patterns now added
# to prescreen_jd.py (role-subject form and the bare "not available for ... visa sponsorship").
# Also caught manually: Bright Vision Technologies, "Embedded AI Engineer", Remote US, 2026-10-08 —
# "We are unable to sponsor new H-1B visa petitions for this position." (EAD holders welcome, but no new
# H-1B petitions = no path past OPT). Regex missed it: verb "sponsor" + H-1B object, not "sponsorship".
# Pattern now added to prescreen_jd.py.

[hard_blockers]
# These are ABSOLUTE DISQUALIFIERS for F-1 OPT holders.
# If ANY phrase below is detected in the JD, APPLY = No and tailoring MUST NOT proceed
# under any circumstances — even if the user explicitly asks to continue.

# Export control / federal contractor
itar_ear_phrases = must be a u.s. person, u.s. person, itar, ear compliance, export control, itar/ear, deemed
export, export administration regulations, controlled technology
# First caught (exact phrase not in prior list): ASML, "Embedded Software Engineer", Wilton, CT,
# J-00352651, 2026-09-14 — "Controlled Technology Statement" citing 15 C.F.R. § 730 (EAR), requiring
# candidates be "legally authorized to access such controlled technology" — deemed-export clause,
# caught only on the manual A5 second pass, not the A2.5 regex.

# Security clearance
clearance_phrases = security clearance, secret clearance, top secret, ts/sci, dod clearance, clearance
required, active clearance, obtain clearance, public trust clearance

# Citizenship / PR hard requirement
citizenship_phrases = must be a u.s. citizen, u.s. citizen only, citizens only, permanent resident only, us
citizen or green card, us citizen or pr, us citizen or permanent resident, us citizen/visa only, u.s.
citizen/visa only, visa: us citizen/visa only, us citizenship or green card, requires us citizenship,
position requires us citizenship, requires u.s. citizenship, us citizen.
# Also caught: The University of Texas at Austin (Applied Research Laboratories), "Robotics Engineering
# Scientist Associate", Pickle Research Campus, Austin TX, R_00048689, 2026-09-24 — standalone declarative
# sentence "US Citizen." (bare, period-terminated, no surrounding qualifier), immediately followed by
# "Applicant selected will be subject to a government security investigation and must meet eligibility
# requirements for access to classified information." Regex missed it (no prior pattern for the bare
# "US Citizen." form); added "us citizen." to the list. Also a defense-category role (Applied Research
# Laboratories = federal contractor, classified access) reinforcing the clearance blocker.
# First caught (structured field, not prose): Andson Biotech, "Embedded Systems Engineer", Atlanta GA,
# 2026-09-23 — YC job-board "Visa" metadata field reading "US citizen/visa only." Means only citizens or
# candidates who already hold independent work authorization may apply; sponsorship is not offered. F-1 OPT
# does not count as an independent visa here. Caught only on the manual A5 second pass, not A2.5 regex.
# Also caught (exact phrase not in prior list — "citizenship" not "citizen"): Analog Devices,
# "Embedded Systems Applications Engineer", Wilmington MA, R265602, 2026-09-24 — "US citizenship or
# Green Card" listed under Preferred Education and Experience, reinforced by an export-control
# paragraph excluding non-US-Citizens/PR/protected-individuals from the ITAR/EAR licensing exemption.
# Regex missed it (singular "citizen" forms only); added "us citizenship or green card" to the list.
# Also caught: Nautilus Defense LLC, "Embedded Software Engineer", Pawtucket RI, 2026-09-24 — standalone
# sentence "This position requires US Citizenship." (no "citizen"/"citizens", declarative "requires"
# phrasing). Regex missed it (no prior pattern for "requires ... citizenship"); added "requires us
# citizenship" and variants to the list.
# Also caught manually: Niyam IT, "AI/ML Engineer", Ashburn VA (Hybrid), careers/444, 2026-10-10 —
# qualifications bullet "US Citizenship with ability to successfully complete a federal background
# investigation." Regex missed it (no "requires"/"must be" verb — bare noun-phrase bullet pairing
# citizenship with a background-investigation clause). Also a federal-contractor/defense-category role
# (CMMC Level 2, federal client, "trusted partner to the U.S. Federal Government"). Pattern now added
# to prescreen_jd.py.

# Government / defense categories that almost always have one of the above
# (flag for review even if exact phrase not found)
defense_category_keywords = federal contractor, department of defense, dod, u.s. air force, u.s. army, u.s.
navy, u.s. government, nato, classified, aerospace defense, lockheed, raytheon, northrop, boeing defense,
l3harris, bae systems, saic, leidos, booz allen, general dynamics, mitre

# Foreign on-site work authorization — not caught by any regex above (those are US-specific).
# F-1 OPT only authorizes employment INSIDE the United States, so an on-site role outside the US
# is work Justin cannot legally start today. That fact is unchanged — but as of 2026-09-23 he is
# deliberately applying to EU/UK roles IN PARALLEL with the US search, expecting the employer to
# sponsor the permit. So this blocker is now SCOPED BY REGION:
#
#   EU / UK / EEA / Switzerland  -> NOT a hard blocker. Analyse and apply normally.
#     The whole point of applying is to obtain the permit; refusing to apply because he does not
#     already hold it is circular. Treat "no visa/relocation sponsorship mentioned" as UNKNOWN,
#     not as a refusal — most EU postings never mention it either way. Only an EXPLICIT refusal
#     blocks, and prescreen_jd.py still catches those in every region.
#
#   Anywhere else outside the US (India, Canada, LATAM, APAC, Middle East, etc.)
#     -> UNCHANGED. Still a hard blocker unless the posting explicitly offers sponsorship.
#
# Judge this manually in A5 (location field vs "current = Arlington, TX, USA") — it will not
# match a keyword list. Instead of blocking an EU/UK role, attach the soft flag described in
# [eu_uk_visa_bars] below when the stated salary is visibly under that country's permit floor.
#
# The "Also caught" entries below that sit in Europe (Austria, Sweden, Netherlands, Spain) are
# retained as AUDIT HISTORY ONLY. They are superseded by the rule above and must NOT be read as
# precedent for blocking a European role today.
# First caught: Delta Electronics / LOYTEC, "Software Developer for Embedded Systems", Vienna,
# Austria, on-site, 2026-09-14.
# Also caught: Dentsply Sirona / Wellspect Healthcare, "Embedded System Engineer", Mölndal,
# Sweden (HQ; no US location stated), on-site, 2026-09-14.
# Also caught: Hewlett Packard Enterprise, "Junior Embedded Software Engineer", Heredia,
# Costa Rica, hybrid on-site (2 days/week in-office), 2026-09-14.
# Also caught: Verisure, "Embedded Software Engineer" (Central Unit team), Pozuelo de
# Alarcon, Madrid, Spain (or Malmo, Sweden), on-site ("office in Madrid or Malmo",
# "Madrid and Malmo-based team"), 2026-09-23 — no visa/relocation sponsorship mentioned.
# Also caught: Husqvarna Group, "Embedded Software Verification Engineer", Huskvarna,
# Sweden, on-site (HIL lab + field validation work, R-18346), 2026-09-23 — no US location
# stated, no visa/relocation sponsorship mentioned.
# Also caught: Xsens, "Embedded Software Engineer", Enschede, Overijssel, Netherlands,
# on-site/hybrid, 2026-09-23 — no visa/relocation sponsorship mentioned anywhere in posting.
# Also caught: Bit Addict (via Oddwork/Oddworks staffing), "Embedded Software Engineer",
# Gothenburg, Sweden, on-site, 2026-09-23 — no US location, no visa/relocation sponsorship
# mentioned; also requires 8+ years experience and "very good" Swedish fluency, neither of
# which Justin has, compounding the hard blocker.
foreign_onsite_no_us_authorization = true   # scope: NON-EU/UK only — see rule above

[eu_uk_visa_bars]
# Soft flag only — NEVER a hard blocker, and never a reason to skip tailoring.
# If an EU/UK posting states a salary visibly below its country's floor, flag:
#   "SALARY UNDER PERMIT FLOOR — confirm exact figure before accepting"
# If no salary is stated (the norm in Europe), say nothing. Verify live before relying on these;
# every one of them is indexed annually.
# Figures current as of 2026-09-23.
ireland_critical_skills = 40904 EUR/yr (from Mar 2026; Dublin/Cork clear it, Limerick ~40000 is borderline)
netherlands_hsm_under_30 = 4357 EUR/month excl. holiday allowance (Justin is under 30 until 2032-05-01)
netherlands_hsm_30_plus = 5942 EUR/month
germany_blue_card_shortage = 45934 EUR/yr (IT/STEM shortage + recent-graduate rate; standard is 50700)
uk_skilled_worker_standard = 41700 GBP/yr general floor, BUT the binding number is the SOC going
  rate — SOC 2134 is ~54700
uk_new_entrant = 38290 GBP/yr — higher of 33400 or 70% of the going rate. Justin qualifies via the
  under-26 criterion until 2028-05-01 (DOB 2002-05-01). This is the number that matters for UK roles.
czechia_blue_card = ~35400 EUR/yr (CZK 73823/month, from May 2026)
poland_blue_card = ~37200 EUR/yr (PLN 13355/month, from Feb 2026)
sweden_work_permit = ~401000-413600 SEK/yr — junior embedded pay (~297000 SEK) typically FAILS this.
  Sweden is the one region where the floor is a real filter; flag hard, but still do not block.

[job_preferences]
# RECALIBRATED for the A4 scoring fix (classified-set denominator, adjacency at
# half credit, zero-HAVE floor). That change shifted scores down ~15 points, so
# the old 70/45 thresholds would have rejected almost everything.
# Measured on 87 target-track roles carrying have_skills:
#   apply @70(old) passed 67.8%  ->  @60(new) passes 50.6%   (deliberately tighter)
#   can-try @45(old) passed 95.4% ->  @40(new) passes 86.2%
# Tighter is the point: fewer, better-targeted applications per day.

# Minimum keyword match % to recommend APPLY (0-100)
min_match_for_apply = 60
# Match % where it becomes CAN TRY despite gaps
min_match_for_can_try = 40
# If required experience years exceeds this, flag as mismatch
experience_threshold_years = 3
