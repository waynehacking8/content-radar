---
id: the-gap-between-demo-and-production
platform: linkedin
status: draft
publish_date: 2026-07-15
title: "The gap between demo and production"
angle: opinionated-take
tags:
  - AI
  - AgenticAI
  - SolutionsArchitecture
  - SoftwareEngineering
  - LLM
sources:
  - https://kiro.dev/blog/introducing-kiro/
---

Kiro's own launch post has a line that stuck with me: you prompt your way to a working app, it feels like magic, then production asks questions the demo never had to answer. What assumptions did the model make? Why did it choose this schema over that one? Who signs off on the parts you didn't review line by line?

That gap is the actual job now. Writing code with an LLM is the easy 20%. The other 80% is the same as it's always been: understanding failure modes, tracing decisions back to requirements, building in the checkpoints that let a human catch a bad assumption before it ships. Agentic tools are shrinking the time to a working prototype, not the time to a system you can hand to a customer.

If you're moving from building models to deploying them for real users, this is the muscle to build: turning "it works on my machine" into "here's why it's safe to trust."
