---
id: 250-documents-can-backdoor-any-model
platform: linkedin
status: draft
publish_date: 2026-07-19
title: "250 documents can backdoor any model"
angle: accessible-lesson
tags:
  - AI
  - AISecurity
  - LLM
  - MachineLearning
  - Anthropic
sources:
  - https://www.anthropic.com/research/small-samples-poison
---

Anthropic ran a joint study with the UK AI Security Institute and found something counterintuitive: it takes roughly the same small number of poisoned documents — around 250 — to backdoor a large model as it does a small one. Scale doesn't protect you here. A bigger model doesn't dilute a fixed number of bad examples, because it isn't averaging over more of them; it's still learning from the same handful of poisoned samples relative to its training run.

For anyone deploying LLMs against real data pipelines, this matters more than it sounds. "We have a huge, diverse training/fine-tuning corpus" is not a security argument on its own. Data provenance and filtering matter regardless of how much compute or data you're throwing at the problem.

If you're building systems that ingest external content — scraped docs, user uploads, third-party feeds — into anything that touches a model's context or weights, treat that ingestion path like an attack surface, not a convenience.
