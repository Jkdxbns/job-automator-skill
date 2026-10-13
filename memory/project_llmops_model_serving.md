---
name: project-llmops-model-serving
description: "Future project idea (not yet scoped): reuse the telemetry_gateway container/K8s/CI-CD pattern but for serving an AI model, to cover cloud/K8s/LLM-serving/RAG gaps for AIML roles"
metadata:
  type: project
  originSessionId: b3517308-bd3c-4152-a8c8-4d1c22446930
  modified: 2026-09-13T06:57:13.316Z
---

Justin flagged on 2026-09-13 that after [[project-telemetry-gateway]] he wants to build a
similar container/deployment project, but serving an **AI model** instead of sensor telemetry,
so the pattern becomes relevant to AIML/LLM roles rather than only embedded/edge roles.

**Why:** this was already identified during the 491-fit-analysis gap recalibration that scoped
telemetry_gateway — the gap categories cloud (31), Kubernetes (24), LLM serving (11), RAG (17),
LangChain (11) are NOT covered by telemetry_gateway (which only proves Docker/K8s/CI-CD/Ethernet/
embedded Linux/networking/C++ for the edge side). A model-serving version of the same
Docker→K8s→CI/CD skeleton would close the cloud/LLM-serving/RAG side instead.

**Status:** idea only, not scoped. No steps, stack, or timeline decided yet — do not start
building or drafting a guidebook until Justin explicitly asks to scope this.

**Likely relationship to other projects (not yet confirmed):**
- [[project-inference-engine]] is the from-scratch C++/CUDA inference engine for SmolVLA on the
  Jetson — that's the model/runtime itself. This new project would be about *deploying and
  operating* a model (containerize, serve behind an API, autoscale/update via K8s, CI/CD), which
  is complementary, not a duplicate. The inference engine's compiled artifact could plausibly be
  the thing this project serves, but that's a possibility to confirm later, not a decision.
- Should stay a separate project from both, the same way [[project-telemetry-gateway]] and
  [[project-embedded-linux-bbb]] were kept separate — one finishable, defensible project per
  resume line beats one merged mega-project.

Related: [[project-telemetry-gateway]], [[project-inference-engine]], [[feedback-resume-defensibility]].
