---
id: design-md-agent-contracts
platform: linkedin
status: draft
publish_date: 2026-06-27
title: "design-md-agent-contracts"
angle: opinionated-take
tags:
  - AgentDevelopment
  - DesignSystems
  - AIEngineering
  - SoftwareArchitecture
  - DeveloperExperience
sources:
  - https://github.com/google-labs-code/design.md
---

CLAUDE.md taught agents your project structure. DESIGN.md teaches them your brand.

Google Labs just proposed a format spec — a structured file that describes a visual identity (colors, typography, spacing, component patterns) in a way coding agents can actually use. The idea: stop pasting design tokens into every prompt. Give the agent a persistent, machine-readable contract for your design system instead.

I think this is the right direction, and it's bigger than UI work. We're slowly building a grammar for talking to agents about systems. CLAUDE.md = project structure. DESIGN.md = visual identity. What's next — SCHEMA.md for data contracts? INFRA.md for deployment topology? Each file is a machine-readable expression of domain knowledge that used to live only in someone's head.

For solutions engineers, this framing is useful: part of the job becomes authoring and maintaining these contracts — translating organizational knowledge into agent-legible formats. That's a real skill, and it compounds.

#agentdevelopment #designsystems #aiengineering #softwarearchitecture #developerexperience
