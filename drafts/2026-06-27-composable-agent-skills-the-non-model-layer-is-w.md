---
id: composable-agent-skills-the-non-model-layer-is-w
platform: linkedin
status: draft
publish_date: 2026-06-27
title: "composable agent skills: the non-model layer is where leverage lives"
angle: accessible-lesson
tags:
  - agentdev
  - llm
  - aiengineering
  - agentic
  - softwareengineering
sources:
  - https://github.com/obra/superpowers
  - https://github.com/openai/skills
---

Agents aren't just models — they're models plus the instructions, tools, and context you hand them. Two projects released this week make that concrete.

obra/superpowers is a software development methodology built around composable skills: small, reusable instruction sets that agents can pick up and use across sessions. openai/skills is a similar idea — skill folders that Codex agents can discover and apply across different projects. Both are solving the same problem: you shouldn't have to re-explain "how to run our test suite" or "how to write a PR description" to every new agent session.

The pattern is worth understanding even if you don't adopt either framework directly. Agentic workflows improve most when you treat the non-model parts — context, instructions, tool definitions — as first-class engineering artifacts. Version-control them. Reuse them. Review them. The model is increasingly a commodity; the skills layer is where teams build durable leverage.

This distinction between model quality and harness quality is what separates one-off AI demos from systems that actually hold up in production.
