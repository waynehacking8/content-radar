---
id: llm-inevitabilism-is-an-excuse-to-skip-design-th
platform: linkedin
status: draft
publish_date: 2026-06-09
title: "LLM inevitabilism is an excuse to skip design thinking"
angle: opinionated-take
tags:
  - llmengineering
  - solutionsarchitecture
  - aistrategy
  - systemsdesign
  - aiengineering
sources:
  - https://tomrenner.com/posts/llm-inevitabilism/
---

"LLM inevitabilism" is the belief that every software system will eventually be AI-native — resistance is futile, and the only question is when, not whether.

I find this framing dangerous. Not because AI isn't transformative, but because it short-circuits the design thinking that actually makes AI systems work.

Not every workflow benefits from replacing structured logic with an LLM. Deterministic code is cheaper, faster, more auditable, and easier to debug. The question an architect should ask isn't "can I use an LLM here?" — it's "what does the LLM do better here than structured code?" Usually the answer is: tasks requiring language understanding, flexible reasoning over messy inputs, or synthesizing unstructured information into structured outputs.

When you skip that question and default to "just use an LLM," you get expensive, brittle pipelines where a simple conditional would have worked.

Inevitabilism is a business narrative. Engineering requires judgment about fit.
