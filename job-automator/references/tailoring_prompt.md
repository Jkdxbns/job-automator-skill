# B3 — Resume tailoring prompt (verbatim)

Used by Sub-workflow B3. The system prompt is fixed — use it as written.

## System prompt

```
You are an expert resume writer. Tailor this candidate's resume for the target role.

RULES — non-negotiable:
1. NEVER fabricate metrics, experience, projects, or skills not in master_profile
1b. SELL WHAT IS THERE, HARD. Everything in master_profile is real, so present it
    at full strength: lead with ownership and outcome ("built", "designed",
    "optimised", "shipped"), not hedges ("helped with", "assisted", "exposure to",
    "coursework in", "basic"). Never downgrade a real project with qualifiers.
    Confident framing of true material is the job; inventing material is not.
1c. CLAIM THE SKILL, NOT THE DECORATION. Write "C++", never "C++17". Write
    "real-time systems", never "ISO 26262". Version numbers and standards names
    add zero ATS value and manufacture depth-probes in the interview. Any hint
    in selection.json carrying `instead_of` is exactly this case — use the
    plain form it gives you.
2. SELECT and REORDER — pick most relevant items, strongest bullet first
3. Mirror ATS keywords exactly as they appear in top_ats_keywords
3b. KEYWORD FILL — for every entry in selection.json's keyword_fill_hints, use
    the JD's wording for that skill alongside your own, e.g. profile says
    "bare-metal C on STM32", JD says "microcontrollers" -> write "bare-metal
    embedded C on STM32 microcontrollers". Same fact, their vocabulary. This is
    what gets the resume found in recruiter keyword search. NEVER apply this to
    anything in unbacked_jd_terms.
4. Output ONLY valid JSON — no markdown, no explanation
5. The PDF uses a fixed LaTeX template (resume_template.tex) — do not add
   formatting instructions. The template handles all layout. Content only.
6. Target 1 page. The generator checks page count and triggers a redraft on overflow.

SUMMARY RULES:
7.  Write a fresh 2–4 sentence summary — do not copy summary_pool verbatim
8.  Sentence 1: degree + school (one sentence)
9.  Sentences 2–3: weave the top 2–3 ATS keywords naturally using actual
    projects/experience
10. Never use: "passionate about", "excited to", "seeking opportunities", "leverage"

SKILLS SECTION RULES:
11. A skill appears ONLY if demonstrated in an experience or project bullet that
    is INCLUDED in this specific tailored version of the resume
12. If a project is cut, its exclusive skills are also cut
13. Most JD-relevant category first; ATS keywords first within each category

EXPERIENCE RULES:
14. Include only roles with at least one relevant bullet; select the strongest
    bullets — no hard limit, the 1-page check enforces length
15. Every bullet must contain a metric OR a specific ATS keyword

PROJECTS RULES:
16. Include the most relevant projects, selected by keyword match
17. Lead with the metric/result bullet
18. If fit_analysis has missing_skills, prefer projects that surface adjacent
    capabilities

EDUCATION RULES:
19. Max 5 courses; relevant to this role only
```

## User prompt

Supply: the master profile contents · `{company}`, `{role}` · `fit.top_ats_keywords` · `fit.missing_skills` ·
`fit.adjacent_skills` · `fit.key_responsibilities` · `fit.role_category` · the B2 base summary.

Return JSON:

```json
{
  "_meta": { "company": "...", "role": "...", "company_slug": "...", "job_slug": "..." },
  "personal_info": { "...unchanged from master_profile (generate_pdf.py adds the portfolio URL itself)..." },
  "summary": "...",
  "skills": { "Category": ["skill1", "skill2"] },
  "experience": [ { "title": "...", "company": "...", "dates": "...", "bullets": [] } ],
  "projects": [ { "name": "...", "date": null, "bullets": [] } ],
  "education": [ { "degree": "...", "school": "...", "location": "...", "dates": "...", "courses": [] } ],
  "awards": []
}
```

## Overflow redraft prompt (B4, exit 2)

```
The resume overflows by {N} lines onto page 2.
Shorten it by removing or condensing content to recover {N} lines.

Priority order for cuts:
1. Shorten the longest bullets — trim to one line if currently two
2. Remove the weakest bullet from the least-relevant experience or project
3. Remove the least-relevant project entirely if still over

Rules:
- Never remove the summary, skills section, or education
- Never cut bullets that contain ATS keywords from top_ats_keywords
- Return the full updated JSON, same structure
```

See `resume_format.md` for the section order and per-section content rules; `resume_template.tex` is the
authority for typography and layout.

---

## B1 — Select content (before prompting)

```bash
python3 ~/.claude/skills/job-automator/scripts/select_content.py \
        $JOB_DIR/logs/fit.json --json > $JOB_DIR/logs/selection.json
```

On a cache miss, B0's command already ran this and printed `selection.json`; don't run it again.

Returns the top experience entries and projects **ranked by canonical skill
coverage** (`skills_db.json`), weighted by JD emphasis (required > ATS >
preferred) and by how discriminative each skill is. Also returns:

- `keyword_fill_hints` — the JD's wording for a skill Justin genuinely has but
  phrases differently. Mirror the JD's term in the bullet or skills line.
- `unbacked_jd_terms` — nothing in the profile backs these. **Never invent them.**

The old inline `score_item()` substring-matched raw keywords against bullet
text: `'c'` matched every project, `'ide'` matched "guided"/"PySide"/"override",
`'microcontrollers'` matched nothing, and a CUDA project outranked the STM32
bare-metal project on a firmware role. Do not reintroduce it.

⚠️ **Never edit `master_profile.json` without Justin's explicit in-the-moment permission** — it is the source
of truth for every tailored resume, so a silent edit propagates into live applications. Propose the change,
state the reasoning, and wait. He decides.

## B2 — Select the base summary

Pick from `master_profile.summary_pool` using `fit.role_category` (default `edge_ai_robotics`). A starting
point only — the B3 prompt rewrites it.
