# Sub-workflow G — Post-submission recruiter outreach (Hunter.io)

Finds hiring-side people at a company Justin has **already applied to**, verifies their emails, and drafts
one email each. **Never sends.** Engineers are not in scope — he asks them for referrals on LinkedIn himself.

## G0 — The gate (non-negotiable)

**The Hunter API is only touched after the job is marked submitted.** `hunt_contacts.py` enforces this
itself: it reads `~/job_search/submitted_log.csv` and exits 2 if the company+role has no row. Company is the
hard key; the role only needs ~50% token overlap, because log titles drift from `fit.json` titles
("Robotics Systems Engineer, Tech Deployment" vs "Robotics Systems Engineer II, RDPI Technology Deployment").
Do not pass `--force` to get around a missing row — run Sub-workflow D first.

## G1 — How many (n)

From `fit.json`'s `match_pct`, computed by the script:

| match_pct | n |
|---|---|
| ≥ 80 | 10 |
| 60–79 | 5 |
| < 60 | **0 — no API call at all** (script exits 3) |

## G2 — Ask first, hunt second

Right after D4 confirms the submission, ask **one** question and stop:

> Drafted outreach for {company}? Match is {match_pct}%, so that's **{n}** recruiter emails. Yes / No / a number.

- **No** → done, nothing runs, zero credits.
- **Yes** → `n` as computed.
- **"yes but 20"** / any number → that number wins, passed as `--n 20`.

Asking before hunting is deliberate: a declined offer costs nothing.

## G3 — Hunt

```bash
python3 ~/.claude/skills/job-automator/scripts/hunt_contacts.py --job-dir $JOB_DIR [--n N]
```

What it does: resolves the domain from the company name (trying progressively simpler variants — a 0-result
search is free, so `Amazon.com Services LLC` → `Amazon` costs nothing extra), pulls `department=hr`, drops
comp/benefits/payroll titles, ranks the rest (technical recruiter → sourcer → recruiter → talent acquisition
→ university/early-career → talent → people ops → hiring manager → HR), verifies each address, and drops
anything undeliverable. Writes `$JOB_DIR/logs/contacts.json`.

Pass `--domain company.com` when the company name is ambiguous or resolution failed.

**Verification status matters when drafting:** `valid` = confirmed. `accept_all` = the domain accepts
everything, so it could not be confirmed — fine to draft, but it is a guess. `invalid` never reaches you.

## G4 — Draft one email per contact

Use the C4 rules in [outreach_rules.md](outreach_rules.md) and the voice in
[outreach_examples.md](outreach_examples.md) — same length (120–170 words), same fixed closing line, same
banned phrases. Three differences, because this is a recruiter after an application, not a cold pitch:

1. **Never ask for a referral.** They own the process; a referral ask makes no sense to them. (Referrals come
   from engineers, on LinkedIn, and Justin does that himself.)
2. **Say the application is already in** — name the role, and the date from the submitted log.
3. **The ask is a conversation**, carrying up to three threads: why he fits (one concrete line from
   `fit.json`'s `have_skills`), what the team is actually looking for in this role, and **whether someone
   else on their team owns this req** — that last one recovers the case where Hunter returned a generic HR
   partner rather than the technical recruiter (common at very large employers).

Per the standing rule, never mention visa, OPT, EAD or sponsorship.

## G5 — Draft directly to Gmail, never send

**Standing rule: "draft emails" means create the Gmail drafts directly — do not ask permission first.**
Creating a draft is not sending; the ask-before-Gmail step from earlier in this skill's history is gone.

For each contact, follow **C5-Email** exactly (`outreach_delivery.md`): `draft_gmail_message` with
`user_google_email: jmascarenhas1998@gmail.com`, `to: contact.email`, `subject`, `body` (greeting + body
paragraphs + sign_off as one plain-text string), `body_format: "plain"`, `include_signature: false`. On an
error (auth, quota), fall back to printing that one draft inline and say the Gmail save failed for it — don't
let one failure block the rest of the batch.

Also write every draft to `$JOB_DIR/logs/recruiter_drafts.md` (the tracking copy) and run C5b
(`save_and_print_draft.py`) per contact, disambiguating filenames by target name. Then print one short
confirmation block per contact (subject, to, hook, follow-up date) — never the full body, it is already in
Gmail. **Never send** — that is still a separate, explicit, per-message approval.

## Quota reality (free plan, resets monthly)

50 searches and 100 verifications a month. One role costs **1 search + n verifications**, so at n=10 that is
~10 roles a month; at n=5, ~20. `hunt_contacts.py --quota` prints the balance and costs nothing; the script
refuses to start a run it cannot finish (exit 4).

## Known limitation — big companies give generic contacts

The free plan returns only 10 people per search and cannot paginate. At a mid-size company that is the right
10 (Zoox → three Technical Recruiters and a Technical Recruiting Lead; Rivian → Directors of Talent
Acquisition and Recruiting). At a mega-employer with thousands of HR staff it is an arbitrary 10 (Amazon →
five generic "Human Resources Partner"). For those, expect lower yield, lean on the "is someone else on your
team closer to this req?" ask, and consider answering **No** at G2 rather than spending ten verifications.
