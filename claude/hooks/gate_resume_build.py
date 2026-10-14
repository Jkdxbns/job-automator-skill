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

MULTI-LINE COMMANDS AND $JOB_DIR (fixed 2026-10-14)
---------------------------------------------------
Two holes let a gated build through, both on the documented B4 command:
  1. shlex.split() treats a newline as plain whitespace and keeps a `;` glued
     to the word before it, so `python3 -c "..." '<json>'` followed by
     generate_pdf.py on the next line (or after `';`) was ONE "simple command"
     whose script was the -c code string — never a build. _flatten() now turns
     unquoted newlines into `;`, drops heredoc bodies (data, not commands) and
     comments, and the shlex lexer splits shell operators into their own tokens.
     Shell keywords (if/then/do/...) are stripped like wrappers.
  2. The hook never sees the Bash tool's environment, so `$JOB_DIR` in a path
     resolved to nothing and the hook failed open. find_job_dir() now expands
     $JOB_DIR from a JOB_DIR=... assignment in the same command, resolves
     relative paths against the hook input's cwd, and as a last resort takes
     the newest JOB_DIR=... the session's own Bash commands set (transcript).

OVERRIDE
--------
The user chooses "Tailor anyway" in the B-GATE AskUserQuestion popup, which
writes the marker:

    touch "$JOB_DIR/logs/.tailor_override"

A hard blocker (ITAR / clearance / citizenship) is NEVER overridable — the
marker is ignored in that case, matching the HARD BLOCKER RULE.

WIRING (live in ~/.claude/settings.json under PreToolUse/Bash, alongside
protect_resumes.py). This is the only copy: the byte-identical duplicate that
used to sit in the skill's own hooks dir was removed so the two cannot
drift. In the repo it lives at claude/hooks/.

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
OPERATORS = {";", "&&", "||", "|", "&", "|&", ";;", "(", ")"}

# Prefix wrappers that take no argument of their own.
WRAPPERS = {"env", "nohup", "nice", "stdbuf", "command", "exec", "time"}

# Shell keywords that can sit in front of a command: `then python3 x.py`.
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "}"}

HEREDOC_RE = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
JOB_DIR_ASSIGN_RE = re.compile(r"JOB_DIR=([^\s;&|'\"`$]+)")


