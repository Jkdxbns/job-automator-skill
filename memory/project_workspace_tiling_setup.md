---
name: project_workspace_tiling_setup
description: GNOME desktop setup — named workspaces + Tiling Shell panel layouts to group multiple windows into one workspace instead of spreading a project across several
metadata: 
  node_type: memory
  type: project
  originSessionId: 056c1785-1d8c-4b01-8e78-71b7d1a2fb58
  modified: 2026-08-27T21:17:42.665Z
---

Justin's Fedora 44 / GNOME 50 (Wayland) desktop uses named workspaces (`gsettings org.gnome.desktop.wm.preferences workspace-names`) plus the **Tiling Shell** extension (`tilingshell@ferrarodomenico.com`, already installed at `~/.local/share/gnome-shell/extensions/`) to solve workspace clutter (had 12 workspaces, several redundant — e.g. `ROS`/`ROS`/`RTOS` as 3 separate spaces for one project).

- **Pattern:** one workspace per project, with Tiling Shell zones ("panels") inside it so 2-4 related windows (browser tabs, terminal, docs) sit snapped side-by-side instead of needing extra workspaces to avoid overlap/clutter.
- Confirmed working 2026-08-27 on the `RTOS` workspace: browser (top-left) + terminal (top-right) + second browser with README/GUIDEBOOK/MILESTONE/BUILD_LOG/PROJECT tabs (bottom-left), all tiled.
- Also installed: `gnome-shell-extension-workspace-indicator` (top-bar widget, later disabled — too cluttered with 12 workspaces) and `gnome-shell-extension-just-perfection` (still enabled). `gnome-shell-extension-vertical-workspaces` (V-Shell) was recommended for a Mission-Control-style full overview but Tiling Shell + workspace consolidation solved the actual need first, so V-Shell install may not have happened — verify before assuming it's active.
- **Why:** [[feedback_resume_defensibility]]-adjacent — Justin juggles many parallel projects (job search, RTOS build, inference engine, turret build) and needs low-friction context switching without losing track of which windows belong to which project.
- **How to apply:** when helping with desktop/workflow setup, prefer consolidating related workspaces via Tiling Shell layouts over adding more named workspaces. The `~/Desktop/projects/rtos/` repo (README.md, GUIDEBOOK, MILESTONES, BUILD_LOG, PROJECT files) is the custom RTOS project referenced in [[project_custom_rtos]] — confirm that memory's path still matches this one before citing.
