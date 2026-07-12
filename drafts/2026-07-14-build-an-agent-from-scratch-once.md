---
id: build-an-agent-from-scratch-once
platform: linkedin
status: draft
publish_date: 2026-07-14
title: "Build an agent from scratch, once"
angle: accessible-lesson
tags:
  - AIAgents
  - LLM
  - SoftwareEngineering
  - BuildingInPublic
sources:
  - https://fly.io/blog/everyone-write-an-agent/
---

Thomas Ptacek's line stuck with me: you don't really understand agents until you've built one, even a bad one. Not integrated a framework, not called an API that says "agent" on the tin, actually built the loop yourself: tool calls, memory, the works.

I get why frameworks are tempting. But abstractions hide the exact mechanics you need when something breaks in production: why the model called the wrong tool, why the loop didn't terminate, why the plan drifted. If you've never written that loop by hand, debugging it in someone else's system is guesswork.

This matters more the closer you get to customer-facing, forward-deployed work. Clients don't want a framework explanation, they want you to know why their agent did what it did, on their data, in their environment. That kind of fluency only comes from having built the thing once without training wheels.

If you work with agents professionally, spend a weekend writing one from scratch. It's the fastest way to earn the intuition.

#aiagents #llm #softwareengineering #buildinpublic
