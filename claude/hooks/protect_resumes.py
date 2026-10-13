#!/usr/bin/env python3
"""
PreToolUse hook (matcher: Bash).

Enforces the CLAUDE.md rule "Never Delete User Files": block `rm` of resume
artifacts (.tex / .pdf / .docx) and anything under ~/resumes or the job-search
dirs. This is prose in CLAUDE.md today; because this account runs in auto mode
(permission prompts skipped), a hook is the only thing that actually stops an
accidental deletion. The rule's escape hatch is to move the file to a .trash/
dir instead, so this denies rm but not mv.

Reads the PreToolUse JSON on stdin. Emits a PreToolUse permission decision:
deny (with a reason) when the command is an rm of a protected artifact, else
nothing (fall through to normal permission handling).
"""

import json
import os
import re
import sys

HOME = os.path.expanduser("~")
PROTECTED_EXT = (".tex", ".pdf", ".docx", ".doc")
PROTECTED_DIRS = (
    os.path.join(HOME, "resumes"),
    os.path.join(HOME, "Desktop", "jobs"),
    os.path.join(HOME, "job_search"),
    os.path.expanduser("~/.claude/skills/job-automator/references"),
)
# Deletions here are always fine (scratch / system temp).
EXEMPT_PREFIXES = ("/tmp/", "/var/tmp/", os.path.join(HOME, ".trash"))


def is_rm(cmd: str) -> bool:
    # rm as its own token: start of a segment or after ; && || | & (
    return re.search(r"(^|[;&|(]|\bxargs\s+)\s*rm\b", cmd) is not None


def targets_protected(cmd: str) -> bool:
    # crude but conservative token scan of everything after each rm
    for seg in re.split(r"[;&|()]", cmd):
        seg = seg.strip()
        if not re.match(r"^(sudo\s+)?rm\b", seg):
            continue
        for tok in seg.split()[1:]:
            t = tok.strip("'\"")
            if t.startswith("-"):
                continue  # flag
            full = os.path.expanduser(t)
            if any(full.startswith(p) or ("/tmp/" in full) for p in EXEMPT_PREFIXES):
                if any(full.startswith(p) for p in EXEMPT_PREFIXES):
                    continue
            low = full.lower()
            if low.endswith(PROTECTED_EXT):
                return True
            if any(full.startswith(d + os.sep) or full == d for d in PROTECTED_DIRS):
                return True
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if data.get("tool_name") != "Bash":
        return 0
    cmd = (data.get("tool_input") or {}).get("command", "")
    if not cmd or not is_rm(cmd) or not targets_protected(cmd):
        return 0  # let normal handling proceed

    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": (
                "Blocked by protect_resumes hook: this rm targets a resume "
                "artifact (.tex/.pdf/.docx) or a file under ~/resumes, "
                "~/Desktop/jobs, or the skill references dir. Per CLAUDE.md, "
                "never delete these — move them to a .trash/ dir instead "
                "(mv <file> <dir>/.trash/). If deletion is truly intended, the "
                "user must do it manually outside Claude."),
        }
    }
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
