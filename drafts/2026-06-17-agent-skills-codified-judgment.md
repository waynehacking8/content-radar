---
id: agent-skills-codified-judgment
platform: linkedin
status: draft
publish_date: 2026-06-17
title: "agent-skills-codified-judgment"
angle: accessible-lesson
tags:
  - aiagents
  - agentengineering
  - llmops
  - softwareengineering
  - buildingaiproducts
sources:
  - https://github.com/addyosmani/agent-skills
  - https://github.com/obra/superpowers
---

The gap between a demo agent and a production agent isn't model quality. It's codified judgment.

Two projects surfaced this week — agent-skills and superpowers — both tackling the same problem: how do you get a coding agent to behave like a senior engineer instead of an intern who just read the docs?

The answer, it turns out, is that you write it down. Quality gates. Review checklists. Rollback procedures. Patterns for when to stop and ask versus when to proceed. Senior engineers carry this knowledge implicitly; agents need it explicit and portable.

This matters at the solutions layer. When you're helping a customer deploy an AI coding workflow, the model is almost never the bottleneck. What's missing is the surrounding structure: the guardrails, the escape hatches, the handoff points where a human re-enters the loop.

"Skills" packages are an attempt to make that structure reusable. It's still early, but the direction is right: agent behavior is an engineering artifact, not a prompt.

#aiagents #agentengineering #llmops #softwareengineering #buildingaiproducts
