---
name: project-telemetry-gateway
description: "Edge Telemetry Gateway — BBB+MPU6050 C kernel driver → C++ epoll TCP/IP over Ethernet → Jetson/laptop clients; 3-arch Docker, GitHub Actions CI/CD; one project for Docker/CI-CD/Ethernet/embedded Linux/networking/C++"
metadata: 
  node_type: memory
  type: project
  originSessionId: b3517308-bd3c-4152-a8c8-4d1c22446930
  modified: 2026-10-08T00:00:00.000Z
---

**Folder:** `~/Desktop/projects/telemetry_gateway/`. Read its `memory.md` first; `docs/PROJECT_GUIDE.md` is the plan on one page. Justin restructured the repo on 2026-10-08 and builds the source folders himself as needed. Only README, PROPOSAL, REPORT and PROTOCOL are public; everything else is local.

**What it does:**
- An MPU6050 on I2C2 of the BeagleBone Black.
- A C++ epoll gateway reads it through a source interface: simulated, then `/dev/i2c-2`, then Justin's own C kernel char driver `/dev/mpu6050` (device-tree overlay, own compatible string `jm,tg-mpu6050`).
- Each sample is framed with length-prefix, seq and CRC-32 and streamed over TCP/IP.
- Clients: the Jetson (Ethernet) logs CSV; the laptop (Wi-Fi) is the live view and load tester.
- Multi-arch Docker images (amd64, arm64, arm/v7); GitHub Actions builds, tests, pushes to GHCR and deploys to the BBB on push to main.

**Plan:** steps skip 5 (dropped scope): protocol, epoll networking, Docker, BBB + sensor, CI/CD, kernel driver + overlay. Estimates only, no deadlines.

**Why:** Justin wants one project that fills defensible keywords across his applications. C++ fluency cost 2 of 3 lost interviews.

[[project-embedded-linux-bbb]] is NOT replaced (later: Yocto, U-Boot, IIO, multiple sensors, CAN).

**Guardrails:**
- Kernel code is C; userspace is C++ (no span/jthread). Never name the C++ standard version in any doc or on the resume.
- Say "streamed over TCP/IP on the LAN, Ethernet + Wi-Fi". Never "broadcast", "Internet" or "Ethernet driver".
- Never measure over usb0.
- Answer only what is asked, no unprompted theory; mentor only, no code unless asked.
- AI may write code, but Justin answers `DEFENSE_QA` unaided on his own schedule (it doesn't gate steps).

Related: [[feedback-resume-defensibility]], [[reference-interview-log]], [[feedback-master-profile-permission]], [[reference-hardware-inventory]], [[project-custom-rtos]].
