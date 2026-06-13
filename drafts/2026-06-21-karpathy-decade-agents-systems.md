---
id: karpathy-decade-agents-systems
platform: linkedin
status: draft
publish_date: 2026-06-21
title: "karpathy-decade-agents-systems"
angle: opinionated-take
tags:
  - aiagents
  - llmops
  - solutionsarchitect
  - agentinfrastructure
  - mlplatform
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy thinks agents will take a decade to get right. I think he's being optimistic.

His point: agents aren't better autocomplete — they're systems that act, and acting introduces a whole class of problems we don't have good answers to yet. Trust, verification, rollback, cost control, permission scoping. Each is its own unsolved engineering problem.

The reflex in this industry is to treat it as a capability problem. Make the model smarter and the issues go away. But watch what actually breaks in production: agents that spend money they shouldn't, write things they shouldn't, retry into infinite loops, or escalate from a blocked task to an adverse action. None of those are fixed by a better model.

What's missing is the surrounding infrastructure. Robust checkpointing. Auditability. Graceful degradation when confidence drops. Human escalation paths that don't require the agent to know it's confused.

A decade might be right. The practitioners who close that gap fastest will be the ones treating agents as distributed systems problems, not NLP problems.

#aiagents #llmops #solutionsarchitect #agentinfrastructure #mlplatform
