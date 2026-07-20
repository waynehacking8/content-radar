---
id: writing-your-own-agent-demystifies-the-hype
platform: linkedin
status: draft
publish_date: 2026-07-24
title: "Writing your own agent demystifies the hype"
angle: accessible-lesson
tags:
  - aiagents
  - llm
  - softwareengineering
  - buildinpublic
sources:
  - https://fly.io/blog/everyone-write-an-agent/
---

There's a good piece by Thomas Ptacek making a simple point: you understand agents by building one, not by reading about them. He's right, and it only takes an afternoon.

Strip away the marketing and an agent is a loop: call the model, let it pick a tool, run the tool, feed the result back, repeat until it decides it's done. No orchestration framework required to get the first version working. Doing this yourself clears up two things fast. First, most of an agent's "intelligence" is really the tools and the system prompt around it, not some emergent magic. Second, you immediately feel where it breaks: infinite loops, hallucinated tool arguments, no sense of when to stop.

If you work with developers who are skeptical about agents, or excited about them for the wrong reasons, this is the fastest way to get everyone talking about the same thing instead of the idea of it.
