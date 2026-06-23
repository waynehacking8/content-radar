---
id: airllm-why-70b-on-4gb-works-and-what-it-teaches-
platform: linkedin
status: draft
publish_date: 2026-06-29
title: "AirLLM: why 70B on 4GB works, and what it teaches you"
angle: accessible-lesson
tags:
  - llm
  - aiinfrastructure
  - mlops
  - aiengineering
sources:
  - https://github.com/lyogavin/airllm
---

Running a 70B model on a 4GB GPU sounds like a miscalculation. The technique behind AirLLM is worth understanding even if you never run it yourself.

Standard inference loads the full model into GPU memory at once. AirLLM layers it — loading and offloading transformer weights one block at a time as the forward pass progresses. You trade throughput for memory footprint. On the right workload (low concurrency, latency-tolerant), that tradeoff is acceptable.

What makes this useful as a learning artifact: it makes the memory hierarchy explicit in a way most inference frameworks hide. GPU memory during inference holds three things — model weights, the KV cache, and intermediate activations. These compete. When someone tells you their inference is slow or expensive, knowing which of those three is the bottleneck is the starting point for every diagnosis.

Quantization, layer offloading, and pipeline parallelism are all answers to the same constraint: weights are large and memory is finite. Understanding the problem before reaching for the solution is how you make defensible infrastructure recommendations.
