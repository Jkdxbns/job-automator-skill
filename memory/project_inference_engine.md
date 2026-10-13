---
name: project-inference-engine
description: "From-scratch inference engine for a VLA on Jetson — primary Edge-AI project, gap-closer, C++/CUDA depth, track-record substitute"
metadata:
  node_type: memory
  type: project
  originSessionId: b3517308-bd3c-4152-a8c8-4d1c22446930
  modified: 2026-08-28T22:05:59.268Z
---

**DIRECTION FINALIZED 2026-07-14 (supersedes the old 4-backend CNN plan).** The earlier design
(x86/CUDA/NEON/Cortex-M, MobileNetV2, bit-exactness) is ARCHIVED at
`~/Desktop/projects/inference_engine/DESIGN_ARCHIVED_multibackend_cnn.md`. Do NOT build that.

**Current project:** a from-scratch C++/CUDA inference engine for a **VLA (SmolVLA)** on the
**Jetson Orin Nano Super** (SM 8.7, CUDA 12.6, TensorRT 10.7). Full mentor guidebook at
`~/Desktop/projects/inference_engine/GUIDEBOOK.md`.

**Locked decisions:**
- **HYBRID kernel depth:** from scratch = graph/IR runtime, offline compiler (model→flat binary),
  per-channel INT8 quantization + fixed-point requant, arena memory planner, KV/attention-prefix
  handling, AND one tiled GEMM + one attention kernel hand-written in CUDA (benchmarked vs cuBLAS).
  cuBLAS/cuDNN for the remaining heavy matmuls. (Industry-standard; not "reinvent cuBLAS.")
- **Target = SmolVLA**, which has a **flow-matching action-expert head** (NOT autoregressive tokens).
  So: encoder runs ONCE per observation, then the head does a FEW iterative flow steps → action
  chunk. No growing KV cache, not one pass either. (OpenVLA would be autoregressive → full LLM
  decoder; deliberately NOT chosen.) This nuance is the #1 interview probe — get it exact.
- **Weight-only INT8/INT4 + FP16 activations** (activation outliers make full-INT8 hard; GPTQ/AWQ).
  Bit-exactness is NOT a goal (FP16 reductions order-dependent) — that was the old CNN design.
- **Staged build:** tiny MLP/CNN (plumbing) → single transformer block (kernels vs cuBLAS) → full
  SmolVLA. Correctness vs PyTorch/ONNX reference BEFORE optimizing. Benchmark vs TensorRT (not
  TensorRT-LLM).
- Develops against a STOCK SmolVLA checkpoint; the fine-tuned one from [[project-vla-finetune]]
  drops in later.
- Builds on Justin's real prior CUDA work (VGG16 coalesced kernels).

Related: [[project-vla-finetune]], [[reference-jetson-ssh]], [[feedback-resume-defensibility]].
