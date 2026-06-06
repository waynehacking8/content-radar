---
id: context-compression-before-the-llm
platform: linkedin
status: draft
publish_date: 2026-06-06
title: "context compression before the LLM"
angle: tool-spotlight
tags:
  - LLMOps
  - agent engineering
  - context window
  - AI infrastructure
  - RAG
sources:
  - https://github.com/chopratejas/headroom
---

Most LLM cost discussions focus on model choice. But there's a cheaper lever: compress what you send before it ever hits the model.

headroom is an open-source library — also available as a proxy and MCP server — that compresses tool outputs, log files, and RAG chunks before they reach the LLM. The claimed reduction is 60–95% fewer tokens with equivalent answer quality.

The insight is straightforward: a lot of what lands in your context window is structurally redundant. Logs repeat timestamps and prefixes. Tool output includes headers and metadata the model doesn't need. RAG chunks overlap. Stripping that noise isn't lossy compression — it's noise removal.

For production agentic systems where every tool call adds to the context, upstream filtering like this can be the difference between a workflow that fits in one call and one that hits your limit halfway through.

If you're building agent pipelines, worth a look before you reach for a bigger context window.

#llmops #agentengineering #contextwindow #aiinfrastructure #rag
