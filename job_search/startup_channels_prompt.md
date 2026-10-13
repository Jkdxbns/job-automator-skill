# Research brief: low-competition job discovery channels for embedded / ML engineering roles at startups (US)

## Objective
Produce a ranked, cited inventory of job boards, alert services, talent networks, and other discovery channels that surface **early-stage and startup engineering roles in the US** BEFORE or INSTEAD OF the mainstream aggregators (LinkedIn, Indeed, Google Jobs, ZipRecruiter). The goal is to find postings where an applicant realistically competes against tens of candidates, not the 500-2000 that pile onto a LinkedIn post within hours.

## Who this is for (use as the relevance filter)
- Master's in Computer Engineering, US university, graduated May 2026. Entry level / new grad, roughly 0-2 years professional experience.
- Target roles: embedded software, firmware, RTOS, C/C++, robotics, edge AI / on-device inference, CUDA and GPU acceleration, computer vision, ML infrastructure. Hardware-adjacent software, not general web/full-stack.
- US-based, open to relocation, remote or onsite. Primary hubs of interest: Bay Area, Boston, Seattle, Austin, NYC, plus robotics clusters (Pittsburgh, Boulder, San Diego).
- International candidate on F-1 OPT: needs employers that hire OPT/CPT and are not blanket "US citizens only" or ITAR/export-control restricted. Treat "does this channel let me filter or identify visa-friendly / non-ITAR employers" as a scoring dimension, not a disqualifier.
- Constraint that matters most: **applicant volume per posting and time-to-post freshness.** A board with 200 relevant jobs that each get 40 applicants beats a board with 20,000 jobs that each get 900.

## Sub-questions to answer

1. **Startup-native boards.** Catalogue the boards where startups post first, before syndicating to aggregators. Cover at minimum: Y Combinator Work at a Startup, Wellfound (formerly AngelList Talent), Handshake, and then go well beyond those. Include VC-portfolio job boards (a16z, Sequoia, Greylock, Accel, Founders Fund, Lux Capital, Eclipse Ventures, Root Ventures, Khosla, First Round, General Catalyst, 8VC, and any hardware/deep-tech-heavy funds), accelerator boards (Techstars, AlchemistX, HAX, Y Combinator, Neo, Pear VC), and startup-community boards. For each, state whether it carries meaningful **embedded/hardware/robotics** volume or is dominated by software/GTM roles.

2. **Job alert and monitoring tools.** Evaluate the paid and free services that watch boards and push new matches within minutes. Cover at minimum: Notify.careers, RefereeAI, First2Apply, Emploive. Then find and evaluate competitors and alternatives in the same category (e.g. JobRight, Simplify, Careerflow, Huntr, Teal, Jobscan alerts, Hiring Cafe, Otta/Welcome to the Jungle, Talentprise, Sonara, LazyApply, AIApply, Jobsolv, or anything else current). For each report: pricing, what sources it actually monitors, alert latency, whether it does ATS-direct discovery (Greenhouse / Lever / Ashby / Workable / Rippling / SmartRecruiters boards) versus re-scraping LinkedIn, and whether it supports embedded/hardware keyword filtering.

3. **ATS-direct and "post-source" discovery.** Explain and evaluate the tactic of searching ATS platforms directly rather than aggregators: Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Rippling ATS, Gem, Dover. Identify the search interfaces, meta-search engines, public APIs, RSS feeds, sitemap patterns, or Google search operators that make this practical, and which tools already do it well. Name specific working search endpoints or URL patterns where they exist.

4. **Niche and vertical channels for hardware / embedded / robotics / edge AI.** Find the discipline-specific boards, newsletters, Slack and Discord communities, subreddits, Hacker News "Who is Hiring" workflows and its scrapers, conference and IEEE job boards, robotics-specific boards, defense-tech and space-tech boards (flagging ITAR/citizenship exposure), semiconductor and chip-startup channels, and any hardware-focused talent collectives or matching networks. These are the highest-value finds if they have real posting volume.

5. **Curated / reverse-marketplace / invite-only channels.** Cover talent marketplaces where companies apply to the candidate or a curator gatekeeps the pool: Otta, Triplebyte's successors, Hired, Rora, A.Team, Pallet, Lunar/Paraform-style recruiter marketplaces, university-affiliated and alumni-only boards, and new-grad-specific pipelines. Assess whether an entry-level embedded candidate is actually admitted and matched, or whether these skew senior / full-stack.

6. **Evidence on competition levels.** Wherever data exists, cite it: published applicants-per-posting figures, LinkedIn's own "over 100 applicants" thresholds, Greenhouse/Ashby benchmark reports, Wellfound or YC stated response rates, and any 2025-2026 reporting on AI-driven application flooding. Also report which of these channels have themselves been flooded and are no longer low-competition — a board that was good in 2023 and is saturated now is a finding, not an omission.

7. **Operating playbook.** Given all of the above, describe the concrete weekly workflow that maximizes early-applicant advantage: which 5-8 channels to monitor, what to automate versus check manually, realistic alert latency to expect, whether paid tiers are worth it at this profile, and what the actual apply-within window is (minutes? hours? days?) for startup postings.

## Output format
1. **Executive summary** — 8-12 bullets, the actionable conclusions only.
2. **Master table** of every channel found, with columns: Name | URL | Type (board / alert tool / ATS-direct / community / marketplace) | Cost | Embedded-and-robotics volume (high/med/low/none) | Estimated competition level with the basis for that estimate | Startup-stage skew (pre-seed / seed / Series A-B / growth) | New-grad friendly? | Notes.
3. **Tier 1 deep dives** — the top 10 channels for this exact profile, ~150 words each on why it ranks, how to set it up, and its failure mode.
4. **Search operators and URL patterns** — a copy-pasteable appendix of Google dorks, ATS search URLs, RSS feeds and saved-search recipes.
5. **The weekly playbook** from sub-question 7, as a numbered routine.
6. **Saturated / avoid list** — channels that look attractive but are not worth the time, with the reason.

## Rules
- Cite a live URL for every factual claim, especially pricing, feature claims, and competition statistics. Uncited claims are worthless here.
- Prioritise information current as of 2025-2026. Explicitly flag anything whose currency you could not verify, and note where a service has shut down, been acquired, or changed its pricing model.
- Aim for breadth: 40+ distinct channels in the master table. Obscure-but-real beats famous-but-flooded — do not pad the list with LinkedIn, Indeed, Glassdoor, Monster, Dice, or ZipRecruiter except in the "avoid" section.
- Verify each site still exists and is operating before listing it. Do not invent tool names, URLs, or pricing.
- No preamble, no restating this brief, no generic career advice ("tailor your resume", "network more"). Findings and evidence only.
