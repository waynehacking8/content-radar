---
id: karpathy-decade-agents
platform: linkedin
status: draft
publish_date: 2026-06-04
title: "karpathy-decade-agents"
angle: accessible-lesson
tags:
  - AI Agents
  - LLM
  - Production AI
  - AI Engineering
  - Software Architecture
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy says it'll take a decade to work through the fundamental problems with AI agents. Worth sitting with that, given who's saying it.

What does he mean? Agents fail in ways that don't look like failures at first. They hallucinate steps in a multi-tool chain. They get stuck in retry loops. They succeed in demos because demos are short—production is long, messy, and full of edge cases the agent has never seen.

The core gap: LLMs are trained to generate plausible next tokens, not to model the real-world consequences of a sequence of actions. Closing that gap is harder than adding parameters.

This doesn't mean stop building. It means build defensively: short task horizons, explicit checkpoints, scoped actions. An agent that does one thing reliably beats one that claims to do everything.

If someone sells you "fully autonomous" today, ask how it handles failure. That question alone filters most of the hype.

#aiagents #productionai #llm #aiengineering #softwarearchitecture
