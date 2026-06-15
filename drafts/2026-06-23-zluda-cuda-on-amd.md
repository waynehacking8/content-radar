---
id: zluda-cuda-on-amd
platform: linkedin
status: draft
publish_date: 2026-06-23
title: "zluda-cuda-on-amd"
angle: tool-spotlight
tags:
  - GPU
  - CUDA
  - mlops
  - aiinfrastructure
  - opensource
sources:
  - https://www.phoronix.com/review/radeon-cuda-zluda
---

AMD quietly funded a drop-in CUDA replacement. Now it's open source. The benchmarks are mixed — but that's not the interesting part.

ZLUDA lets you run unmodified CUDA code on AMD GPUs via ROCm. AMD funded the project, things got complicated, and it's now fully open. Some workloads run well. Others don't yet.

What's actually worth paying attention to is what this signals: CUDA lock-in is a real problem the industry is actively trying to solve. If you're designing infrastructure for ML workloads, your choice of GPU compute shapes everything downstream — libraries, tooling, cost, and availability during supply crunches.

CUDA didn't win because it's technically superior in every dimension. It won because it was first with a mature ecosystem. ZLUDA, ROCm, and similar projects are the industry's hedge against that monoculture. They don't need to beat CUDA — they just need to make switching possible.

GPU vendor diversity is infrastructure strategy, not a hobby project.

#gpu #cuda #mlops #aiinfrastructure #opensource
