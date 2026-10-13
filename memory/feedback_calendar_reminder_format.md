---
name: feedback-calendar-reminder-format
description: "Outreach follow-up calendar events should be 3 minutes long with zero popup/email alerts, not the job-automator skill's stated 30 min + multi-alert default"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f1027b80-c56a-4df9-9b88-c8703b3965cd
  modified: 2026-09-02T19:35:56.011Z
---

When creating a "Follow up: [Name] ([Company])" Google Calendar event for outreach tracking (Sub-workflow C6.5 in the job-automator skill, or any ad hoc follow-up reminder), use:
- Duration: 3 minutes (not the skill's stated 30 min, and not the 15 min this session used before the correction).
- Reminders: none at all — `use_default_reminders: false` and `reminders: []`. Do not add the pa skill's usual popup 10 min / popup 2 hr / popup 12 hr / email 1 day overrides, and do not add the job-automator skill's stated "popup 10 min before + popup at start" either.

**Why:** Justin explicitly asked to update every existing followup email/DM reminder from 15 minutes to 3 minutes and to strip all before-event alerts, after they had been created with the pa skill's standard reminder overrides. This is a direct correction of both skills' stated defaults for this specific event type.

**How to apply:** Applies specifically to outreach follow-up reminder events (the ones titled "Follow up: ..."). Other calendar events (actual meetings/calls, like the Ashutosh Kumar call) should still use normal duration and the pa skill's standard reminder defaults — this override is scoped to the no-alert, quick-marker style follow-up reminders only.
