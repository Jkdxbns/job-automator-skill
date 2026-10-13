---
name: reference-jetson-ssh
description: Jetson Orin SSH credentials and environment details for COFFIN project
metadata: 
  node_type: memory
  type: reference
  originSessionId: 43b0802f-def4-4394-9616-153dfd543053
---

Jetson Orin (COFFIN project device)

**SSH:** `ssh jkdxbns@192.168.0.146`
**Username:** jkdxbns
**Password:** 010502 (low-criticality, only accessible when Jetson is active on local network)
**Key auth:** `~/.ssh/id_ed25519` is authorized — no password prompt needed after setup

**Environment:**
- CUDA 12.6, Driver 540.4.0, TensorRT 10.7.0
- Python 3.10.12
- COFFIN venv: `~/Desktop/drone/venv/` — activate with `source ~/Desktop/drone/venv/bin/activate`
- Main COFFIN code: `~/Desktop/drone/working_arm/`

**Model files:**
- `~/Desktop/drone/working_arm/best_03_14.pt` — original PyTorch
- `~/Desktop/drone/working_arm/best_03_14.onnx` — ONNX export
- `~/Desktop/drone/working_arm/best_03_14.engine` — TRT FP16 at imgsz=512 (built June 5 2026)
- `~/Desktop/drone/job/yolo-tensorrt-jetson-benchmark/best_03_14.engine` — benchmark TRT (imgsz=256)

**Benchmark results (imgsz=256, 300 frames):**
- PyTorch: 56.65ms / 17.65 FPS, detection rate 67.7%
- TensorRT: 10.87ms / 92 FPS, detection rate 90.3%
- Speedup: 5.21×
