#!/usr/bin/env python3
"""
gate_resume_build.py — PreToolUse/Bash hook. Makes B-GATE structural.

WHY
---
B-GATE is a rule the model has to remember to check before tailoring. A rule the
model executes freehand is a rule the model can skip — that is the same failure
class that produced the zoox_ds_pv contradiction. This hook turns it into
something the model cannot bypass even if it forgets the rule entirely.

WHAT IT DOES
------------
Denies any Bash command that generates a tailored resume (generate_pdf.py, or a
resume_cache.py index/copy) when the job's own fit.json says APPLY = "No" (or a
hard blocker fired) and no override marker exists.

The job dir is resolved from the command's own arguments — the $JOB_DIR that the
generate_pdf.py invocation names — so the hook checks the verdict for the role
actually being tailored, not whatever happens to be in the environment.

TRIGGERING (fixed 2026-09-18)
-----------------------------
The trigger is EXECUTION, not mention. Earlier this hook used a bare
`re.search("generate_pdf\\.py", cmd)` over the whole command string, so a
read-only command that merely NAMED the script — `grep -rn generate_pdf.py .`,
`echo ... generate_pdf.py`, a heredoc quoting it — matched. Combined with
find_job_dir() accepting a bare `.`, running any such command from inside a
"No"-verdict job folder got denied. See is_build_invocation(): the command is
tokenized, split on shell operators, wrappers and interpreters are stripped, and
only a script sitting in COMMAND POSITION counts.

find_job_dir() is unchanged and correct: for a genuine build launched from the
job dir, `.` really is the target job.

OVERRIDE
--------
The user chooses "Tailor anyway" in the B-GATE AskUserQuestion popup, which
writes the marker:

    touch "$JOB_DIR/logs/.tailor_override"

A hard blocker (ITAR / clearance / citizenship) is NEVER overridable — the
marker is ignored in that case, matching the HARD BLOCKER RULE.

WIRING (live in ~/.claude/settings.json under PreToolUse/Bash, alongside
protect_resumes.py). This is the only copy: the byte-identical duplicate that
used to sit in ~/.claude/skills/job-automator/hooks/ was removed so the two
cannot drift. In the repo it lives at claude/hooks/.

    {
      "type": "command",
      "command": "python3 ~/.claude/hooks/gate_resume_build.py",
      "timeout": 10,
      "statusMessage": "Checking fit verdict before resume build"
    }

Fails open on any unexpected condition: a hook that crashes must not block
unrelated Bash commands.
"""

import json
import os
import re
import shlex
import sys

# Shell operators that end one simple command and begin the next.
OPERATORS = {";", "&&", "||", "|", "&", "|&"}

# Prefix wrappers that take no argument of their own.
WRAPPERS = {"env", "nohup", "nice", "stdbuf", "command", "exec", "time"}

# Wrappers of the form `<tool> run <script>`.
RUNNERS = {"uv", "poetry", "pipenv", "pdm", "hatch", "rye"}

INTERPRETER_RE = re.compile(r"python3?(\.\d+)?$")
ENV_ASSIGN_RE = re.compile(r"\w+=.*")
SHELL_RE = re.compile(r"(ba|z|k|da)?sh$")


def _split_simple(toks):
    """Split a token list into simple commands on shell operators."""
    out, cur = [], []
    for t in toks:
        if t in OPERATORS:
            if cur:
                out.append(cur)
            cur = []
        else:
            cur.append(t)
    if cur:
        out.append(cur)
    return out


def _is_build_argv(argv, depth):
    """True if this single simple command EXECUTES a build script."""
    i = 0
    n = len(argv)

    # Strip leading env assignments (FOO=bar python3 ...).
    while i < n and ENV_ASSIGN_RE.fullmatch(argv[i]):
        i += 1

    # Strip prefix wrappers, including `timeout 30`.
    while i < n:
        base = os.path.basename(argv[i])
        if base in WRAPPERS:
            i += 1
        elif base == "timeout":
            i += 1
            while i < n and argv[i].startswith("-"):
                i += 1
            if i < n:
                i += 1  # the duration
        else:
            break

    if i >= n:
        return False

    base = os.path.basename(argv[i])

    # `bash -c "<payload>"` → recurse into the payload so it is not a bypass.
    if SHELL_RE.fullmatch(base) and depth < 3:
        j = i + 1
        while j < n:
            if argv[j] == "-c" and j + 1 < n:
                return is_build_invocation(argv[j + 1], depth + 1)
            if argv[j].startswith("-"):
                j += 1
            else:
                break
        return False

    # `uv run script.py`
    if base in RUNNERS:
        i += 1
        if i < n and argv[i] == "run":
            i += 1
        while i < n and argv[i].startswith("-"):
            i += 1
        if i >= n:
            return False
        base = os.path.basename(argv[i])

    # `python3 -X flag script.py`
    if INTERPRETER_RE.fullmatch(base):
        i += 1
        while i < n and argv[i].startswith("-"):
            i += 1
        if i >= n:
            return False
        base = os.path.basename(argv[i])

    if base == "generate_pdf.py":
        return True
    if base == "resume_cache.py" and argv[i + 1:i + 2] == ["index"]:
        return True
    return False


