#!/usr/bin/env python3
"""
print_refs.py — print the reference files a step needs, byte for byte, in ONE Bash call.

WHY
---
The Read tool prefixes every line with a line-number gutter ("    12\t"), about 2.5 tokens a
line that carry no information: ~1.5k tokens for the A pack below and ~1.1k for the A6.5
pack. Reading the files one by one also costs round trips. This prints exactly the same
file contents, with nothing added or removed inside a file.

PACKS
-----
  fit       references/fit_payload.md · references/keywords_only.json ·
            references/candidate_context.md                     (A1, A3, A5, A6)
  semantic  references/semantic_read.md · references/master_profile.json   (A6.5)

Each file is framed as
  ===== references/<file> — verbatim, <N> chars (Read the file before any Edit) =====
  <exactly the N characters of the file>
  ===== end references/<file> =====
(a newline is added before the end line only if the file does not end with one).

Claude Code truncates Bash output past 30,000 characters (BASH_MAX_OUTPUT_LENGTH). A file
that would push the output past that limit is NOT printed and is named on a final
"NOT PRINTED" line; Read those files with the Read tool instead. A file is never cut off
partway, so nothing the model sees is ever a silent fragment.

Read-only: never writes anything (master_profile.json included).

USAGE
  python3 print_refs.py fit|semantic

EXIT CODES
  0 — printed (possibly with a NOT PRINTED line)
  2 — unknown pack / missing file
"""

import os
import sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PACKS = {
    "fit": ["references/fit_payload.md", "references/keywords_only.json",
            "references/candidate_context.md"],
    "semantic": ["references/semantic_read.md", "references/master_profile.json"],
}

MARGIN = 600   # room for the NOT PRINTED line and Claude Code's own wrapper


def output_limit():
    try:
        return int(os.environ.get("BASH_MAX_OUTPUT_LENGTH", "30000"))
    except ValueError:
        return 30000


def frame(rel, text):
    tail = "" if text.endswith("\n") else "\n"
    return (f"===== {rel} — verbatim, {len(text)} chars (Read the file before any Edit) =====\n"
            f"{text}{tail}===== end {rel} =====\n")


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in PACKS:
        print(__doc__, file=sys.stderr)
        return 2
    budget = output_limit() - MARGIN
    out, skipped = [], []
    used = 0
    for rel in PACKS[sys.argv[1]]:
        path = os.path.join(SKILL, rel)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"ERROR: cannot read {path}: {e}", file=sys.stderr)
            return 2
        block = frame(rel, text)
        if skipped or used + len(block) > budget:
            skipped.append(rel)   # keep file order: once one is skipped, Read the rest
            continue
        out.append(block)
        used += len(block)
    sys.stdout.write("".join(out))
    if skipped:
        print(f"NOT PRINTED (the output would pass the {output_limit()}-char Bash limit) — Read these "
              f"with the Read tool instead: {', '.join(os.path.join(SKILL, r) for r in skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
