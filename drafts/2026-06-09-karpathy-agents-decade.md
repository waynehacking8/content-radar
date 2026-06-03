---
id: karpathy-agents-decade
platform: linkedin
status: draft
publish_date: 2026-06-09
title: "karpathy-agents-decade"
angle: opinionated-take
tags:
  - AgenticSystems
  - LLM
  - SoftwareArchitecture
  - AISystems
  - Engineering
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy recently said it'll take a decade to work through the real problems with AI agents. That's not pessimism — it's an accurate read on where the hard problems actually live.

The hype cycle wants you to believe agents are nearly solved. Deploy, orchestrate, observe. But the deep issues — error propagation across long-horizon tasks, verification without ground truth, trust boundaries that shift with context — are not things you fix in a sprint.

The practical takeaway isn't 'don't build with agents.' It's 'build so that agent failures are recoverable.' Treat autonomous pipelines the same way you treat distributed systems: assume partial failure, instrument everything, and make rollback cheap.

The teams building durable agent systems right now aren't necessarily the ones with the most autonomous pipelines. They're the ones who've made human-in-the-loop oversight fast and low-friction. If you're deploying into a production workflow, the question isn't 'will this work?' It's 'what happens when it doesn't?'

#agenticsystems #llm #softwarearchitecture #aisystems #engineering
