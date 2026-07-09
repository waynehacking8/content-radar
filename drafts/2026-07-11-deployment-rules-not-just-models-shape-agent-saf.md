---
id: deployment-rules-not-just-models-shape-agent-saf
platform: linkedin
status: draft
publish_date: 2026-07-11
title: "Deployment rules, not just models, shape agent safety"
angle: opinionated-take
tags:
  - AI
  - AIsafety
  - MultiAgent
  - SolutionsArchitecture
  - LLM
sources:
  - https://arxiv.org/abs/2607.07695v1
---

A new paper on institutional red-teaming makes a point I think gets underweighted in most AI deployment conversations: they held the agents, the objectives, and the task state completely fixed, and varied only the deployment rules — and that alone caused meaningfully different collective behavior in a multi-agent system. Not a different model. Not a different prompt. Just different rules about how agents interact.

This matches what I've seen building and deploying AI systems: teams spend enormous energy debating which model to use, then wire up the surrounding orchestration, permissions, and interaction rules almost as an afterthought. But that surrounding structure is often where the actual risk and actual reliability get decided. It's a useful reframe if you're the person responsible for taking an AI system from 'works in the demo' to 'works safely in a real environment' — your leverage isn't only in model selection, it's in the rules you set around it.
