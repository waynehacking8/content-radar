---
id: build-an-agent-yourself
platform: linkedin
status: draft
publish_date: 2026-06-08
title: "build-an-agent-yourself"
angle: building-in-public
tags:
  - AI Agents
  - Building in Public
  - LLM Engineering
  - AI Engineering
  - Solutions Architecture
sources:
  - https://fly.io/blog/everyone-write-an-agent/
---

Fly.io published something I keep thinking about: you only truly understand agents once you've built one. Not read about one—built one.

Agents feel obvious in the abstract (loop, tool call, respond) until you actually run them. Then you hit the things no blog post mentions: the model confidently calls a tool with invalid parameters, retries silently, and produces a result that looks correct but isn't. Or it completes step 3 of 5 and then invents steps 4 and 5 rather than admitting it doesn't know.

These aren't edge cases. They're normal behavior from a system that wasn't designed to know when it's lost.

The best way to build intuition for where agents fail is to watch one fail yourself. Start with a single-tool agent on a task you know cold. Add tools one at a time. The bugs you find in the first 100 runs will shape every agent you design after.

If you're evaluating AI agent products right now, this hands-on instinct is what separates a real technical assessment from a demo-shaped opinion.

#aiagents #buildinginpublic #llmengineering #aiengineering #solutionsarchitecture
