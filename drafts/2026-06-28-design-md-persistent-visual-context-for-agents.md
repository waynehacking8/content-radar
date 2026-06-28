---
id: design-md-persistent-visual-context-for-agents
platform: linkedin
status: draft
publish_date: 2026-06-28
title: "DESIGN.md — persistent visual context for agents"
angle: accessible-lesson
tags:
  - agentdevelopment
  - designsystems
  - devtools
  - AI
  - codingagents
sources:
  - https://github.com/google-labs-code/design.md
---

Your coding agent doesn't know what your brand looks like.

Every time you start a new session and ask an agent to build a UI component, you're starting from scratch — describing button radii, color tokens, typography choices all over again. Google Labs just proposed a fix: DESIGN.md, a structured format for describing your visual identity directly to coding agents.

The idea is straightforward. A DESIGN.md file lives in your repo like a README, but instead of explaining what the project does, it explains how it should look. Color palettes, spacing systems, component naming conventions, tone. The agent reads it at context load, and suddenly it has a persistent understanding of your design system without you typing "use our brand blue" for the hundredth time.

This is the right direction. Most teams have a Figma library and a design token file that agents never see. DESIGN.md is a bridge between the human design artifact and machine-readable context. Expect this pattern to spread quickly once a few frameworks adopt it as a default.
