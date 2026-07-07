---
id: we-ve-quietly-moved-from-agents-that-code-to-man
platform: linkedin
status: draft
publish_date: 2026-07-13
title: "We've quietly moved from 'agents that code' to 'managing fleets of agents'"
angle: opinionated-take
tags:
  - AIAgents
  - DevTools
  - ClaudeCode
  - AgenticEngineering
sources:
  - https://github.com/ogulcancelik/herdr
  - https://github.com/steipete/CodexBar
---

Two small tools trending this week say a lot about where coding agents actually are: herdr, a terminal multiplexer that shows you which of your several running agents is blocked, working, or done, and CodexBar, a menu-bar app that just tracks usage limits across providers so you don't get surprised mid-task.

Neither tool makes a model smarter. Both exist because a growing number of developers are now running multiple agents concurrently — one on a bug fix, one on a refactor, one reviewing a PR — and the bottleneck has shifted from "can the model do this" to "can I keep track of what all of them are doing, and afford to keep them running."

That's a genuinely different problem than the one most AI tooling was built to solve a year ago. If you're advising a team on adopting agentic coding at scale, the orchestration and observability layer is usually where the real friction shows up, not the model choice.
