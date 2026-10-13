---
name: feedback-resume-project-selection
description: Rules for selecting projects when tailoring resumes — what to include vs exclude based on JD relevance
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 550f8423-8a39-4607-935f-af83f2cd8b6e
---

Only include projects that are directly supported by the JD's requirements. Do not add projects because they show general technical depth if they don't match what the role actually asks for.

**Specific rules:**
- CUDA / GPU kernel projects → only include if JD explicitly mentions GPU, inference optimization, or CUDA
- ROS / MoveIt projects → only include if JD explicitly mentions ROS or middleware; custom robotics stacks don't imply ROS
- STM32 bare-metal / embedded C projects → include for any role involving hardware interfacing, sensor integration, or embedded software
- Do not add skills (e.g. ROS2, MoveIt, DH parameters) to the skills section if their only backing projects were cut

**Why:** User corrected this on LinkTech Robotics Software Engineer role — ROS Arm project was included despite ROS not appearing in the JD; CUDA project was proposed despite no GPU workload in scope. STM32 bare-metal was correctly identified as more relevant (hardware interfacing, ADC, I2C, interrupts).

**How to apply:** Before finalizing project selection, check each project against the JD's actual technical requirements. If a project's primary keywords don't appear in the JD, cut it in favor of projects that do — even if the cut project shows more impressive technical depth.
