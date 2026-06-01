---
id: karpathy-a-decade-for-agents
platform: linkedin
status: draft
publish_date: 2026-06-03
title: "Karpathy: a decade for agents"
angle: accessible-lesson
tags:
  - aiagents
  - llmengineering
  - systemsdesign
  - forwarddeployedengineering
  - reliableai
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy said it'll take a decade to work through the issues with AI agents. My first reaction was "too pessimistic." My second reaction, after building agents daily, was "he's probably right."

The gap isn't capability — agents can already write code, browse the web, and call APIs. The gap is reliability at the tail. In a demo, 95% success looks great. In a production workflow handling thousands of tasks, 5% failure is a disaster. And that last 5% is genuinely hard to fix: failures are rare, hard to reproduce, and often caused by subtle ambiguities that humans would resolve with common sense.

The practical upshot for architects: design for failure. Assume your agent will misunderstand roughly 1 in 20 tasks. Build checkpoints, reversible actions, and human escalation paths. Not because AI is bad — because any complex system eventually hits its edge cases.

Ten years may be pessimistic. But "production-ready agents" is definitely not a 2025 story.
