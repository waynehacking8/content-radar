---
id: self-improving-loops-still-need-a-human-in-them
platform: linkedin
status: draft
publish_date: 2026-07-08
title: "Self-improving loops still need a human in them"
angle: accessible-lesson
tags:
  - aiagents
  - llm
  - agentdesign
  - aiengineering
sources:
---

The most interesting agent designs I'm seeing right now aren't trying to remove the human from the loop — they're trying to give the human more leverage inside it. Introspection's Roland Gavrilescu describes this as "autoresearch": agents that build and refine their own recipes for a task, but where a person still sits at the center deciding what counts as good enough. That framing matters because a lot of agent hype implies the goal is full autonomy, and in practice that's rarely what actually ships. What ships is a tight feedback loop where the agent proposes, something checks the work, and a human makes the judgment calls that are genuinely hard to encode. If you're designing an agent system, the useful question isn't "how do I remove the human," it's "where exactly does the human's judgment add the most value, and how do I make that checkpoint fast." That's a much more buildable problem.
