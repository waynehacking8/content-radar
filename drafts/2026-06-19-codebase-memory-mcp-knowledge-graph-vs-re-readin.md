---
id: codebase-memory-mcp-knowledge-graph-vs-re-readin
platform: linkedin
status: draft
publish_date: 2026-06-19
title: "codebase-memory-mcp: knowledge graph vs. re-reading files"
angle: accessible-lesson
tags:
  - llm
  - agentdev
  - codetools
  - contextwindow
  - mcp
sources:
  - https://github.com/DeusData/codebase-memory-mcp
---

Your AI coding tool is spending most of its tokens just figuring out what your codebase looks like. Every session it re-reads files, re-parses imports, re-traces dependencies — before it even starts helping you.

codebase-memory-mcp takes a different approach: index the repo once into a persistent knowledge graph, then answer queries against that graph in under a millisecond. The claimed result is 99% fewer tokens per query. That matters because token cost in agentic workflows isn't just about money — it's about latency and context window limits. A 200k-token context sounds huge until your codebase has 2,000 files.

The approach works by treating code structure as a graph problem: functions, classes, imports, and references become nodes and edges. Querying "what calls this function?" becomes a graph traversal, not a grep. It supports 158 languages and ships as a single static binary with zero dependencies.

If you're building agents that need to reason over large codebases, the retrieval layer deserves as much attention as the model itself.
