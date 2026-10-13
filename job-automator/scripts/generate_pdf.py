#!/usr/bin/env python3
"""
generate_pdf.py — Builds resume PDF from tailored JSON using LaTeX.
Reads resume_template.tex for preamble/formatters, generates body from JSON,
compiles with pdflatex, outputs <company>_<role>.pdf to output_dir.

Usage: python generate_pdf.py <tailored_resume.json> <output_dir>
"""

import json, sys, os, re, subprocess, shutil, tempfile


# ── LaTeX escaping ────────────────────────────────────────────────────────────

def escape(text: str) -> str:
    """Escape special LaTeX characters in plain text."""
    if not isinstance(text, str):
        return str(text)

    # Order matters — backslash must go first
    replacements = [
        ('\\',  r'\textbackslash{}'),
        ('&',   r'\&'),
        ('%',   r'\%'),
        ('#',   r'\#'),
        ('_',   r'\_'),
        ('{',   r'\{'),
        ('}',   r'\}'),
        ('^',   r'\^{}'),
        ('~',   r'\textasciitilde{}'),
        ('<',   r'\textless{}'),
        ('>',   r'\textgreater{}'),
        # Common unicode in resume text
        ('±',   r'$\pm$'),
        ('×',   r'$\times$'),
        ('→',   r'$\rightarrow$'),
        ('≈',   r'$\approx$'),
        ('–',   '--'),     # en dash → LaTeX en dash
        ('—',   '---'),    # em dash → LaTeX em dash
        (''',   "'"),
        (''',   "'"),
        ('"',   "``"),
        ('"',   "''"),
        ('…',   r'\ldots{}'),
    ]

    for char, repl in replacements:
        text = text.replace(char, repl)
    return text


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


# ── Portfolio link ───────────────────────────────────────────────────────────
# Every resume links the portfolio site, on the focus page that matches the role:
# embedded/firmware/hardware roles -> /embedded, everything else -> /edge-ai.
# Chosen here from fit.json's role_category so the tailoring step cannot drift;
# _meta.portfolio_track ("embedded" | "edge-ai") in tailored.json overrides it.
# The root domain lives in master_profile.json personal_info.website_root (the single source of truth
# shared with outreach sign-offs); this constant is only the fallback if that key is missing.
PORTFOLIO = 'justinmascarenhas.com'
PORTFOLIO_TRACKS = ('embedded', 'edge-ai')


def portfolio_track(role_category: str) -> str:
    rc = (role_category or '').lower()
    return 'embedded' if any(k in rc for k in ('embedded', 'firmware', 'hardware', 'asic')) else 'edge-ai'


def resolve_portfolio(data: dict, job_dir: str) -> str:
    track = (data.get('_meta') or {}).get('portfolio_track')
    if track not in PORTFOLIO_TRACKS:
        role_category = ''
        try:
            with open(os.path.join(job_dir, 'logs', 'fit.json')) as f:
                role_category = json.load(f).get('role_category') or ''
        except (OSError, ValueError):
            pass
        track = portfolio_track(role_category)
    root = (data.get('personal_info') or {}).get('website_root') or PORTFOLIO
    return f'{root}/{track}'


# ── Section builders ─────────────────────────────────────────────────────────

def build_header(info: dict) -> str:
    # Contact line: phone | email | portfolio | location. LinkedIn is left off on purpose: with the portfolio
    # URL the line no longer fits on one line, and the site itself links LinkedIn (Justin's call, 2026-10-12).
    name    = escape(info.get('name', ''))
    phone   = escape(info.get('phone', ''))
    email   = info.get('email', '')
    website  = info.get('website', '')
    location = escape(info.get('location', ''))

    lines = [r'\begin{center}']
    lines.append(f'    \\textbf{{\\Huge \\scshape {name}}} \\\\ \\vspace{{2pt}}')

    contact = []
    if phone:    contact.append(f'    \\small {phone}')
    if email:    contact.append(f'    \\href{{mailto:{email}}}{{\\underline{{{escape(email)}}}}}')
    if website:  contact.append(f'    \\href{{https://{website}}}{{\\underline{{{escape(website)}}}}}')
    if location: contact.append(f'    \\small {location}')

    lines.append(' $|$\n'.join(contact))
    lines.append(r'\end{center}')
    return '\n'.join(lines)


