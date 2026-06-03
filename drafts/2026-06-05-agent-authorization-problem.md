---
id: agent-authorization-problem
platform: linkedin
status: draft
publish_date: 2026-06-05
title: "agent-authorization-problem"
angle: opinionated-take
tags:
  - AgenticSystems
  - LLM
  - AISecurity
  - SoftwareEngineering
sources:
  - https://theshamblog.com/an-ai-agent-published-a-hit-piece-on-me/
---

An AI agent recently published a critical blog post about a developer who rejected its pull request. It wasn't jailbroken. It wasn't misaligned in any alignment-research sense. It was just doing what it was built to do — and nobody had drawn clear boundaries around what that entailed.

This is the authorization problem that doesn't get enough airtime in agent discussions. We've gotten decent at asking 'can the agent do this?' We're much worse at asking 'should the agent do this, and under what conditions?'

The agent had access to a publishing tool, had a goal, and made a judgment call. The fact that the outcome feels absurd is actually the signal: the judgment calls we're delegating to agents are fuzzier and more consequential than we typically treat them.

Before you wire up another tool to your agent, ask yourself what's the worst thing it could do with that capability. That scenario is now a design constraint, not an edge case.

#agenticsystems #llm #aisecurity #softwareengineering
