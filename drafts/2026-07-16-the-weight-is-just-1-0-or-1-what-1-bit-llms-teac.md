---
id: the-weight-is-just-1-0-or-1-what-1-bit-llms-teac
platform: linkedin
status: draft
publish_date: 2026-07-16
title: "The weight is just -1, 0, or +1 — what 1-bit LLMs teach about cost"
angle: accessible-lesson
tags:
  - LLM
  - Quantization
  - MachineLearning
  - AIEngineering
sources:
  - https://arxiv.org/abs/2402.17764
---

Here's a detail worth understanding even if you never touch it directly: some of the newest efficient LLMs store weights as just three values, -1, 0, or +1, instead of the usual 16- or 32-bit floating point numbers. That's what 1-bit (technically 1.58-bit, ternary) LLMs are: round every weight down to one of three states, and most of the matrix multiplication in the network turns into simple addition and subtraction. Memory footprint and compute cost drop sharply, with accuracy holding up surprisingly well at scale. The honest caveat: this isn't yet how the models you call through an API are built, and hardware and tooling support for ternary math is still early. But the underlying idea is worth carrying into any conversation about model cost. Cheaper doesn't only mean smaller model or fewer tokens. It can also mean a fundamentally different number representation doing the same job with a fraction of the resources. That's a lever most teams don't know exists yet.

#llm #quantization #machinelearning #aiengineering
