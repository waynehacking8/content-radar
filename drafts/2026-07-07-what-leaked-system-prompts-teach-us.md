---
id: what-leaked-system-prompts-teach-us
platform: linkedin
status: draft
publish_date: 2026-07-07
title: "What leaked system prompts teach us"
angle: opinionated-take
tags:
  - PromptEngineering
  - LLM
  - AIAgents
  - SystemDesign
sources:
  - https://github.com/asgeirtj/system_prompts_leaks
---

This week a repo collecting leaked system prompts from Claude, ChatGPT, Gemini, Grok, and tools like Cursor and Copilot cracked 1,300+ stars almost overnight. The interesting part isn't the gossip value of seeing a competitor's prompt — it's that these prompts have converged on a similar shape: explicit tool-use rules, tone constraints, refusal boundaries, and long lists of edge-case handling written in plain English.

That convergence is the actual lesson. System prompts have quietly become the primary interface for controlling model behavior in production, more than fine-tuning or RAG tricks for a lot of teams. If you're building or deploying agents for a client, the system prompt is usually where most of the "why did it do that" debugging ends up. Treating it like throwaway glue code instead of a reviewed, versioned artifact is a mistake I still see teams make. Read a few of these leaks not for tricks to copy, but to see how much real engineering goes into the "boring" instructions layer.