def _flatten(cmd):
    """One `;`-separated line per top-level command: unquoted newlines become
    `;`, backslash-newline joins lines, comments are dropped, and heredoc
    bodies are removed (they are data, not commands)."""
    out, i, n, quote, heredocs = [], 0, len(cmd), None, []
    while i < n:
        c = cmd[i]
        if quote:
            out.append(c)
            if c == "\\" and quote == '"' and i + 1 < n:
                out.append(cmd[i + 1])
                i += 2
                continue
            if c == quote:
                quote = None
            i += 1
            continue
        if c == "\\" and i + 1 < n:
            if cmd[i + 1] != "\n":
                out.append(cmd[i:i + 2])
            i += 2
            continue
        if c in "'\"":
            quote = c
            out.append(c)
            i += 1
            continue
        prev = out[-1][-1] if out else " "
        if c == "#" and prev in " \t;&|()":
            while i < n and cmd[i] != "\n":
                i += 1
            continue
        if cmd.startswith("<<", i) and not cmd.startswith("<<<", i):
            m = HEREDOC_RE.match(cmd, i)
            if m:
                heredocs.append((m.group(1) == "-", m.group(3)))
                out.append(" ")
                i = m.end()
                continue
        if c == "\n":
            out.append(" ; ")
            i += 1
            for strip_tabs, delim in heredocs:      # skip each body, in order
                while i < n:
                    j = cmd.find("\n", i)
                    line = cmd[i:] if j == -1 else cmd[i:j]
                    i = n if j == -1 else j + 1
                    if (line.lstrip("\t") if strip_tabs else line) == delim:
                        break
            heredocs = []
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _tokens(cmd):
    """Shell-ish tokens with operators split out (`a';` -> `a`, `;`)."""
    flat = _flatten(cmd)
    try:
        lex = shlex.shlex(flat, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        toks = list(lex)
    except ValueError:
        toks = flat.split()
    return toks

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

    # Strip prefix wrappers, including `timeout 30`, and shell keywords.
    while i < n:
        base = os.path.basename(argv[i])
        if base in WRAPPERS or argv[i] in KEYWORDS:
            i += 1
        elif ENV_ASSIGN_RE.fullmatch(argv[i]):
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
    return any(_is_build_argv(argv, depth) for argv in _split_simple(_tokens(cmd)))


def _all_tokens(cmd, depth=0):
    """
    Every token in the command, descending into `bash -c "<payload>"` payloads
    so a build wrapped in a subshell still resolves its job dir.
    """
    toks = _tokens(cmd)

    out = []
    for idx, t in enumerate(toks):
        out.append(t)
        if t == "-c" and idx + 1 < len(toks) and depth < 3:
            prev = toks[idx - 1] if idx else ""
            if SHELL_RE.fullmatch(os.path.basename(prev)):
                out.extend(_all_tokens(toks[idx + 1], depth + 1))
    return out


def _has_fit(d):
    return bool(d) and os.path.exists(os.path.join(d, "logs", "fit.json"))


def _transcript_job_dir(transcript_path, cwd):
    """Last resort: the newest JOB_DIR=<path> this session's own Bash commands set.

    The hook never sees the Bash tool's environment, so a build written as
    `generate_pdf.py $JOB_DIR/logs/tailored.json $JOB_DIR` is only resolvable
    from where the session assigned it. Reads at most the last 4 MB."""
    if not transcript_path:
        return None
    try:
        with open(os.path.expanduser(transcript_path), "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - 4 * 1024 * 1024))
            lines = f.read().decode("utf-8", errors="replace").splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        if "JOB_DIR=" not in line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        content = ((rec.get("message") or {}).get("content")) or []
        if not isinstance(content, list):
            continue
        for block in reversed(content):
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            command = (block.get("input") or {}).get("command") or ""
            for val in reversed(JOB_DIR_ASSIGN_RE.findall(command)):
                d = os.path.join(cwd or "", os.path.expanduser(val))
                if _has_fit(d):
                    return d
    return None


def find_job_dir(cmd, cwd=None, transcript_path=None):
    """
    Resolve the job dir from the command's own tokens.

    generate_pdf.py <tailored.json> <job_dir>
    resume_cache.py index <fit.json> <job_dir> ...

    Strategy: any token that is (or contains) a path with a logs/fit.json under
    it wins. `$JOB_DIR` / `${JOB_DIR}` is expanded from a JOB_DIR=... set in the
    same command, relative paths resolve against the session cwd. Falls back to
    $JOB_DIR in the hook's own environment, then to the session transcript.
    """
    cwd = cwd or os.getcwd()
    toks = _all_tokens(cmd)
    assigned = None
    for t in toks:
        m = JOB_DIR_ASSIGN_RE.fullmatch(t) or JOB_DIR_ASSIGN_RE.fullmatch(t.replace("export ", ""))
        if m:
            assigned = os.path.join(cwd, os.path.expanduser(m.group(1)))

    cands = []
    for t in toks:
        t = t.strip("'\"")
        if assigned:
            t = t.replace("${JOB_DIR}", assigned).replace("$JOB_DIR", assigned)
        if not t or t.startswith("-") or "$" in t:
            continue
        t = os.path.join(cwd, os.path.expanduser(t))
        # a fit.json / tailored.json path → its job dir is two levels up
        if t.endswith(".json") and os.sep + "logs" + os.sep in t:
            cands.append(os.path.dirname(os.path.dirname(t)))
        elif os.path.isdir(t):
            cands.append(t)
    if assigned:
        cands.append(assigned)

    env = os.environ.get("JOB_DIR")
    if env:
        cands.append(os.path.expanduser(env))

    for c in cands:
        if _has_fit(c):
            return c
    return _transcript_job_dir(transcript_path, cwd)


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

    job_dir = find_job_dir(cmd, data.get("cwd"), data.get("transcript_path"))
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
