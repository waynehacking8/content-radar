---
id: context-bloat-is-your-real-llm-cost
platform: linkedin
status: draft
publish_date: 2026-06-21
title: "context-bloat-is-your-real-llm-cost"
angle: accessible-lesson
tags:
  - llm
  - agenticsystems
  - contextwindow
  - aiengineering
  - tokencost
sources:
  - https://github.com/chopratejas/headroom
---

Your LLM isn't expensive because the model is slow. It's expensive because you're sending it thousands of tokens it doesn't need.

Tool outputs, logs, file dumps, and RAG chunks get copy-pasted into context in their raw form — verbose JSON, full stack traces, entire config files. Most of that carries very little signal.

headroom is a library (also available as a proxy and MCP server) that compresses all of that before it reaches the model. The claim is 60–95% token reduction with no meaningful drop in answer quality. The core idea is simple: structured data has a lot of redundancy, and you can strip it without losing what the model actually needs to reason over.

For anyone building agentic systems where tools return large payloads, this is the kind of infrastructure detail that compounds fast — lower latency, lower cost, and often better behavior because the model isn't buried under noise.

Context hygiene is underrated. Most teams optimize the model. The better lever is what you feed it.
