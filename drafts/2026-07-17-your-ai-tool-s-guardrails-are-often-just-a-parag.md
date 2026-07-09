---
id: your-ai-tool-s-guardrails-are-often-just-a-parag
platform: linkedin
status: draft
publish_date: 2026-07-17
title: "Your AI tool's guardrails are often just... a paragraph"
angle: opinionated-take
tags:
  - AI
  - LLM
  - PromptEngineering
  - AISafety
  - SoftwareEngineering
sources:
  - https://github.com/asgeirtj/system_prompts_leaks
---

Ever wonder why your AI coding assistant refuses certain requests, or always structures its answers a certain way? Often it's not a hard-coded rule at all — it's a system prompt, a plain-English instruction sitting in front of every conversation. A repo tracking leaked system prompts across Claude, GPT, Gemini, and others makes this very visible: a lot of what feels like model 'personality' or 'policy' is really just carefully written instructions.

I find this useful to sit with rather than treat as a gotcha. It's honest about what these guardrails actually are: a behavior specification, not a security boundary. Text-based instructions can be a strong steering mechanism, but they're not the same as an access control system, and conflating the two is how teams end up over-trusting prompt-based safety in places that need real enforcement. If you're building on top of these models, it's worth knowing which of your guardrails are prompts and which are actual constraints — they fail very differently.
