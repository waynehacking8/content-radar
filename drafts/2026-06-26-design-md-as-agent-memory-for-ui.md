---
id: design-md-as-agent-memory-for-ui
platform: linkedin
status: draft
publish_date: 2026-06-26
title: "DESIGN.md as agent memory for UI"
angle: opinionated-take
tags:
  - aiagents
  - developertools
  - frontend
  - agentengineering
sources:
  - https://github.com/google-labs-code/design.md
---

We write CLAUDE.md to tell agents how to behave. We write README.md to tell humans how the project works. But there's a gap: nothing tells an agent what your design system looks like.

Google Labs just open-sourced DESIGN.md — a spec format for describing visual identity to coding agents. Commit a structured file documenting your color tokens, typography scale, component names, and brand guidelines. Now every coding session starts with that context already loaded, instead of the agent guessing Bootstrap defaults or inventing arbitrary hex values.

The bigger insight is about agent memory architecture. Agents are stateless between sessions. If you want consistent behavior across a project, you need to externalize implicit knowledge into files the model can read. DESIGN.md does for UI consistency what CLAUDE.md does for workflow.

Small pattern, large surface area. Worth stealing for your own projects even before the spec matures — even a hand-written version beats re-explaining your design tokens every session.
