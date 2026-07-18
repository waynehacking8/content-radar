---
id: build-one-before-you-sell-one
platform: linkedin
status: draft
publish_date: 2026-07-18
title: "Build one before you sell one"
angle: accessible-lesson
tags:
  - aiagents
  - forwarddeployedengineering
  - solutionsarchitecture
  - llmops
sources:
  - https://fly.io/blog/everyone-write-an-agent/
---

Last week I built the simplest possible AI agent: a loop that calls an LLM, runs a tool, feeds the result back in, and repeats. That's the entire "big idea" behind most agent frameworks you've seen demoed. The loop itself takes an afternoon. What takes longer, and what nobody shows in the demo video, is everything you bolt on once it starts making real mistakes: limits so it can't spin forever, logging so you can reconstruct why it picked a bad tool, and a kill switch for when it goes off the rails mid-run.

If you're moving toward solutions or forward-deployed engineering, this exercise is worth doing yourself before you ever pitch it to a client. Buyers don't actually want to hear "the agent decided to do X." They want to know what stops it from deciding to do something expensive, irreversible, or embarrassing. You cannot design those guardrails from a blog post or a vendor's marketing page. Build a bad one first, watch it fail, then fix it.