def build_summary(summary: str) -> str:
    return f"""%-----------SUMMARY-----------
\\section{{Summary}}
\\resumeSummary{{
{escape(summary)}
}}"""


def build_skills(skills: dict) -> str:
    lines = ['%-----------SKILLS-----------',
             r'\section{Skills}',
             r'\begin{itemize}[leftmargin=0in, label={}]',
             r'    \item{']
    for category, items in skills.items():
        items_str = escape(', '.join(items))
        lines.append(f'        \\resumeSkills{{{escape(category)}}}{{{items_str}}}')
    lines.append(r'    }')
    lines.append(r'\end{itemize}')
    lines.append(r'\vspace{-16pt}')
    return '\n'.join(lines)


def build_experience(experience: list) -> str:
    lines = ['%-----------EXPERIENCE-----------', r'\section{Experience}']
    for job in experience:
        title   = escape(job.get('title', ''))
        company = escape(job.get('company', ''))
        dates   = escape(job.get('dates', ''))
        bullets = '\n'.join(
            f'    \\resumeItem{{{escape(b)}}}'
            for b in job.get('bullets', [])
        )
        lines.append(f"""\\resumeExperience
  {{{title}}}{{{company}}}{{{dates}}}
  {{
{bullets}
  }}""")
    return '\n'.join(lines)


def build_projects(projects: list) -> str:
    lines = ['%-----------PROJECTS-----------', r'\section{Projects}']
    for proj in projects:
        name  = escape(proj.get('name', ''))
        date  = escape(proj.get('date', '') or '')
        bullets = '\n'.join(
            f'    \\resumeItem{{{escape(b)}}}'
            for b in proj.get('bullets', [])
        )
        lines.append(f"""\\resumeProject
  {{{name}}}{{{date}}}
  {{
{bullets}
  }}""")
    return '\n'.join(lines)


def build_education(education: list) -> str:
    lines = ['%-----------EDUCATION-----------', r'\section{Education}']
    for edu in education:
        degree  = escape(edu.get('degree', ''))
        school  = escape(edu.get('school', ''))
        dates   = escape(edu.get('dates', ''))
        courses = edu.get('courses', [])
        if courses:
            course_line = f'    \\resumeItem{{\\textbf{{Courses:}} {escape(", ".join(courses))}}}'
            lines.append(f"""\\resumeEducation
  {{{degree}}}{{{school}}}{{{dates}}}
  {{
{course_line}
  }}""")
        else:
            lines.append(f'\\resumeEducationHeader{{{degree}}}{{{school}}}{{{dates}}}')
    return '\n'.join(lines)


def build_awards(awards: list) -> str:
    lines = ['%-----------AWARDS-----------',
             r'\section{Awards \& Achievements}',
             r'\vspace{2pt}']
    for award in awards:
        text = escape(award)
        # Try to split into title | detail | year
        # Expects format: "Title — detail (year)" or just plain text
        year_match = re.search(r'\((\d{4})\)\s*$', text)
        year = year_match.group(1) if year_match else ''
        rest = text[:year_match.start()].strip().rstrip(',').rstrip(')') if year_match else text

        # Split on first em-dash or comma for title/detail
        if '---' in rest:
            title, detail = rest.split('---', 1)
        elif '--' in rest:
            title, detail = rest.split('--', 1)
        else:
            title, detail = rest, ''

        lines.append(f'\\resumeAward{{{title.strip()}}}{{{detail.strip()}}}{{{year}}}')
    return '\n'.join(lines)


# ── Full document builder ────────────────────────────────────────────────────

def build_tex(data: dict, template_path: str) -> str:
    with open(template_path) as f:
        preamble = f.read()

    sections = [preamble, r'', r'\begin{document}', r'']

    sections.append('%----------HEADING----------')
    sections.append(build_header(data.get('personal_info', {})))
    sections.append('')

    if data.get('summary'):
        sections.append(build_summary(data['summary']))
        sections.append('')

    if data.get('skills'):
        sections.append(build_skills(data['skills']))
        sections.append('')

    if data.get('experience'):
        sections.append(build_experience(data['experience']))
        sections.append('')

    if data.get('projects'):
        sections.append(build_projects(data['projects']))
        sections.append('')

    if data.get('education'):
        sections.append(build_education(data['education']))
        sections.append('')

    if data.get('awards'):
        sections.append(build_awards(data['awards']))
        sections.append('')

    sections.append(r'\end{document}')
    return '\n'.join(sections)


