---
id: long-agent-tasks-don-t-need-bigger-context-windo
platform: linkedin
status: draft
publish_date: 2026-07-09
title: "Long agent tasks don't need bigger context windows"
angle: accessible-lesson
tags:
  - AIAgents
  - LLM
  - AgenticAI
  - SystemDesign
sources:
  - https://arxiv.org/abs/2607.05378v1
---

New research this week (CompactionRL, and a related debate coming out of the AI Engineer World's Fair) is converging on the same point: for agents doing long-horizon work, the fix for running out of context isn't a bigger window, it's compaction — periodically summarizing what happened so far and continuing from that summary instead of the raw transcript.

This matters for anyone building agents that run longer than a few minutes: a coding agent refactoring a large repo, a support agent working a multi-day ticket, a research agent chasing a lead across dozens of sources. The naive approach — stuff everything into context and hope the window is big enough — degrades quietly. The model starts losing track of earlier decisions long before it ever hits a hard token limit.

Compaction is really an old idea, summarizing state instead of replaying history, applied to LLM agents. Worth internalizing if you're designing anything meant to outlive a single request-response turn.
