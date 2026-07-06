---
id: what-leaked-system-prompts-actually-teach-you
platform: linkedin
status: draft
publish_date: 2026-07-08
title: "What leaked system prompts actually teach you"
angle: accessible-lesson
tags:
  - PromptEngineering
  - LLM
  - AI
  - SoftwareEngineering
sources:
  - https://github.com/asgeirtj/system_prompts_leaks
---

There's a repo on GitHub collecting leaked system prompts from most major AI products — Claude, ChatGPT, Gemini, Grok, and the coding-agent tools built on top of them. Read a few back to back and the thing that stands out isn't secret sauce. It's how much of the system prompt is just constraints: don't do this, always do that, prefer this tone, refuse this category of request.

That's a useful correction if you think of "prompt engineering" as clever phrasing that unlocks hidden model capability. In practice, a huge share of what makes a product's AI behave well is unglamorous: explicit boundaries, formatting rules, and fallback instructions for edge cases someone already got burned by. The model is the same underlying model — the difference is how much thought went into fencing it in for a specific use case.

If you're building anything on top of an LLM, that's the actual work — not finding a magic prompt, but writing and maintaining the boring rules that keep behavior predictable.
