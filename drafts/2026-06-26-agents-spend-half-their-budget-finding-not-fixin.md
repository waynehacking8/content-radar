---
id: agents-spend-half-their-budget-finding-not-fixin
platform: linkedin
status: draft
publish_date: 2026-06-26
title: "agents-spend-half-their-budget-finding-not-fixing"
angle: opinionated-take
tags:
  - codeagents
  - llmevaluation
  - agentarchitecture
  - softwareengineering
  - ai
sources:
  - https://arxiv.org/abs/2606.24820v1
---

Here's a number worth sitting with: LLM agents solving real code tasks spend roughly half their tool-call budget just locating the fault — before writing a single line of a fix. That's a finding from SHERLOC, a new paper on structured diagnostic localization for code repair agents.

The implication is direct. If you benchmark a code agent by "did it fix the bug," you're measuring the whole pipeline — but half the cost is pure navigation overhead. Better localization isn't a nice-to-have; it's a multiplier on every downstream repair attempt.

This is exactly what gets lost in headline accuracy numbers. Agent systems have stages, and optimizing the wrong stage is expensive. If you're deploying a code agent and it feels slow or costly, the bottleneck probably isn't the edit — it's the search. Measurement has to match the structure of what you're actually running.
