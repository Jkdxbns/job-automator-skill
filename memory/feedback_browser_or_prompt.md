---
name: feedback-browser-or-prompt
description: "For changes outside CLI reach (Cloudflare DNS, web dashboards), drive Claude in Chrome or prompt Justin with exact steps — don't stop at \"I can't\""
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9ee6148a-4a4b-48ac-b3a5-8c794eb119a5
  modified: 2026-10-13T01:24:39.688Z
---

When a change needs a web dashboard I can't reach from the shell (e.g. Cloudflare DNS for justinmascarenhas.com, GitHub UI-only settings), either do it through Claude in Chrome in his signed-in browser or give him exact click-by-click steps to do it himself.

**Why:** He said so on 2026-10-12 while we were maintaining the portfolio site. He wants the work finished, not handed back with "I can't access that".

**How to apply:** Prefer the `gh` CLI or another shell route first. Otherwise use Claude in Chrome. Account and DNS changes still need his explicit yes before each save, and he signs in himself. If the browser isn't connected, give precise steps with the exact values.

Related: [[project-portfolio-site]].
