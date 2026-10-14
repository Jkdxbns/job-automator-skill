#!/usr/bin/env python3
"""
validate_skill.py — Lint a Claude Agent Skill against Anthropic's limits and
its own internal reference integrity.

Two jobs:
  1. LIMITS   — frontmatter `name`/`description` against the hard caps, and
                SKILL.md body size against the progressive-disclosure guidance.
  2. WIRING   — every scripts/*.py and references/* path the SKILL.md mentions
                actually exists on disk. A dangling reference is a pipeline
                break waiting to happen (the model runs a script that isn't there).

Usage:
  python3 validate_skill.py [<skill_dir>]   # defaults to the job-automator dir

Exit codes:
  0 — no errors (warnings allowed)
  1 — one or more ERRORS (a hard-limit breach or a dangling reference)
  2 — bad invocation / SKILL.md not found

Run it after editing SKILL.md or adding/removing a script.
"""

import os
import re
import sys

# Anthropic hard caps for skill frontmatter.
NAME_MAX = 64
DESC_MAX = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Progressive-disclosure guidance (soft — warn, don't fail).
BODY_WORDS_WARN = 5000
BODY_LINES_WARN = 500


def parse_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


def get_name(fm):
    m = re.search(r"^name:\s*(.+)$", fm, re.M)
    return m.group(1).strip() if m else ""


def get_description(fm):
    # Handles both inline and block-scalar (>, |) descriptions.
    m = re.search(r"description:\s*[>|]?\s*\n?(.*?)(?=\n[a-z_]+:\s|\Z)", fm, re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()


def find_referenced_paths(body, skill_dir):
    """Every scripts/... or references/... path token mentioned in the body."""
    # Matches things like scripts/render_report.py, references/master_profile.json,
    # optionally prefixed by the skill dir or ~/.claude/skills/<skill>/.
    pat = re.compile(r"(?:scripts|references)/[A-Za-z0-9_./-]+")
    found = set()
    for tok in pat.findall(body):
        tok = tok.rstrip(".,);:`'\"")
        # normalize away any leading path noise
        idx = tok.find("scripts/")
        idx2 = tok.find("references/")
        cut = min(x for x in (idx, idx2) if x >= 0)
        found.add(tok[cut:])
    return sorted(found)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    # Default to the skill this script actually lives in, resolved from
    # __file__, so it lints the right skill no matter where it is run from
    # and keeps working after a rename.
    own_skill = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_dir = os.path.expanduser(args[0]) if args else own_skill
    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        print(f"ERROR: no SKILL.md at {skill_md}", file=sys.stderr)
        return 2

    text = open(skill_md).read()
    fm = parse_frontmatter(text)
    body = text[len(fm) + 8:] if fm else text

    errors, warnings, oks = [], [], []

    # ── frontmatter limits ──
    name = get_name(fm)
    if not name:
        errors.append("frontmatter has no `name`")
    else:
        if len(name) > NAME_MAX:
            errors.append(f"name is {len(name)} chars (max {NAME_MAX})")
        if not NAME_RE.match(name):
            errors.append(f"name '{name}' must be lowercase letters/digits/hyphens only")
        # Spec: the name MUST match the parent directory name.
        dirname = os.path.basename(os.path.normpath(skill_dir))
        if name != dirname:
            errors.append(
                f"name '{name}' does not match its directory '{dirname}' — the "
                f"spec requires them to be identical (and a directory name with "
                f"'_' can never match, since names allow only a-z 0-9 and '-')")
        if not (errors and errors[-1].startswith("name")):
            oks.append(f"name '{name}' — {len(name)}/{NAME_MAX} chars, matches dir, format ok")

    desc = get_description(fm)
    if not desc:
        errors.append("frontmatter has no `description`")
    elif len(desc) > DESC_MAX:
        errors.append(f"description is {len(desc)} chars (max {DESC_MAX}) — MUST trim")
    else:
        headroom = DESC_MAX - len(desc)
        msg = f"description {len(desc)}/{DESC_MAX} chars"
        if headroom < 80:
            warnings.append(f"{msg} — only {headroom} chars of headroom, near the cap")
        else:
            oks.append(msg)

    # ── body size (soft) ──
    words = len(body.split())
    lines = body.count("\n") + 1
    if words > BODY_WORDS_WARN or lines > BODY_LINES_WARN:
        warnings.append(
            f"SKILL.md body is {lines} lines / {words} words — over the "
            f"~{BODY_LINES_WARN}-line / ~{BODY_WORDS_WARN}-word progressive-disclosure "
            f"guidance. Consider moving deep rationale into references/.")
    else:
        oks.append(f"body size {lines} lines / {words} words — within guidance")

    # ── reference integrity ──
    # A skill is "self-contained" if it has its own scripts/ or references/ dir.
    # Skills that run out of an external project root (e.g. meeting) reference
    # paths relative to that root, so we don't hard-fail those.
    has_scripts = os.path.isdir(os.path.join(skill_dir, "scripts"))
    has_refs = os.path.isdir(os.path.join(skill_dir, "references"))
    # User-supplied input files (copy-your-own): missing = warning, not error.
    USER_DATA_EXT = (".docx", ".pdf", ".doc", ".png", ".jpg")

    refs = find_referenced_paths(body, skill_dir)
    checked = 0
    for r in refs:
        exists = os.path.exists(os.path.join(skill_dir, r))
        if exists:
            checked += 1
            continue
        is_script = r.startswith("scripts/")
        is_ref = r.startswith("references/")
        # external-runtime skill: its scripts/ live elsewhere — skip quietly
        if is_script and not has_scripts:
            continue
        if is_ref and not has_refs:
            continue
        if r.lower().endswith(USER_DATA_EXT):
            warnings.append(f"user-supplied input '{r}' is not present "
                            f"(copy it in, or the doc default is stale)")
        else:
            errors.append(f"SKILL.md references '{r}' which does not exist on disk")
    if checked and not any("references '" in e for e in errors):
        oks.append(f"{checked} internal script/reference paths resolve")

    # ── report ──
    print(f"── validate_skill: {skill_dir} ──")
    for o in oks:
        print(f"  ✅ {o}")
    for w in warnings:
        print(f"  ⚠️  {w}")
    for e in errors:
        print(f"  ❌ {e}")
    print()
    if errors:
        print(f"FAIL — {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS — 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    if sys.argv[1:2] in (['-h'], ['--help']):   # usage, no side effects
        print(__doc__)
        sys.exit(0)
    sys.exit(main())