def is_build_invocation(cmd, depth=0):
    """
    True only when a build script is actually EXECUTED.

    Merely naming the script — in a grep pattern, a cat argument, an echo, a
    heredoc — is NOT a build and must not be gated.
    """
    try:
        toks = shlex.split(cmd)
    except ValueError:
        toks = cmd.split()
    return any(_is_build_argv(argv, depth) for argv in _split_simple(toks))


def _all_tokens(cmd, depth=0):
    """
    Every token in the command, descending into `bash -c "<payload>"` payloads
    so a build wrapped in a subshell still resolves its job dir.
    """
    try:
        toks = shlex.split(cmd)
    except ValueError:
        toks = cmd.split()

    out = []
    for idx, t in enumerate(toks):
        out.append(t)
        if t == "-c" and idx + 1 < len(toks) and depth < 3:
            prev = toks[idx - 1] if idx else ""
            if SHELL_RE.fullmatch(os.path.basename(prev)):
                out.extend(_all_tokens(toks[idx + 1], depth + 1))
    return out


def find_job_dir(cmd):
    """
    Resolve the job dir from the command's own tokens.

    generate_pdf.py <tailored.json> <job_dir>
    resume_cache.py index <fit.json> <job_dir> ...

    Strategy: any token that is (or contains) a path with a logs/fit.json under
    it wins. Falls back to $JOB_DIR.
    """
    cands = []
    for t in _all_tokens(cmd):
        t = os.path.expanduser(t.strip("'\""))
        if not t or t.startswith("-"):
            continue
        # a fit.json / tailored.json path → its job dir is two levels up
        if t.endswith(".json") and os.sep + "logs" + os.sep in t:
            cands.append(os.path.dirname(os.path.dirname(t)))
        elif os.path.isdir(t):
            cands.append(t)

    env = os.environ.get("JOB_DIR")
    if env:
        cands.append(os.path.expanduser(env))

    for c in cands:
        if os.path.exists(os.path.join(c, "logs", "fit.json")):
            return c
    return None


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if (data.get("tool_name") or "") != "Bash":
        return 0
    cmd = ((data.get("tool_input") or {}).get("command")) or ""
    if not is_build_invocation(cmd):
        return 0

    job_dir = find_job_dir(cmd)
    if not job_dir:
        return 0  # cannot resolve a verdict → fail open, don't block

    try:
        with open(os.path.join(job_dir, "logs", "fit.json")) as f:
            fit = json.load(f)
    except (OSError, json.JSONDecodeError):
        return 0  # fail open

    v = fit.get("verdicts") or {}
    apply_v = (v.get("apply") or "").strip().lower()
    blocked = bool(v.get("hard_blocker_triggered")
                   or fit.get("hard_blocker_triggered")
                   or apply_v.startswith("hard block"))
    role = f"{fit.get('company') or '?'} — {fit.get('role') or '?'}"

    if blocked:
        reason = (v.get("hard_blocker_reason")
                  or fit.get("hard_blocker_reason") or "hard disqualifier")
        deny(f"HARD BLOCKER on {role}: {reason}. Resume generation is disabled "
             f"for this role and cannot be overridden (SKILL.md HARD BLOCKER "
             f"RULE). Do not retry, do not write the override marker.")
        return 0

    if apply_v.startswith("no"):
        marker = os.path.join(job_dir, "logs", ".tailor_override")
        if os.path.exists(marker):
            return 0  # user explicitly chose "Tailor anyway"
        deny(
            f"B-GATE: fit.json for {role} says APPLY = \"No\" "
            f"(match {fit.get('match_pct')}%). Tailoring is gated. Present the "
            f"B-GATE AskUserQuestion popup (\"Tailor anyway\" / \"Skip this "
            f"role\", skip recommended). Only if the user picks \"Tailor "
            f"anyway\", run:  touch '{marker}'  and retry.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
