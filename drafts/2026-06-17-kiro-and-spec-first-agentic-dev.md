---
id: kiro-and-spec-first-agentic-dev
platform: linkedin
status: draft
publish_date: 2026-06-17
title: "Kiro and spec-first agentic dev"
angle: tool-spotlight
tags:
  - AgenticAI
  - SoftwareEngineering
  - AITools
  - LLM
  - DeveloperExperience
sources:
  - https://kiro.dev/blog/introducing-kiro/
---

Kiro launched with a design principle I find genuinely interesting: before the agent writes any code, it writes a spec. Requirements, data models, API contracts—all captured in structured documents that the model and the developer agree on before implementation starts.

This is the opposite of how most people use coding agents today. The typical loop is prompt, review, prompt again, patch the surprises. Kiro's bet is that most of the wasted time in that loop comes from misaligned assumptions that a spec would have surfaced upfront.

This resonates with me. The model usually isn't failing because it can't code—it's failing because "build me a user authentication flow" contains ten unstated decisions that the model guesses and you disagree with later. Writing those decisions down first isn't overhead. It's the actual engineering work.

Whether Kiro specifically succeeds isn't the point. The pattern of spec-first agentic development is worth watching. It's a more honest model of what working with AI on real systems actually requires.

#agenticai #softwareengineering #aitools #llm #developerexperience