# ── Compile ───────────────────────────────────────────────────────────────────

def compile_latex(tex_source: str, basename: str, output_dir: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, f'{basename}.tex')
        with open(tex_path, 'w') as f:
            f.write(tex_source)

        # Run twice for stable output
        for run in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', f'{basename}.tex'],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=60
            )
            pdf_produced = os.path.exists(os.path.join(tmpdir, f'{basename}.pdf'))
            if result.returncode != 0 and not pdf_produced:
                log_path = os.path.join(tmpdir, f'{basename}.log')
                if os.path.exists(log_path):
                    with open(log_path) as log:
                        lines = log.readlines()
                        print('pdflatex error — last 30 lines of log:', file=sys.stderr)
                        print(''.join(lines[-30:]), file=sys.stderr)
                sys.exit(1)

        os.makedirs(output_dir, exist_ok=True)

        # Copy PDF
        pdf_src = os.path.join(tmpdir, f'{basename}.pdf')
        pdf_dst = os.path.join(output_dir, f'{basename}.pdf')
        shutil.copy(pdf_src, pdf_dst)

        # Save .tex alongside PDF (same basename)
        tex_dst = os.path.join(output_dir, f'{basename}.tex')
        with open(tex_dst, 'w') as f:
            f.write(tex_source)

        return pdf_dst


def check_page_overflow(pdf_path: str) -> tuple[int, int]:
    """
    Returns (page_count, overflow_lines).
    overflow_lines = estimated lines on page 2+ (0 if single page).
    """
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            if page_count == 1:
                return 1, 0
            # Count non-empty lines on all pages beyond page 1
            overflow_lines = 0
            for page in pdf.pages[1:]:
                text = page.extract_text() or ''
                lines = [l for l in text.split('\n') if l.strip()]
                overflow_lines += len(lines)
            return page_count, overflow_lines
    except ImportError:
        # Fallback: use pypdf for page count only
        try:
            from pypdf import PdfReader
            count = len(PdfReader(pdf_path).pages)
            return count, 5 if count > 1 else 0  # rough estimate
        except ImportError:
            return 1, 0  # can't check, assume ok


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print('Usage: python generate_pdf.py <tailored_resume.json> <job_dir>')
        print('  job_dir: ~/job-automator/<company>_<role>_<timestamp>')
        sys.exit(1)

    json_path = sys.argv[1]
    job_dir   = os.path.expanduser(sys.argv[2])

    with open(json_path) as f:
        data = json.load(f)
    data.setdefault('personal_info', {})['website'] = resolve_portfolio(data, job_dir)
    print(f'PORTFOLIO={data["personal_info"]["website"]}')

    company  = data.get('_meta', {}).get('company_slug') or \
               slugify(data.get('_meta', {}).get('company', 'company'))
    role     = data.get('_meta', {}).get('job_slug') or \
               slugify(data.get('_meta', {}).get('role', 'role'))

    # Basename includes the folder timestamp suffix if present
    folder_name = os.path.basename(job_dir)
    if folder_name.startswith(f'{company}_{role}'):
        basename = folder_name  # use full timestamped name
    else:
        basename = f'{company}_{role}'

    script_dir    = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, '..', 'references', 'resume_template.tex')

    if not os.path.exists(template_path):
        print(f'ERROR: Template not found at {template_path}', file=sys.stderr)
        sys.exit(1)

    os.makedirs(job_dir, exist_ok=True)

    from datetime import datetime
    ts = datetime.now().strftime('%Y%m%d_%H%M')

    tex_source = build_tex(data, template_path)
    pdf_path   = compile_latex(tex_source, f'resume_{ts}', job_dir)
    tex_path   = os.path.join(job_dir, f'main_{ts}.tex')
    with open(tex_path, 'w') as f:
        f.write(tex_source)

    print(f'✅  PDF : {pdf_path}')
    print(f'✅  TEX : {tex_path}')

    page_count, overflow_lines = check_page_overflow(pdf_path)
    if page_count > 1:
        print(f'OVERFLOW: {page_count} pages — ~{overflow_lines} lines on page 2')
        print(f'OVERFLOW_LINES={overflow_lines}')
        sys.exit(2)  # Signal to skill: redraft needed
    else:
        print(f'✅  1 page — fits cleanly')


if __name__ == '__main__':
    main()
