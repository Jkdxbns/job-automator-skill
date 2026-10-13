#!/usr/bin/env python3
"""
reflow.py — Re-wrap ONLY the prose in a markdown file to a wider column.

Leaves untouched, byte for byte:
  - fenced code blocks (``` ... ```) and their contents
  - tables (any line whose stripped form starts with '|')
  - headings (#...), horizontal rules (---), blank lines
  - YAML frontmatter

Reflows paragraph groups, preserving:
  - list markers ('- ', '* ', '1. ') and their hanging indent
  - blockquote prefixes ('> ', '> - ')
  - the original leading indentation of the block

Usage: reflow.py <file> <width> [--write]
"""
import re
import sys
import textwrap

LIST_RE = re.compile(r'^(\s*)([-*+]\s+|\d+\.\s+)(.*)$')
QUOTE_RE = re.compile(r'^(\s*>\s?)(.*)$')


def is_atomic(line):
    s = line.strip()
    if not s:
        return True
    if s.startswith('|'):
        return True
    if s.startswith('#'):
        return True
    if re.fullmatch(r'-{3,}|\*{3,}|_{3,}', s):
        return True
    return False


def flush(buf, width, out):
    """buf is a list of raw lines forming one logical prose block."""
    if not buf:
        return

    # Blockquote block: strip the '>' prefix, reflow the inside, re-add it.
    qm = QUOTE_RE.match(buf[0])
    if qm:
        prefix = qm.group(1)
        if not prefix.endswith(' '):
            prefix += ' '
        inner = []
        for l in buf:
            m = QUOTE_RE.match(l)
            inner.append(m.group(2) if m else l.strip())
        # Recurse through the full reflow so fenced blocks INSIDE a
        # blockquote are still passed through verbatim.
        inner_txt = reflow('\n'.join(inner), max(20, width - len(prefix)))
        for s in inner_txt.split('\n'):
            out.append((prefix + s).rstrip() if s.strip() else prefix.rstrip())
        return

    flush_indented(buf, width, out)


def flush_indented(buf, width, out):
    lm = LIST_RE.match(buf[0])
    if lm:
        indent, marker, first = lm.groups()
        hang = indent + ' ' * len(marker)
        text = ' '.join([first.strip()] + [l.strip() for l in buf[1:]])
        text = re.sub(r'\s+', ' ', text).strip()
        wrapped = textwrap.wrap(text, width=width,
                                initial_indent=indent + marker,
                                subsequent_indent=hang,
                                break_long_words=False,
                                break_on_hyphens=False)
        out.extend(wrapped or [indent + marker.rstrip()])
        return

    indent = re.match(r'^(\s*)', buf[0]).group(1)
    text = ' '.join(l.strip() for l in buf)
    text = re.sub(r'\s+', ' ', text).strip()
    wrapped = textwrap.wrap(text, width=width,
                            initial_indent=indent, subsequent_indent=indent,
                            break_long_words=False, break_on_hyphens=False)
    out.extend(wrapped or [''])


def flush_plain(buf, width, out):
    """Reflow a list of already-unprefixed lines, splitting on list items."""
    group = []
    for l in buf:
        if not l.strip():
            if group:
                flush_indented(group, width, out)
                group = []
            out.append('')
            continue
        if LIST_RE.match(l) and group:
            flush_indented(group, width, out)
            group = [l]
        else:
            group.append(l)
    if group:
        flush_indented(group, width, out)


def reflow(text, width):
    lines = text.split('\n')
    out = []
    i = 0

    # Pass frontmatter through verbatim.
    if lines and lines[0].strip() == '---':
        out.append(lines[0])
        i = 1
        while i < len(lines) and lines[i].strip() != '---':
            out.append(lines[i])
            i += 1
        if i < len(lines):
            out.append(lines[i])
            i += 1

    buf = []
    infence = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('```'):
            if buf:
                flush(buf, width, out)
                buf = []
            out.append(line)
            infence = not infence
            i += 1
            continue
        if infence:
            out.append(line)
            i += 1
            continue
        if is_atomic(line):
            if buf:
                flush(buf, width, out)
                buf = []
            out.append(line)
            i += 1
            continue

        # A new list item or a blockquote/non-blockquote switch starts a block.
        starts_new = bool(LIST_RE.match(line))
        qm_line = QUOTE_RE.match(line)
        if qm_line and qm_line.group(2).lstrip().startswith('```'):
            # keep the quoted fence with its block; recursion handles it
            pass
        switch = buf and (bool(QUOTE_RE.match(line)) != bool(QUOTE_RE.match(buf[0])))
        if buf and (starts_new or switch):
            flush(buf, width, out)
            buf = []
        buf.append(line)
        i += 1

    if buf:
        flush(buf, width, out)
    return '\n'.join(out)


def content_words(text):
    """Words excluding pure markdown line-structure syntax.

    A blockquote '>' prefix is syntax, not content: reflowing 16 quoted lines
    into 14 legitimately drops two '>' markers while changing no prose. Strip
    them (and list bullets, whose count also tracks line structure) before
    comparing, so the guard flags real content loss only.
    """
    out = []
    for line in text.split('\n'):
        s = line
        while s.lstrip().startswith('>'):
            s = s.lstrip()[1:]
        out.extend(w for w in s.split() if w not in ('-', '*', '+'))
    return out


def main():
    path, width = sys.argv[1], int(sys.argv[2])
    write = '--write' in sys.argv
    src = open(path).read()
    res = reflow(src, width)
    ca, cb = content_words(src), content_words(res)
    ok = ca == cb

    # A prose line that wraps so it BEGINS with '|' is parsed by markdown as a
    # table row, silently breaking the page. Same for a stray '```'. Detect any
    # such line that the reflow created but the source did not have.
    def bad_starts(text):
        out, inf = set(), False
        for i, l in enumerate(text.split('\n')):
            if l.strip().startswith('```'):
                inf = not inf
                continue
            if inf:
                continue
            s = l.strip()
            if s.startswith('|'):
                out.add(s)
        return out
    created = bad_starts(res) - bad_starts(src)
    if created:
        ok = False
        for c in sorted(created):
            print(f"    NEW pipe-leading prose line: {c[:90]}", file=sys.stderr)
    if ok and write:
        open(path, 'w').write(res)
    print(f"{src.count(chr(10))+1} -> {res.count(chr(10))+1} lines, "
          f"content words {len(ca)} -> {len(cb)}  "
          f"{'IDENTICAL ✅' if ok else 'CHANGED ❌'}")
    if not ok:
        import difflib
        for d in list(difflib.unified_diff(ca, cb, lineterm='', n=1))[:20]:
            print("   ", d, file=sys.stderr)
        print("  !! CONTENT ALTERED — not written", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
