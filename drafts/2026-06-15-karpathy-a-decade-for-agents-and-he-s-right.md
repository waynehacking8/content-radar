---
id: karpathy-a-decade-for-agents-and-he-s-right
platform: linkedin
status: draft
publish_date: 2026-06-15
title: "Karpathy: a decade for agents — and he's right"
angle: opinionated-take
tags:
  - AI agents
  - LLMOps
  - agentic AI
  - software engineering
  - production AI
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy said it'll take a decade to work through the real issues with AI agents. I think that's probably right, and I don't mean it as pessimism.

The agent failure modes I keep seeing in production are not capability failures. The model is usually capable enough. The failures are infrastructure failures: state that doesn't persist correctly, tools called with hallucinated parameters, retry loops that take irreversible actions on ambiguous inputs, authorization boundaries that were never defined because nobody thought they needed to be.

We spent three decades building reliability primitives for distributed systems — circuit breakers, idempotency, dead letter queues, backpressure. We're roughly two years into doing equivalent work for agentic AI. Most of those primitives don't exist yet, and teams are learning what they need by hitting production incidents.

A decade is probably the right timescale for that infrastructure to mature. The interesting work right now is building the early versions of those primitives.

#aiagents #llmops #agentic #softwareengineering #aigengineer
