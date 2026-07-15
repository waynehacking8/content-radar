---
id: karpathy-on-the-decade-of-agent-debt
platform: linkedin
status: draft
publish_date: 2026-07-17
title: "Karpathy on the decade of agent debt"
angle: accessible-lesson
tags:
  - AI
  - AgenticAI
  - MachineLearning
  - SystemsEngineering
  - Karpathy
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy said recently that it'll take about a decade to work through the issues with agents — not because the models aren't smart enough, but because the surrounding infrastructure (memory, permissions, evaluation, recovery from mistakes) hasn't caught up.

That framing is useful because it reorders priorities. Most teams I talk to are optimizing the wrong layer: better prompts, bigger context windows, fancier tool schemas. Meanwhile the actual failure points are boring — an agent silently retries a non-idempotent action, nobody defined what "done" means for a task, or there's no audit trail when something goes wrong at 2am.

The interesting work over the next few years isn't going to be prompt engineering. It's going to be building the plumbing: guardrails, observability, rollback, permissioning — the unglamorous systems work that makes an agent safe to hand real responsibility to. That's infrastructure work, and it rewards people who think like engineers first and AI enthusiasts second.
