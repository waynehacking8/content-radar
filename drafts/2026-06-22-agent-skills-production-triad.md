---
id: agent-skills-production-triad
platform: linkedin
status: draft
publish_date: 2026-06-22
title: "agent-skills-production-triad"
angle: accessible-lesson
tags:
  - AIAgents
  - LLM
  - EngineeringPractices
  - BuildingInPublic
  - SoftwareEngineering
sources:
  - https://github.com/addyosmani/agent-skills
  - https://fly.io/blog/everyone-write-an-agent/
---

The best way to learn what AI agents are actually bad at is to build one that does something consequential.

Addy Osmani open-sourced a library of "agent skills" — production-grade workflows for common engineering tasks like code review, test generation, and deployment checks. They're not magic; they're structured prompts with quality gates and feedback loops. But reading through them taught me more about reliable agent design than most blog posts have.

What stands out: every skill has an explicit definition of done, a checkpoint where a human can intervene, and a fallback for when the model outputs garbage. That's the triad that separates a demo from something you can actually put in a pipeline. If you're curious about agents and haven't built one yet, pick a boring internal task — summarizing PRs, triaging bug reports — and instrument it the way these skills do. You'll hit the real failure modes faster than any tutorial will show you.

#aiagents #llm #engineeringpractices #buildinginpublic #softwareengineering
