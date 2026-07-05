---
id: program-as-weights-fuzzy-functions
platform: linkedin
status: draft
publish_date: 2026-07-09
title: "Program-as-weights: fuzzy functions"
angle: accessible-lesson
tags:
  - LLM
  - SoftwareEngineering
  - AIArchitecture
  - PromptEngineering
sources:
  - https://arxiv.org/abs/2607.02512v1
---

A new paper calls this out directly: plenty of everyday programming tasks — flagging an important log line, fixing a malformed JSON blob, ranking search results by intent — resist clean rule-based logic. Teams increasingly just hand these to an LLM API call and move on, trading locality and reproducibility for something that actually works.

That trade is usually made without naming it. The paper frames it as a real paradigm: "program-as-weights," where a fuzzy function's behavior lives in a model's weights rather than in explicit code you can read line by line. It's a useful mental model because it makes the tradeoff visible instead of accidental — you're not writing worse code, you're choosing a different kind of function for a task that never had a clean rule-based answer in the first place.

The practical takeaway: when you reach for an LLM call inside a pipeline, be deliberate about it. Version the prompt like you'd version code, test it like you'd test a function, and expect it to fail differently than code does — not because it's less rigorous, but because it's a different kind of building block.

#llm #softwareengineering #aiarchitecture #promptengineering
