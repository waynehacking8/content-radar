---
id: what-agent-skills-actually-are
platform: linkedin
status: draft
publish_date: 2026-07-09
title: "What 'agent skills' actually are"
angle: accessible-lesson
tags:
  - AI
  - LLM
  - AgentEngineering
  - SoftwareEngineering
  - DevTools
sources:
  - https://github.com/addyosmani/agent-skills
---

Everyone's suddenly talking about 'skills' for AI coding agents, and it's worth pausing on what that actually means. A skill isn't a bigger prompt — it's a packaged workflow: the steps, quality gates, and judgment calls a senior engineer applies to a recurring task, written down so an agent can follow them consistently. addyosmani's agent-skills repo is a good example: instead of hoping the model remembers to write tests, check edge cases, or follow a review checklist, you encode that process once and reuse it. The interesting shift here isn't the AI part, it's the systems-engineering part: you're building repeatable procedures with defined inputs, outputs, and failure modes, the same discipline you'd apply to any production pipeline. That's the piece I think gets missed when people frame this as 'prompt engineering.' It's really process design, and process design is what actually holds up when you move from a demo to something a team depends on daily.

what's your team encoding as reusable skills vs. leaving to chance?
