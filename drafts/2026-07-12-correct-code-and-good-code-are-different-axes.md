---
id: correct-code-and-good-code-are-different-axes
platform: linkedin
status: draft
publish_date: 2026-07-12
title: "Correct code and good code are different axes"
angle: accessible-lesson
tags:
  - AIagents
  - ProductDesign
  - ClaudeCode
  - SoftwareEngineering
sources:
  - https://github.com/Leonxlnx/taste-skill
---

A small Claude Code skill called taste-skill is built around a problem a lot of people building with AI have noticed but not named well: an agent can write code that's completely correct and still generic in a way that's hard to point at. Right layout, right components, technically working — and it still reads like it was assembled from the most common answer to every question.

The skill's approach is to give the agent explicit opinions about layout, motion, and typography instead of leaving "good design" as an unstated assumption the model is supposed to infer. That's the more general lesson: capability and taste are different axes. A model can be extremely capable at producing working output while having no signal about which of many working outputs is actually good, because "good" was never in the spec.

If an agent keeps producing correct-but-forgettable results, the fix usually isn't a smarter model — it's making your actual preferences explicit instead of assuming they're obvious.
