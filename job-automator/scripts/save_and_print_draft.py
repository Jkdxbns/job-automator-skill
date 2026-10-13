#!/usr/bin/env python3
"""
save_and_print_draft.py — Saves the outreach draft, echoing it to stdout.

NOTE: this stdout is NOT what the user sees. Claude Code collapses Bash output
to "ran N shell commands", so the echo is a debugging aid only. The draft
reaches the user because C5-DM pastes it into the assistant message (C5-Email
puts it in Gmail). The durable deliverable here is the saved file pair, which
is what the C6.5 follow-up reminder points at.

Usage: python save_and_print_draft.py <job_dir> '<draft_json>'
"""

import json, sys, os, textwrap
from datetime import datetime, timedelta

UNICODE_DASH_MAP = str.maketrans({
    "–": "-",   # en dash
    "—": "-",   # em dash
    "‒": "-",   # figure dash
    "―": "-",   # horizontal bar
    "·": "-",   # middle dot (used as bullet in some editors)
})


def normalize_body(text: str) -> str:
    """
    Collapse mid-sentence hard wraps and replace Unicode dashes with ASCII.
    Paragraphs separated by \n\n. Within each paragraph, bare newlines
    (visual wraps) are joined into a single flowing line.
    """
    text = text.translate(UNICODE_DASH_MAP)
    paragraphs = text.split("\n\n")
    cleaned = []
    for para in paragraphs:
        lines = [l.strip() for l in para.splitlines() if l.strip()]
        cleaned.append(" ".join(lines))
    return "\n\n".join(cleaned)


def normalize_signoff(text: str) -> str:
    """Replace Unicode dashes but preserve intentional single-line breaks."""
    return text.translate(UNICODE_DASH_MAP)


def print_draft(draft_data: dict):
    draft  = draft_data.get("draft", draft_data)
    target = draft_data.get("target", {})
    meta   = draft_data.get("meta", {})

    outreach_type = draft.get("type", "email").upper()
    name          = target.get("full_name") or "Recipient"
    company       = meta.get("company") or target.get("current_company") or ""
    subject       = draft.get("subject")
    greeting      = draft.get("greeting", "")
    body          = normalize_body(draft.get("body", "").replace("\\n", "\n"))
    sign_off      = normalize_signoff(draft.get("sign_off", "").replace("\\n", "\n"))
    word_count    = draft.get("word_count") or len(body.split())
    hook          = draft.get("hook_used", "-")
    followup_days = draft.get("followup_days", 5)
    followup_date = (datetime.now() + timedelta(days=followup_days)).strftime("%b %d, %Y")

    div = "-" * 64
    print()
    print(div)
    print(f"  {outreach_type}  |  {name}  @  {company}")
    print(div)
    if subject:
        print(f"  Subject: {subject}")
        print()
    for line in greeting.split("\n"):
        print(line)
    print()
    for para in body.split("\n\n"):
        for line in textwrap.wrap(para, width=72):
            print(line)
        print()
    for line in sign_off.split("\n"):
        print(line)
    print()
    print(div)
    print(f"  Hook      : {hook}")
    print(f"  Words     : {word_count}")
    print(f"  Follow-up : {followup_date} if no reply")
    print(div)
    if outreach_type == "EMAIL":
        print("  ✅  Copy above → paste into Gmail / Outlook")
    else:
        print("  ✅  Copy above → paste into LinkedIn Messages")
    print()


def save_draft(job_dir: str, draft_data: dict):
    job_dir_exp = os.path.expanduser(job_dir)
    logs_dir = os.path.join(job_dir_exp, "logs")
    os.makedirs(logs_dir, exist_ok=True)

    draft        = draft_data.get("draft", draft_data)
    outreach_type = draft.get("type", "email").lower()
    ts           = datetime.now().strftime("%Y%m%d_%H%M")

    # Full JSON to logs/ — type-specific + timestamped
    json_filename = f"{outreach_type}_{ts}.json"
    json_path     = os.path.join(logs_dir, json_filename)
    with open(json_path, "w") as f:
        json.dump(draft_data, f, indent=2)

    # Plain text to job root — email.txt or linkedin_dm.txt, timestamped
    if outreach_type == "dm":
        txt_filename = f"linkedin_dm_{ts}.txt"
    else:
        txt_filename = f"email_{ts}.txt"

    subject  = draft.get("subject")
    greeting = draft.get("greeting", "")
    body     = normalize_body(draft.get("body", "").replace("\\n", "\n"))
    sign_off = normalize_signoff(draft.get("sign_off", "").replace("\\n", "\n"))

    out = []
    if subject:
        out.append(f"Subject: {subject}\n")
    out.append(f"{greeting}\n")
    for para in body.split("\n\n"):
        out.append(f"{para.strip()}\n")
    out.append(sign_off.strip())

    txt_path = os.path.join(job_dir_exp, txt_filename)
    with open(txt_path, "w") as f:
        f.write("\n".join(out) + "\n")

    return json_path, txt_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python save_and_print_draft.py <job_dir> '<draft_json>'")
        sys.exit(1)

    job_dir  = sys.argv[1]
    json_str = sys.argv[2]

    try:
        draft_data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON — {e}", file=sys.stderr)
        sys.exit(1)

    # PRINT FIRST
    print_draft(draft_data)

    # THEN SAVE
    json_path, dm_path = save_draft(job_dir, draft_data)
    print(f"💾  Saved JSON : {json_path}")
    print(f"📄  Saved DM   : {dm_path}")


if __name__ == "__main__":
    main()
