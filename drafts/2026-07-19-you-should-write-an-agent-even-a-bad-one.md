---
id: you-should-write-an-agent-even-a-bad-one
platform: linkedin
status: draft
publish_date: 2026-07-19
title: "You should write an agent, even a bad one"
angle: accessible-lesson
tags:
  - AI
  - agents
  - buildinpublic
  - softwareengineering
sources:
  - https://fly.io/blog/everyone-write-an-agent/
---

There's a good point buried in a recent piece about agents: you don't really understand how they work until you build one yourself, the same way you only think you understand a bicycle until you try to ride it. Reading about tool-calling loops and reasoning traces is not the same as watching your own agent confidently do the wrong thing with a tool you gave it. That failure teaches you more about prompting, scoping, and guardrails than any writeup will. This matters beyond curiosity. If your job involves recommending, evaluating, or deploying agentic systems for other people, secondhand understanding shows. You'll miss the failure modes that only show up when you're the one debugging why the agent looped, or why it picked the wrong tool with total confidence. A weekend spent wiring up a small agent against a real API, then watching it break, is worth more than a stack of vendor decks. Build the small, boring version before you evaluate the big one.
