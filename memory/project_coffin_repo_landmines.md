---
name: project-coffin-repo-landmines
description: COFFIN — public GitHub is STALE vs the real local production source; the capstone notes are accurate. Plus the STM32/FreeRTOS framing errors to avoid.
metadata:
  node_type: memory
  type: project
  originSessionId: 2d9322a8-2df1-45d4-aef3-12e5ecdc6c13
---

For TBC/NVIDIA interviews on COFFIN. **CORRECTION (June 2026, verified against `/mnt/e/___COFFIN___/`):** an earlier read of the *public GitHub* repos produced false "landmines." The full local source proves `01_coffin_capstone.md` is **accurate**. Key fact: **the public `voice-controlled-robotic-arm` repo is a STALE snapshot** (older firmware + trackers). The real production code lives in `/mnt/e/___COFFIN___/Server/FlaskServer_v12/`.

**ToF range gate is REAL** — `Server/FlaskServer_v12/scripts/tracker_pick_controller.py`: `TOF_MAX_MM=250` (l.56), `_query_cam_tof_mm()` sends `b"tof?\n"` (l.157), l.411-416 do `range_check` → `raise RuntimeError("TARGET_TOO_FAR")` if dist<0 or >250. Firmware answers `tof?` in `test_yolo.ino:577` / `vla_executor.ino:277`. Notes Q6/failure#1/BonusQ all code-accurate. (Earlier "gate missing" conclusion was wrong — it read the stale arm repo.)

**Firmware CAN complete a pick** — `test_yolo.ino`/`test.ino`/`test_fast.ino` handle `prepick`,`grab`,`pick`/`pp` and print `OK`/`ERR`. `minimal_tof_pick.ino` is a SEPARATE variant doing the whole sequence as one blind `doPickAndPlace()` (reads cam ToF only to compute IK target, aborts on read-fail L<0, no 250 gate). Don't conflate the two firmware families.

**TensorRT is real + a strength — VERIFIED ON JETSON (ssh `jetson`, `~/Desktop/drone/job/benchmark_original_engine_256/raw_pt_vs_trt_summary.json`).** Benchmark exact: imgsz 256, `pytorch_half:false` (PyTorch ran **FP32**), 56.65→10.87 ms, **5.21×**, 17.6→92 FPS, 203 vs 271 detections, conf 0.589 vs 0.659. **Engine is INT8 (RESOLVED, not FP16):** `yolo_quantizer.py` = Ultralytics `model.export(format="engine", int8=True, data=dataset.yaml)` PTQ w/ calibration; `quantize.txt` trtexec shows `Precision: FP32+FP16+INT8`. The "INT8 detected MORE at higher conf than FP32" is NOT a paradox — it's a raw above-threshold count on in-domain frames (not mAP); calibration shifts borderline scores across the 0.45 gate + TRT graph differs (fusion/NMS). Defensible claim = the 5.21× speedup, not an accuracy gain. Reconcile imgsz 256 (benchmark) vs 512 (tracker INFER_IMGSZ).

**TRUE TOPOLOGY (verified in jetson_arm_service.env):** Flask server + Gemini + Whisper STT run on Justin's **LAPTOP (ROG Zephyrus G14, LAN IP 192.168.0.168:5000)**. The **Jetson Orin is a Socket.IO CLIENT** running YOLO via the **TensorRT .engine** (`best_03_14.engine`, not .pt) + the arm bridge + USB-serial to the Arduino. Phone → laptop (HTTP audio + Socket.IO) → Jetson client → Arduino. **No WebRTC in COFFIN** (HTTP multipart audio + Socket.IO events only; camera read locally by OpenCV). The only aiortc/WebRTC code in the tree is Prerit's separate `Monocular_Obstacle_Avoidance_System`. MCU is **Arduino Nano (ATmega328P), Arduino framework, single-thread superloop — NOT "bare-metal" (no register-level) and NOT RTOS.**

**FRAMING ERRORS to avoid (esp. for Mitch, who reads GitHub):**
- COFFIN arm MCU = **Arduino/AVR** (`#include <Servo.h>`, CH340/FTDI), **NOT STM32**. STM32 belongs to the Turret + drone flight-controller only. Justin's Mitch-doc wrongly says "pushed servo control to the STM32" — say "Arduino/AVR."
- **No FreeRTOS** anywhere in COFFIN (arm is bare-metal single-thread). The drone flight-controller is **ArduPilot on ChibiOS**, not FreeRTOS. Drop the "FreeRTOS mutex" claim for COFFIN.

**Mitch-specific lead:** embedded-Linux layer (Jetson userspace processes + `jetson-arm-bridge.service` systemd unit) vs bare-metal Arduino split; closing-the-loop sensor→action theme; reliability failures (serial errno-5 reconnect + VID autodetect, servo brown-out staggered attach, BT route recovery). UR5e ROS jumps to #2 for him — NOT yet reviewed by assistant.

Related: [[project-tbc-pipeline]], [[feedback-resume-project-selection]]
