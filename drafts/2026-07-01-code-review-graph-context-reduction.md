---
id: code-review-graph-context-reduction
platform: linkedin
status: draft
publish_date: 2026-07-01
title: "code-review-graph-context-reduction"
angle: accessible-lesson
tags:
  - AIEngineering
  - CodeReview
  - DeveloperProductivity
  - LLM
  - SoftwareArchitecture
sources:
  - https://github.com/tirth8205/code-review-graph
---

You're probably burning more tokens than you need to on AI code reviews.

code-review-graph builds a persistent map of your codebase — a local graph that tracks file dependencies, call relationships, and what context is actually relevant for a given change. When you run a review, it loads only the relevant subgraph instead of dumping your whole repo into the context window.

That tracks with something I've observed: most of the tokens in a "review this PR" prompt are filler — files that are technically in scope but irrelevant to the actual diff. An agent that knows your codebase structure ahead of time makes better decisions about what to include.

This matters for cost and latency, but also architecturally. A local-first knowledge graph as a layer between your codebase and your AI tools is a pattern that's going to become standard. The MCP compatibility here is the right call — it means the graph is usable across any agent that supports the protocol.

#aiengineering #codereview #developerproductivity #llm #softwarearchitecture
