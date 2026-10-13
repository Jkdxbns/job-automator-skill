---
name: project-portfolio-site
description: "justinmascarenhas.com portfolio — repo Jkdxbns/justinmascarenhas.com (static, GitHub Pages), system-hero design, content rules, track resumes; status as of 2026-10-12"
metadata:
  node_type: memory
  type: project
  originSessionId: 9ee6148a-4a4b-48ac-b3a5-8c794eb119a5
  modified: 2026-10-13T01:24:02.838Z
---

**Repo:** `Jkdxbns/justinmascarenhas.com` (public). Static HTML/CSS/vanilla JS, no build step. Content single source: `assets/data/content.js` (`window.JM_CONTENT`). Built by a Claude Code web session (Opus 5.5, High) from a handoff brief; all Section 7 checks passed headless, and real-Chrome spot checks (video, console, Resume button) passed.

**Design (user-approved after many previews):** "Datasheet" palette (IBM Plex, teal accent). Hero = one robot *system board*: Perceive (his real QAT int8 MLP classifies a drawn digit → arm picks that numbered block) → Command (servo firmware: speed + joint limits, 3-ch PWM scope) → Move (2-link IK arm, collisions, planner, Retry). Focus switch System/Embedded/Robotics/Edge AI gates which panel is editable; routes `/`, `/embedded/`, `/robotics/`, `/edge-ai/`.

**Content rules he set:** no phone or street address on the site or public PDFs (location shown as "Dallas–Fort Worth, TX", per his 2026-10-12 request; master_profile still says Arlington, untouched); no phone card (his call); no visa/OPT terms; QAT = training only (internal rule lives in `claim_rule`, never rendered); Robocon never first; Telemetry Gateway shown as in-progress, no metrics.

**Track resumes:** sources in `~/Desktop/jobs/0000generic0000/Portfolio_{Embedded,Robotics,Edge_AI}/`; PDFs in repo `assets/resume/`. His asks: no sensor model names, no counts of challenges/versions/time; Embedded includes the Object Tracking Turret (his call); Edge AI summary is an elevator pitch. No System PDF: in System focus the hero button reads "Resumes (PDF)" and jumps to the Contact card that lists all three.

**LIVE since 2026-10-12** at https://justinmascarenhas.com (repo renamed to `Jkdxbns/justinmascarenhas.com`, public; GitHub Pages from `main` root; HTTPS enforced, cert auto-renews). DNS on **Cloudflare**: 4 A + 4 AAAA (GitHub Pages IPs) + `www` CNAME → jkdxbns.github.io, all **DNS only** (proxy off). Cloudflare also holds **Zoho Mail** MX/SPF/DKIM records — never touch them. If a cert ever stalls at null, remove and re-add the custom domain in Pages to restart provisioning.

**Local working copy:** `/mnt/e/Maal/_____Mera_____/portfolio/site` (clone of main; git identity set). Edit there → preview with `python3 -m http.server` → commit + push to main → Pages redeploys in ~1 min. After editing root `index.html`, run `python3 tools/make-shells.py && python3 tools/make-pages.py && python3 tools/stamp-assets.py` (regenerates the focus pages and the Projects/CV/About pages, then stamps ?v=hash on asset URLs; Pages caches 10 min, so unstamped assets once paired a new page with an old script). Text lives in `assets/data/content.js`.

**Structure (since 2026-10-12, commit 4cdf711):** Home = hero, Featured (fixed order: COFFIN, STM32, QAT / Turret, CUDA VGG16, SLM), Ongoing (Telemetry Gateway), Skills, Contact. `/projects/` = filterable grid + search + ongoing + archive; `/cv/` = Experience first, then project one-liners, education, skills, awards, 3 track PDFs; `/about/` = photo + facts + "about this site" + education. Project details open as a centred tile (modal). `/projects/` order: Ongoing on top, then the grid (Telemetry Gateway also appears there as a text-only card/tile, no metrics), then Archive. Firmware and Edge AI chips pin their own lead order via `content.js` `filter_order` (Firmware: STM32, Turret, COFFIN; Edge AI: VGG16, SLM, COFFIN, Turret, QAT, Whisper ASR, GPT-2). No HPC filter. The two MPI projects (neuron sim, ray tracer) and the fingerprint+SMS-OTP 2FA lock live in the Archive only, not the grid. MPI/SLURM stay in the skills table.

**Headshot:** live since 2026-10-12 as `assets/img/me.webp` (640×800, Gemini-edited from his suit photo IMG_2491; he approved the edit). Source pictures (project art, `myself.jpeg`, og image) live in `/mnt/e/Maal/_____Mera_____/portfolio/pictures/`; the raw crop is in `portfolio/photo/`.

**Tailored resumes link the site (since 2026-10-12):** job-automator's `generate_pdf.py` puts `justinmascarenhas.com/embedded` (embedded/firmware/hardware roles) or `/edge-ai` (all others) in the header, chosen from `role_category`; LinkedIn was dropped from the resume header at his request so the line fits. Rule documented in the skill's `resume_format.md § Header`.

**Contact form:** live since 2026-10-13 via Web3Forms (public key in `content.js` `person.contact_form`, free tier 250/mo) → jmascarenhas1998@gmail.com, subject `[Portfolio · <topic>] <subject>`, Reply-To = visitor. Verified with a real test message.

**Still open:** nothing pending.

Related: [[feedback-resume-defensibility]], [[project-coffin-repo-landmines]], [[feedback-master-profile-permission]].
