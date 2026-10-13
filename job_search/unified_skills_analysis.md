# Unified Skills Demand vs Profile — 2026-10-06

Source: 860 unique fit.json files in ~/Desktop/jobs. 755 are target roles (some in more than one track).
Skill terms come from the JD side only (each role's top_ats_keywords and missing_skills), matched by tightened regex against a 70-skill taxonomy. have/adjacent/responsibility text is excluded so your own skills do not inflate demand. A first pass that included them overstated your strong skills by 10-15 points (embedded C 45% vs 31%). Gap skills barely moved.
Justin's depth rating (strong / working / exposure / none) is only partly from skills_db.json. 30 of 70 ratings match a skills_db entry. 20 are the author's own judgement with no skills_db entry (CAN, Docker, cloud, CI/CD, LiDAR, bootloader, etc.). 16 map to an entry that disagrees or only loosely fits (SLAM, sensor fusion, path planning, BSP, etc.). The CSV column rating_source marks which. Correct any rating before choosing projects from the gap ranking.
Raw data: skills_demand_histogram.csv and .json (same folder).

| Track | Roles | Avg keyword match | Hard-blocked |
|---|---|---|---|
| Firmware/Embedded | 336 | 58.2 | 14 |
| Robotics/Perception | 196 | 62.0 | 2 |
| Edge-AI/ML-Systems | 406 | 57.8 | 8 |
| All target | 755 | 57.3 | 22 |

Share of all skill mentions that Justin backs at working depth or better: Firmware 77%, Robotics 73%, Edge-AI 75%.

## Demand histogram (% of roles asking, All / FW / RB / AI)

| Skill | Depth | All | FW | RB | AI |
|---|---|---|---|---|---|
| Python | strong | 55 | 41 | 62 | 68 |
| C++ | working | 52 | 66 | 64 | 43 |
| C / embedded C | strong | 31 | 60 | 11 | 8 |
| Unit/HIL/SIL testing & validation | working | 25 | 36 | 17 | 18 |
| CUDA / GPU kernels | strong | 16 | 4 | 15 | 27 |
| Deep learning (general) | strong | 23 | 4 | 26 | 39 |
| ARM Cortex-M / MCU | strong | 14 | 30 | 6 | 2 |
| TensorRT / Jetson / edge deployment | strong | 12 | 6 | 24 | 19 |
| Computer vision (OpenCV/YOLO/detection) | strong | 19 | 7 | 47 | 29 |
| Linux (userland / admin) | strong | 25 | 41 | 24 | 15 |
| RTOS (any) | working | 17 | 37 | 7 | 3 |
| ROS / ROS2 | strong | 13 | 6 | 42 | 18 |
| Ethernet / TCP-IP / networking | working | 15 | 26 | 9 | 5 |
| Cloud (AWS/GCP/Azure) | none | 18 | 6 | 18 | 28 |
| CI/CD / DevOps | none | 18 | 21 | 16 | 16 |
| Docker / containers / K8s | none | 15 | 7 | 14 | 21 |
| CAN / CAN-FD / LIN | none | 8 | 18 | 3 | 0 |
| BSP / board bring-up | exposure | 8 | 18 | 2 | 1 |
| Embedded Linux (kernel/drivers/Yocto) | exposure | 11 | 23 | 4 | 2 |
| Path planning / navigation / autonomy | exposure | 9 | 3 | 30 | 14 |
| LiDAR / point cloud / 3D | exposure | 10 | 4 | 31 | 14 |
| Sensor fusion / Kalman / IMU | exposure | 8 | 6 | 24 | 11 |
| SLAM / localization / odometry | exposure | 5 | 2 | 19 | 8 |
| Functional safety / MISRA / AUTOSAR | none | 7 | 15 | 5 | 1 |
| Bootloader / secure boot / OTA | none | 5 | 11 | 2 | 0 |
| MLOps / serving | none | 9 | 0 | 3 | 16 |

Full 70-row table is in the CSV.

## Gap ranking (demand x depth penalty: none 1.0, exposure 0.6, working 0.2)

1. Cloud, CI/CD, Docker/K8s, MLOps. These are zero-evidence and hit all three tracks. The planned telemetry_gateway (Docker, k3s, GitHub Actions) and LLMOps projects close them.
2. Production-scale ownership. This is a seniority signal, not a skill. Only shipped and deployed work moves it.
3. CAN and automotive buses. 18% of firmware roles, the biggest hardware-specific gap. Boards are owned, but no project exists.
4. C++ depth. It is the most-asked skill after Python (52% overall, 66% of firmware) and rated "working". Two of three interview losses came from C++ fluency.
5. Robotics autonomy stack: path planning (30% of robotics roles), LiDAR/point cloud (31%), sensor fusion (24%), SLAM (19%). All are exposure only.
6. Embedded Linux, BSP and bootloader. Embedded Linux is 23% of firmware roles, BSP 18%, bootloader/OTA 11% and are exposure or none.
7. Safety standards (MISRA, ISO 26262). These are a ceiling, not something to build toward.

## Where the planned projects land

| Project | Closes | Coverage |
|---|---|---|
| telemetry_gateway (BBB + MPU6050, C++17 epoll, Docker, k3s, CI) | Embedded Linux, networking, C++, Docker/K8s, CI/CD, IMU | Strong |
| inference_engine (C++/CUDA, SmolVLA, Jetson) | C++, CUDA, TensorRT-style deployment, LLM inference, profiling | Strong |
| custom RTOS (STM32 L476RG) | RTOS depth, Cortex-M, scheduling, bare-metal | Strong. Add a bootloader/OTA stage. |
| llmops_model_serving | MLOps, cloud, serving | Partial |
| turret virtual build | Control, sensors | Partial |

Uncovered by any plan: CAN bus, SLAM/sensor fusion/point cloud, and a bootloader.

## Suggested additions, highest return first

1. A CAN node project (two STM32/CAN modules, with bootloader and OTA over CAN). It closes CAN, bootloader and OTA, and adds an automotive-firmware story. It could fold into the RTOS project as its final stage.
2. A robotics perception and state-estimation project: IMU + ToF/GPS fusion with an EKF, then 2D SLAM or LiDAR odometry on the Jetson in ROS2. It closes sensor fusion, SLAM and point cloud together.
3. Make sure the telemetry_gateway CI/CD stage actually ships. Cloud, CI/CD and Docker are the cheapest wins and apply to every track.

## Caveats

- Matching is regex over each role's extracted keyword lists, not the full posting. Spot-check on 33 raw JDs found 93% agreement. The lists miss mostly soft skills (simulation, agile, testing), so those are undercounted.
- "Python", "C++" and "testing" are still broad matches.
- Depth ratings for FreeRTOS and C++ follow the repo-landmines and interview-log notes.

## Cleanup done in ~/job_search

Moved to `.trash/stale_20261006/`:
- all `.bak*` copies of the fit, outreach and submitted logs
- `fit_analysis_log.json.corrupted`
- the old `skills_surveys.html`
- the two `hive_embedded*` job folders
- the empty `logs/` folder was removed

Kept: the live logs (fit_analysis_log.json, outreach_log.json, submitted_log.csv), tracker_search_profile.md (the shared alert-search config), startup_channels_prompt.md and workday_fill.html.
The last two are unrelated to skills, so say if you want them moved too.
