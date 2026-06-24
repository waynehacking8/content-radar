---
id: evaluating-agentic-outputs-three-outputs-one-sco
platform: linkedin
status: draft
publish_date: 2026-07-02
title: "evaluating-agentic-outputs-three-outputs-one-score"
angle: opinionated-take
tags:
  - llmevaluation
  - agenticsystems
  - aiengineering
  - mlops
  - datascience
sources:
  - https://arxiv.org/abs/2606.24839v1
---

A new paper on evaluating agentic data analysis systems makes a point that should be obvious but often isn't: agents produce three kinds of output simultaneously — code, numerical results, and verbal diagnostics. Evaluating any one in isolation misses the picture.

The harder problem it surfaces: when a human evaluator and the agent disagree, you need to know whether it's genuine factual disagreement or just a formatting or phrasing difference. Most teams aren't making that distinction. They're measuring agreement on outputs that weren't designed to be unambiguously comparable, then calling it accuracy.

If you're deploying any agentic system and reporting metrics, ask yourself: am I measuring agreement, or correctness? They're not the same thing, and conflating them will mislead you about what's actually working. Evaluation design is part of the system design, not an afterthought.
