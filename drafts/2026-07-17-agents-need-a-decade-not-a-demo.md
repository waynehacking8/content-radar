---
id: agents-need-a-decade-not-a-demo
platform: linkedin
status: draft
publish_date: 2026-07-17
title: "Agents need a decade, not a demo"
angle: opinionated-take
tags:
  - AIagents
  - MLOps
  - SolutionsArchitecture
  - PragmaticAI
  - EnterpriseAI
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Karpathy said something recently that matched what I've seen firsthand: agents will take about a decade to work through their issues, not a product cycle. That's not pessimism, it's an honest timeline.

The demo is the easy 80%. An agent that reads a repo, writes code, and opens a PR looks like magic in a five-minute video. The hard 20% is everything a demo skips: what happens when the agent is confidently wrong, when it has access it shouldn't use, when its output needs a human to actually be accountable for it. Those aren't bugs to patch, they're the actual shape of the problem.

This is exactly why the interesting work right now isn't "can an agent do X," it's "what scaffolding makes X safe to hand to an agent." Permissions, guardrails, human checkpoints, rollback paths. Less flashy than a demo, far more valuable in production.

If you're building or buying agent systems, budget for the decade, not the demo.
