#!/usr/bin/env python3
"""Split company names into allowed / blocked using references/blocked_companies.txt.

usage:  filter_companies.py "Company A" "Company B" ...
        printf 'Company A\nCompany B\n' | filter_companies.py -

Prints one line per input:  ALLOW<TAB>name   or   BLOCK<TAB>name<TAB>matched entry
Whole-word, case-insensitive. Also strips punctuation so "Lockheed Martin Corp." still matches.
"""
import os, re, sys

LIST = os.path.join(os.path.dirname(__file__), "..", "references", "blocked_companies.txt")

def load():
    out = []
    for line in open(LIST, encoding="utf-8"):
        line = line.strip().lower()
        if line and not line.startswith("#"):
            out.append(line)
    return out

def norm(s):
    return " " + re.sub(r"[^a-z0-9]+", " ", s.lower()).strip() + " "

def blocked_by(company, entries):
    n = norm(company)
    for e in entries:
        if norm(e) in n:
            return e
    return None

def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    names = [l.rstrip("\n") for l in sys.stdin if l.strip()] if args == ["-"] else args
    entries = load()
    for c in names:
        hit = blocked_by(c, entries)
        print(f"BLOCK\t{c}\t{hit}" if hit else f"ALLOW\t{c}")

main()
