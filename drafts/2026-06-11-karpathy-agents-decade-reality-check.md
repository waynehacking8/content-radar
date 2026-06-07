---
id: karpathy-agents-decade-reality-check
platform: linkedin
status: draft
publish_date: 2026-06-11
title: "karpathy-agents-decade-reality-check"
angle: opinionated-take
tags:
  - aiagents
  - softwareengineering
  - llmops
  - systemsthinking
  - ai
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy recently said it will take a decade to work through the fundamental issues with AI agents. That kind of measured take is rare right now, and I think he's calibrated correctly.

The current narrative treats agent failures as capability gaps — problems that will dissolve as models get better. But many of the real issues are systems problems: error propagation across multi-step pipelines, inconsistent tool-use reliability, difficulty specifying what success means over a long task, and the trust question of what an agent is actually allowed to do unsupervised.

A larger context window doesn't fix those.

What this means practically: if you're building agentic workflows today, design for the failure modes you can see right now. Build in human checkpoints. Make the agent's action log auditable. Keep the blast radius of individual steps small.

Don't wait for the model to become reliable enough to remove the guardrails. Build systems that stay safe even when the model isn't. That's engineering, not pessimism.
