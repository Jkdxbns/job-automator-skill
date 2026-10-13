#!/usr/bin/env python3
"""
PostToolUse hook (matcher: Edit|Write).

When a SKILL.md is edited, run validate_skill.py on that skill and, if it finds
errors (a dangling script/reference path or a hard-limit breach), inject the
report back into the model's context so the break is caught the moment it is
introduced instead of at pipeline runtime.

Non-blocking: it never fails the edit. It only surfaces a warning. Input is the
PostToolUse JSON on stdin; only the edited file_path matters.
"""

import json
import os
import subprocess
import sys

VALIDATOR = os.path.expanduser(
    "~/.claude/skills/job-automator/scripts/validate_skill.py")


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    ti = data.get("tool_input") or {}
    tr = data.get("tool_response") or {}
    path = ti.get("file_path") or tr.get("filePath") or ""
    if os.path.basename(path) != "SKILL.md":
        return 0  # not a skill file — nothing to do

    skill_dir = os.path.dirname(path)
    if not os.path.exists(VALIDATOR):
        return 0

    try:
        proc = subprocess.run(
            ["python3", VALIDATOR, skill_dir],
            capture_output=True, text=True, timeout=20)
    except (subprocess.SubprocessError, OSError):
        return 0

    # Exit 1 = the validator found ERRORS (dangling ref / limit breach).
    if proc.returncode == 1:
        report = (proc.stdout or "").strip()
        skill_name = os.path.basename(skill_dir) or "skill"
        out = {
            "systemMessage": f"⚠️ {skill_name} SKILL.md failed validation — see lint report.",
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    "validate_skill.py flagged ERRORS in the SKILL.md you just "
                    "edited. Fix them before relying on the pipeline:\n\n" + report),
            },
        }
        print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
