---
id: codex-output-tokens-56x-what-it-means
platform: linkedin
status: draft
publish_date: 2026-07-01
title: "Codex output tokens 56x — what it means"
angle: opinionated-take
tags:
  - llm
  - aiengineering
  - enterpriseai
  - agenticworkflows
  - productengineering
sources:
---

OpenAI shared an internal number this week that tells you more about enterprise AI adoption than any benchmark.

Median output tokens from their internal Codex usage grew 56x in Research, 32x in Customer Support, 27x in Engineering, and 13x in Legal since November 2025.

What this signals: AI isn't writing quick summaries anymore. It's doing extended, multi-step work across the board. The tasks are getting longer and more complex month over month.

For anyone building AI systems for enterprise clients, this is the pattern to pay attention to. Latency budgets and cost models that worked for short completions break down completely at 56x scale. Streaming UX stops being optional. Output token quotas become a hard constraint, not an afterthought.

If you're designing agentic workflows today without thinking through what happens when the model needs to reason for thousands of tokens, you're building for 2024 usage patterns.
