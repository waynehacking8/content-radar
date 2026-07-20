---
id: karpathy-on-agents-it-s-a-decade-long-problem
platform: linkedin
status: draft
publish_date: 2026-07-22
title: "Karpathy on agents: it's a decade-long problem"
angle: opinionated-take
tags:
  - aiagents
  - llm
  - softwareengineering
  - aieng
sources:
  - https://www.dwarkesh.com/p/andrej-karpathy
---

Andrej Karpathy said something recently that matched my own experience deploying agents more than any benchmark has: it will take about a decade to work through the real issues with agentic systems. Not because the models aren't smart enough, but because agents fail in ways that look nothing like traditional software bugs. They forget context, misjudge when a task is actually done, and recover from errors inconsistently.

This is why so many agent demos look magical and so many agent deployments quietly get scaled back six months later. The gap isn't capability, it's reliability engineering: retries, verification steps, human checkpoints, and knowing which failure modes are acceptable to automate away and which aren't.

If you're building or buying agentic tooling right now, the useful question isn't "how capable is the model." It's "what happens on the 1-in-20 run where it's confidently wrong," and whether your system notices.
