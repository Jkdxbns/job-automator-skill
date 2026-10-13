# C4 — Outreach drafting rules

Loaded by Sub-workflow C4. `outreach_examples.md` (first 80 lines) carries the worked examples; this file
carries the hard rules. Evidence behind the numbers: `scoring_rationale.md` §7.

## Output shape

```
{ type, subject (null for dm), greeting, body, sign_off,
  word_count, hook_used, followup_days }
```

## Length

- **Email**: 120–170 words. Recruiter response data shows 50–125 word emails perform best and reply rates drop
  sharply past ~150 words. The old 200–280 target was too long.
- **DM**: 120–180 words, opening line ≤ 280 chars.

## Substance

- **Fit must be explicit** against the JD's stated minimum qualifications, not just adjacent. Say plainly why
  the background matches rather than trusting the reader to infer it.

- **CLOSING LINE (email only — fixed template, do not vary).** Every email's final paragraph is exactly this
  sentence pair, verbatim, standing as its own paragraph right before the sign_off:

  > I would appreciate the opportunity to discuss the role further, if your time allows. I can share my resume
  > if that would be helpful.

  Do not rephrase, shorten, or merge it into the prior paragraph. Applies only to `type: "email"`.

- **SIGN-OFF (both channels) — fixed, carries the site.** Every email and DM closes with exactly:

  ```
  Best,
  Justin Mascarenhas
  justinmascarenhas.com
  ```

  The portfolio site **replaces** the LinkedIn URL that older drafts carried: the site links LinkedIn itself,
  and a LinkedIn URL inside a LinkedIn DM is noise (Justin's call, 2026-10-13). Use the **root domain only**.
  Never the `/embedded` or `/edge-ai` track pages here — those carry a hyphen, which the no-dash rule below
  forbids outright, and they are the resume's job, not outreach's. The root is stored as
  `personal_info.website_root` in `master_profile.json`.

- **DM ASK (dm only) — ONE ASK ONLY.** Every DM ends with exactly one clear, low-pressure call to action (e.g.
  "let me know if you're the right contact" OR "happy to send my resume" — not both, and not stacked with a
  third ask for a referral). Stacked asks measurably hurt reply rates on LinkedIn. Pick the single most
  relevant ask for this contact and drop the rest.

## Body formatting — non-negotiable, copy-paste safety

- Each paragraph is a single unbroken string. **NO mid-sentence line breaks.** Paragraphs are separated by
  `\n\n` only; never insert `\n` within a paragraph.
- **Never use any hyphen or dash character** — no `-`, no `--`, no en dash, no em dash — anywhere in the body,
  subject, greeting, or sign_off. Rewrite around it (split the sentence, use "and"/"which", use a comma)
  instead of substituting a different dash. Compound adjectives that would normally take a hyphen get
  rephrased as plain phrases: "real-time" → "in real time", "bare-metal" → "at the bare metal level".
- **No numbers in the body** — no exact metrics, percentages, sizes, or counts. Describe achievements
  qualitatively. Numbers stay in the resume; they don't belong in outreach mail.
- **No permission-granting or forgiving language**, especially in follow-ups. Never write "no worries if it
  got buried", "no rush on your end", or "totally understand if you're busy". These sound like Justin is
  excusing the recipient's delay from a position of authority he doesn't have — he is the one asking for a
  favor, not the one who gets to grant absolution. State the follow-up directly and drop the reassurance
  clause entirely.
- **Keep language plain and a little uneven in rhythm** — vary sentence length, use everyday words over formal
  synonyms, avoid stacked adjectives and tidy "Furthermore/Moreover" transitions. This is what keeps it from
  reading as AI-generated.
- **Always open with a one-line self-identification**: Justin's name and that he has (or is completing) an
  M.S. in Computer Engineering. Attach a specific graduation date only if the role is explicitly grad-date
  bound (e.g. a "New College Grad" posting) — and check the current date against May 2026 before choosing
  "graduating" vs "graduated".
- **Never mention visa, OPT, EAD, or sponsorship status** unless Justin explicitly asks (global CLAUDE.md →
  Outreach Message Rules).
- No markdown blockquotes when printing a draft in chat — the left bar breaks copy-paste.

These rules apply to the `greeting`, `body`, and `sign_off` fields alike.

## Hook quality (C2)

A generic line like "your recruiting background made you a good person to reach out to" is **not** a real hook
— it reads as filler because it could apply to any recruiter. Only use a hook that references something
specific to that person: their actual profile, a specific past employer, a specific post, a specific shared
detail. **If no specific hook exists, drop the hook line entirely** — a message with no hook line beats a
message with a fake one.
