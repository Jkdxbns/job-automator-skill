---
name: reference-interview-prep-files
description: Where the 17 project analysis files live (Desktop/interview_prep/projects/) and their study priority order
metadata: 
  node_type: memory
  type: reference
  originSessionId: 19dc278c-33a3-41d7-b9a2-367d25062250
  modified: 2026-09-11T19:20:52.720Z
---

All deep technical analysis files are at `/home/jkdxbns/Desktop/interview_prep/projects/`
(NOT `Desktop/jobs/interview_prep/` — that older path was wrong). Folder conventions live in
`/home/jkdxbns/Desktop/interview_prep/CLAUDE.md` (its own file table only lists 01–15).

Each file contains: architecture deep-dive, code-level evidence, claims vs code verification, iteration history, key concepts to explain, and interview Q&A per difficulty level.

| File | Project | Priority for embedded/edge roles |
|---|---|---|
| `01_coffin_capstone.md` | COFFIN Voice-Controlled Arm (MS Capstone) | ★★★★★ |
| `02_vgg16_cuda.md` | CUDA Kernel Optimization VGG16 | ★★★★★ |
| `03_stm32_baremetal.md` | STM32 Bare-Metal + smart_fan personal project | ★★★★★ |
| `04_carla_autonomous.md` | CARLA Autonomous Driving | ★★★☆☆ |
| `05_ros_robotic_arm.md` | ROS2 UR5e + AL5B | ★★★★☆ |
| `06_abb_robotstudio.md` | ABB RobotStudio RAPID | ★★☆☆☆ |
| `07_slm_compression.md` | TinyLlama 8-bit Quantization + pynvml | ★★★☆☆ |
| `08_barc_research.md` | BARC Image Stitching + ZoeDepth | ★★★☆☆ |
| `09_planctech_glove.md` | ADXL345 Gesture Glove + HID | ★★★★☆ |
| `10_barc_gui.md` | PyQt5 Serial Data GUI | ★★☆☆☆ |
| `11_mpi_projects.md` | MPI HH Neuron + Ray Tracer | ★★★☆☆ |
| `12_coffin_asr.md` | Whisper-Style ASR from Scratch | ★★★☆☆ |
| `13_iit_donut.md` | DONUT Fine-tuning at IIT Bombay | ★★☆☆☆ |
| `14_tusk_yolov8.md` | YOLOv8n Toothbrush Detection | ★★★☆☆ |
| `15_teesside_unet.md` | U-Net BraTS 2020 Segmentation | ★★☆☆☆ |
| `16_object_tracking_turret.md` | Turret — synthesis claim, virtual-build gap list | ★★★★☆ (risk) |
| `17_undergrad_projects.md` | 8 claimable unlisted projects (Study Controller, QAT, Frames Sim, PyPI steg, MP1B 2FA, joystick, Avana, SIH) + provenance, excluded items, skills/awards to add | ★★★★★ (Study Controller) |

`17` records provenance per project in Justin's words (2026-09-11): QAT = training only (FPGA was a friend's); Avana = solo; excluded: fitness_app / JobCopilot / janki / omkar / pritha, Flipkart GRiD (he did CAD + fabrication only, no code), `hid_mouse` (actually a hexapod sketch); MP2B Verilog held pending refresh. Nothing from 17 is in master_profile.json yet.

**Study style:** Quiz format, "why this not that" focus, one project at a time, rebuild mental models from code up. See [[feedback-interview-prep-style]].

**TBC interview context:** [[project-tbc-pipeline]]
