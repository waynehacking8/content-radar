---
id: agents-need-a-decade-and-that-s-fine
platform: linkedin
status: draft
publish_date: 2026-07-11
title: "Agents need a decade, and that's fine"
angle: opinionated-take
tags:
  - AIagents
  - forwarddeployedengineering
  - softwareengineering
  - llm
  - AI
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Karpathy said something last week that stuck with me: agents will take a decade to work through, not a year. Coming from someone who literally coined 'vibe coding,' that's not pessimism, it's calibration. Everyone building agent demos right now hits the same wall in production: the happy path works beautifully, and then a tool call fails silently, a retry loop burns through a budget, or the agent confidently does the wrong thing with no human in the loop to catch it. That gap between demo and deployment is where forward-deployed and solutions engineering actually live. It's not about picking the flashiest model, it's about building the guardrails, observability, and fallback paths that make an agent trustworthy enough to hand to a customer who can't debug a stack trace. If you're evaluating an agent platform, the pitch to worry about isn't 'look what it can do,' it's 'here's what happens when it's wrong.' That question is doing a lot of the real engineering work these days.
