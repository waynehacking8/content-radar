---
id: your-gpu-bill-is-a-kernel-problem-before-it-s-a-
platform: linkedin
status: draft
publish_date: 2026-07-18
title: "Your GPU bill is a kernel problem before it's a model problem"
angle: tool-spotlight
tags:
  - GPUs
  - MLInfra
  - Performance
  - CloudCosts
sources:
  - https://hazyresearch.stanford.edu/blog/2024-05-12-tk
---

Most conversations about AI cost jump straight to which model or how many tokens. Hazy Research's 'GPUs Go Brrr' post, and the ThunderKittens kernel library that came out of it, are a good reminder that a lot of the cost is actually decided one layer down, in how efficiently the GPU kernels themselves are written. Vendor-default kernels leave real performance on the table; hand-tuned ones can close a meaningful gap without touching the model at all. You don't need to write kernels yourself to benefit from knowing this. When someone tells you compute is expensive, the honest follow-up question is whether the workload is actually using the hardware well, or just running on defaults. That question, not a bigger GPU order, is often where the real savings live. Worth having in your back pocket the next time a client conversation turns into 'we just need more GPUs.'

#gpus #mlinfra #performance #cloudcosts
